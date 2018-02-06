# -*- coding: utf-8 -*-
import re
import sys
import json
import time
import pickle
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

def out_category_question():
    time_sleep = uniform(1,3) 
    time.sleep(time_sleep)
    url = 'https://python-forum.io/index.php'
    page = requests.get(url, headers=user_agent)

    if page.status_code == 404:
        print 'Error 404'

    if (page.status_code == 429):
        print u"Сайт заблокирован. Нужно подождать..."
        while (page.status_code == 429):
            time.sleep(60)
            page = requests.get(url, headers=user_agent)

    soup = BeautifulSoup(page.text.encode('utf-8'), "html.parser")
    
    div_wrapper = soup.find('div', {'id': 'content'}).find_all('table')

    td_list_orig = []
    for i, dt in enumerate(div_wrapper[:-1]):
        data = dt.tbody.find_all('tr')
        for i, dt in enumerate(data):
            data = dt.find_all('td', { "class" : re.compile("trow\d") })
            td_list_orig.append(data)

    for i, td_list in enumerate(td_list_orig):
        if td_list == []:
            del td_list_orig[i]

    url_for_category = []
    for i, td in enumerate(td_list_orig):
        url_for_category.append('https://python-forum.io/' + str(td[1].a.get('href')))

    category_url = []
    for i, td_list in enumerate(td_list_orig):
        category_url.append([str(td_list[1].strong.text), str(url_for_category[i])])

    for i in category_url: print i


# TODO -> переходы по страницам, парсинг всей категории

def parse_question_info(url):
    time_sleep = uniform(1,3) 
    time.sleep(time_sleep)

    page = requests.get(url, headers=user_agent)

    if page.status_code == 404:
        print 'Error 404'

    if (page.status_code == 429):
        print u"Сайт заблокирован. Нужно подождать..."
        while (page.status_code == 429):
            time.sleep(60)
            page = requests.get(url, headers=user_agent)

    soup = BeautifulSoup(page.text, "html.parser")
    div_wrapper = soup.find('div', {'id': 'content'}).find_all('table')

    full_info = []
    tr_list = div_wrapper[1].find_all('tr')

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

        info = []
        info.append(title)
        info.append(div_content)
        info.append(str(href))
        info.append(str(answer))
        info.append(str(views))
        info.append(str(last_date))
        full_info.append(info)

    print full_info

def parse_question(url):
    page = requests.get(url, headers=user_agent)

    if page.status_code == 404:
        print 'Error 404'

    if (page.status_code == 429):
        print u"Сайт заблокирован. Нужно подождать..."
        while (page.status_code == 429):
            time.sleep(60)
            page = requests.get(url, headers=user_agent)

    soup = BeautifulSoup(page.text, "html.parser")
    div_content = soup.find('div', {'class': 'post_content'})
    post_text = div_content.find('div', {'class': 'post_body scaleimages'})
    question = post_text.text
    return question

def parse_count_pages(url):
    page = requests.get(url, headers=user_agent)

    if page.status_code == 404:
        print 'Error 404'

    if (page.status_code == 429):
        print u"Сайт заблокирован. Нужно подождать..."
        while (page.status_code == 429):
            time.sleep(60)
            page = requests.get(url, headers=user_agent)

    soup = BeautifulSoup(page.text, "html.parser")
    div_pagination = soup.find('div', {'class': 'pagination'})
    count = re.findall('\d+', str(div_pagination.span.text))
    return int(count[0])


if __name__ == '__main__':
    # out_category_question()
    for i in range(parse_count_pages('https://python-forum.io/Forum-Board')):
        print i
        parse_question_info('https://python-forum.io/Forum-Board?page=' + str(i+1))
    # ('https://python-forum.io/Forum-Board?page=13')
