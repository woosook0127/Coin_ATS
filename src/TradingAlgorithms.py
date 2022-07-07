import pyupbit
import time
from tqdm import tqdm
import pandas as pd
import numpy as np
import datetime

#----------------------------------------------------------------------
class TradingAlgorithms():
    def __init__(self, sys_stat):
        self.sys_stat = sys_stat
        self.BREAKTHROUGH = 0
        self.RANGECOMPARE = 1
        self.TPCHANGE = 2
        self.NOISETRADE = 3
        self.k_value = self.sys_stat.k_value
        self.k_term = self.sys_stat.k_term 
        
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

        return hyper_k

    def update_k(self, coin_type):
        print(f"[SYSYEM] Update k-value: {self.k_value}")
        self.k_value = self.find_hyper_k(coin_type, self.k_term)
        self.sys_stat.k_value = self.k_value
        print(f"[SYSTEM] k-value Updated: {self.k_value}")

    def activate_BT(self, coin_type):
        if self.sys_stat.is_activating:
            self.upbit = pyupbit.Upbit(self.access, self.secret) # log-in
            # 자동매매 시작
            print("[SYSTEM] Start AutoTrading")
        else:
            return 
        while True:
            try:
                now = datetime.datetime.now()
                start_time = self.get_start_time(coin_type)
                end_time = start_time + datetime.timedelta(days=1)
                self.sys_stat.my_coin = self.my_coin
                apr_price = self.my_coin * pyupbit.get_current_price(coin_type) # appraised price

                # Trading time
                if start_time < now < end_time - datetime.timedelta(seconds=120): # don't trading during 2min
                    target_price = self.get_target_price(coin_type, self.sys_stat.k_value)
                    current_price = pyupbit.get_current_price(coin_type)
                    profit_rate = current_price/buying_price

                    if target_price < current_price:
                        my_krw = self.upbit.get_balance("KRW")
                        if my_krw > 5000:
                            print(f"SYS: Buy {coin_type}: {current_price}")
                            self.upbit.buy_market_order(coin_type, my_krw*0.9995) # 전량 매수
                            buying_price = current_price
                    if profit_rate >= 1.03: # 익절: 2.5%
                        self.upbit.sell_market_order(coin_type, self.my_coin*0.9995)# 전량 매도 
                    if 0 < profit_rate <= 0.97: # 손절: 3%
                        self.upbit.sell_market_order(coin_type, self.my_coin*0.9995)# 전량 매도

                # Resting time
                else:
                    if apr_price > 5000: # 거래 최소금액 이상이면
                        self.upbit.sell_market_order(coin_type, self.my_coin*0.9995) # 전량 매도
                    self.update_k(coin_type)
                time.sleep(1)

            except Exception as e:
                time.sleep(0.1)

#----------------------------------------------------------------------
    # Range compare function
    def range_before(coin_type):   
        df = pyupbit.get_ohlcv(coin_type, "day")    # coin data
        two_days_ago = df.iloc[-3]                  # 2 days ago
        yesterday = df.iloc[-2]                     # yesterday

        two_days_ago_range = two_days_ago['high'] - two_days_ago['low']
        yesterday_range = yesterday['high'] - yesterday['low']

        if yesterday_range/two_days_ago_range > 1.5:
            return 1
        return 0

    def activate_RC(self, coin_type):
        if self.sys_stat.is_activating:
            self.upbit = pyupbit.Upbit(self.access, self.secret) # log-in
            # 자동매매 시작
            print("[SYSTEM] Start AutoTrading")
            
            target_price = cal_target(coin_type)
            before = self.range_before(coin_type)
            op_mode = False
            hold = False
        else:
            return

        try:
            while (True):
                price = pyupbit.get_current_price(coin_type)

                # Try selling at every seconds checking selling conditions
                if op_mode is True and price is not None:
                    if price >= target_price and before == 1 and hold is False:
                        krw_balance = self.upbit.get_balance(coin_type)
                        self.upbit.buy_market_order(coin_type, krw_balance)
                        hold = True

        except Exception as e:
            time.sleep(0.1)

#----------------------------------------------------------------------
    def change_target(coin_type):
        df = pyupbit.get_ohlcv(coin_type, "day")    # coin data
        two_days_ago = df.iloc[-3]                  # 2 days ago
        yesterday = df.iloc[-2]                     # yesterday
        today = df.iloc[-1]                         # today
        
        two_days_ago_range = two_days_ago['high'] - two_days_ago['low']
        yesterday_range = yesterday['high'] - yesterday['low']

        return today['open'] + yesterday_range*(yesterday_range/two_days_ago_range)

    def activate_TC(self, coin_type):
        if self.sys_stat.is_activating:
            self.upbit = pyupbit.Upbit(self.access, self.secret) # log-in
            # 자동매매 시작
            print("[SYSTEM] Start AutoTrading")

            target_price = self.change_target(coin_type)
            op_mode = False
            hold = False
        else:
            return

        try:
            while (True):
                price = pyupbit.get_current_price(coin_type)

                # Try selling at every seconds checking selling conditions
                if op_mode is True and price is not None:
                    if price >= target_price and hold is False:
                        krw_balance = self.upbit.get_balance(coin_type)
                        self.upbit.buy_market_order(coin_type, krw_balance)
                        hold = True

        except Exception as e:
            time.sleep(0.1)

#----------------------------------------------------------------------
    def noise_function(coin_type):
        df = pyupbit.get_ohlcv(coin_type, "day")    # coin data
        yesterday = df.iloc[-2]                     # yesterday
 
        # Get noise
        noise = 1-np.abs((yesterday['open']-yesterday['close'])/(yesterday['high']-yesterday['low']))
        if (noise <= 0.3):
            return 1
        return 0

    def activate_NT(self):
        if self.sys_stat.is_activating:
            self.upbit = pyupbit.Upbit(self.access, self.secret) # log-in
            # 자동매매 시작
            print("[SYSTEM] Start AutoTrading")
            target_price = cal_target(coin_type)
            noise = self.noise_function(coin_type)  # Calculate noise
            op_mode = False
            hold = False
        else:
            return

        try:
            while (True):
                price = pyupbit.get_current_price(coin_type)

                # Try selling at every seconds checking selling conditions
                if op_mode is True and price is not None:
                    if price >= target_price and noise == 1 and hold is False:
                        krw_balance = self.upbit.get_balance(coin_type)
                        self.upbit.buy_market_order(coin_type, krw_balance)
                        hold = True

        except Exception as e:
            time.sleep(0.1)
