import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from pyupbit import WebSocketManager

class OverViewWorker(QThread):
    data24Sent = pyqtSignal(float, float, int, float, int, float, int, int)

    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        self.alive = True
        self.wm = WebSocketManager("ticker", [f"KRW-{self.ticker}"])

    def run(self):
        while self.alive:
            data = self.wm.get()
            self.data24Sent.emit(float(data.get("signed_change_rate")),
                                 float(data.get("change_rate")), #volumePower acc_trade_volume
                                 int  (data.get("trade_price")),
                                 float(data.get("acc_trade_volume_24h")),
                                 int  (data.get("high_price")),
                                 float(data.get("acc_trade_price_24h")),
                                 int  (data.get("low_price")),
                                 int  (data.get("prev_closing_price")))

        self.wm.terminate()

    def updateWebsocket(self):
        self.wm = WebSocketManager("ticker", [f"KRW-{self.ticker}"])

    def close(self):
        self.alive = False
        super().terminate()


class OverviewWidget(QWidget):
    def __init__(self, parent=None, ticker="BTC", ):
        super().__init__(parent)
        uic.loadUi("resource/overview.ui", self)

        self.ticker = ticker
        self.ovw = OverViewWorker(ticker)
        self.updateTicker(ticker)
        self.ovw.data24Sent.connect(self.fill24Data)
        self.ovw.start()

    def updateTicker(self, ticker):
        self.ovw.ticker = ticker
        self.ovw.updateWebsocket()

    def closeEvent(self, event):
        self.ovw.close()

    def fill24Data(self, chgRate, volumePower, currPrice, volume, highPrice, value, lowPrice, PrevClosePrice):
        self.label.setText(f"{self.ticker}")
        self.label_1.setText(f"{currPrice:,}")
        self.label_2.setText(f"{chgRate*100:+.2f} %")
        self.label_4.setText(f"{volume:.2f} {self.ticker}")
        self.label_6.setText(f"{highPrice:,}")
        self.label_8.setText(f"{value/100000000:,.1f} 억")
        self.label_10.setText(f"{lowPrice:,}")
        self.label_12.setText(f"{volumePower*100:.3f}%")
        self.label_14.setText(f"{PrevClosePrice:,}")
        self.__updateStyle()

    def __updateStyle(self):
        if '-' in self.label_2.text():
            self.label_1.setStyleSheet("color:blue;")
            self.label_2.setStyleSheet("background-color:blue;color:white")
        else :
            self.label_1.setStyleSheet("color:red;")
            self.label_2.setStyleSheet("background-color:red;color:white")

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    ob = OverviewWidget()
    ob.show()
    exit(app.exec_())
