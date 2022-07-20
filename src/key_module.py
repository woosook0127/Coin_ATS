import jwt
import uuid
import json
import requests
import psycopg2
import pyupbit
from pprint import pprint
import time


class UpbitKey:
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.server_url = 'https://api.upbit.com/v1/'

    def get_auth(self):
        payload = {'access_key': self.access_key,
                   'nonce': str(uuid.uuid4())}
        jwt_token = jwt.encode(payload, self.secret_key).decode('utf8')
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}
        return headers

    def request_private(self, content: str):
        headers = self.get_auth()
        res = requests.get(self.server_url + content, headers=headers).json()[0]
        return res

    def request_public(self, content: str, querystring: dict):
        res = requests.request("GET", self.server_url + content, params=querystring).json()
        return res

if __name__ == '__main__':
    access_key = 'xAfZ6fJqTwCygtSCxbUKiVVVAZCrzm16D6xl4mWi'
    secret_key = 'qkAnthvqDvx6qChrXpNS9dPIdWuaUIxif6bvxYLo'
    up = UpbitKey(access_key, secret_key)

    while 1:
        # price = pyupbit.get_ohlcv("KRW-BTC", "minute3",to='20210101')
        # time.sleep(10)
        # pprint(price)

        # markets = up.request_public('market/all', None)
        # markets = [m['market'] for m in markets]
        res = up.request_public('candles/minutes/1/', {'market': "KRW-BTC", 'count': '200'})
        print(res)
        data = list(res[0].values())[::]
        time.sleep(60)

        db = psycopg2.connect(host='localhost', dbname="coin_info", user='postgres', password='9876', port='5432')
        cursor = db.cursor()
        sql = "INSERT INTO candle(market, candle_date_time_utc, candle_date_time_kst, opening_price, high_price, low_price, trade_price, timestamp, candle_acc_trade_price, candle_acc_trade_volume,unit) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        cursor.execute(sql, data)
        # cursor.fetchall()
        db.commit()
        print("done")
        # try:
        #     db = psycopg2.connect(host='localhost', dbname="coin_info", user='postgres', password='9876', port='5432')
        #     cursor = db.cursor()
        #     sql = "INSERT INTO candle(market, candle_date_time_utc, candle_date_time_kst, opening_price, high_price, low_price, trade_price, timestamp, candle_acc_trade_price, candle_acc_trade_volume,unit) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        #     cursor.execute(sql, data)
        #     cursor.fetchmany()
        #     db.commit()
        #     print("done")
        # except Exception as e:
        #     print("please wait")

        cursor.close()
        db.close()
    # CREATE TABle candle(
    # market    VARCHAR(10),
    # candle_date_time_utc    VARCHAR(10),
    # candle_date_time_kst    VARCHAR(10),
    # opening_price    NUMERIC,
    # high_price    NUMERIC,
    # low_price    NUMERIC,
    # trade_price    NUMERIC,
    # timestamp     NUMERIC,
    # candle_acc_trade_price    NUMERIC,
    # candle_acc_trade_volume    NUMERIC,
    # unit   Integer);
