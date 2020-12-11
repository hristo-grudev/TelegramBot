from telegram import (
	Update,
)
from telegram.ext import (
	CallbackContext,
	run_async,
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