#! python3
# -*- coding: utf-8 -*-

import logging
from random import choice

logger = logging.getLogger(__name__)

def save_log(filename):
	# создаём объект с именем модуля
	logger = logging.getLogger(__name__)
	# задаём уровень логгирования
	logger.setLevel(logging.DEBUG)

	# форматируем записи
	formatter1 = logging.Formatter('%(message)s')
	formatter2 = logging.Formatter(
			'%(levelname)-6s\ [%(asctime)s] |%(message)s',
		'%m/%d/%Y %H:%M:%S')

	# создаём обрабочтик консольного лога
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)

	# устанавливаем формат для обработчика для консоли
	console.setFormatter(formatter1)

	# создаём обрабочтик файла лога
	filehandler = logging.FileHandler(filename,encoding='utf-8')
	filehandler.setLevel(logging.DEBUG)

	# устанавливаем формат для обработчика для out.log
	filehandler.setFormatter(formatter2)

	# добавляем обработчик к логгеру
	logger.addHandler(console)
	logger.addHandler(filehandler)

	return logger
