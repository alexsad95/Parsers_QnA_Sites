# -*- coding: utf-8 -*-
'''
	Скрипт который собирает данные с основной таблицы БД 
	и записывает в отдельные категории (по отдельным таблицам)
	по тегам сайта StackOveflow

'''
import psycopg2

rowcount = 0

def select_tag_from_mass(mass):
	data = ''
	try:
		cur = conn.cursor()
		cur.execute('''
		SELECT id, tag FROM 
			(SELECT *
			 from questions
			 where %(mass)s && tag ) as t
			 order by id;
		''',{'mass': mass})

		data = cur.fetchall()
		cur.close()

	except psycopg2.Error as err:
		print("Query error: {}".format(err))

	for i, dt in enumerate(data):
		print str(i+1) + ") "+ str(dt)


def select_tag_web():
	data = ''
	try:
		cur = conn.cursor()
		cur.execute('SELECT * FROM tag_web;')

		data = cur.fetchall()
		cur.close()

	except psycopg2.Error as err:
		print("Query error: {}".format(err))

	for i, dt in enumerate(data):
		print str(i+1) + ") "+ str(dt)



def select_tag_from_table():
	data = ''

	try:
		cur = conn.cursor()
		cur.execute('''
		SELECT * 
		FROM questions q JOIN tag_web w
		ON q.id = w.id;''')

		data = cur.fetchall()
		cur.close()

	except psycopg2.Error as err:
		print("Query error: {}".format(err))
	print data[0]


def insert_tag_to_table(mass):
	try:
		cur = conn.cursor()
		cur.execute('''
		INSERT INTO tag_other (id)
		SELECT id FROM 
				(SELECT * from questions
				 where %(mass)s && tag ) as t
				 order by id;
		''',{'mass': mass})
		global rowcount
		rowcount += cur.rowcount
		conn.commit()
		cur.close()

	except psycopg2.Error as err:
		print("Query error: {}".format(err))


def main():
	mass = [	'random', 'apache', 'celery', 'apache-spark', 'api', 'python-imaging-library', 'logging',
			'pycharm', 'module', 'ipython', 'image', 'import', 'unit-testing', 'unicode', 'datetime',
			'selenium', 'beautifulsoup', 'dataframe', 'google-app-engine', 'csv', 'raspberry-pi',
			'selenium-webdriver', 'indexing', 'virtualenv', 'anaconda', 'pip',
			'pyspark', 'encoding', 'xpath', 'twitter', 'email', 'file-io', 'utf-8', 'heroku',
			'rest', 'ctypes', 'split', 'pyside', 'openerp', 'pickle', 'input', 'debugging', 'time',
			'python-import', 'url', 'date', 'eclipse', 'testing', 'printing', 'pdf', 'argparse',
			'google-cloud-datastore', 'encryption', 'setuptools', 'pydev','nginx', 'templates',
			'py.test','io', 'git', 'path', 'amazon-s3', 'syntax', 'audio', 'command-line',
			'typeerror', 'mocking', 'facebook', 'mechanize', 'append', 'jython', 'boto', 'terminal',
			'arguments', 'exception-handling', 'itertools', 'tweepy', 'slice', 'error-handling',
			'time-series', 'installation', 'python-sphinx', 'swig', 'openpyxl', 'docker', 'amazon-ec2', 
			'spyder', 'attributes', 'importerror','pyserial', 'filter', 'cmd', 'popen',
			'install', 'scripting', 'vim', 'package', 'cherrypy', 'process', 'maya',
			'serial-port', 'python-unittest', 'character-encoding', 'formatting', 'range', 'syntax-error',
			'directory', 'python-module', 'animation', 'screen-scraping', 'pillow', 'firefox'
			'ascii', 'automation', 'hex', 'key', 'nose', 'ironpython', 'mongoenginepython-idle', 'security',
			'video', 'output', 'dll', 'xlrd', 'text-files', 'server', 'string-formatting', 'zip', 'coding-style',
			'gevent', 'download'
]




	insert_tag_to_table(mass)
	# select_tag_from_table()
	# select_tag_from_mass(mass)




if __name__== "__main__":
	conn = psycopg2.connect("dbname='diplom' user='postgres'" \
							" host='localhost' password='77896499'")
	main()
	print u"Количествов записанных вопросов:", rowcount
	conn.close()



# Массивы для категорий:
# ----------------------

# WEB = [	'flask', 'django','pyramid','authentication', 'web', 'html', 'css',
# 		'javascript', 'django-models', 'beautifulsoup', 'sqlalchemy',
# 		'scrapy', 'web-scraping', 'heroku', 'parsing', 'requests',
# 		'python-requests', 'php', 'django-rest-framework', 'django-forms',
# 		'django-templates', 'lxml', 'api', 'jquery', 'apache',
# 		'amazon-web-services', 'selenium-webdriver', 'http', 'urllib2',
# 		'web-crawler', 'urllib', 'flask-sqlalchemy', 'url', 'templates',
# 		'django-queryset', 'wsgi', 'html-parsing', 'node.js', 'proxy',
# 		'tcp', 'bottle', 'websocket', 'web2py', 'request',
# 		'screen-scraping', 'web-applications', 'django-urls', 'nginx', 
# 		'mod-wsgi', 'cgi', 'uwsgi', 'angularjs', 'web.py', 'wtforms',
# 		'django-orm', 'webapp2', 'https', 'github', 'webserver', 
# 		'django-cms', 'django-south', 'bs4', 'urllib2', 'django-admin', 
# 		'flask-sqlalchemy', 'bokeh', 'curl', 'cookies', 'session', 'validation',
# 		'web-services', 'webdriver', 'scrapy-spider', 'web.py',
# 		'soap', 'xml-parsing', 'oauth-2.0', 'oauth', 'reactjs',
# 		'wtforms', 'django-orm', 'flask-wtforms', 'pyparsing'
# 		]

# GUI = [	"tkinter", "cx-freeze", "user-interface",
# 		"pyqt", "pyqt5", "windows-console", "exe", "qt", "pyqt4",
# 		"opencv", "pygame", "wxpython", "excel", "kivy", "gtk", "pygtk", 
# 		"py2exe", "winapi", "opengl", "win32com", "gtk3", "tk", 
# 		"tkinter-canvas", "qt4", "ttk", "pyinstaller", "web2py",
# 		"cx-freeze", "button", "3d", "pywin32", "widget", "signals",
# 		"setup.py", "winapi", "win32com"
# ]

# NETWORK = [	'networking', 'tcp', 'websocket', 'network-protocols', 'sockets', 
# 			'twisted', 'tornado', 'ssh', 'search', 'networkx', 'ssl', 'paramiko', 'scapy',
# 			'ftp', 'tftp', 'tcpip', 'udp', 'proxy', 'netstat', 'ip', 'webserver', 'server',
# 			'client', 'ipv6', 'ipv4', 'http', 'https', 'port', 'client-server', 'p2p'
# ]

# CScience = [	'numpy', 'matplotlib', 'scipy', 'opencv', 'scikit-learn', 'tensorflow', 'machine-learning', 'plot', 'nltk',
# 				'image-processing', 'math', 'nlp', 'matlab', 'neural-network', 'keras', 'deep-learning', 'theano',
# 				'hadoop', 'seaborn', 'ipython-notebook', 'filter', 'computer-vision', 'jupyter', 'jupyter-notebook',
# 				'histogram', 'matplotlib-basemap', 'computer-science', 'bigdata'
# ]

# DataBase = [	'mysql', 'sqlalchemy', 'postgresql', 'sql', 'mongodb', 'database', 'sqlite', 'sqlite3', 'pymongo',
# 				'flask-sqlalchemy', 'mysql-python', 'orm', 'psycopg2', 'sql-server', 'group-by', 'hash', 'redis', 'pyodbc',
# 				'elasticsearch', 'rabbitmq', 'caching', 'mongoengine', 'oracle', 'jdbc', 'cx-oracle'
# ]

# ALGHORITM = [	'list', 'dictionary', 'regex', 'string', 'arrays', 'json', 'multithreading', 'function', 'class',
# 				'xml', 'loops', 'file', 'tensorflow', 'algorithm', 'sockets', 'subprocess', 'for-loop', 'multiprocessing',
# 				'performance', 'sorting', 'recursion', 'matrix', 'tuples', 'variables', 'nltk', 'if-statement', 'oop'
# 				'api','image-processing', 'inheritance', 'nlp', 'exception', 'object', 'graph', 'lambda', 'generator', 'replace',
# 				'iteration', 'decorator', 'memory', 'multidimensional-array', 'set', 'authentication', 'methods',
# 				'statistics', 'data-structures', 'floating-point', 'binary', 'nested', 'python-multithreading', 'iterator',
# 				'merge', 'asynchronous', 'python-multiprocessing', 'hash', 'types', 'fabric', 'filter', 'integer', 'queue',
# 				'elasticsearch', 'tree', 'scope', 'return', 'histogram', 'parallel-processing', 'serialization',
# 				'boost', 'global-variables', 'int', 'stdout', 'stdin', 'turtle-graphics', 'sparse-matrix', 'model',
# 				'vectorization', 'interpolation', 'boolean', 'sum', 'statsmodels', 'python-asyncio', 'classification',
# 				'python-decorators', 'numbers', 'quicksort', 'cluster-analysis', 'algorithm'
# ]

# Programm Language = ['python-2.7', 'python-3.x', 'javascript', 'html', 'c++', 'java', 'sql', 'bash',
# 					'php', 'c', 'shell', 'jquery', 'ajax', 'jinja2', 'r', 'c#', 'python-3.4',
# 					'python-3.5', 'python-2.x', 'ruby', 'perl', 'css', 'node.js', 'python-2.6', 'python-3.3', 'swift',
# 					'objective-c', 'haskel', 'erlang', 'd', 'sass', 'less', 'react', 'programming-languages', 
# 					'coffeescript', 'common-lisp', 'cuda', 'cython', 'lisp', 'elixir', 'fortran', 'go',
# 					'jade', 'jython', 'jscript', 'livescript', 'lua', 'mathcad', 'rust', 'typescript', '.net'
# ]

# OS = [		'linux', 'windows', 'osx', 'macos-sierra', 'macports', 'osx-elcapitan', 'macbook', 'ubuntu', 'applescript',
# 			'android', 'unix', 'operating-system', 'ios', 'debian', 'arch', 'dos', 'gnu', 'windows-7'
# ]

# OTHER = [	'random', 'apache', 'celery', 'apache-spark', 'api', 'python-imaging-library', 'logging',
# 			'pycharm', 'module', 'ipython', 'image', 'import', 'unit-testing', 'unicode', 'datetime',
# 			'selenium', 'beautifulsoup', 'dataframe', 'google-app-engine', 'csv', 'raspberry-pi',
# 			'selenium-webdriver', 'indexing', 'virtualenv', 'anaconda', 'pip',
# 			'pyspark', 'encoding', 'xpath', 'twitter', 'email', 'file-io', 'utf-8', 'heroku',
# 			'rest', 'ctypes', 'split', 'pyside', 'openerp', 'pickle', 'input', 'debugging', 'time',
# 			'python-import', 'url', 'date', 'eclipse', 'testing', 'printing', 'pdf', 'argparse',
# 			'google-cloud-datastore', 'encryption', 'setuptools', 'pydev','nginx', 'templates',
# 			'py.test','io', 'git', 'path', 'amazon-s3', 'syntax', 'audio', 'command-line',
# 			'typeerror', 'mocking', 'facebook', 'mechanize', 'append', 'jython', 'boto', 'terminal',
# 			'arguments', 'exception-handling', 'itertools', 'tweepy', 'slice', 'error-handling',
# 			'time-series', 'installation', 'python-sphinx', 'swig', 'openpyxl', 'docker', 'amazon-ec2', 
# 			'spyder', 'attributes', 'importerror','pyserial', 'filter', 'cmd', 'popen',
# 			'install', 'scripting', 'vim', 'package', 'cherrypy', 'process', 'maya',
# 			'serial-port', 'python-unittest', 'character-encoding', 'formatting', 'range', 'syntax-error',
# 			'directory', 'python-module', 'animation', 'screen-scraping', 'pillow', 'firefox'
# 			'ascii', 'automation', 'hex', 'key', 'nose', 'ironpython', 'mongoenginepython-idle', 'security',
# 			'video', 'output', 'dll', 'xlrd', 'text-files', 'server', 'string-formatting', 'zip', 'coding-style',
# 			'gevent', 'download'
# ]
