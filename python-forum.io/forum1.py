# -*- coding: utf-8 -*-
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

    page = requests.get('https://python-forum.io/index.php', headers=user_agent)

    if page.status_code == 404: 
        print 'Error 404'

    if (page.status_code == 429):
        print u"Сайт заблокирован. Нужно подождать..."
        while (page.status_code == 429):
            time.sleep(60)
            page = requests.get(dt[1], headers=user_agent)

    soup = BeautifulSoup(page.text.encode('utf-8'), "html.parser")
    question_tag = soup.find('div', {'id': 'content'})
    for i in question_tag.findAll('table'):
        print i

if __name__ == '__main__':
    parse_questions()