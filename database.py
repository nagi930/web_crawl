import time
from functools import wraps
import datetime
from enum import Enum

from pykrx import stock
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
from sqlalchemy import create_engine, types


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter() - start
        print(f'#duration of time: {end:.2f}s ')
        return result
    return wrapper

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
            print(super().__call__(*args, **kwargs))
        return cls._instances[cls]

class DataBase(metaclass=Singleton):
    class Sql(Enum):
        CREATE = 0
        DELETE = 1
        SELECT = 2

    def __init__(self, user='root', password='******', database='default_db', table='default_tb', date=datetime.datetime.today().strftime('%Y%m%d'), corp=None):
        self.user = user
        self.password = password
        self.database = database
        self.table = table
        self.con = None
        self.error_list = []
        self._corp = corp or stock.get_market_ticker_list(date)

    @property
    def corp(self):
        return self._corp

    @corp.setter
    def corp(self, codes):
        self._corp = [code for code in codes
                            if code in self._corp]
        print('상장 리스트에 없는 종목코드는 삭제됩니다.', codes, self._corp, sep='\n')

    @property
    def connect(self):
        self.con = pymysql.connect(host='localhost', port=3306, user=self.user,
                                   password=self.password, charset='utf8')
        return self.con

    def sql(self, query, database=None, table=None):
        database = database or self.database
        table = table or self.table

        if query == DataBase.Sql.CREATE:
            c = self.connect.cursor()
            c.execute(f'CREATE DATABASE IF NOT EXISTS {database}')
            self.con.commit()
            c.close()

        elif query == DataBase.Sql.SELECT:
            c = self.connect.cursor()
            c.execute(f'SELECT * FROM {database}.{table}')
            a = c.fetchone()
            print(a)
            c.close()

    def __getattr__(self, item):
        if item == 'engine':
            try:
                eg = create_engine(f'mysql+mysqldb://{self.user}:{self.password}@localhost/{self.database}', encoding='utf-8')
                setattr(self, item, eg)
                return eg
            except Exception as e:
                print(e)
        else:
            raise AttributeError

    @timer
    def save(self, start, end):
        with self.engine.connect() as conn:
            for code in self._corp:
                try:
                    df = stock.get_market_ohlcv_by_date(start, end, code)
                    df.reset_index(inplace=True)
                    df.insert(loc=1, column='종목코드', value=code)
                    df.columns = ['stock_date', 'stock_code', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']
                    df.to_sql(self.table, conn, if_exists='append',
                              index=False, dtype={'stock_date': types.DATE(),
                                                  'stock_code': types.VARCHAR(10),
                                                  'open_price': types.INTEGER(),
                                                  'high_price': types.INTEGER(),
                                                  'low_price': types.INTEGER(),
                                                  'close_price': types.INTEGER(),
                                                  'volume': types.INTEGER()
                                                  })
                except Exception as e:
                    self.error_list.append(f'Error occurred: {e} , at saving {code}')
                    print(e)
        self.engine.dispose()


if __name__ == '__main__':
    d = DataBase()
    # d.sql(DataBase.Sql.CREATE)
    # d.corp = ['005930', '051910', '063160', '006400', '185750', '006980', '096770', '035720', '214390', '011200']
    # d.save('20000101', '20210324')


