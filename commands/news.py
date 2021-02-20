import requests
from lxml import html
from newsapi import NewsApiClient
from pandas.io.json import json_normalize
import pandas as pd
from bs4 import BeautifulSoup
from random import choice
from telegram import (
	Update,
)
from telegram.ext import (
	CallbackContext,
	run_async,

)
def top_headlines():
	newsapi = NewsApiClient(api_key='3dfa9a8cae284dc5a022f17a754df3aa')
	country = 'bg'
	category = 'technology'
	top_headlines1 = newsapi.get_top_headlines(category=category, language='en', country=country)
	print(top_headlines1)
	top_headlines2 = json_normalize(top_headlines['articles'])
	print(top_headlines2)
	newdf = top_headlines2[["title", "url"]]
	dic = newdf.set_index('title')['url'].to_dict()

	return dic


def news(update, context):
	data = top_headlines()
	list_data = list(data.keys())
	number = choice(range(len(list_data)))
	update.message.reply_text(f'{list_data[number]} - {data[list_data[number]]}', disable_web_page_preview = True)


def daily_news(context: CallbackContext):
	url = 'https://novini.bg/bylgariya'
	response = requests.get(url)
	tree = html.fromstring(response.text)
	posts = tree.xpath('//article[@class="g-grid__item js-content"]')
	elements = []
	for post in posts:
		text = post.xpath('.//h2/text()')[0]
		link = post.xpath('./a/@href')[0]
		elements.append(str(text) + '\n' + str(link))
	number = choice(range(len(elements)))
	context.bot.send_message(chat_id='-1001356679470', text=f'{elements[number].text}')
