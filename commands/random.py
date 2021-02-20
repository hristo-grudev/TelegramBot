from random import randint, choice


def random_number(update, context):
	"""Flips a coin"""
	args = context.args
	if len(args) == 1:
		num_range = [num for num in range(0, int(args[0]) + 1)]
	else:
		num_range = [num for num in range(int(args[0]), int(args[1]) + 1)]
	update.message.reply_text(f'{choice(num_range)}')
