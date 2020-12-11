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
	CallbackContext,
	run_async,
)

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
