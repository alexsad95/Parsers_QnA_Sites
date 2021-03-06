#! python3
# -*- coding: utf-8 -*-
'''
    Скрипт который парсит  вопросы с сайта python-forum.io
'''

import re, sys, time, requests, psycopg2, pickle
from uuid import uuid4
from random import uniform, choice
from bs4 import BeautifulSoup

sys.path.append(r'\\path_to_project')
import py3parser

logger = py3parser.save_log('../py3parser/files/out_forum1.log')

# настройка user-agent
f = open('../py3parser/files/user-agents.txt', 'r')
l = [line.strip() for line in f]
user_agents = choice(l)
user_agent = {'User-Agent': user_agents}
f.close()

conn = psycopg2.connect(
        "dbname='dbname' user='db_user'"
        " host='host' password='password'")
curs = conn.cursor()


# вывод справки
def print_help():
    print('''
  Программа извлекает все необходимые данные с форума python-forum.io, и сохраняет в БД.
  Для работы необходимо ввести команду: python forum1.py [аргументы]
  Необходимаые аргументы и их обозначение:
      -help                - вывод справки.
      -last                - вывод последней категории и страницы.
      -p_category [num]    - парсинг определённой категории или определённой страницы.
      ''')
    sys.exit()


# комманда выводит последнюю категорию и страницу с файла
def last_page():
    with open('../py3parser/files/category_page.txt', "rb") as f:
        data = pickle.load(f)
    print('  Категория:', data['category'], '\n  Страница:', data['page'])


# делает запрос на сайт и возвращает html объект
def url_request(url):
    page = requests.get(url, headers=user_agent)

    # стандартная проверка на доступность сайта
    if page.status_code == 404:
        print('  Error 404')
    if (page.status_code == 429):
        print('  Сайт заблокирован. Нужно подождать...')
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

        # словарь где хранятся данные
        info = {}
        info.update({'id': str(uuid4())[0:8]})
        info.update({'title':  title})
        info.update({'category': category})
        info.update({'questions': question})
        info.update({'href': str(href)})
        info.update({'answers': int(answer.replace(",",""))})
        info.update({'views': int(views.replace(",",""))})
        full_info.append(info)

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
    difference = 0

    # добавление в БД
    for i, items in enumerate(questions):
        try:
            curs.execute("""select title from python_forum1 where question = (%s)""",
                        (items["questions"],))

            result = curs.fetchall()

            # проверка на идентичность
            list_of_results = map(lambda x: x[0], result)
            if items["title"] in list_of_results:
                logger.info('  Вопрос уже есть в БД: %s' % items["title"])
                difference += 1
                continue


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
            print("  Query error: {}".format(err))
    conn.commit()

    if count > difference:
        count_questions = count - difference
    else: 
        count_questions = 0

    # логирование в файл, вывод полученных результатов
    logger.info("  Кол-во вопросов с страницы: %s" % count_questions)
    logger.info("\n")


# главная фукция 
def main_function(command):

    if command == '-p_category':
        out_category_question()

        category = input('\n  Введите название категории: ')
        page = input('  Введите номер страницы: ')
        url = 'https://python-forum.io/' + category
        logger.info('  Парсинг категории: %s' % category)

        # если были введены страницы, парсинг по страницам
        if page:
            page = [int(s.strip()) for s in page.split(',')]
            for i in page:
                logger.info('  Страница № %s' % i)
                # print(url + '?page=' + str(i))
                parse_question_info(url + '?page=' + str(i))

                category_page = {'category': str(category), 'page': str(i)}

                with open('../py3parser/files/category_page.txt', "wb+") as f:
                    pickle.dump(category_page, f)

        # если страницы не были введены, парсинг всех страниц
        else:
            for i in range(parse_count_pages(url)):
                logger.info('  Страница № %s' % (i + 1))
                parse_question_info(url + '?page=' + str(i+1))

    elif command == '-last':
        last_page()

    elif command == '-help':
        print_help()

    curs.close()
    conn.close()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print_help()
        sys.exit(1)

    command = sys.argv[1]
    main_function(command)
