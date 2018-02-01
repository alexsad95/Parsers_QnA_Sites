# -*- coding: utf-8 -*-
import re
import sys
import json
import time
import pickle
import requests
from random import uniform, choice
from bs4 import BeautifulSoup
sys.path.append('C:\Users\\alexsad\Dropbox\Stud\Diplom\DIPLOM PROJECT')
import ParserQuestions

logger = ParserQuestions.save_log('../files/out_forum1.log')


# настройка user-agent
f = open('../files/user-agents.txt', 'r')
l = [line.strip() for line in f]

user_agents = choice(l)
user_agent = {'User-Agent': user_agents}

def parse_questions():
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
    question_tag = soup.find('div', {'id': 'content'})
    table_array = question_tag.findAll('table')
    mass_td = []
    for i, dt in enumerate(table_array):
        data = dt.tbody.find_all('tr')
        for i, dt in enumerate(data):
            data = dt.find_all('td', { "class" : re.compile("trow\d") })
            mass_td.append(data)
            
    for i, mass in enumerate(mass_td):
        if mass == []:
            del mass_td[i]
        else: 
            # print str(i) + ') \n\n'
            print mass[1].strong.text

if __name__ == '__main__':
    parse_questions()