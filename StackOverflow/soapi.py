# -*- coding: utf-8 -*-
'''
    Скрипт который собирает данные с сайта StackOverflow с 
    помощью Stack Exchange API и записывает в БД 
'''

import sys
import time
from datetime import datetime
import calendar
import psycopg2
from stackapi import StackAPI, StackAPIError
from files import log

PG_DBNAME    = 'dbname'
PG_USER      = 'user_db'
PG_HOST      = 'host'
PG_PASSWORD  = 'password'

# подключение модуля для логирования
logger = log.save_log('../ParserQuestions/files/out_forum1.log')

# работа с модулем StackAPI (сайт )
SITE = StackAPI('stackoverflow', key='api_key')
SITE.max_pages = 1000

conn = psycopg2.connect(
        "dbname="+PG_DBNAME+
        " user="+PG_USER+
        " host="+PG_HOST+ 
        " password="+PG_PASSWORD)

curs = conn.cursor()

def print_help():
    print('-'*80)
    print('''
    Программа извлекает все вопросы по тегу "Python"
    с сайта stackoverflow.com, и сохраняет в БД.
    Работает с аргументами:
            -help    - вывод справки.
            -mml     - вывод минимальной, максимальной.
                       даты и количества вопросов в БД
            [date1] [date2]   - начальная и конечная дата
                                для диапазона извлечения
                                вопросов.
            [date]   - дата для диапазона извлечения
                       с конечной даты находящейся в
                       БД по указаную.
''')
    print('-'*80)
    sys.exit()


# проверка в БД минимальной/максимальной даты и количества вопросов
def min_max_len(date):
    try:
        if date == "min":
            curs.execute(
                """select min(dtime) from questions"""
                )
        elif date == "max":
            curs.execute(
                """select max(dtime) from questions"""
                )
        elif date == "len":
            curs.execute(
                """select count(*) from questions"""
                )
        result = curs.fetchall()

    except psycopg2.Error as err:
        print("Query error: {}".format(err))
    print(type(result[0][0]),result[0][0])
    return result[0][0]


# извлечение вопросов циклом по диапазону дат
def recieve_questions(start_date=None, end_date=None):
    logger.info("   Идёт извлечение данных...")
    if type(start_date) == int:
        logger.info(
            "   Start_date: %s"
            % datetime.utcfromtimestamp(start_date))
    else:
        logger.info("   Start_date: %s" % start_date)
    logger.info("   End_date: %s" % end_date)
    try:
        questions = SITE.fetch(
            'questions',
            fromdate = start_date,
            todate   = end_date,
            tagged   = 'python',
            sort     = 'creation',
            order    = 'asc')
    # вывод сообщения с ошбкой
    except StackAPIError as e:
        logger.error("   Error URL: %s" % e.url)
        logger.error("   Error Code: %s" % e.code)
        logger.error("   Error Error: %s" % e.error)
        logger.error("   Error Message: %s" % e.message)
    return questions


# сохранение в БД полученных вопросов
def save_to_db(questions):
    count = 0
    for i, items in enumerate(questions['items']):
        count = i+1
        try:
            curs.execute(
                """ INSERT INTO questions
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (int(items["question_id"]),
                    items["title"],
                    items["tags"],
                    int(items["view_count"]),
                    int(items["answer_count"]),
                    int(items["score"]),
                    str(items["link"]),
                    str(int(items["creation_date"])))
                    )
        except psycopg2.Error as err:
            print("Query error: {}".format(err))
    conn.commit()

    # логирование в файл, вывод полученных результатов
    logger.info("   Вопросы за данный диапазон: %s" % count)
    logger.debug("\n")


# главная функция
def main():

    if (min_max_len('min') is None) and len(sys.argv) != 3:
        print(
            "\n   Данных нет. Введите начальное " +
            "и конечное значение для диапазона даты")
        sys.exit()

    elif len(sys.argv) == 1 and min_max_len('min') is not None:
        print("\n   Введите начальное и конечное значение даты")
        sys.exit()

    elif sys.argv[1] == "-mml":
        print(
            "\n   Начальная дата  (общ.): %s"
            % datetime.utcfromtimestamp(min_max_len("min")))

        print(
            "   Конечная дата   (общ.): %s"
            % datetime.utcfromtimestamp(min_max_len("max")))

        print(
            "   Количесвто вопросов:    %s"
            % min_max_len("len"))
        sys.exit()

    elif sys.argv[1] == "-help":
        print_help()

    # начало считывания времени выполнения работы цикла
    time.clock()
    start_date = 0
    end_date   = 0

    if (len(sys.argv) == 2 and (
        sys.argv[1] != "-mml"or
        sys.argv[1] != "-help"
    )):
        start_date = datetime.utcfromtimestamp(min_max_len("max")).timetuple()
        end_date = datetime.utcfromtimestamp(
            calendar.timegm(time.strptime(sys.argv[1], '%d.%m.%Y'))
            ).timetuple()
        # print(end_date)
        mass = []
        mass2 = []

        for i in start_date:
            mass.append(i)
        start_date2 = mass[:6]

        for i in end_date:
            mass2.append(i)
        end_date2 = mass2[:6]

        # цикл с вызовом вопросов по дате выполняющийся
        # по месяцам, с конечной даты
        # по указаную в аргументах
        while True:

            # если месяц 12-ый, то увеличиваем
            # год и начинаем с 1-го месяца
            if start_date2[1] >= 11:
                start_date2[0] += 1
                start_date2[1] = 1
                questions = recieve_questions(
                    min_max_len("max")+1,
                    datetime(
                        start_date2[0],
                        start_date2[1],
                        start_date2[2],
                        start_date2[3],
                        start_date2[4],
                        start_date2[5]))

            # указываем если конечная приблизилась
            # к указаной и равна или меньше на месяц,
            # то мы выполняем извлечение по указаную дату
            elif start_date2[0] == end_date2[0] and (
                end_date2[1] - start_date2[1] == 1 or
                end_date2[1] == start_date2[1]
            ):
                questions = recieve_questions(
                    min_max_len("max")+1,
                    datetime(
                        end_date2[0],
                        end_date2[1],
                        end_date2[2],
                        end_date2[3],
                        end_date2[4],
                        end_date2[5]))
                save_to_db(questions)
                break

            # в любом другом случае увеличиваем
            # на месяц конечную дату
            else:
                start_date2[1] += 1
                questions = recieve_questions(
                    min_max_len("max")+1,
                    datetime(
                        start_date2[0],
                        start_date2[1],
                        start_date2[2],
                        start_date2[3],
                        start_date2[4],
                        start_date2[5]))
            save_to_db(questions)

    # если мы указали в аргументах две даты
    # начала и конца, то выполнить извлечение по этим датам
    elif len(sys.argv) == 3:
        dt = [int(i) for i in sys.argv[1].split('.')]
        dt2 = [int(i) for i in sys.argv[2].split('.')]
        questions = recieve_questions(
            datetime(dt[2], dt[1], dt[0]),
            datetime(dt2[2], dt2[1], dt2[0]))
        save_to_db(questions)

    # логирование результатов
    logger.info("-"*80)
    logger.info(
        "   Начальная дата (общ.): %s"
        % datetime.utcfromtimestamp(min_max_len("min")))
    logger.info(
        "   Конечная дата  (общ.): %s"
        % datetime.utcfromtimestamp(min_max_len("max")))
    logger.info("   Всего количество вопросов: %s" % min_max_len("len"))
    logger.info(
        "   Время выпонения скрипта " +
        str(round(time.clock(), 2)) + " сек. или " +
        str(round(time.clock()/60, 2)) + " мин.")
    logger.debug("\n")

    curs.close()
    conn.close()


if __name__ == '__main__':
    main()
