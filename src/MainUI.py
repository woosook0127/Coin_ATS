#----------------------------------------------------------------------
import sys
import time
import datetime
import math
import pyupbit

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal

form_main = uic.loadUiType("resource/mymain.ui")[0]        
form_dialog = uic.loadUiType("resource/asset.ui")[0]

#-----------------------------------------------------------------------
class QDialogClass(QtWidgets.QDialog, form_dialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.DialogButton.clicked.connect(self.dialogColse)

    def dialogAccount(self, apiKey, secKey):
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

    def dialogColse(self):
        self.close()

#-----------------------------------------------------------------------
class MainUI(QMainWindow, form_main):
    start_trading = pyqtSignal()
    stop_trading = pyqtSignal()

    def __init__(self, sys_stat):
        print("Init MainUI")
        super().__init__()
        self.sys_stat = sys_stat

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

        self.btn_BTC.clicked.connect(lambda: self.clickCoin("BTC"))
        self.btn_ETH.clicked.connect(lambda: self.clickCoin("ETC"))
        self.btn_STX.clicked.connect(lambda: self.clickCoin("STX"))
        self.btn_SOL.clicked.connect(lambda: self.clickCoin("SOL"))
        self.btn_KNC.clicked.connect(lambda: self.clickCoin("KNC"))
        self.btn_TRX.clicked.connect(lambda: self.clickCoin("TRX"))

        self.show()
    
    def clickBtn(self):
        if self.StartButton.text() == "Start":
            apiKey = self.sys_stat.access
            secKey = self.sys_stat.secret

            self.textEdit.append("▶ 계좌 정보를 불러오는 중입니다.")
            upbit = pyupbit.Upbit(apiKey, secKey)
            if upbit == None:
                self.textEdit.append("    << KEY가 올바르지 않습니다.>>")
                return
            else:
                self.textEdit.append("    << KEY로 로그인 성공.>>")
                self.UI_Balance.def_inputkey(apiKey, secKey)
                balances = upbit.get_balances() # self.ticker
                balance = upbit.get_balance()
                COIN = upbit.get_balance(ticker=f"KRW-{self.ticker}")
                
                # 이 if문빼도 되나??
                if balances == {'error': {'message': '잘못된 엑세스 키입니다.', 'name': 'invalid_access_key'}} :
                    # print(self.balance)
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
                    self.start_trading.emit()

        else:
            self.stop_trading.emit()
            # 변동성 돌파 알고리즘 종료
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
        dialog.dialogAccount(apiKey, secKey)
        dialog.exec_()

    def clickCoin(self, coin_type):
        kct = f"KRW-{coin_type}" # krw coin type
        self.sys_stat.coin_type = kct

        self.textEdit.append(f"-------- {coin_type} --------")
        self.ticker = coin_type
        self.UI_Overview.ticker = coin_type
        self.UI_Overview.updateTicker(coin_type)
        self.UI_Orderbook.ticker = kct
        self.UI_Orderbook.updateTicker(kct)
        self.UI_HighChart.ticker = kct
        self.UI_HighChart.updateTicker(kct)
        self.UI_CandleChart.ticker = kct
        self.UI_CandleChart.updateTicker(kct)
        self.UI_CandleChart.redrawChart(kct)
        self.UI_Overview.fill24Data(0, 0, math.trunc(pyupbit.get_current_price(kct)), 0, 0, 0, 0, 0)

    def receiveTradingSignal(self, time, type, amount):
        self.textEdit.append(f"[{time}] {type} : {amount}")

    def closeEvent(self, event):
        self.UI_Overview.closeEvent(event)
        self.UI_Orderbook.closeEvent(event)
        self.UI_HighChart.closeEvent(event)
        self.UI_CandleChart.closeEvent(event)
        self.UI_Balance.closeEvent(event)
        self.close()

    def __del__():
        print("Sys: Deactivate MainUI")


#-----------------------------------------------------------------------


#-----------------------------------------------------------------------


#-----------------------------------------------------------------------


#-----------------------------------------------------------------------


#-----------------------------------------------------------------------


#-----------------------------------------------------------------------



#-----------------------------------------------------------------------
