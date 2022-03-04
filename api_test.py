import pyupbit 

access = "xTgB4NarGyQ1hYbkFRtMGVJhskdVTsw0mRlzdyES"
secret = "1xk3iwoQgqyCO7uQ1ZE9Ce0fyAFrFm0w3FOUDNOr"
upbit = pyupbit.Upbit(access, secret)

print(upbit.get_balance("KRW-XRP"))     # KRW-XRP 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회
