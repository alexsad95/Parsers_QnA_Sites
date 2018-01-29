# -*- coding: utf-8 -*-
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



conn = psycopg2.connect("dbname='diplom' user='postgres' host='localhost' password='77896499'")
curs = conn.cursor()

reddit = praw.Reddit(client_id='NEADcG3-PzvVSw', 
					 client_secret="lBPTI4IoH9eUFyyxn3RSZrDwE0o",
					 password='77896499Alex',
					 user_agent='alexsad95_app',
					 username='Alexsad95')

subreddit = reddit.subreddit('flask')

hot_python = subreddit.hot(limit=1200)

for i,submis in enumerate(hot_python):
	if submis.is_self:
		save_to_db(submis)
		# print i,"  Title:", submis.title
		# print "    Url:", submis.url
		# print "    CreationDate:", datetime.utcfromtimestamp(submis.created_utc)
		# print "    FromTimestamp:", datetime.fromtimestamp(submis.created_utc)
print u"Всего записанных вопросов:", count
curs.close()
conn.close()