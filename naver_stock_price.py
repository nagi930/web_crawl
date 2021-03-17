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
    def __init__(self, code_list, start=1, end=5):
        self.code_list = code_list
        self.start = start
        self.end = end
        self.sep = end - start + 1
        self.item = None
        self.dfs = []

    def make_dataframe(self):
        url_list = [(code, f'https://finance.naver.com/item/sise_day.nhn?code={code}&page={page}')
                    for code in self.code_list
                    for page in range(self.start, self.end+1)]
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
    stocks = StockPrice(['005930', '051910', '063160', '006400', '185750',
                         '006980', '096770', '035720', '214390', '011200'])

    dataframes = stocks.make_dataframe()

    for dataframe in dataframes:
        print(dataframe)
        print('-' * 100)

    stocks.save_dataframe('./source/dataframe')