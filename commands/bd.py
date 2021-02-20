from telegram import (
	Update,
)
from telegram.ext import (
	CallbackContext,
	run_async,
)
from commands.run_sql import *
import datetime


def bd(update, context):
	#nickname = context.args[0]
	birthday_sql = f"""select distinct name, date, nickname from holidays order by 2 desc"""
	birthdays = run_sql(birthday_sql)
	message = ''
	for birthday in birthdays:
		name = birthday[0]
		date = datetime.datetime.strptime(birthday[1], '%Y-%m-%d')
		nickname = birthday[2]
		message += f'{name} е роден на {date.strftime("%d.%m.%Y")}\n'
	update.message.reply_text(message)


def daily_job(context: CallbackContext):
	birthday_sql = '''select name, date, nickname from holidays
	where strftime('%d.%m', date) = strftime('%d.%m', date('now'))'''
	print(birthday_sql)
	birthdays = run_sql(birthday_sql)
	#context.bot.send_message(chat_id='67310463', text=f"It's work!")
	for birthday in birthdays:
		name, date, nickname = [*birthday]
		greeting_date = datetime.datetime.now()
		today = greeting_date.strftime('%d.%m')
		years = int(greeting_date.strftime('%Y')) - int(date[:4])
		context.bot.send_message(chat_id='-1001356679470', text=f'Днес {today} - {name} става на {years} години. Да ни е жив и здрав!')

