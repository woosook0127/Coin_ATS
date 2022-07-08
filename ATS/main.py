import sys
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import *
import time
import datetime
from PyQt5.QtCore import QThread, pyqtSignal
from volatility import *
import pyupbit
import math

class VolatilityWorker(QThread):
    tradingSent = pyqtSignal(str, str, str)

    def __init__(self, ticker, upbit):
        super().__init__()
        self.ticker = ticker
        self.upbit = upbit
        self.alive = True

    def run(self):

        while self.alive:
            try:
                now = datetime.datetime.now()
                start_time = get_start_time("KRW-BTC")
                end_time = start_time + datetime.timedelta(days=1)

                if start_time < now < end_time - datetime.timedelta(seconds=10):
                    target_price = get_target_price("KRW-BTC", 0.5)
                    current_price = get_current_price("KRW-BTC")
                    if target_price < current_price:
                        krw = get_balance("KRW")
                        if krw > 5000:
                            print("매수를 시도합니다.")
                            # now = datetime.now()
                            # current_time = now.strftime("%H:%M:%S")
                            self.upbit.buy_market_order("KRW-BTC", krw * 0.9995)
                            # self.tradingSent.emit(current_time, "매수", "???")

                else:
                    btc = get_balance("BTC")
                    if btc > 0.00008:
                        print("매도를 시도합니다.")
                        # now = datetime.now()
                        # current_time = now.strftime("%H:%M:%S")
                        self.upbit.sell_market_order("KRW-BTC", btc * 0.9995)
                        # self.tradingSent.emit(current_time, "매도", "???")
                time.sleep(1)
            except Exception as e:
                print(e)
                time.sleep(1)

    def close(self):
        self.alive = False


form_main = uic.loadUiType("resource/mymain.ui")[0]  # 메인창 UIC
form_dialog = uic.loadUiType("resource/asset.ui")[0]  # 자산창 UIC


class QDialogClass(QtWidgets.QDialog, form_dialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.DialogButton.clicked.connect(self.dialog_close)

        self.apiKey = ""
        self.secKey = ""

    def dialog_account(self, apiKey, secKey):
        self.apiKey = apiKey
        self.secKey = secKey

        upbit = pyupbit.Upbit(apiKey, secKey)
        BTC = upbit.get_balance(ticker="KRW-BTC")
        ETH = upbit.get_balance(ticker="KRW-ETH")
        STX = upbit.get_balance(ticker="KRW-STX")
        SOL = upbit.get_balance(ticker="KRW-SOL")
        KNC = upbit.get_balance(ticker="KRW-KNC")
        TRX = upbit.get_balance(ticker="KRW-TRX")

        self.BTC_Quantity.setText(f"{BTC:,}")
        self.ETH_Quantity.setText(f"{ETH:,}")
        self.STX_Quantity.setText(f"{STX:,}")
        self.SOL_Quantity.setText(f"{SOL:,}")
        self.KNC_Quantity.setText(f"{KNC:,}")
        self.TRX_Quantity.setText(f"{TRX:,}")

        BTC_Price = pyupbit.get_current_price("KRW-BTC")
        ETH_Price = pyupbit.get_current_price("KRW-ETH")
        STX_Price = pyupbit.get_current_price("KRW-STX")
        SOL_Price = pyupbit.get_current_price("KRW-SOL")
        KNC_Price = pyupbit.get_current_price("KRW-KNC")
        TRX_Price = pyupbit.get_current_price("KRW-TRX")

        self.BTC_Price.setText(f"{BTC * BTC_Price:.2f}")
        self.ETH_Price.setText(f"{ETH * ETH_Price:.2f}")
        self.STX_Price.setText(f"{STX * STX_Price:.2f}")
        self.SOL_Price.setText(f"{SOL * SOL_Price:.2f}")
        self.KNC_Price.setText(f"{KNC * KNC_Price:.2f}")
        self.TRX_Price.setText(f"{TRX * TRX_Price:.2f}")



    def dialog_close(self):
        self.close()


class MainWindow(QMainWindow, form_main):
    def __init__(self):
        super().__init__()
        # UI 세팅
        self.vw = None
        self.setupUi(self)
        self.ticker = "BTC"
        self.IdentityVerification = False
        self.setWindowTitle("Auto Trading System Profit 5%")
        self.textEdit.append("▶ 거래내역")
        self.setFixedSize(1480, 780)

        # 버튼과 버튼 함수 연결
        self.ToggleButton.clicked.connect(self.clickToggle)
        self.ToggleButton.resize(23, 23)
        self.StartButton.clicked.connect(self.clickBtn)
        self.AccountButton.clicked.connect(self.clickAccount)
        self.AccountButton.setDisabled(True)
        self.btn_BTC.clicked.connect(self.clickBTC)
        self.btn_ETH.clicked.connect(self.clickETH)
        self.btn_STX.clicked.connect(self.clickSTX)
        self.btn_SOL.clicked.connect(self.clickSOL)
        self.btn_KNC.clicked.connect(self.clickKNC)
        self.btn_TRX.clicked.connect(self.clickTRX)

        # 사전 작성된 Key 파일 불러오기
        with open("key.txt") as f:
            lines = f.readlines()
            apikey = lines[0].strip()
            seckey = lines[1].strip()
            self.apiKey.setText(apikey)
            self.secKey.setText(seckey)

    def clickBtn(self):
        if self.StartButton.text() == "Start":
            apiKey = self.apiKey.text()
            secKey = self.secKey.text()
            if len(apiKey) != 40 or len(secKey) != 40:
                self.textEdit.append("▶ KEY의 길이가 올바르지 않습니다.")
                return
            else:
                self.textEdit.append("▶ 계좌 정보를 불러오는 중입니다.")
                self.UI_Balance.def_inputkey(apiKey, secKey)
                upbit = pyupbit.Upbit(apiKey, secKey)
                balances = upbit.get_balances() # self.ticker
                balance = upbit.get_balance()
                COIN = upbit.get_balance(ticker=f"KRW-{self.ticker}")
                print(balances)

                if balances == {'error': {'message': '잘못된 엑세스 키입니다.', 'name': 'invalid_access_key'}} : # print(self.balance)
                    self.textEdit.append("▶ KEY값이 에러를 반환 했습니다.")
                    return
                else:
                    self.IdentityVerification = True
                    self.secKey.setDisabled(True)
                    self.apiKey.setDisabled(True)
                    self.AccountButton.setDisabled(False)
                    self.textEdit.append("▶ 계좌 정보를 가져오는데 성공했습니다.")
                    self.textEdit.append(f"[ 보유 현금 : {balance:.4f} 원 ]")
                    self.textEdit.append(f"[ 보유 {self.ticker} : {COIN} {self.ticker} ]")
                    self.textEdit.append(f"------ START / {self.ticker} ------")
                    self.StartButton.setText("Stop")

            # 변동성 돌파 알고리즘 시작
            self.vw = VolatilityWorker(self.ticker, upbit)
            self.vw.tradingSent.connect(self.receiveTradingSignal)
            self.vw.start()

        else:
            # 변동성 돌파 알고리즘 종료
            self.vw.close()
            self.textEdit.append(f"------- STOP / {self.ticker} -------")
            self.StartButton.setText("Start")

    def clickToggle(self):
        if self.ToggleButton.text() == "◀":
            self.btn_BTC.hide()
            self.btn_ETH.hide()
            self.btn_STX.hide()
            self.btn_SOL.hide()
            self.btn_KNC.hide()
            self.btn_TRX.hide()
            self.ToggleButton.setText("▶")
        else:
            self.btn_BTC.show()
            self.btn_ETH.show()
            self.btn_STX.show()
            self.btn_SOL.show()
            self.btn_KNC.show()
            self.btn_TRX.show()
            self.ToggleButton.setText("◀")

    def clickAccount(self):
        if self.IdentityVerification:
            self.dialog_open(self.apiKey.text(), self.secKey.text())

    def dialog_open(self, apiKey, secKey):
        dialog = QDialogClass() # apiKey, secKey
        dialog.setWindowTitle('Asset Management')
        dialog.setFixedSize(400, 330)
        dialog.dialog_account(apiKey, secKey)
        dialog.exec_()

    def clickBTC(self):
        self.textEdit.append("------ BTC ------")
        self.ticker = "BTC"
        self.UI_Overview.ticker = "BTC"
        self.UI_Overview.updateTicker("BTC")
        self.UI_Orderbook.ticker = "KRW-BTC"
        self.UI_Orderbook.updateTicker("KRW-BTC")
        self.UI_HighChart.ticker = "KRW-BTC"
        self.UI_HighChart.updateTicker("KRW-BTC")
        self.UI_CandleChart.ticker = "KRW-BTC"
        self.UI_CandleChart.updateTicker("KRW-BTC")
        self.UI_CandleChart.redrawChart("KRW-BTC")
        self.UI_Overview.fill24Data(0, 0, math.trunc(pyupbit.get_current_price("KRW-BTC")), 0, 0, 0, 0, 0)
        # def fill24Data(chgRate, volumePower, currPrice, volume, highPrice, value, lowPrice, PrevClosePrice):

    def clickETH(self):
        self.textEdit.append("------ ETH ------")
        self.ticker = "ETH"
        self.UI_Overview.ticker = "ETH"
        self.UI_Overview.updateTicker("ETH")
        self.UI_Orderbook.ticker = "KRW-ETH"
        self.UI_Orderbook.updateTicker("KRW-ETH")
        self.UI_HighChart.ticker = "KRW-ETH"
        self.UI_HighChart.updateTicker("KRW-ETH")
        self.UI_CandleChart.ticker = "KRW-ETH"
        self.UI_CandleChart.updateTicker("KRW-ETH")
        self.UI_CandleChart.redrawChart("KRW-ETH")
        self.UI_Overview.fill24Data(0, 0, math.trunc(pyupbit.get_current_price("KRW-ETH")), 0, 0, 0, 0, 0)

    def clickSTX(self):
        self.textEdit.append("------ STX ------")
        self.ticker = "STX"
        self.UI_Overview.ticker = "STX"
        self.UI_Overview.updateTicker("STX")
        self.UI_Orderbook.ticker = "KRW-STX"
        self.UI_Orderbook.updateTicker("KRW-STX")
        self.UI_HighChart.ticker = "KRW-STX"
        self.UI_HighChart.updateTicker("KRW-STX")
        self.UI_CandleChart.ticker = "KRW-STX"
        self.UI_CandleChart.updateTicker("KRW-STX")
        self.UI_CandleChart.redrawChart("KRW-STX")
        self.UI_Overview.fill24Data(0, 0, math.trunc(pyupbit.get_current_price("KRW-STX")), 0, 0, 0, 0, 0)

    def clickSOL(self):
        self.textEdit.append("------ SOL ------")
        self.ticker = "SOL"
        self.UI_Overview.ticker = "SOL"
        self.UI_Overview.updateTicker("SOL")
        self.UI_Orderbook.ticker = "KRW-SOL"
        self.UI_Orderbook.updateTicker("KRW-SOL")
        self.UI_HighChart.ticker = "KRW-SOL"
        self.UI_HighChart.updateTicker("KRW-SOL")
        self.UI_CandleChart.ticker = "KRW-SOL"
        self.UI_CandleChart.updateTicker("KRW-SOL")
        self.UI_CandleChart.redrawChart("KRW-SOL")
        self.UI_Overview.fill24Data(0, 0, math.trunc(pyupbit.get_current_price("KRW-SOL")), 0, 0, 0, 0, 0)

    def clickKNC(self):
        self.textEdit.append("------ KNC ------")
        self.ticker = "KNC"
        self.UI_Overview.ticker = "KNC"
        self.UI_Overview.updateTicker("KNC")
        self.UI_Orderbook.ticker = "KRW-KNC"
        self.UI_Orderbook.updateTicker("KRW-KNC")
        self.UI_HighChart.ticker = "KRW-KNC"
        self.UI_HighChart.updateTicker("KRW-KNC")
        self.UI_CandleChart.ticker = "KRW-KNC"
        self.UI_CandleChart.updateTicker("KRW-KNC")
        self.UI_CandleChart.redrawChart("KRW-KNC")
        self.UI_Overview.fill24Data(0, 0, math.trunc(pyupbit.get_current_price("KRW-KNC")), 0, 0, 0, 0, 0)

    def clickTRX(self):
        self.textEdit.append("------ TRX ------")
        self.ticker = "TRX"
        self.UI_Overview.ticker = "TRX"
        self.UI_Overview.updateTicker("TRX")
        self.UI_Orderbook.ticker = "KRW-TRX"
        self.UI_Orderbook.updateTicker("KRW-TRX")
        self.UI_HighChart.ticker = "KRW-TRX"
        self.UI_HighChart.updateTicker("KRW-TRX")
        self.UI_CandleChart.ticker = "KRW-TRX"
        self.UI_CandleChart.updateTicker("KRW-TRX")
        self.UI_CandleChart.redrawChart("KRW-TRX")
        self.UI_Overview.fill24Data(0, 0, math.trunc(pyupbit.get_current_price("KRW-TRX")), 0, 0, 0, 0, 0)

    def receiveTradingSignal(self, time, type, amount):
        self.textEdit.append(f"[{time}] {type} : {amount}")

    def closeEvent(self, event):
        self.vw.close()
        self.UI_Overview.closeEvent(event)
        self.UI_Orderbook.closeEvent(event)
        self.UI_HighChart.closeEvent(event)
        self.UI_CandleChart.closeEvent(event)
        self.UI_Balance.closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    exit(app.exec_())
