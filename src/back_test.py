import pyupbit
import numpy as np

# OHLCV: Open High Low Close Volume. 당일 시가, 고가, 저가, 종가, 거래량에 대한 data
df = pyupbit.get_ohlcv("KRW-BTC", count=7)

# ==========================================================
# 전략 

# 변동폭*k 계산. (고가-저가)*k value
df['range'] = (df['high'] - df['low']) *0.5

# target(매수가), range column을 한 칸씩 밑으로 내림
df['target'] = df['open'] + df['range'].shift(1)

# ==========================================================


# np.where(조건문, 참일때 값, 거짓일 때 값)
fee = 0.0005
df['ror'] = np.where(df['high'] > df['target'], df['close']/df['target'] - fee, 1)

# 누적 곱 계산(cumprod) => 누적 수익률
df['hpr'] = df['ror'].cumprod()
# Draw Down 계산. (누적 최대 값과 현재 hpr 차이/ 누적 최대값*100)
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() *100

print(f"MDD(%): {df['dd'].max()}") 
df.to_csv("dd.csv")
