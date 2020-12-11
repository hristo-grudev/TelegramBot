from telegram import (
	Update,
)
from telegram.ext import (
	CallbackContext,
	run_async,
)


def help_handler(update: Update, context: CallbackContext) -> None:
	"""Display a help message"""
	update.message.reply_text(
		"Използвай /start за произволна рецепта, "
		"/cook за да я сготвиш, "
		"/set {секунди} за таймер, "
		"/random {число1} {число2(опционално)} за число от 0 до {число} или в диапазон.")
