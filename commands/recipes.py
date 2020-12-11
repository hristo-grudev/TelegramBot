from telegram import (
	Update,
)
from telegram.ext import (
	CallbackContext,
	run_async,
)


@run_async
def start(update: Update, context: CallbackContext) -> None:

	"""Inform user about what this bot can do"""
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
