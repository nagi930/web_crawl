import time
import os
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


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
        self.sep = 5
        self.item_list = []
        self.dfs = []

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
        self.sep = end - start + 1
        print(f'start page: {self._start}, end page: {self._end}')

    def make(self, urls):
        df_list = []
        for stock_code, stock_name, url in urls:
            time.sleep(0.1)
            html = requests.get(url, headers=HEADERS).text
            df_list.append(pd.read_html(html)[0].dropna())
        self.item_list.append(urls[0][1])
        df = pd.concat(df_list)
        df.insert(loc=1, column='stock_name', value=urls[0][1])
        df.insert(loc=0, column='stock_code', value=urls[0][0])
        df = df.sort_values(by='날짜', ascending=True)
        df = df[['stock_code', '날짜', 'stock_name', '시가', '고가', '저가', '종가', '거래량']]
        df.columns = ['stock_code', 'stock_date', 'stock_name', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']
        return df.reset_index(drop=True)

    def make_dataframe(self):
        url_list = [[(code, StockPrice.stock_items.get(code, code),
                    f'https://finance.naver.com/item/sise_day.nhn?code={code}&page={page}')
                    for page in range(self._start, self._end+1)] for code in self.code_list]

        MAX = 20
        WORKERS = min(MAX, len(url_list))

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=WORKERS) as executor:  # with ProcessPoolExecutor() as executor:
            self.dfs = executor.map(self.make, url_list)

        end_time = time.time() - start_time

        print(f'duration of time: {end_time:.2f}s')
        return self.dfs


    def save_dataframe(self, dir):
        make_dir(dir)
        self.make_dataframe()
        for i, df in enumerate(self.dfs):
            df.to_csv(dir+f'/{self.code_list[i]}.csv')


if __name__ == '__main__':
    stocks = StockPrice('005930', '051910', '063160', '006400', '185750',
                         '006980', '096770', '035720', '214390', '011200', '000660')
    stocks.page = (1, 1)
    stocks.make_dataframe()
    for stock_df in stocks.dfs:
        print(stock_df)

    stocks.save_dataframe('./source/dataframe')




