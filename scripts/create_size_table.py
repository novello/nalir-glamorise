import sys
reload(sys)
sys.setdefaultencoding('utf8')

import mysql.connector
import sys
import string
import json
import re


connector = mysql.connector.connect(user='paulo',\
 password='paulo', host='localhost',\
 database='Mondial',charset="utf8")


query_create_table = "CREATE TABLE size(size integer, relation varchar(255))"

cursor = connector.cursor()
try:
	cursor.execute("SELECT '' from size")
	for x in cursor:
		continue

except Exception as e:
	print('creating table')
	cursor.execute(query_create_table)
	query_select = "SELECT DISTINCT cl.table_name \
	FROM information_schema.columns cl, information_schema.tables tb WHERE  \
	tb.table_name = cl.table_name and tb.table_schema = cl.table_schema and \
	tb.table_schema = '{}' order by cl.table_name;".format('imdb')

	cursor.execute(query_select)
	tables = []

	for (table_name,) in cursor:
		if table_name != 'size':
			tables+=[table_name]

	tables = list(set(tables))
	insert_lines = 'INSERT INTO size(relation,size) VALUES (%s, %s)'
	values = []
	for table in tables:
		sql_count = 'SELECT count(*) as cnt from {}'.format(table)
		cursor.execute(sql_count)
		for (cnt,) in cursor:
			values += [(table, cnt)]
			#insert_lines += "('{}',{}),".format(table,cnt)

	#insert_lines = insert_lines[:-1]
	#insert_lines += ';'
	print(values)
	cursor.executemany(insert_lines, values)
	connector.commit()
