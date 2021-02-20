import requests
from lxml import html
from random import choice

url = 'https://novini.bg/bylgariya'
response = requests.get(url)
tree = html.fromstring(response.text)
posts = tree.xpath('//article[@class="g-grid__item js-content"]')
elements = []
for post in posts:
    text = post.xpath('.//h2/text()')[0]
    link = post.xpath('./a/@href')[0]
    print(link)
    elements.append(str(text)+'\n'+str(link))
number = choice(range(len(elements)))
text = f'{elements[number]}'
print(text)