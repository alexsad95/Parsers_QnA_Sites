# -*- coding: utf-8 -*-

#    [ ] TODO текущий -> Исправить ошибку tr в Forum-Bar 1 стр.

# 1) [x] TODO -> Написать отдельную главную функцию с параметрами
# 2) [x] TODO -> Изменить список на словарь для удобства
# 3) [ ] TODO -> Добавить исключения, логгирование
# 4) [ ] TODO -> Создать таблицу с полями 
# 5) [ ] TODO -> Сохранение в БД
# 6) [ ] TODO -> Распарсить форум

import re
import sys
import json
import time
import psycopg2
import requests
from random import uniform, choice
from bs4 import BeautifulSoup, UnicodeDammit
sys.path.append('C:\Users\\alexsad\Dropbox\Stud\Diplom\DIPLOM PROJECT')
import ParserQuestions

logger = ParserQuestions.save_log('../files/out_forum1.log')

# настройка user-agent
f = open('../files/user-agents.txt', 'r')
l = [line.strip() for line in f]
user_agents = choice(l)
user_agent = {'User-Agent': user_agents}


def print_help():
    print u'''
  Программа извлекает все необходимые данные с форума python-forum.io, и сохраняет в БД.
  Для работы необходимо ввести команду: python forum1.py [аргументы]
  Необходимаые аргументы и их обозначение:
      -help           - вывод справки.
      -count          - вывод количества сохранённых данных.
      -p_category     - парсинг определённой категории.
      -p_all          - парсинг всех категорий с последних сохранённых вопросов.'''
    sys.exit()


# парсинг и вывод категорий в списке с ссылкой 
def out_category_question():
    time_sleep = uniform(1,3) 
    time.sleep(time_sleep)

    url = 'https://python-forum.io/index.php'
    page = requests.get(url, headers=user_agent)

    # стандартная проверка на доступность сайта
    if page.status_code == 404:
        print 'Error 404'
    if (page.status_code == 429):
        print u'Сайт заблокирован. Нужно подождать...'
        while (page.status_code == 429):
            time.sleep(60)
            page = requests.get(url, headers=user_agent)

    soup = BeautifulSoup(page.text.encode('utf-8'), 'html.parser')
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

    for i in category_url: print i


# парсинг основной информации
def parse_question_info(url):
    time_sleep = uniform(1,3)
    time.sleep(time_sleep)

    page = requests.get(url, headers=user_agent)

    if page.status_code == 404:
        print 'Error 404'
    if (page.status_code == 429):
        print u'Сайт заблокирован. Нужно подождать...'
        while (page.status_code == 429):
            time.sleep(60)
            page = requests.get(url, headers=user_agent)

    soup = BeautifulSoup(page.text, 'html.parser')
    div_wrapper = soup.find('div', {'id': 'content'}).find_all('table')

    # основной список с информацией о вопросе
    full_info = []
    tr_list = div_wrapper[1].find_all('tr', { 'class' : 'inline_row' })

    # for i,tr in enumerate(tr_list):
    #     print '\n'+str(i)+') Tag.Name: ', tr.name
    #     print '   Tag.Attrs: ', tr.attrs

    for i, dt in enumerate(tr_list[2:]):
        td_list = dt.find_all('td')
        if len(td_list) == 1:
            break

        if td_list[2].div.span == None:
            td_list[2].div.decompose()

        title = td_list[2].div.span.span.a.text.encode('utf-8')
        short_questions = td_list[2].get('title').encode('utf-8')
        href = 'https://python-forum.io/'+ str(td_list[2].div.span.span.a.get('href'))
        div_content = parse_question(str(href))
        answer = td_list[3].a.text
        views = td_list[4].text
        last_date = td_list[6].span.text[:22]

        info = {}
        info.update({'title':  title})
        info.update({'questions': div_content})
        info.update({'href': str(href)})
        info.update({'anser': str(answer)})
        info.update({'views': str(views)})
        info.update({'last_date': str(last_date)})
        full_info.append(info)

    for i,info in enumerate(full_info):
        print str(i+1)+'\n{'
        for key, value in info.items():
            print '{0}: {1}'.format(key, value)
        print '}'


# парсинг самого вопроса переходя на его страницу
def parse_question(url):
    page = requests.get(url, headers=user_agent)

    if page.status_code == 404:
        print 'Error 404'
    if (page.status_code == 429):
        print u'Сайт заблокирован. Нужно подождать...'
        while (page.status_code == 429):
            time.sleep(60)
            page = requests.get(url, headers=user_agent)

    soup = BeautifulSoup(page.text, 'html.parser')
    div_content = soup.find('div', {'class': 'post_content'})

    post_text = div_content.find('div', {'class': 'post_body scaleimages'})
    question = post_text.text

    return question


# парсинг количества страниц с вопросами в категории
def parse_count_pages(url):
    page = requests.get(url, headers=user_agent)

    if page.status_code == 404:
        print 'Error 404'
    if (page.status_code == 429):
        print u'Сайт заблокирован. Нужно подождать...'
        while (page.status_code == 429):
            time.sleep(60)
            page = requests.get(url, headers=user_agent)

    soup = BeautifulSoup(page.text, 'html.parser')
    div_pagination = soup.find('div', {'class': 'pagination'})
    count = re.findall('\d+', str(div_pagination.span.text))

    return int(count[0])

# сохраняет данные в БД
# def save_to_db(data):

# главная фукция 
def main_function(command):


    if command == '-p_category':
        out_category_question()
        category = raw_input(u'Введите название категории: '.encode('cp866'))
        url = 'https://python-forum.io/' + category

        for i in range(parse_count_pages(url)):
            print u'Страница №',int(i) + 1 
            parse_question_info(url + '?page=' + str(i+1))

    elif command == '-help':
        print_help()


if __name__ == '__main__':
    try:
        command = sys.argv[1]
        main_function(command)

    except Exception as e:
        e = sys.exc_info()
        print '\n\n'+'--'*20 + u'\nСведения об исключении: \n' + str(e[0]) + '\n' + str(e[1])
