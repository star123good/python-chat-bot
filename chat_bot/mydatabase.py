import mysql.connector

HOSTNAME = 'localhost'
DATABASENAME = 'bin'
USERNAME = 'binbot'
PASSWORD = 'football!!!'

try:
	conn = mysql.connector.connect(host=HOSTNAME, database=DATABASENAME, user=USERNAME, password=PASSWORD)
	query_conn = conn.cursor(buffered=True)
except Exception as e:
	print(e)