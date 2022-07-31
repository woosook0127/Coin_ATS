#-----------------------------------------------------------------------
class SystemStatus():
    def __init__(self):
        self.access = "xTgB4NarGyQ1hYbkFRtMGVJhskdVTsw0mRlzdyES"
        self.secret = "1xk3iwoQgqyCO7uQ1ZE9Ce0fyAFrFm0w3FOUDNOr"
        self.coin_type = "DEFAULT"  # default [KRW-???]
        self.k_value = -1           # default [0-1]
        self.k_term = 14            # default [days]
        self.buying_price = -1      # defatlt [buying price of coin]

        self.my_coin = 0
        self.activate_trading = False 
        self.is_activating = False
        self.algorithm = -1

#-----------------------------------------------------------------------