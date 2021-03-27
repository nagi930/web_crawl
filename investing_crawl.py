import time
import re

import requests
from bs4 import BeautifulSoup


class Article:
    __slots__ = ['title', 'url', 'publish', 'content', 'date']
    def __init__(self, title, url, publish, content, date):
        self.title = title
        self.url = url
        self.publish = publish
        self.content = content
        self.date = date


HEADERS = {"User-Agent":'Mozilla/5.0'}
base = 'https://kr.investing.com/news/economy'
res = requests.get(base, headers=HEADERS).text.encode('utf-8')
soup = BeautifulSoup(res, 'lxml')

temp = soup.find('div', class_='largeTitle')
articles = temp.find_all('article', class_="js-article-item articleItem")

for article in articles[:10]:
    time.sleep(0.1)
    title = article.find('a', class_='title').text
    href = article.find('a', class_='title').attrs['href']
    article_num = href.split('/')[-1]
    publish = article.find('span', class_='articleDetails').contents[0].string




    url = base + '/' + article_num
    res = requests.get(url, headers=HEADERS).text.encode('utf-8')
    soup = BeautifulSoup(res, 'lxml')

    date = soup.select_one('div.contentSectionDetails > span').string
    date = re.search(r'\(.*\)', date).group()
    content = soup.find('div', class_='WYSIWYG articlePage').text
    content = re.sub(r'© Reuters\.s*', '', content)

    print(title, article_num, publish, date, content, sep='\n')

