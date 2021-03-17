import os
import re
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
import requests


HEADERS = {"User-Agent":'Chrome/88.0.4044.113'}

class NewsImage:
    def __init__(self, date, base='http://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=001', start=1, end=3):
        self.base = base
        self.date = date
        self._start_page = start
        self.end_page = end
        self.url = base + f'&date={self.date}' + f'&page={self._start_page}'
        reviews = requests.get(self.url, headers=HEADERS).text.encode('utf-8')
        self.soup = BeautifulSoup(reviews, 'html.parser')
        self.dl = self.soup.find('ul', class_='type06_headline').find_all('dl')

    @property
    def start_page(self):
        return self._start_page

    @start_page.setter
    def start_page(self, value):
        self._start_page = value
        self.url = self.base + f'&date={self.date}' + f'&page={self._start_page}'
        reviews = requests.get(self.url, headers=HEADERS).text.encode('utf-8')
        self.soup = BeautifulSoup(reviews, 'html.parser')
        self.dl = self.soup.find('ul', class_='type06_headline').find_all('dl')


    def save_images(self, soup):
        for item in soup:
            title = item.find('dt', class_='').find('a').text.strip()
            try:
                img_link = item.find('dt', class_='photo').find('img')['src'].split('?')[0]
                urlretrieve(img_link, f'source/image/{self.date}/{title}.jpg')
                print(f'download - /image/{self.date}/{title}.jpg')

            except OSError as e:
                title = re.sub('[\/:*?\"<>|]', '', title)
                img_link = item.find('dt', class_='photo').find('img')['src'].split('?')[0]
                urlretrieve(img_link, f'source/image/{self.date}/{title}.jpg')
                print(e, f'renamed as "{title}.jpg"', sep='\n')

            except AttributeError as e:
                print(e, '--- No image')

        print(f'download complete. date: {self.date} page: {self.start_page}/{self.end_page}')

    def start(self):
        makedir(f'source/image/{self.date}')
        while self.start_page <= self.end_page:
            self.save_images(self.dl)
            self.start_page += 1

def makedir(dir):
        if not os.path.exists(dir):
            os.makedirs(dir)
        else:
            print('already existed dir')
            return


if __name__ == '__main__':
    image = NewsImage(20210315)
    image.start()

