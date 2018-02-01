# -*- coding: utf-8 -*-
import sys
import json
import time
import pickle
import psycopg2
import requests
from random import uniform, choice 
from bs4 import BeautifulSoup 
from log import *
sys.path.append('C:\Users\\alexsad\Dropbox\Stud\Diplom\DIPLOM PROJECT')
import ParserQuestions

# подключение модуля для логирования
logger = ParserQuestions.save_log('../files/out_parseq.log')

rowcount = 0
dictionar = {}
start = 0
end = 0
name = ''

# настройка user-agent
f = open('../files/user-agents.txt', 'r')
l = [line.strip() for line in f]

user_agents = choice(l)
user_agent = {'User-Agent': user_agents}

# Функция получающая список всех вопросов у которых нет question
def get_id():
    data = ''
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, href FROM questions WHERE question is NULL order by id asc;")
        data = cur.fetchall()
        cur.close() 

    except psycopg2.Error as err:
        logger.error("Query error: {}".format(err))

    return data


# Запись спарсенных вопросов в БД
def update_question(string, id):
    try:
        cur = conn.cursor()
        sql = """UPDATE questions
                    SET question = %s
                    WHERE id = %s"""
        cur.execute(sql , (str(string), id))
        global rowcount 
        rowcount += cur.rowcount
        conn.commit()
        cur.close()

    except psycopg2.Error as err:
        logger.error("Query error: {}".format(err))


# Главная функция выполняющая парсинг 
def parse_questions(data, json_or_db):
    time.clock()

    question = {}
    global dictionar
    global rowcount
    global start
    global end
    global name

    for num, dt in enumerate(data):
        end = int(start)
        end += num
        time_sleep = uniform(1,3) 
        time.sleep(time_sleep)

        page = requests.get(dt[1], headers=user_agent)

        if page.status_code == 404: 
            update_question("Not Found",dt[0])
            continue

        if (page.status_code == 429):
            print u"Сайт заблокирован. Нужно подождать..."
            while (page.status_code == 429):
                time.sleep(60)
                page = requests.get(dt[1], headers=user_agent)

        soup = BeautifulSoup(page.text.encode('utf-8'), "html.parser")
        question_tag = soup.find('div', {'class': 'post-text'})


        logger.info(str(end) + ") " + dt[1])

        if question_tag.find('pre'):
            # logger.info("-"*20 + "\nPRE\n"+"-"*20)
            pre = question_tag.find_all('pre')
            for i in pre:
                # logger.info(i.text)
                i.extract()

        if question_tag.find('blockquote'):
            block = question_tag.find_all('blockquote')
            for i in block:
                i.extract()

        string = question_tag.text.encode('utf-8')

        if json_or_db == 'db':
            update_question(string, dt[0])

        elif json_or_db == 'json':
            name = str(start) +"-"+str(end)
            rowcount = num+1
            dictionar[dt[0]] = string



    logger.info(u"Количество записаных вопросов: " + str(rowcount))
    logger.info(u"Время выпонения скрипта " +
                unicode(round(time.clock(), 2)) + u" сек. или " +
                unicode(round(time.clock()/60, 2)) + u" мин.")



if __name__ == '__main__':
    try:
        json_or_db = ''


        #  записывать ли в БД?
        host = raw_input("Host: ")
        if host == 'not db':
            pass
        else:
            conn = psycopg2.connect("dbname='diplom' user='postgres'"\
                    "hostaddr='"+str(host)+"' password='77896499'")

        # запрашивает команду
        # len - показывает количество вопросов с файла question.txt
        # getid -  выводит ID последнего вопроса с файла 
        # parse - начинает парсить вопросы с start по end 
        # quit - выход с программы 

        line = raw_input("Command: ")

        if line == 'len':
            with open("files/questions.txt", "rb") as f:
                data = pickle.load(f)

            print u"Количество вопросов: ", len(data)

        elif line == 'getid':
            data = get_id()
            with open("files/questions.txt", "wb") as f:
                pickle.dump(data, f)
            print u"Все Id записанны"

        elif line == 'parse':
            start = raw_input("Start: ")
            end = raw_input("End: ")
            with open("files/questions.txt", "rb") as f:
                data = pickle.load(f)
            json_or_db = raw_input("Write to Json or DB: ")

            parse_questions(data[int(start):int(end)], json_or_db)

        elif line == 'quit':
            sys.exit(1)

        else:
            with open("files/questions.txt", "rb") as f:
                data = pickle.load(f)
            parse_questions(data)

        raw_input()


    # обработка всех исключений 
    except KeyboardInterrupt:
        sys.exit(1)

    except EOFError:
        sys.exit(1)

    except Exception as e:
        e = sys.exc_info()
        if str(e[1]).find('unexpected EOF while parsing') != -1:
            conn.close()
            sys.exit(1)
        else:
            conn.close()
            logger.error(u"Сведения об исключении: " + str(e))

    finally:
        if host == 'not db' and line == 'len':
            conn.close()
            sys.exit(1)
        elif json_or_db == 'json':
            with open("files/"+name+".json", "wb") as f:
                pickle.dump(dictionar, f)
            logger.info(u"Время выпонения скрипта " +
                unicode(round(time.clock(), 2)) + u" сек. или " +
                unicode(round(time.clock()/60, 2)) + u" мин.")
            conn.close()
            raw_input()

        elif json_or_db == 'db':
            conn.close()
            logger.info(u"Время выпонения скрипта " +
                unicode(round(time.clock(), 2)) + u" сек. или " +
                unicode(round(time.clock()/60, 2)) + u" мин.")
            raw_input()
