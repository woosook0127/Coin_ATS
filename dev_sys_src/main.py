#----------------------------------------------------------------------
import sys
import os, time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from SystemStatus import SystemStatus
from AutoTrading import AutoTrading
from MainUI import MainUI

#-----------------------------------------------------------------------
class main(QWidget):
    def __init__(self):
        super(main, self).__init__()
        
        self.sys_stat = SystemStatus()
        self.main_ui = MainUI(self.sys_stat)
        self.auto_trading = AutoTrading(self.sys_stat)
            
        self.main_ui.start_trading.connect(lambda: self.auto_trading.start())
        self.main_ui.stop_trading.connect(lambda: self.auto_trading.deactivate())
        self.main_ui.stop_system.connect(lambda: self.closeAll())
        self.main_ui.show()
        
    def closeAll(self):
        time.sleep(2)
        os.kill(os.getpid(), 9)
#-----------------------------------------------------------------------
if __name__ == "__main__":
    # Main process
    app = QApplication(sys.argv)

    main()
    sys.exit(app.exec_())    
#-----------------------------------------------------------------------
