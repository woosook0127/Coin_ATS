#-----------------------------------------------------------------------
class SystemStatus():
    def __init__(self):
        self.access = ""
        self.secret = ""
        self.coin_type = "DEFAULT"  # default [KRW-???]
        self.k_value = -1           # default [0-1]
        self.k_term = 14            # default [days]
        self.buying_price = -1      # defatlt [buying price of coin]

        self.my_coin = None
        self.activate_trading = False 
    
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
