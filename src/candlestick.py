import sys
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtChart import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import *
import pyupbit
import time
import os
from pandas import Series


class Worker(QThread):
    price = pyqtSignal(float)

    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker

    def run(self):
        while True:
            cur_price = pyupbit.get_current_price(self.ticker)
            self.price.emit(cur_price)
            time.sleep(1)


class candleWidget(QWidget):
    def __init__(self, parent=None, ticker="KRW-BTC"):
        super().__init__(parent)
        uic.loadUi("resource/candle.ui",self)
        self.ticker = ticker
        self.interval = 'minute1'

        # 쓰레드 초기화
        self.worker = Worker(ticker)
        self.updateTicker(ticker)
        self.worker.price.connect(self.get_price)
        self.worker.start()

        self.minute_cur = QDateTime.currentDateTime()
        self.minute_pre = self.minute_cur.addSecs(-60)
        self.ticks = Series(dtype='float64')

        # 위젯 사이즈
        self.setMinimumSize(750, 350)
        df = pyupbit.get_ohlcv(self.ticker, interval=self.interval, count=80)

        # 캔들스틱 초기화
        self.series = QCandlestickSeries()
        self.series.setIncreasingColor(QColor(225,35,60))
        self.series.setDecreasingColor(QColor(25,100,180))
        self.series.setBodyOutlineVisible(0)

        # OHLC 초기화
        for index in df.index:
            open = df.loc[index, 'open']
            high = df.loc[index, 'high']
            low = df.loc[index, 'low']
            close = df.loc[index, 'close']

            # time conversion
            format = "%Y-%m-%d %H:%M:%S"
            str_time = index.strftime(format)
            dt = QDateTime.fromString(str_time, "yyyy-MM-dd hh:mm:ss")
            ts = dt.toMSecsSinceEpoch()
            #ts = index.timestamp() * 1000
            #print(ts)

            elem = QCandlestickSet(open, high, low, close, ts)
            self.series.append(elem)

        # Qchart 사용
        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.addSeries(self.series)         # data feeding

        # 축 설정
        axis_x = QDateTimeAxis()
        if self.interval == 'minute1':
            axis_x.setFormat("hh:mm:ss")
        if self.interval == 'minute15':
            axis_x.setFormat("hh:mm:ss")
        if self.interval == 'minute60':
            axis_x.setFormat("hh:mm:ss")
        if self.interval == 'minute240':
            axis_x.setFormat("hh:mm:ss")
        if self.interval == 'day':
            axis_x.setFormat("yyyy-MM-dd")
        if self.interval == 'week':
            axis_x.setFormat("yyyy-MM-dd")
        if self.interval == 'month':
            axis_x.setFormat("yyyy-MM-dd")

        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%i")
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        self.series.attachAxis(axis_y)

        # 레이아웃 설정
        self.chart.layout().setContentsMargins(0, 0, 0, 0)

        # 차트 그리기
        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        self.candleView.setChart(self.chart)
        self.redrawChart(ticker)

    def updateTicker(self, ticker):
        self.worker.ticker = ticker

    def redrawChart(self, ticker):
        self.updateTicker(ticker)

        self.minute_cur = QDateTime.currentDateTime()
        self.minute_pre = self.minute_cur.addSecs(-60)
        self.ticks = Series(dtype='float64')

        # 위젯 사이즈
        self.setMinimumSize(750, 350)
        df = pyupbit.get_ohlcv(self.ticker, interval=self.interval, count=80)

        # 캔들스틱 초기화
        self.series = QCandlestickSeries()
        self.series.setIncreasingColor(QColor(225, 35, 60))
        self.series.setDecreasingColor(QColor(25, 100, 180))
        self.series.setBodyOutlineVisible(0)

        # OHLC 초기화
        for index in df.index:
            open = df.loc[index, 'open']
            high = df.loc[index, 'high']
            low = df.loc[index, 'low']
            close = df.loc[index, 'close']

            # time conversion
            format = "%Y-%m-%d %H:%M:%S"
            str_time = index.strftime(format)
            dt = QDateTime.fromString(str_time, "yyyy-MM-dd hh:mm:ss")
            ts = dt.toMSecsSinceEpoch()
            # ts = index.timestamp() * 1000
            # print(ts)

            elem = QCandlestickSet(open, high, low, close, ts)
            self.series.append(elem)

        # Qchart 사용
        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.addSeries(self.series)  # data feeding

        # 축 설정
        axis_x = QDateTimeAxis()
        if self.interval == 'minute1':
            axis_x.setFormat("hh:mm:ss")
        if self.interval == 'minute15':
            axis_x.setFormat("hh:mm:ss")
        if self.interval == 'minute60':
            axis_x.setFormat("hh:mm:ss")
        if self.interval == 'minute240':
            axis_x.setFormat("hh:mm:ss")
        if self.interval == 'day':
            axis_x.setFormat("yyyy-MM-dd")
        if self.interval == 'week':
            axis_x.setFormat("yyyy-MM-dd")
        if self.interval == 'month':
            axis_x.setFormat("yyyy-MM-dd")
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%i")
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        self.series.attachAxis(axis_y)

        # 레이아웃 설정
        self.chart.layout().setContentsMargins(0, 0, 0, 0)

        # 차트 그리기
        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        self.candleView.setChart(self.chart)

    def updateInterval(self, interval):
        self.interval = interval
        self.redrawChart(self.ticker)

    def closeEvent(self, event):
        self.chart.close()


    @pyqtSlot(float)
    def get_price(self, cur_price):
        # append current price
        dt = QDateTime.currentDateTime()
        ts = dt.toMSecsSinceEpoch()
        # print(ts, cur_price)

        sets = self.series.sets()
        last_set = sets[-1]

        open = last_set.open()
        high = last_set.high()
        low = last_set.low()
        close = last_set.close()
        ts1 = last_set.timestamp()

        self.series.remove(last_set)
        new_set = QCandlestickSet(open, high, low, cur_price, ts1)
        self.series.append(new_set)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = candleWidget()
    win.show()
    app.exec_()
