◆ volatility : 변동성 돌파 전략
◆ main : 거래내역 창입니다. 메인 윈도우가 포함되어있습니다.
# class VolatilityWorker(QThread)

https://wikidocs.net/119307 참조
https://github.com/youtube-jocoding/pyupbit-autotrade/blob/main/bitcoinAutoTrade.py 참조


-------------프론트엔드------------

# class QDialogClass(QtWidgets.QDialog, form_class) : Asset UI 창을 그리는 QDialog 입니다.
# class MainWindow(QMainWindow, form_class) : 모든 UI를 그리는 QMainWindow입니다.
# def clickBtn(self) : API key를 확인한 후 VolatilityWorker를 활성화합니다.
▶ Label_API : QLabel
▶ apiKey : QLineEdit
▶ secKey : QLineEdit
▶ StartButton : QPushButton
▶ Togglebutton : QPushButton

▶ UI_Profit : QWidget
▶ UI_Balance : QWidget-BalanceWidget
▶ UI_CandleChart : QWidget-candleWidget
▶ UI_HighChart : QWidget-ChartWidget
▶ UI_Orderbook : QWidget-OrderbookWidget
▶ UI_Overview : QWidget-OverviewWidget


◆ balance : 잔고를 보여주는 창입니다. ** key가 있어야해서 주석처리 했습니다. ▶ UI_Balance
# class Worker(QThread) : API key를 확인한 후 실시간으로 잔고 정보를 가져오는 QThread Class 입니다.
# class BalanceWidget(QWidget) : 잔고 UI를 그리는 QWidget Class 입니다.
# def def_balance : Worker에서 받은 정보로 시작가, 현재가, 수익률을 계산하는 함수입니다.
▶ label_start : QLabel #시작가
▶ label_current : QLabel #현재가
▶ label_profit : QLabel #수익률


◆ candlestick : 캔들차트를 보여주는 창입니다. ▶ UI_CandleChart
# class Worker(QThread) : 실시간으로 Ticker 가격 정보를 가져오는 QThread Class 입니다.
# class candleWidget(QWidget) : 캔들차트를 그리는 QWidget Class 입니다.
# def get_price(self, cur_price) : Worker에서 받은 정보로 OHLC를 차트에 업데이트 하는 함수입니다.
▶ priceView : QChartView #Q차트그리기


◆ chart : 하이차트를 보여주는 창입니다. ▶ UI_HighChart
# class PriceWorker(QThread) : 실시간으로 Ticker 가격 정보를 가져오는 QThread Class 입니다.
# class ChartWidget(QWidget) : 하이차트를 그리는 QWidget Class 입니다.
# def appendData(self, currPirce) : viewLimit를 넘은 오래된 정보를 지우고 차트를 업데이트하는 함수입니다.
# def __updateAxis(self) : viewLimit를 넘은 차트축을 업데이트 하는 함수입니다.
▶ priceView : QChartView #Q차트그리기


◆ orderbook : 호가창입니다. ▶ UI_Orderbook
# class OrderbookWorker(QThread) : 실시간으로 Ticker 가격 정보를 가져오는 QThread Class 입니다.
# class OrderbookWidget(QWidget) : 호가창을 그리는 QWidget Class 입니다.
▶ tableBids : QTableWidget #매도표
▶ tableAsks : QTableWidget #매수표


◆ overview : 개요창입니다. ▶ UI_Overview
class OverViewWorker(QThread) : 실시간으로 Ticker 가격 정보를 가져오는 QThread Class 입니다.
class OverviewWidget(QWidget): 개요창을 그리는 QWidget Class 입니다.
▶ label_1 : QLabel #현재가
▶ label_2 : QLabel #전일대비
▶ label_3 ~ label_14 : QLabel #거래정보


시간 기록

3.24 main
3.29 canndlestick
4.07 balance
4.26 highchart
5.01 overview (websocket)
5.04 orderbook
5.05 volatility
5.08 asset (dialog)