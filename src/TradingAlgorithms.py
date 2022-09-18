from operator import is_
import pyupbit
import time
from tqdm import tqdm
import pandas as pd
import numpy as np
import datetime
from SystemStatus import SystemStatus

#----------------------------------------------------------------------
class TradingAlgorithms():
    def __init__(self, sys_stat: SystemStatus):
        self.sys_stat = sys_stat
        self.LOW = 2
        self.MIDDLE = 1
        self.HIGH = 0
        self.access = self.sys_stat.access
        self.secret = self.sys_stat.secret
        self.k_value = self.sys_stat.k_value
        self.k_term = self.sys_stat.k_term 
        self.buying_price = -1

        self.print_tp = True   # Flag for Printing target price
        self.plus_cut = False  # Flag for Sell at a profit

    def print_target_price(self, price):
        if self.print_tp:
            print(f"[SYSTEM] Target pirce: {price}")
            self.print_tp = False

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

#----------------------------------------------------------------------
    def back_testing(self, coin_type, k_value, term, prt:bool=False):
        time.sleep(0.1) # Redundant
        try:
            df = pyupbit.get_ohlcv(coin_type, count=term) # Redundant
            if type(df) == type(None):
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
            print(f"[EXCEPTION] {e}")
            time.sleep(0.1)
            return 7210, 7210
        return profit, df['dd'].max()

    def find_hyper_k(self, coin_type, term):
        # k value의 최적값을 찾기 위해 backtesting하며 수익률을 확인한다.
        df = pd.DataFrame([[0,0,0]], columns=['Profit_rate', 'MDD%', 'k-value'])
        
        for i in tqdm(np.arange(0, 0.5, 0.001), desc='[SYSTEM] Progress', mininterval=0.1):
            if not self.sys_stat.is_activating:
                break
            else:
                profit, mdd = self.back_testing(coin_type, i, term, False)
                max_profit = df['Profit_rate'].max()
        
                if profit >= max_profit:
                    df = df.append(pd.Series([profit, mdd, i], index=df.columns), ignore_index=True)
        filter = df['Profit_rate'] == df['Profit_rate'].max()
        hyper_k = df[filter].iloc[0,2]

        return round(hyper_k, 3)

    def update_k(self, coin_type):
        print(f"[SYSYEM] Update {coin_type}'s k-value: {self.k_value}")
        self.k_value = self.find_hyper_k(coin_type, self.k_term)
        self.sys_stat.k_value = self.k_value
        # self.k_value = 0.1
        print(f"[SYSTEM] {coin_type}'s k-value Updated: {self.k_value}")

#----------------------------------------------------------------------
    def activate_trading(self, coin_type, trading_type):
        if self.sys_stat.is_activating:
            target = None
            selling_price = 0
            self.upbit = pyupbit.Upbit(self.access, self.secret) # log-in
            # 자동매매 시작
            print(f"[SYSTEM] Start AutoTrading with {coin_type}")
        else:
            return 

        while True:
            if not self.sys_stat.is_activating:
                return 

            if trading_type == self.HIGH: # Only Break through algorithm
                constraint = True
            elif trading_type == self.MIDDLE:
                constraint = self.range_before(coin_type) & self.noise_function(coin_type)           
            elif trading_type == self.LOW:
                constraint = self.range_before(coin_type) & self.noise_function(coin_type)
                target = self.change_target(coin_type)
            else:
                return
            try:
                if constraint:
                    now = datetime.datetime.now()
                    start_time = self.get_start_time(coin_type)
                    end_time = start_time + datetime.timedelta(days=1)
                    self.sys_stat.my_coin = self.upbit.get_balance(coin_type)
                    # apr_price = self.sys_stat.my_coin * pyupbit.get_current_price(coin_type) # appraised price
                    
                    # Trading time
                    is_trading_time = start_time < now < end_time - datetime.timedelta(seconds=120)
                    
                    if is_trading_time: # don't trading during 2min
                        current_price = pyupbit.get_current_price(coin_type)
                        if target:
                            target_price = target
                        else:
                            if self.plus_cut:
                                target_price = selling_price*1.0075
                            else:
                                target_price = self.get_target_price(coin_type, self.sys_stat.k_value)
                        self.print_target_price(target_price)
                        profit_rate = current_price/self.buying_price
                    
                        if target_price < current_price :
                            my_krw = self.upbit.get_balance("KRW")
                            if my_krw > 5000:
                                self.print_tp=True
                                print(f"[SYSTEM] Buy {coin_type} at {current_price}")
                                self.upbit.buy_market_order(coin_type, my_krw*0.9995) # 전량 매수
                                self.buying_price = current_price
                        if profit_rate >= 1.03: # 익절: 3%, 목표가 재설정
                            self.upbit.sell_market_order(coin_type, self.sys_stat.my_coin)# 전량 매도
                            selling_price = current_price
                            self.plus_cut = True
                        if 0 < profit_rate <= 0.985: # 손절: 1.5%
                            self.upbit.sell_market_order(coin_type, self.sys_stat.my_coin)# 전량 매도

                    # Resting time
                    else:
                        self.plus_cut = False
                        self.print_tp = True
                        self.update_k(coin_type)
                    time.sleep(1)

            except Exception as e:
                print(f"{e}, except")
                time.sleep(0.1)

#----------------------------------------------------------------------
    # Range compare function
    def range_before(self, coin_type):   
        df = pyupbit.get_ohlcv(coin_type, interval="day")    # coin data
        if type(df) != type(None):   
            two_days_ago = df.iloc[-3]                  # 2 days ago
            yesterday = df.iloc[-2]                     # yesterday

            two_days_ago_range = two_days_ago['high'] - two_days_ago['low']
            yesterday_range = yesterday['high'] - yesterday['low']

            if two_days_ago_range/yesterday_range >= 1.5:
                return True

        return False

#----------------------------------------------------------------------
    def change_target(self, coin_type):
        df = pyupbit.get_ohlcv(coin_type, interval="day")    # coin data
        if type(df) != type(None):   
            two_days_ago = df.iloc[-3]                  # 2 days ago
            yesterday = df.iloc[-2]                     # yesterday
            today = df.iloc[-1]                         # today
            
            two_days_ago_range = two_days_ago['high'] - two_days_ago['low']
            yesterday_range = yesterday['high'] - yesterday['low']

            return today['open'] + yesterday_range*yesterday_range/two_days_ago_range
        return None

#----------------------------------------------------------------------
    def noise_function(self, coin_type):
        df = pyupbit.get_ohlcv(coin_type, interval="day")    # coin data
        if type(df) != type(None):   
            yesterday = df.iloc[-2]                     # yesterday
    
            # Get noise
            noise = 1-np.abs((yesterday['open']-yesterday['close'])/(yesterday['high']-yesterday['low']))
            if (noise <= 0.3):
                return True
        return False