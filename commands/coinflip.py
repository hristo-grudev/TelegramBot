from random import randint, choice


def coinflip(update, context):
	"""Flips a coin"""
	args = context.args
	if len(args) == 2:
		coin = [args[0], args[1]]
	else:
		coin = ['Стотинка', 'Герб']
	update.message.reply_text(f'🔄 {choice(coin)}')
