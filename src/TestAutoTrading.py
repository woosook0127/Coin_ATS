import time
import pyupbit
import datetime

class main:
	def __init__(self):	
		print("Initialize")
		self.access = "xTgB4NarGyQ1hYbkFRtMGVJhskdVTsw0mRlzdyES"
		self.secret = "1xk3iwoQgqyCO7uQ1ZE9Ce0fyAFrFm0w3FOUDNOr"
		self.coin_type = "KRW-NEAR"
		self.k_value = 0.048

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

	def activate(self):
		print("Enter activate")
		buying_price = 99999999999
		print("Get start Login")
		upbit = pyupbit.Upbit(self.access, self.secret) # log-in
		# 자동매매 시작
		print("Trading activated")
		while True:
			try:
				now = datetime.datetime.now()
				start_time = self.get_start_time(self.coin_type)
				end_time = start_time + datetime.timedelta(days=1)
				my_btc = upbit.get_balance(self.coin_type)
				apr_price = my_btc * pyupbit.get_current_price(self.coin_type) # appraised price
        
				# Trading time
				if start_time < now < end_time - datetime.timedelta(seconds=10):
					target_price = self.get_target_price(self.coin_type, self.k_value)
					current_price = pyupbit.get_current_price(self.coin_type)
           
					if target_price < current_price:
						my_krw = get_balance("KRW")
						if my_krw > 5000:
							upbit.buy_market_order(self.coin_type, my_krw*0.9995) # 전량 매수
							buying_price = current_price
					if current_price/buying_price > 1.3:
						upbit.sell_market_order(self.coin_type, my_btc*0.9995)# 전량 매도 
        
	        	# Resting time
				else:
					if apr_price > 5000: # 거래 최소금액 이상이면
						upbit.sell_market_order(self.coin_type, my_btc*0.9995) # 전량 매도
				time.sleep(1)
			except Exception as e:
				print(e)
				time.sleep(0.1)


if __name__=='__main__':
	ma = main()
	ma.__init__()
	ma.activate()
