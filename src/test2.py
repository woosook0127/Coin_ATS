import pyupbit
from pprint import pprint
from tests import insertDB
import psycopg2
import time

access = 'xAfZ6fJqTwCygtSCxbUKiVVVAZCrzm16D6xl4mWi'
secret = 'qkAnthvqDvx6qChrXpNS9dPIdWuaUIxif6bvxYLo'

upbit = pyupbit.Upbit(access, secret)

data = upbit.get_order("KRW-BTC", state='done')
# time.sleep(5)
for i in data:
    datas = list(i.values())
    # print(datas)
    try:
        insertDB('result', datas)
        print("OK")
    except Exception as e:
        print("already done!")
        break;