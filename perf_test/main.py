#----------------------------------------------------------------------
import sys
import os, time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from SystemStatus import SystemStatus
from AutoTrading import AutoTrading
from TradingAlgorithms import TradingAlgorithms

#-----------------------------------------------------------------------
class main():
    def __init__(self):
        super(main, self).__init__()

        self.sys_stat = SystemStatus()
        self.trading_algs = TradingAlgorithms(self.sys_stat)
        self.auto_trading = AutoTrading(self.sys_stat, self.trading_algs)
        
        
        
    def closeAll(self):
        os.system("ps -aux | grep main.py | awk '{print $2}' | xargs kill -9 > res.out 2>&1")
        
#-----------------------------------------------------------------------
if __name__ == "__main__":
    # Main process
    main()

#-----------------------------------------------------------------------
