import sqlite3


def run_sql(sql):
	conn = sqlite3.connect(r'D:\TelegramBot\recipes.db')
	cursor = conn.cursor()
	cursor.execute(sql)
	data = cursor.fetchall()
	cursor.close()
	conn.close()
	return data
