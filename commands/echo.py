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
