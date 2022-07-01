import sys
from PyQt5.QtGui import QPalette, QBrush, QPixmap
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pyupbit
import time

from SystemStatus import SystemStatus

# UPBIT KEY 확인 후 시작 잔고와 현재 잔고를 반환하는 QThread Class 입니다.
class Worker(QThread):
    balance = pyqtSignal(float, float)

    def __init__(self, apikey, seckey):
        super().__init__()
        self.apikey = apikey
        self.seckey = seckey
        self.alive = True
        self.upbit = pyupbit.Upbit(self.apikey, self.seckey)
        self.start_balance = self.upbit.get_balance()

    def run(self):
        while self.alive:
            self.upbit = pyupbit.Upbit(self.apikey, self.seckey)

            if self.start_balance != None:
                cur_balance = self.upbit.get_balance()
                self.balance.emit(self.start_balance, cur_balance)
                time.sleep(1)
            else:
                time.sleep(1)

    def pyupbit_update(self):
        self.upbit = pyupbit.Upbit(self.apikey, self.seckey)
        self.start_balance = self.upbit.get_balance()

    def close(self):
        self.alive = False


# 잔고 UI를 그리는 QWidget Class 입니다.
class BalanceWidget(QWidget):
    def __init__(self, parent=None, ticker="KRW-BTC"):
        super().__init__(parent)
        self.sys_stat = SystemStatus()
        uic.loadUi("resource/balance.ui", self)
        
        self.apikey = self.sys_stat.access
        self.seckey = self.sys_stat.secret

        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("./resource/bg.png")))
        palette.shadow()
        self.setPalette(palette)

        self.worker = Worker(self.apikey, self.seckey)
        self.worker.balance.connect(self.def_balance)
        self.worker.start()

    @pyqtSlot(float, float)
    def def_balance(self, start_balance, cur_balance):
        # print(cur_balance)
        self.label_start.setText(f"{start_balance:.4f}")
        self.label_current.setText(f"{cur_balance:.4f}")
        profit = (cur_balance / start_balance) * 100 - 100
        self.label_profit.setText(f"{profit:,} %")
        self.def_updateStyle()

    def def_updateStyle(self):
        if '-' in self.label_profit.text():
            self.label_profit.setStyleSheet("color:blue;font-weight:bold;")
        else:
            self.label_profit.setStyleSheet("color:red;font-weight:bold;")

    def def_inputkey(self, apikey, seckey):
        self.worker.apikey = apikey
        self.worker.seckey = seckey
        self.worker.pyupbit_update()

    def closeEvent(self, event):
        self.worker.close()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    ob = BalanceWidget()
    ob.show()
    exit(app.exec_())
