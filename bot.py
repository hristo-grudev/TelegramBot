#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that works with polls. Only 3 people are allowed to interact with each
poll/quiz the bot generates. The preview command generates a closed poll/quiz, excatly like the
one the user sends the bot
"""
import logging, sqlite3
from random import randint, choice
from config import __TOKEN__

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

from commands.run_sql import *
from commands.recipes import *
from commands.random import *
from commands.quiz import *
from commands.poll import *
from commands.news import *
from commands.help import *
from commands.coinflip import *
from commands.bd import *
from commands.alarm import *


logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

global last_recipes

last_recipes = 1


def main() -> None:
	# Create the Updater and pass it your bot's token.
	# Make sure to set use_context=True to use the new context based callbacks
	# Post version 12 this will no longer be necessary
	updater = Updater(__TOKEN__, use_context=True)
	job = updater.job_queue
	dispatcher = updater.dispatcher
	dispatcher.add_handler(CommandHandler('start', start))
	dispatcher.add_handler(CommandHandler('cook', cook))
	dispatcher.add_handler(CommandHandler('bd', bd))
	dispatcher.add_handler(CommandHandler('poll', poll))
	dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))
	dispatcher.add_handler(CommandHandler('quiz', quiz))
	dispatcher.add_handler(PollHandler(receive_quiz_answer))
	dispatcher.add_handler(CommandHandler('preview', preview))
	dispatcher.add_handler(MessageHandler(Filters.poll, receive_poll))
	dispatcher.add_handler(CommandHandler('help', help_handler))
	dispatcher.add_handler(CommandHandler("set", set_timer))
	dispatcher.add_handler(CommandHandler("unset", unset))
	dispatcher.add_handler(CommandHandler("news", news))
	dispatcher.add_handler(CommandHandler('coinflip', coinflip, pass_args=True))
	dispatcher.add_handler(CommandHandler('random', random_number, pass_args=True))
	target_time = datetime.time(hour=8, minute=0)
	news_time = datetime.time(hour=6, minute=12)
	job.run_daily(daily_job, target_time, days=range(6))
	job.run_daily(daily_news, news_time, days=range(6))

	# on noncommand i.e message - echo the message on Telegram
	#dispatcher.add_handler(MessageHandler(Filters.text, echo))

	# Start the Bot
	updater.start_polling()

	# Run the bot until the user presses Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT
	updater.idle()


if __name__ == '__main__':
	main()