#----------------------------------------------------------------------
import time
import pyupbit
import datetime
from tqdm import tqdm
import pandas as pd
import numpy as np
import warnings

from PyQt5.QtCore import *
import pdb
#----------------------------------------------------------------------
class AutoTrading(QThread):
    def __init__(self, sys_stat, trading_algs):
        warnings.filterwarnings(action='ignore')
        super().__init__()
        print("[SYSTEM] Init AutoTrading")
        self.sys_stat = sys_stat
        self.trading_algs = trading_algs
        self.access = self.sys_stat.access
        self.secret = self.sys_stat.secret
        self.coin_type = self.sys_stat.coin_type

        self.buying_price = self.sys_stat.buying_price
        print("[SYSTEM] Start Login")

#----------------------------------------------------------------------
    def activate(self, type_of_algs):
        self.trading_algs.update_k(self.coin_type)
        if type_of_algs == self.trading_algs.HIGH:
            self.trading_algs.activate_trading(self.coin_type, type_of_algs)
        elif type_of_algs == self.trading_algs.MIDDLE:
            self.trading_algs.activate_trading(self.coin_type, type_of_algs)
        elif type_of_algs == self.trading_algs.LOW:
            self.trading_algs.activate_trading(self.coin_type, type_of_algs)
        else:
            print("[SYSTEM] Error alg_types")
            return
            
    def run(self):
        self.upbit = pyupbit.Upbit(self.access, self.secret) # log-in
        self.my_coin = self.upbit.get_balance(self.coin_type)
        self.sys_stat.is_activating = True
        self.activate(self.sys_stat.algorithm)

    def deactivate(self):
        print("[SYSTEM] Stop Trading")
        self.sys_stat.is_activating = False
        try:
            if self.my_coin != None:
                self.upbit.sell_market_order(self.coin_type, self.my_coin*0.9995)

        except Exception as e:
            print(f"[EXECPTION] {e}")
            time.sleep(0.1)

    def __del__(self):
        self.exit()

#----------------------------------------------------------------------
if __name__=='__main__':
    AT = AutoTrading()
    AT.__init__()
    AT.run()

#----------------------------------------------------------------------