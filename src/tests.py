import pyupbit
from pprint import pprint
import jwt
import hashlib
import os
import requests
import uuid
import psycopg2
import pandas as pd
"""
데이터베이스에서 데이터를 조회하는 함수
"""
def selectDB(columns, table):
    db = psycopg2.connect(host='localhost', dbname="coin_info", user='postgres', password='9876', port='5432')
    cursor = db.cursor()
    sql = "SELECT {columns} FROM {table};".format(columns=columns,table=table)

    cursor.execute(sql)
    result = cursor.fetchall()
    for i in result:
        print(i)
    db.commit()
    cursor.close()
    db.close()

"""
데이터베이스에 데이터를 저장하는 함수
"""
def insertDB(table,data):
    db = psycopg2.connect(host='localhost', dbname="coin_info", user='postgres', password='9876', port='5432')
    cursor = db.cursor()
    sql = "INSERT INTO {table}(uuid,side,ord_type,price,state,market,created_at,volume,remaining_volume,reserved_fee,remaining_fee,paid_fee,locked,executed_volume,trade_count)" \
          " VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s);".format(table=table)

    cursor.execute(sql,data)
    # cursor.fetchall()
    db.commit()


if __name__ == "__main__":
    access = 'xAfZ6fJqTwCygtSCxbUKiVVVAZCrzm16D6xl4mWi'
    secret = 'qkAnthvqDvx6qChrXpNS9dPIdWuaUIxif6bvxYLo'

    upbit = pyupbit.Upbit(access, secret)
    # 매도하기 ask
    # data = upbit.sell_market_order("KRW-BTC",0.0002)
    # 매수하기 bid
    # data = upbit.buy_market_order("KRW-BTC", 6000)
    # data = list(data.values())
    # print(data)
    # insertDB(table='orders',data=data)
    # selectDB('uuid, side','result')


# """
# order 주문시 데이터베이스에 기록 저장하기
# """
# db = psycopg2.connect(host='localhost', dbname="coin_info", user='postgres', password='9876', port='5432')
# cursor = db.cursor()
# sql = "INSERT INTO orders(uuid, side, ord_type, price, state, market, created_at, volume, remaining_volume, reserved_fee, remaining_fee, paid_fee, locked, executed_volume, trade_count)" \
#       " VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s);"
# cursor.execute(sql, data)
# # cursor.fetchall()
# db.commit()
# print("done")
# cursor.close()
# db.close()
# """
# 체결된 주문을 데이터 베이스에 기록하기
# """

#     try:
#     db = psycopg2.connect(host='localhost', dbname="coin_info", user='postgres', password='9876', port='5432')
#     cursor = db.cursor()
#     sql = "INSERT INTO result(uuid, side, ord_type, price, state, market, created_at, volume, remaining_volume, reserved_fee, remaining_fee, paid_fee, locked, executed_volume, trade_count)" \
#           " VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s)" \
#           "WHERE NOT EXISTS (select * from result);"
#     cursor.execute(sql, datas)
#     cursor.fetchall()
#     db.commit()
#     print("done")
    # except Exception as e:
    #     # break;
    #     print ("already done")
    # # cursor.close()
    # db.close()

# pprint(data)
# # pprint(data[0])
# print(type(data))


# print(upbit.buy_market_order("KRW-BTC",6000))
# class Databases:
#     def __int__(self):
#          self.db = psycopg2.connect(host='localhost', dbname="coin_info", user='postgres', password= '9876', port='5432')
#          self.cursor = self.db.cursor()
#
#
#
#     def execute(self,query,args={}):
#         self.cursor.execute(query,args)
#         row = self.cursor.fetchall()
#         return row
#
#     def commit(self):
#         self.cursor.commit()

# def __del__(self):
#     self.cursor.close()
#     self.db.close()


# except Exception as e:
#     print("insert DB err",e)
# class CRUD(Databases):
#     super__init__()
#     def insertDB(self,table,data):
#         sql = "INSERT INTO {table}(uuid, side, ord_type, price, state, market, created_at, volume, remaining_volume, reserved_fee, remaining_fee, paid_fee, locked, executed_volume, trade_count)" \
#               " VALUES('{data}');".format(table=table, data=data)
#         self.cursor.execute(sql)
#         self.db.commit()
# try:
#     self.cursor.execute(sql)
#     self.db.commit()
# except Exception as e:
#     print("insert DB err",e)