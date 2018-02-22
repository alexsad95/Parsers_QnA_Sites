#! python3
# -*- coding: utf-8 -*-
# ============================================================

# ----------------GLOBAL TODO и сделанные---------------------
# Были сделаны
# [x] TODO -> Написать отдельную главную функцию с параметрами
# [x] TODO -> Изменить список на словарь для удобства
# [x] TODO -> Исправить ошибку tr в Forum-Bar 1 стр (поиск tr по классу)
# [x] TODO -> Исправить ошибку UnicodeEncodeError 3 row "Funny English" (python3 и папка py3parser)

# Сделал недавно
# [x] TODO -> Исправить views и answer на int и убрать запятую
# [x] TODO -> Убрал lastdate т.к. не имеет смысл добавлять дату изменения вопросов, тем более нет точной даты создания
# [x] TODO -> Парсинг по категории и странице
# [x] TODO -> Добавление уникального ID
# [x] TODO -> Вычисление категории и запись

# Нужно сделать
# [ ] TODO <текущее> -> Создать таблицу с полями 
# [ ] TODO -> Сохранение в БД
# [ ] TODO -> Добавить исключения, логгирование
# [ ] TODO -> Распарсить форум
# ============================================================

import re, sys, json, time, requests, psycopg2
from uuid import uuid4
from random import uniform, choice
from bs4 import BeautifulSoup

sys.path.append(r'C:\Users\alexsad\Dropbox\Stud\Diplom\DIPLOM PROJECT\ParserQuestions')
import py3parser

logger = py3parser.save_log('../py3parser/files/out_forum1.log')

# настройка user-agent
f = open('../py3parser/files/user-agents.txt', 'r')
l = [line.strip() for line in f]
user_agents = choice(l)
user_agent = {'User-Agent': user_agents}

conn = psycopg2.connect(
        "dbname='diplom' user='postgres'"
        " host='localhost' password='77896499'")
curs = conn.cursor()


def print_help():
    print('''
  Программа извлекает все необходимые данные с форума python-forum.io, и сохраняет в БД.
  Для работы необходимо ввести команду: python forum1.py [аргументы]
  Необходимаые аргументы и их обозначение:
      -help                - вывод справки.
      -count               - вывод количества сохранённых данных.
      -p_category [num]    - парсинг определённой категории или определённой страницы.
      -p_all               - парсинг всех категорий с последних сохранённых вопросов.''')
    sys.exit()

# делает запрос на сайт и возвращает html объект
def url_request(url):
    # time_sleep = uniform(1,3)
    # time.sleep(time_sleep)

    page = requests.get(url, headers=user_agent)

    # стандартная проверка на доступность сайта
    if page.status_code == 404:
        print('Error 404')
    if (page.status_code == 429):
        print('Сайт заблокирован. Нужно подождать...')
        while (page.status_code == 429):
            time.sleep(60)
            page = requests.get(url, headers=user_agent)

    soup = BeautifulSoup(page.text, 'html.parser')
    return soup


# парсинг и вывод категорий в списке с ссылкой 
def out_category_question():
    soup = url_request('https://python-forum.io/index.php')
    div_wrapper = soup.find('div', {'id': 'content'}).find_all('table')

    # ищем в таблицах столбцы с классами trow1 или trow2
    td_list_orig = []
    for i, dt in enumerate(div_wrapper[:-1]):
        data = dt.tbody.find_all('tr')
        for i, dt in enumerate(data):
            data = dt.find_all('td', { 'class' : re.compile('trow\d') })
            td_list_orig.append(data)

    # удаляем ненужные столбцы без контента
    for i, td_list in enumerate(td_list_orig):
        if td_list == []:
            del td_list_orig[i]

    # достаём ссылку категории
    url_for_category = []
    for i, td in enumerate(td_list_orig):
        url_for_category.append('https://python-forum.io/' + str(td[1].a.get('href')))

    # создаём и записываем в список category_url
    category_url = []
    for i, td_list in enumerate(td_list_orig):
        category_url.append([str(td_list[1].strong.text), str(url_for_category[i])])

    for i in category_url: print(" ",i)


# парсинг основной информации
def parse_question_info(url):
    soup = url_request(url)
    div_wrapper = soup.find('div', {'id': 'content'}).find_all('table')

    # основной список, где хранятся словари с данными о вопросе
    full_info = []
    tr_list = div_wrapper[1].find_all('tr', { 'class' : 'inline_row' })

    for i, dt in enumerate(tr_list):
        td_list = dt.find_all('td')
        if len(td_list) == 1:
            break

        # отбрасываем лишние блоки
        if td_list[2].div.span == None:
            td_list[2].div.decompose()

        # получаем нужные данные
        title = td_list[2].div.span.span.a.text
        short_questions = td_list[2].get('title')
        href = 'https://python-forum.io/'+ str(td_list[2].div.span.span.a.get('href'))
        question, category = parse_question_and_category(str(href))
        answer = td_list[3].a.text
        views = td_list[4].text
        # last_date = td_list[6].span.text[:22]

        # словарь где хранятся данные
        info = {}
        info.update({'id': str(uuid4())[0:8]})
        info.update({'title':  title})
        info.update({'category': category})
        info.update({'questions': question})
        info.update({'href': str(href)})
        info.update({'answers': int(answer.replace(",",""))})
        info.update({'views': int(views.replace(",",""))})
        # info.update({'last_date': str(last_date)})
        full_info.append(info)

    # вывод полученных данных
    # for i,info in enumerate(full_info):
    #     logger.info(str(i+1)+'\n{')
    #     for key, value in info.items():
    #         logger.info('{0}: {1}'.format(key, value))
    #     logger.info('}')

    save_to_db(full_info)

# парсинг самого вопроса переходя на его страницу
def parse_question_and_category(url):
    soup = url_request(url)
    div_content = soup.find('div', {'class': 'post_content'})

    # парсинг вопроса
    post_text = div_content.find('div', {'class': 'post_body scaleimages'})
    question = post_text.text

    # парсинг категории
    div_navigation = soup.find('div', {'class': 'navigation'})
    div_navigation = div_navigation.find_all('a')

    category = div_navigation[2].text

    return question, category


# парсинг количества страниц с вопросами в категории
def parse_count_pages(url):
    soup = url_request(url)

    div_pagination = soup.find('div', {'class': 'pagination'})
    count = re.findall('\d+', str(div_pagination.span.text))

    return int(count[0])

# сохранение в БД полученных вопросов
def save_to_db(questions):
    count = 0

    # добавление в БД
    for i, items in enumerate(questions):
        try:
            curs.execute("""select title from python_forum1 where question = (%s)""",
                        (items["questions"],))

            result = curs.fetchall()
            if result:
                break

            curs.execute(
                """ INSERT INTO python_forum1
                    VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (items["id"],
                    items["title"],
                    int(items["answers"]),
                    items["category"],
                    items["href"],
                    int(items["views"]),
                    items["questions"])
                    )
            count = i+1
        except psycopg2.Error as err:
            print("Query error: {}".format(err))
    conn.commit()

    # логирование в файл, вывод полученных результатов
    logger.info(u"  Вопросы за данный диапазон: %s" % count)
    logger.debug("\n")


# главная фукция 
def main_function(command):

    if command == '-p_category':
        out_category_question()

        category = input('\n  Введите название категории: ')
        page = input('  Введите номер страницы: ')
        url = 'https://python-forum.io/' + category

        # если были введены страницы, парсинг по страницам
        if page:
            page = [int(s.strip()) for s in page.split(',')]
            for i in page:
                print('  Страница №', i)
                # print(url + '?page=' + str(i))
                parse_question_info(url + '?page=' + str(i))

        # если стр не были введены, парсинг всех страниц
        else:
            for i in range(parse_count_pages(url)):
                print('  Страница №',int(i) + 1)
                parse_question_info(url + '?page=' + str(i+1))

    elif command == '-help':
        print_help()

    curs.close()
    conn.close()

if __name__ == '__main__':
    # try:
    if len(sys.argv) == 1:
        print_help()
        sys.exit(1)

    command = sys.argv[1]
    main_function(command)

    # except Exception as e:
        # e = sys.exc_info()
        # logger.error('\n\n'+'--'*20 + u'\nСведения об исключении: \n' + str(e[0]) + '\n' + str(e[1]))