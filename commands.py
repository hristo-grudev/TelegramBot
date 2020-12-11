import sqlite3
from random import randint, choice

from telegram import (
	Poll,
	ParseMode,
	KeyboardButton,
	KeyboardButtonPollType,
	ReplyKeyboardMarkup,
	ReplyKeyboardRemove,
	Update,
)
from telegram.ext import (
	Updater,
	CommandHandler,
	PollAnswerHandler,
	PollHandler,
	MessageHandler,
	Filters,
	CallbackContext,
	run_async,
)
import datetime
from datetime import time


def run_sql(sql):
	conn = sqlite3.connect(r'C:\Users\hristo.grudev\Projects\recipes\recipes.db')
	cursor = conn.cursor()
	cursor.execute(sql)
	data = cursor.fetchall()
	cursor.close()
	conn.close()
	return data


@run_async
def start(update: Update, context: CallbackContext) -> None:
	"""Inform user about what this bot can do"""
	button = [[KeyboardButton("Къв си ти бе?")]]
	if len(context.args) > 0:
		all_recipes = set()
		for product in context.args:
			sql = f"""select distinct recipes_id 
			from main 
			where product_id in (select distinct id from products where name like '%{product}%')"""
			args_recipes = run_sql(sql)
			args_recipes = {rec[0] for rec in args_recipes}
			if len(all_recipes) == 0:
				all_recipes = args_recipes
			else:
				all_recipes = all_recipes.intersection(args_recipes)
		recipes = choice(list(all_recipes))
	else:
		recipes = randint(1, 6601)

	global last_recipes
	last_recipes = recipes

	"""Send a message when the command /start is issued."""
	sql = f'''select r.name, t.name, qty from main s
	join products t on s.product_id=t.id
	join recipes r on r.id=s.recipes_id
	where s.recipes_id = {recipes}
	group by r.name, t.name, qty
	order by s.rowid'''
	data = run_sql(sql)

	text = '<b>' + str(data[0][0]) + '</b>\n'

	for nii in data:
		text += f'{nii[1]} - {nii[2]}\n'
	update.message.reply_text(text, parse_mode=ParseMode.HTML)


@run_async
def cook(update: Update, context: CallbackContext) -> None:
	global last_recipes

	sql = f'''select distinct name from recipes_order
	where recipes_id = {last_recipes}'''
	data = run_sql(sql)

	text = ''

	for nii in data:
		text += f'{nii[0]}\n'
	update.message.reply_text(text)


def echo(update, context):
	text = update.message.text
	if 'вакс' in text:
		echo = 'Бил Гейтс ще ни чипира всички :scream: :scream: :scream:'
	elif 'covid' in text:
		echo = 'Всички ще умрем :scream: :scream: :scream:'
	elif '- ' in text:
		echo = 'Хаха'
	elif 'http' in text:
		echo = 'Това го видях вече.'
	elif 'лекар' in text:
		echo = 'Ако имаш нужда от лекар, звънни ми.'
	"""Echo the user message."""
	if echo:
		update.message.reply_text(echo)


def bd(update, context):
	command = context.args

	update.message.reply_text(f'Честит рожден ден {command}')


def poll(update: Update, context: CallbackContext) -> None:
	"""Sends a predefined poll"""
	questions = ["Добре", "Много добре", "Фантастично", "Жестоко"]
	message = context.bot.send_poll(
		update.effective_chat.id,
		"Как си?",
		questions,
		is_anonymous=False,
		allows_multiple_answers=True,
	)
	# Save some info about the poll the bot_data for later use in receive_poll_answer
	payload = {
		message.poll.id: {
			"questions": questions,
			"message_id": message.message_id,
			"chat_id": update.effective_chat.id,
			"answers": 0,
		}
	}
	context.bot_data.update(payload)


def receive_poll_answer(update: Update, context: CallbackContext) -> None:
	"""Summarize a users poll vote"""
	answer = update.poll_answer
	poll_id = answer.poll_id
	try:
		questions = context.bot_data[poll_id]["questions"]
	# this means this poll answer update is from an old poll, we can't do our answering then
	except KeyError:
		return
	selected_options = answer.option_ids
	answer_string = ""
	for question_id in selected_options:
		if question_id != selected_options[-1]:
			answer_string += questions[question_id] + " and "
		else:
			answer_string += questions[question_id]
	context.bot.send_message(
		context.bot_data[poll_id]["chat_id"],
		f"{update.effective_user.mention_html()} feels {answer_string}!",
		parse_mode=ParseMode.HTML,
	)
	context.bot_data[poll_id]["answers"] += 1
	# Close poll after three participants voted
	if context.bot_data[poll_id]["answers"] == 3:
		context.bot.stop_poll(
			context.bot_data[poll_id]["chat_id"], context.bot_data[poll_id]["message_id"]
		)


def quiz(update: Update, context: CallbackContext) -> None:
	"""Send a predefined poll"""
	questions = ["Утре", "Довечера", "Веднага", "Никога"]
	message = update.effective_message.reply_poll(
		"Кога ще ти се обадя?", questions, type=Poll.QUIZ, correct_option_id=0
	)
	# Save some info about the poll the bot_data for later use in receive_quiz_answer
	payload = {
		message.poll.id: {"chat_id": update.effective_chat.id, "message_id": message.message_id}
	}
	context.bot_data.update(payload)


def receive_quiz_answer(update: Update, context: CallbackContext) -> None:
	"""Close quiz after three participants took it"""
	# the bot can receive closed poll updates we don't care about
	if update.poll.is_closed:
		return
	if update.poll.total_voter_count == 3:
		try:
			quiz_data = context.bot_data[update.poll.id]
		# this means this poll answer update is from an old poll, we can't stop it then
		except KeyError:
			return
		context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])


def preview(update: Update, context: CallbackContext) -> None:
	"""Ask user to create a poll and display a preview of it"""
	# using this without a type lets the user chooses what he wants (quiz or poll)
	button = [[KeyboardButton("Press me!", request_poll=KeyboardButtonPollType())]]
	message = "Press the button to let the bot generate a preview for your poll"
	# using one_time_keyboard to hide the keyboard
	update.effective_message.reply_text(
		message, reply_markup=ReplyKeyboardMarkup(button, one_time_keyboard=True)
	)


def receive_poll(update: Update, context: CallbackContext) -> None:
	"""On receiving polls, reply to it by a closed poll copying the received poll"""
	actual_poll = update.effective_message.poll
	# Only need to set the question and options, since all other parameters don't matter for
	# a closed poll
	update.effective_message.reply_poll(
		question=actual_poll.question,
		options=[o.text for o in actual_poll.options],
		# with is_closed true, the poll/quiz is immediately closed
		is_closed=True,
		reply_markup=ReplyKeyboardRemove(),
	)


def help_handler(update: Update, context: CallbackContext) -> None:
	"""Display a help message"""
	update.message.reply_text(
		"Използвай /start за произволна рецепта, /cook за да я сготвиш, /set {секунди} за таймер, /random {число1} {число2(опционално)} за число от 0 до {число} или в диапазон.")


def alarm(context):
	"""Send the alarm message."""
	job = context.job
	context.bot.send_message(job.context, text='Beep!')


def remove_job_if_exists(name, context):
	"""Remove job with given name. Returns whether job was removed."""
	current_jobs = context.job_queue.get_jobs_by_name(name)
	if not current_jobs:
		return False
	for job in current_jobs:
		job.schedule_removal()
	return True


def set_timer(update: Update, context: CallbackContext) -> None:
	"""Add a job to the queue."""
	chat_id = update.message.chat_id
	try:
		# args[0] should contain the time for the timer in seconds
		due = int(context.args[0])
		if due < 0:
			update.message.reply_text('Sorry we can not go back to future!')
			return

		job_removed = remove_job_if_exists(str(chat_id), context)
		context.job_queue.run_once(alarm, due, context=chat_id, name=str(chat_id))

		text = 'Timer successfully set!'
		if job_removed:
			text += ' Old one was removed.'
		update.message.reply_text(text)

	except (IndexError, ValueError):
		update.message.reply_text('Usage: /set <seconds>')


def unset(update: Update, context: CallbackContext) -> None:
	"""Remove the job if the user changed their mind."""
	chat_id = update.message.chat_id
	job_removed = remove_job_if_exists(str(chat_id), context)
	text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
	update.message.reply_text(text)


@run_async
def coinflip(update, context):
	"""Flips a coin"""
	args = context.args
	if len(args) == 2:
		coin = [args[0], args[1]]
	else:
		coin = ['Head', 'Tails']
	update.message.reply_text(f'🔄 {choice(coin)}')


@run_async
def random_number(update, context):
	"""Flips a coin"""
	args = context.args
	if len(args) == 1:
		num_range = [num for num in range(0, int(args[0]) + 1)]
	else:
		num_range = [num for num in range(int(args[0]), int(args[1]) + 1)]
	update.message.reply_text(f'{choice(num_range)}')


def daily_job(context: CallbackContext):
	birthday_sql = '''select name, date from holidays
	where strftime('%d.%m', date) = strftime('%d.%m', date('now'))'''
	birthdays = run_sql(birthday_sql)
	#context.bot.send_message(chat_id='67310463', text=f"It's work!")
	for birthday in birthdays:
		name, date = [*birthday]
		greeting_date = datetime.datetime.now()
		today = greeting_date.strftime('%d.%m')
		years = int(greeting_date.strftime('%Y')) - int(date[:4])
		context.bot.send_message(chat_id='-1001356679470', text=f'Днес {today} - {name} става на {years} години. Да ни е жив и здрав!')