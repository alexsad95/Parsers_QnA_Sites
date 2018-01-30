# -*- coding: utf-8 -*-
import os
import sys
import pickle
import psycopg2

rowcount = 0

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


def main():
	mass = os.listdir('F:\\ParseQuestions\\files')
	mass2 = []
	for i in mass:
		if i.find('.json') != -1:
			mass2.append(i)
	return mass2

if __name__ == '__main__':
	
	conn = psycopg2.connect("dbname='diplom' user='postgres'"\
							"host='localhost' password='77896499'")
	mass = main()
	print u'\n  Выбирете файл'
	for i, files in enumerate(mass):
		print "    " + str(i+1) + ") " + str(files)
	file = input(" > ")-1

	if file not in range(len(mass)):
		print "Error input"
		sys.exit(1)

	with open("files/"+mass[file], "rb") as f:
		data = pickle.load(f)

	for key, value in data.items():
		update_question(value, key)
	
	print u'Количество записанных в БД вопросов: ' + str(rowcount)

	conn.close()
