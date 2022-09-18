import math
import pyupbit
import time, os, sys, signal, datetime

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal

from SystemStatus import SystemStatus

form_main = uic.loadUiType("resource/mymain.ui")[0]
form_dialog_asset = uic.loadUiType("resource/asset.ui")[0]
form_dialog_algorithm = uic.loadUiType("resource/algorithm.ui")[0]
form_dialog_rest = uic.loadUiType("resource/rest.ui")[0]
form_dialog_transaction = uic.loadUiType("resource/transaction.ui")[0]

# -----------------------------------------------------------------------
class QDialogTransaction(QtWidgets.QDialog, form_dialog_transaction):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)

# -----------------------------------------------------------------------
class QDialogRest(QtWidgets.QDialog, form_dialog_rest):
    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, None)
        self.setupUi(self)
        self.parent = parent

        self.DialogButton.clicked.connect(self.dialogClose)
        self.SoldButton.clicked.connect(self.clickSold)
        self.LeaveButton.clicked.connect(self.clickLeave)

    def clickSold(self):
        self.parent.selling_signal_not_turn_on = False
        self.close()

    def clickLeave(self):
        self.parent.selling_signal_not_turn_on = False
        self.close()

    def dialogClose(self):
        self.close()


# -----------------------------------------------------------------------
class QDialogAlgorithm(QtWidgets.QDialog, form_dialog_algorithm):
    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, None)
        self.setupUi(self)
        self.parent = parent

        self.DialogButton.clicked.connect(self.dialogClose)
        self.Algorithm1Button.clicked.connect(self.clickAlgorithm1)
        self.Algorithm1Button.clicked.connect(self.parent.algorithm_selection_1)
        self.Algorithm2Button.clicked.connect(self.clickAlgorithm2)
        self.Algorithm2Button.clicked.connect(self.parent.algorithm_selection_2)
        self.Algorithm3Button.clicked.connect(self.clickAlgorithm3)
        self.Algorithm3Button.clicked.connect(self.parent.algorithm_selection_3)

    def clickAlgorithm1(self):
        self.parent.alg_type_not_selected = False
        self.close()

    def clickAlgorithm2(self):
        self.parent.alg_type_not_selected = False
        self.close()

    def clickAlgorithm3(self):
        self.parent.alg_type_not_selected = False
        self.close()

    def dialogClose(self):
        self.close()


# -----------------------------------------------------------------------
class QDialogAsset(QtWidgets.QDialog, form_dialog_asset):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.DialogButton.clicked.connect(self.dialogClose)

    def dialogAccount(self, apiKey, secKey):
        self.apiKey = apiKey
        self.secKey = secKey

        upbit = pyupbit.Upbit(apiKey, secKey)
        BTC = upbit.get_balance(ticker="KRW-BTC")
        ETH = upbit.get_balance(ticker="KRW-ETH")
        STX = upbit.get_balance(ticker="KRW-STX")
        SOL = upbit.get_balance(ticker="KRW-SOL")
        KNC = upbit.get_balance(ticker="KRW-KNC")
        ADA = upbit.get_balance(ticker="KRW-ADA")

        self.BTC_Quantity.setText(f"{BTC:,}")
        self.ETH_Quantity.setText(f"{ETH:,}")
        self.STX_Quantity.setText(f"{STX:,}")
        self.SOL_Quantity.setText(f"{SOL:,}")
        self.KNC_Quantity.setText(f"{KNC:,}")
        self.ADA_Quantity.setText(f"{ADA:,}")

        BTC_Price = pyupbit.get_current_price("KRW-BTC")
        ETH_Price = pyupbit.get_current_price("KRW-ETH")
        STX_Price = pyupbit.get_current_price("KRW-STX")
        SOL_Price = pyupbit.get_current_price("KRW-SOL")
        KNC_Price = pyupbit.get_current_price("KRW-KNC")
        ADA_Price = pyupbit.get_current_price("KRW-ADA")

        self.BTC_Price.setText(f"{BTC * BTC_Price:.2f}")
        self.ETH_Price.setText(f"{ETH * ETH_Price:.2f}")
        self.STX_Price.setText(f"{STX * STX_Price:.2f}")
        self.SOL_Price.setText(f"{SOL * SOL_Price:.2f}")
        self.KNC_Price.setText(f"{KNC * KNC_Price:.2f}")
        self.ADA_Price.setText(f"{ADA * ADA_Price:.2f}")

    def dialogClose(self):
        self.close()


# -----------------------------------------------------------------------
class MainUI(QMainWindow, form_main):
    start_trading = pyqtSignal()
    stop_trading = pyqtSignal()
    stop_system = pyqtSignal()

    def __init__(self, sys_stat: SystemStatus):
        print("[SYSTEM] Init MainUI")
        super(MainUI, self).__init__()
        self.sys_stat = sys_stat

        self.coin_type_not_selected = True
        self.alg_type_not_selected = True
        self.selling_signal_not_turn_on = True

        # UI 세팅
        self.vw = None
        self.setupUi(self)
        self.ticker = "BTC"
        self.IdentityVerification = False
        self.setWindowTitle("Auto Trading System Profit 5%")
        self.textEdit.append("▶ 거래내역")
        self.setFixedSize(1480, 800)

        # 버튼과 버튼 함수 연결
        self.ToggleButton.clicked.connect(self.clickToggle)
        self.ToggleButton.resize(23, 23)
        self.btn_toggle.clicked.connect(self.clickToggleCandle)
        self.btn_toggle.resize(23, 23)
        self.LoginButton.clicked.connect(self.clickLogin)
        self.StartButton.clicked.connect(self.clickStart)
        self.AccountButton.clicked.connect(self.clickAccount)
        self.TransactionButton.clicked.connect(self.clickTransaction)

        self.AccountButton.setDisabled(True)
        self.StartButton.setDisabled(True)
        self.TransactionButton.setDisabled(True)
        
        self.btn_min1.clicked.connect(lambda: self.CandleButton('minute1'))
        self.btn_min15.clicked.connect(lambda: self.CandleButton('minute15'))
        self.btn_hour1.clicked.connect(lambda: self.CandleButton('minute60'))
        self.btn_hour4.clicked.connect(lambda: self.CandleButton('minute240'))
        self.btn_day1.clicked.connect(lambda: self.CandleButton('day'))
        self.btn_week1.clicked.connect(lambda: self.CandleButton('week'))
        self.btn_month1.clicked.connect(lambda: self.CandleButton('month'))

        self.btn_BTC.clicked.connect(lambda: self.clickCoin("BTC"))
        self.btn_ETH.clicked.connect(lambda: self.clickCoin("ETH"))
        self.btn_STX.clicked.connect(lambda: self.clickCoin("STX"))
        self.btn_SOL.clicked.connect(lambda: self.clickCoin("SOL"))
        self.btn_KNC.clicked.connect(lambda: self.clickCoin("KNC"))
        self.btn_ADA.clicked.connect(lambda: self.clickCoin("ADA"))

        self.show()

    def clickLogin(self):
        if self.LoginButton.text() == "Login":
            if self.sys_stat.access == None:
                self.sys_stat.access = self.apiKey.text()
                self.sys_stat.secret = self.secKey.text()

            apiKey = self.sys_stat.access
            secKey = self.sys_stat.secret
            upbit = pyupbit.Upbit(apiKey, secKey)
            balances = upbit.get_balances()
            self.textEdit.append("▶ 계좌 정보를 불러오는 중입니다.")
            

            if balances == {'error': {'message': '잘못된 엑세스 키입니다.', 'name': 'invalid_access_key'}}:
                # print(self.balance)
                self.textEdit.append("▶ KEY값이 에러를 반환 했습니다.")
                return

            else:
                self.UI_Balance.def_inputkey(apiKey, secKey)
                balances = upbit.get_balances()  # self.ticker
                balance = upbit.get_balance()
                COIN = upbit.get_balance(ticker=f"KRW-{self.ticker}")

                if balances == {'error': {'message': '잘못된 엑세스 키입니다.', 'name': 'invalid_access_key'}}:
                    # print(self.balance)
                    self.textEdit.append("▶ KEY값이 에러를 반환 했습니다.")
                    return
                else:
                    self.IdentityVerification = True
                    self.secKey.setDisabled(True)
                    self.apiKey.setDisabled(True)
                    self.AccountButton.setDisabled(False)
                    self.TransactionButton.setDisabled(False)
                    self.StartButton.setDisabled(False)
                    self.LoginButton.setDisabled(True)
                    self.textEdit.append("<< KEY로 로그인 성공.>>")
                    self.textEdit.append("▶ 계좌 정보를 가져오는데 성공했습니다.")
                    self.textEdit.append(f"[ 보유 현금 : {balance:.4f} 원 ]")
                    self.textEdit.append(f"[ 보유 {self.ticker} : {COIN} {self.ticker} ]")

    def clickStart(self):
        if self.StartButton.text() == "Start":
            self.dialogAlgorithm_open()
            if self.alg_type_not_selected:
                return
            if self.coin_type_not_selected:
                print("[SYSTEM] Select the Type of coin you want to trade with")
                self.sys_stat.coin_type_not_selected = True
                return
            self.start_trading.emit()  # 알고리즘 시작
            self.textEdit.append(f"------ START / {self.ticker} ------")
            self.StartButton.setText("Stop")
        else:
            self.dialogRest_open()
            if self.selling_signal_not_turn_on:
                return 
            self.stop_trading.emit()  # 알고리즘 종료
            self.textEdit.append(f"------- STOP / {self.ticker} -------")
            self.StartButton.setText("Start")
            self.selling_signal_not_turn_on = True

    def clickToggleCandle(self):
        if self.btn_toggle.text() == "◀":
            self.btn_hour1.hide()
            self.btn_hour4.hide()
            self.btn_min1.hide()
            self.btn_min15.hide()
            self.btn_day1.hide()
            self.btn_week1.hide()
            self.btn_month1.hide()
            self.btn_toggle.setText("▶")
        else:
            self.btn_hour1.show()
            self.btn_hour4.show()
            self.btn_min1.show()
            self.btn_min15.show()
            self.btn_day1.show()
            self.btn_week1.show()
            self.btn_month1.show()
            self.btn_toggle.setText("◀")

    def clickToggle(self):
        if self.ToggleButton.text() == "◀":
            self.btn_BTC.hide()
            self.btn_ETH.hide()
            self.btn_STX.hide()
            self.btn_SOL.hide()
            self.btn_KNC.hide()
            self.btn_ADA.hide()
            self.ToggleButton.setText("▶")
        else:
            self.btn_BTC.show()
            self.btn_ETH.show()
            self.btn_STX.show()
            self.btn_SOL.show()
            self.btn_KNC.show()
            self.btn_ADA.show()
            self.ToggleButton.setText("◀")

    def clickAccount(self):
        if self.IdentityVerification:
            self.dialogAsset_open(self.sys_stat.access, self.sys_stat.secret)
            
    def clickTransaction(self):
        if self.IdentityVerification:
            self.dialogTransaction_open()
            
    def dialogAsset_open(self, apiKey, secKey):
        dialogAsset = QDialogAsset()  # apiKey, secKey
        dialogAsset.setWindowTitle('Asset Management')
        dialogAsset.setFixedSize(400, 330)
        dialogAsset.dialogAccount(apiKey, secKey)
        dialogAsset.exec_()

    def dialogAlgorithm_open(self):
        dialogAlgorithm = QDialogAlgorithm(self)
        dialogAlgorithm.setWindowTitle('Algorithm Select')
        dialogAlgorithm.setFixedSize(400, 330)
        dialogAlgorithm.exec_()

    def dialogRest_open(self):
        dialogRest = QDialogRest(self)
        dialogRest.setWindowTitle('Rest Select')
        dialogRest.setFixedSize(400, 330)
        dialogRest.exec_()
    
    def dialogTransaction_open(self):
        dialogTransaction = QDialogTransaction()
        dialogTransaction.setWindowTitle('Transaction History')
        dialogTransaction.setFixedSize(400, 625)
        dialogTransaction.exec_()

    def clickCoin(self, coin_type):
        kct = f"KRW-{coin_type}"  # krw coin type
        self.sys_stat.coin_type = kct
        self.coin_type_not_selected = False
        
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

    def CandleButton(self, interval):
        self.UI_CandleChart.interval = interval
        self.UI_CandleChart.updateInterval(interval)

    def receiveTradingSignal(self, time, type, amount):
        self.textEdit.append(f"[{time}] {type} : {amount}")

    def algorithm_selection_1(self):
        self.sys_stat.algorithm = 0

    def algorithm_selection_2(self):
        self.sys_stat.algorithm = 1

    def algorithm_selection_3(self):
        self.sys_stat.algorithm = 2

    def closeEvent(self, event):
        self.UI_Overview.closeEvent(event)
        self.UI_Orderbook.closeEvent(event)
        self.UI_HighChart.closeEvent(event)
        self.UI_CandleChart.closeEvent(event)
        self.UI_Balance.closeEvent(event)
        
        print("[SYSTEM] Close MainUI")
        self.close()
        self.stop_system.emit()
        print("[SYSTEM] MainUI Closed")
        


