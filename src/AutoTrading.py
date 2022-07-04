#----------------------------------------------------------------------
import time
import pyupbit
import datetime
from tqdm import tqdm
import pandas as pd
import numpy as np
import warnings

from PyQt5.QtCore import *

#----------------------------------------------------------------------
class AutoTrading(QThread):
    def __init__(self, sys_stat):
        warnings.filterwarnings(action='ignore')
        super().__init__()
        print("Initializition...")
        self.sys_stat = sys_stat
        self.access = self.sys_stat.access
        self.secret = self.sys_stat.secret
        self.coin_type = self.sys_stat.coin_type
        #self.my_coin = self.upbit.get_balance(self.coin_type)
        self.k_value = self.sys_stat.coin_type
        self.k_term = self.sys_stat.k_term 
        self.buying_price = self.sys_stat.buying_price
        self.is_activating = False 
        print("SYS: Get start Login")

    # 매수 목표가 조회 - 변동성 돌파 전략
    def get_target_price(self, coin_type, k):  
        df = pyupbit.get_ohlcv(coin_type, interval="day", count=2)
        target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
        return target_price

    # 시작 시간 조회
    def get_start_time(self, coin_type):
        df = pyupbit.get_ohlcv(coin_type, interval="day", count=1)
        start_time = df.index[0]
        return start_time

    def back_testing(self, coin_type, k_value, term, prt:bool=False):
        time.sleep(0.1) # Redundant
        try:
            df = pyupbit.get_ohlcv(coin_type, count=term) # Redundant
            if df == None:
                return 7210, 7210
            df['range'] = (df['high'] - df['low']) * k_value
            df['target'] = df['open'] + df['range'].shift(1) 
            fee = 0.0032
            df['ror'] = np.where(df['high'] > df['target'], df['close']/df['target'] - fee, 1)
            df['hpr'] = df['ror'].cumprod()
            df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

            pct = df['hpr'][-1]
            profit = round(pct-1, 5) * 100

            if (prt):
                print_str = f"{coin_type} {term}일간 수익률: {profit}%, MDD: {df['dd'].max()}"
                print(print_str)

        except Exception as e:
            print(e)
            time.sleep(0.1)
            return 7210, 7210
        return profit, df['dd'].max()

    def find_hyper_k(self, coin_type, term):
        # k value의 최적값을 찾기 위해 backtesting하며 수익률을 확인한다.
        df = pd.DataFrame([[0,0,0]], columns=['Profit_rate', 'MDD%', 'k-value'])
        
        for i in tqdm(np.arange(0, 0.5, 0.001), desc='Progress', mininterval=0.1):
            if not self.is_activating:
                break
            else:
                profit, mdd = self.back_testing(coin_type, i, term, False)
                max_profit = df['Profit_rate'].max()
        
                if profit >= max_profit:
                    df = df.append(pd.Series([profit, mdd, i], index=df.columns), ignore_index=True)
        filter = df['Profit_rate'] == df['Profit_rate'].max()
        hyper_k = df[filter].iloc[0,2]

        return hyper_k

    def update_k(self, coin_type):
        print(f"SYS: k-value updating...: {self.k_value}")
        self.k_value = self.find_hyper_k(coin_type, self.k_term)
        self.sys_stat.k_value = self.k_value
        print(f"SYS: k-value updated !!!: {self.k_value}")

#----------------------------------------------------------------------
    def run(self):
        self.upbit = pyupbit.Upbit(self.access, self.secret) # log-in
        self.my_coin = self.upbit.get_balance(self.coin_type)
        print("AutoTrading RunnIng")
        self.is_activating = True
        self.update_k(self.coin_type)
        self.activate()

    def activate(self):
        if self.is_activating:
            print("Sys: Activating ...")
            #self.upbit = pyupbit.Upbit(self.access, self.secret) # log-in
         
            # 자동매매 시작
            print("Sys: Trading activated")
        else:
            return
        while True:
            try:
                now = datetime.datetime.now()
                start_time = self.get_start_time(self.coin_type)
                end_time = start_time + datetime.timedelta(days=1)
                #self.my_coin = self.upbit.get_balance(self.coin_type)
                self.sys_stat.my_coin = self.my_coin
                apr_price = self.my_coin * pyupbit.get_current_price(self.coin_type) # appraised price

                # Trading time
                if start_time < now < end_time - datetime.timedelta(seconds=120): # don't trading during 2min
                    target_price = self.get_target_price(self.coin_type, self.k_value)
                    current_price = pyupbit.get_current_price(self.coin_type)
                    profit_rate = current_price/buying_price

                    if target_price < current_price:
                        my_krw = get_balance("KRW")
                        if my_krw > 5000:
                            print(f"SYS: Buy {coin_type}: {current_price}")
                            self.upbit.buy_market_order(self.coin_type, my_krw*0.9995) # 전량 매수
                            buying_price = current_price
                    if profit_rate >= 1.25: # 익절: 2.5%
                        self.upbit.sell_market_order(self.coin_type, self.my_coin*0.9995)# 전량 매도 
                    if 0 < profit_rate <= 0.97: # 손절: 3%
                        self.upbit.sell_market_order(self.coin_type, self.my_coin*0.9995)# 전량 매도

                # Resting time
                else:
                    if apr_price > 5000: # 거래 최소금액 이상이면
                        self.upbit.sell_market_order(self.coin_type, self.my_coin*0.9995) # 전량 매도
                    self.update_k(self.coin_type)
                time.sleep(1)

            except Exception as e:
                time.sleep(0.1)

    def deactivate(self):
        print("SYS: Deactivate trading")
        self.is_activating = False
        try:
            if self.my_coin != None: 
                self.upbit.sell_market_order(self.coin_type, self.my_coin*0.9995)

        except Exception as e:
            print(f"Exception: {e}")
            time.sleep(0.1)

    def __del__(self):
        self.exit()

#----------------------------------------------------------------------

if __name__=='__main__':
    AT = AutoTrading()
    AT.__init__()
    AT.run()
