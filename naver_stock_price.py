import time
import os
from collections import deque
import pandas as pd
import requests


pd.options.display.max_rows = 1000
pd.options.display.max_columns = 1000
HEADERS = {"User-Agent":'Mozilla/5.0'}

def make_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    else:
        print('already existed dir')
        return

class StockPrice:
    stock_items = {
        '005930': '삼성전자', '051910': 'LG화학', '063160': '종근당바이오', '006400': '삼성SDI', '185750': '종근당',
        '006980': '우성사료', '096770': 'SK이노베이션', '035720': '카카오', '214390': '경보제약', '011200': 'HMM',
    }
    stock_names = [name for name in stock_items.values()]

    def __init__(self, *code_list):
        self.code_list = list(code_list)
        self._start = 1
        self._end = 5
        self.sep = self._end - self._start + 1
        self.item = None
        self.item_list = []
        self.dfs = []

    def __len__(self):
        return len(self.dfs)

    def __getitem__(self, index):
        return self.dfs[index]

    def __getattr__(self, name):
        cls = type(self)
        if name in cls.stock_names and name in self.item_list:
            index = self.item_list.index(name)
            return self.dfs[index]
        raise AttributeError(f'{cls.__name__} object has no attribute {name}')

    def __call__(self, idx):
        return self.dfs[idx]

    def __str__(self):
        return f'Stock Information: {self.item_list}, ' \
               f'DataFrame count: {len(self.dfs)}'

    @property
    def page(self):
        return f'start page: {self._start}, end page: {self._end}'

    @page.setter
    def page(self, val):
        try:
            start, end = val
        except ValueError:
            print('please set parameter type tuple')
            return

        if start > end:
            raise ValueError('please set start below end')
        self._start = start
        self._end = end
        self.sep = self._end - self._start + 1
        print(f'start page: {self._start}, end page: {self._end}')

    def make_dataframe(self):
        url_list = [(StockPrice.stock_items.get(code, code),
                    f'https://finance.naver.com/item/sise_day.nhn?code={code}&page={page}')
                    for code in self.code_list
                    for page in range(self._start, self._end+1)]
        url_list = deque(url_list)

        while url_list:
            time.sleep(0.5)
            df_list = []
            for _ in range(self.sep):
                time.sleep(0.1)
                self.item, url = url_list.popleft()
                try:
                    html = requests.get(url, headers=HEADERS).text
                except Exception as e:
                    print(e)
                    return
                df_list.append(pd.read_html(html)[0].dropna())

            self.item_list.append(self.item)
            df = pd.concat(df_list)
            df.insert(loc=0, column='종목코드', value=self.item)
            self.dfs.append(df.sort_values(by='날짜', ascending=True).set_index('날짜'))
        return self.dfs

    def save_dataframe(self, dir):
        make_dir(dir)
        if len(self.dfs) == 0:
            self.make_dataframe()
        for i, df in enumerate(self.dfs):
            df.to_csv(dir+f'/{self.code_list[i]}.csv')


if __name__ == '__main__':
    stocks = StockPrice('005930', '051910', '063160', '006400', '185750',
                         '006980', '096770', '035720', '214390', '011200', '000660')
    print(stocks.page)
    # stocks.page = (4, 3)
    stocks.page = (1, 3)
    dataframes = stocks.make_dataframe()

    print(stocks)
    print(stocks(0))
    print(stocks[0])
    print(stocks.삼성전자)
    # print(stocks.서울식품)

    for dataframe in dataframes:
        print(dataframe)
        print('-' * 100)

    stocks.save_dataframe('./source/dataframe')




