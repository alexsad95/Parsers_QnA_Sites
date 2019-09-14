# -*- coding: utf-8 -*-
'''
    Скрипт который парсит вопросы с сайта Reddit 
    с помощью API и модуля praw   
    Какие данные для аргументов метода и работы модуля 
    псмотреть можно здесь 
    https://praw.readthedocs.io/en/latest/getting_started/authentication.html
'''

import psycopg2
import praw
from datetime import datetime
import calendar

count = 0

# сохранение в БД полученных вопросов
def save_to_db(submis):
    global count
    count += 1
    try:
        curs.execute(
                """ INSERT INTO reddit_python
                    VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (str(submis.id),
                    submis.title,
                    submis.num_comments,
                    int(submis.ups),
                    submis.url,
                    datetime.utcfromtimestamp(submis.created_utc),
                    submis.selftext)
                    )
    except psycopg2.Error as err:
        print("Query error: {}".format(err))
    conn.commit()



conn = psycopg2.connect("dbname='dbname' user='db_user' host='host' password='password'")
curs = conn.cursor()

reddit = praw.Reddit(   client_id     = "client_id", 
                        client_secret = "client_secret",
                        password      = "password",
                        user_agent    = "user_agent",
                        username      = "username")

subreddit = reddit.subreddit('flask')

hot_python = subreddit.hot(limit=1200)

for i,submis in enumerate(hot_python):
    if submis.is_self:
        save_to_db(submis)

print('Всего записанных вопросов:', count)
curs.close()
conn.close()