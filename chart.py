# cython: language_level=3
# -*- coding: utf-8 -*-


import sys
sys.path.insert(0,'/var/workspace/QUANTPI')








import datetime
import math
import random
from collections import OrderedDict
import qdarkstyle
from PyQt5.QtCore import (QPointF, QRect, QRectF, Qt, pyqtBoundSignal, QPoint,
                          pyqtSignal)
from PyQt5.QtGui import (QPalette,QBrush, QColor, QCursor, QFont, QIcon, QPainter, QPen,
                         QPixmap)
from PyQt5.QtWidgets import (QAction, QApplication, QComboBox, QFrame,
                             QHBoxLayout, QMenu, QToolTip,QWidget)
import indicators
from basefunc import np, pd
from modules import globals, parameterSettingDlg, scrollbar, stock, utils,getName
from async_gui import MultiProcessTask
from async_gui.engine import Task
from async_gui.toolkits.pyqt import PyQtEngine
from guiSettings import backgroundColor
engine = PyQtEngine()
sys.path.extend('.')
app = QApplication(sys.argv)
pic = {1: QPixmap('/mnt/HDD/QUANTPI/icon/add.png', "0", Qt.AvoidDither | Qt.ThresholdDither | Qt.ThresholdAlphaDither), 2: QPixmap("/mnt/HDD/QUANTPI/icon/sell.png", "0", Qt.AvoidDither | Qt.ThresholdDither | Qt.ThresholdAlphaDither),
       3:  QPixmap('/mnt/HDD/QUANTPI/icon/minus.png', "0", Qt.AvoidDither | Qt.ThresholdDither | Qt.ThresholdAlphaDither), 4:  QPixmap('/mnt/HDD/QUANTPI/icon/minus.png', "0", Qt.AvoidDither | Qt.ThresholdDither | Qt.ThresholdAlphaDither)}

def toRectF(rect):
    return QRectF(
        rect.x(),
        rect.y(),
        rect.width(),
        rect.height()
    )

def toRect(rectF):
    return QRect(
        rectF.x(),
        rectF.y(),
        rectF.width(),
        rectF.height()
    )

def normalizeRect(rect):
    x = rect.x()
    y = rect.y()
    w = rect.width()
    h = rect.height()
    if w < 0:
        x = x + w
        w = -w
    if h < 0:
        y = y + h
        h = -h
    return QRectF(x, y, w, h)

class chartBase(QFrame):
    resetchartscrollbar = pyqtSignal(int, int)
    showStockInfoDlgSig = pyqtSignal()
    scrollbarsetValueSig = pyqtSignal(int)
    scrollbartriggerSig = pyqtSignal()
    updateStockInfoSig = pyqtSignal()
    updateStockInfoTitleSig = pyqtSignal(str)
    handleDataUpdateSig = pyqtSignal()
    stockcodeChanged = pyqtSignal(bool)
    periodChanged = pyqtSignal(int)
    feedstockkdataSig = pyqtSignal(list)
    ChangeSLayoutSig = pyqtSignal()
    drawHelperlineFineshed = pyqtSignal()
    calculatePriceRangeBasedOnKDataFinished = pyqtSignal(float)
    chartupdatedsig = pyqtBoundSignal(bool)

    def __init__(self):
        super(chartBase, self).__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.canselfdrawing = False
        self.logarithm = True
        self.rightMarkwidth = 60  # 右侧宽度
        self.bottomMarkHeight = 30  # 底部高度
        self.whiteKwidth = 40 #空白k线宽度
        self.topWihteHeight = 10 #k线与顶部显示栏的空白高度
        self.chartwidth = self.rect().width() - self.rightMarkwidth-self.whiteKwidth
        self.mainChartHeight = self.rect().height()
        self.kmarginw = 10
        self.maintitleHeight = 20 #self.maintitleHeight
        self.topMarginheight = self.maintitleHeight + self.topWihteHeight # 顶部宽度
        self.kwidth = 10.82 #每根K线宽度
        self.fontsize = 10
        self.font = 'Tahoma'
        self.stockcode = None
        self.prestockcode = None
        self.period = 0
        self.viewData = None
        self.kdata = OrderedDict()
        self.arraydata = np.array([])
        self.kdispdataArr = np.array([])
        self.colsDict = dict()
        self.resourceData = pd.DataFrame()
        self.kdispdata = None
        self.weightdata = None
        self.kdispcount = 0
        self.ktotalcount = 0
        self.mouseposx = 0
        self.mouseposy = 0
        self.indicatorpos = 0
        self.crossline = True
        self.helperlinepos = None
        self.helperlinekindex = None
        self.zoombase = 1  # 0.75
        self.zoom = self.zoombase
        self.lastzoom = self.zoom
        self.zoominmax = 3
        self.canzoomout = True
        self.mousepos = None
        self.mouseglobalpos = None
        self.daylist = ['一', '二', '三', '四', '五', '六', '日']
        self.pricehigh = 0
        self.pricelow = 100000
        self.pricerange = self.pricehigh - self.pricelow
        self.kdispstartInd = 0 #当前界面第一根k线行索引
        self.endIdx = 10000000  #当前界面最后一根k线行索引
        self.kleft = 0
        self.kindex = 0
        self.maintitle = []
        self.VerticalGridLinePosX = []
        self.dispdataPosX = []
        self.maintitlePox = {'x': 5, 'y': 15}
        self.colorlist = []
        self.colorlist.append(QColor(8, 8, 225))  # blue
        self.colorlist.append(QColor(225, 8, 225))  # pink
        self.colorlist.append(QColor(188, 88, 8))  # yellow
        self.colorlist.append(QColor(88, 8, 188))  # purple
        self.colorlist.append(QColor(102, 102, 123))  # gray
        for i in range(0, 10):
            self.colorlist.append(QColor(random.randint(
                1, 255), random.randint(1, 255), random.randint(1, 255)))
        self.chartIndicator = ['avol']

    def reset_chart(self):
        self.stockcode = None
        self.prestockcode = None
        self.period = 0
        self.viewData = None
        self.kdata = OrderedDict()
        self.arraydata = np.array([])
        self.kdispdataArr = np.array([])
        self.colsDict = dict()
        self.resourceData = pd.DataFrame()
        self.kdispdata = None
        self.weightdata = None
        self.kdispcount = 0
        self.ktotalcount = 0
        self.mouseposx = 0
        self.mouseposy = 0
        self.indicatorpos = 0
        self.crossline = True
        self.helperlinepos = None
        self.helperlinekindex = None
        self.zoombase = 1  # 0.75
        self.zoom = self.zoombase
        self.lastzoom = self.zoom
        self.zoominmax = 3
        self.canzoomout = True
        self.mousepos = None
        self.mouseglobalpos = None
        self.pricehigh = 0
        self.pricelow = 100000
        self.pricerange = self.pricehigh - self.pricelow
        self.kdispstartInd = 0 #当前界面第一根k线行索引
        self.endIdx = 10000000  #当前界面最后一根k线行索引
        self.kleft = 0
        self.kindex = 0
        self.maintitle = []
        self.VerticalGridLinePosX = []
        self.dispdataPosX = []

    def normalizeKdata(self):
        if len(self.resourceData):
            x = self.viewData.data
            self.kdata = []
            nondisp_cols = ['c', 'h', 'date', 'name', 'l',
                            'chg', 'vol', 'volp', 'hsl', 'trade', 'zde', 'yc']
            cols = [i for i in x.columns if i not in nondisp_cols]
            for i in x.index:
                x1 = OrderedDict()
                x1.update({'volp': x.loc[i, 'volp']})
                x1.update({'c': x.loc[i, 'c']})
                x1.update({'date': (x.loc[i, 'date']).replace('-', '')})
                x1.update({'h': x.loc[i, 'h']})
                x1.update({'l': x.loc[i, 'l']})
                x1.update({'o': x.loc[i, 'o']})
                x1.update({'volume': x.loc[i, 'vol']})
                x1.update({'hsl': x.loc[i, 'hsl']})
                x1.update({'chg': x.loc[i, 'chg']})
                for _col in cols:
                    x1.update({_col: x.loc[i, _col]})
                self.kdata.append(x1)
        else:
            return self.kdata
class chartBase(QFrame):
    # 信号
    resetchartscrollbar = pyqtSignal(int, int)
    showStockInfoDlgSig = pyqtSignal()
    scrollbarsetValueSig = pyqtSignal(int)
    scrollbartriggerSig = pyqtSignal()
    updateStockInfoSig = pyqtSignal()
    updateStockInfoTitleSig = pyqtSignal(str)
    handleDataUpdateSig = pyqtSignal()
    stockcodeChanged = pyqtSignal(bool)
    periodChanged = pyqtSignal(int)
    feedstockkdataSig = pyqtSignal(list)
    ChangeSLayoutSig = pyqtSignal()
    drawHelperlineFineshed = pyqtSignal()
    calculatePriceRangeBasedOnKDataFinished = pyqtSignal(float)
    chartupdatedsig = pyqtSignal(bool)

    def __init__(self):
        super(chartBase, self).__init__()

        # 图表相关的基本参数
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.canselfdrawing = False
        self.logarithm = True
        self.rightMarkwidth = 60  # 右侧宽度
        self.bottomMarkHeight = 30  # 底部高度
        self.whiteKwidth = 40  # 空白K线宽度
        self.topWihteHeight = 10  # K线与顶部显示栏的空白高度
        self.chartwidth = self.rect().width() - self.rightMarkwidth - self.whiteKwidth
        self.mainChartHeight = self.rect().height()
        self.kmarginw = 10
        self.maintitleHeight = 20  # 标题高度
        self.topMarginheight = self.maintitleHeight + self.topWihteHeight  # 顶部宽度
        self.kwidth = 10.82  # 每根K线宽度
        self.fontsize = 10  # 字号
        self.font = 'Tahoma'  # 字体
        self.stockcode = None
        self.prestockcode = None
        self.period = 0
        self.viewData = None
        self.kdata = OrderedDict()
        self.arraydata = np.array([])
        self.kdispdataArr = np.array([])
        self.colsDict = dict()
        self.resourceData = pd.DataFrame()
        self.kdispdata = None
        self.weightdata = None
        self.kdispcount = 0
        self.ktotalcount = 0
        self.mouseposx = 0
        self.mouseposy = 0
        self.indicatorpos = 0
        self.crossline = True
        self.helperlinepos = None
        self.helperlinekindex = None
        self.zoombase = 1  # 初始值
        self.zoom = self.zoombase
        self.lastzoom = self.zoom
        self.zoominmax = 3
        self.canzoomout = True
        self.mousepos = None
        self.mouseglobalpos = None
        self.pricehigh = 0
        self.pricelow = 100000
        self.pricerange = self.pricehigh - self.pricelow
        self.kdispstartInd = 0  # 当前界面第一根K线行索引
        self.endIdx = 10000000  # 当前界面最后一根K线行索引
        self.kleft = 0
        self.kindex = 0
        self.maintitle = []
        self.VerticalGridLinePosX = []
        self.dispdataPosX = []
        
        # 用于图表线条的颜色列表
        self.colorlist = [QColor(8, 8, 225), QColor(225, 8, 225), QColor(188, 88, 8),
                          QColor(88, 8, 188), QColor(102, 102, 123)]
        for i in range(0, 10):
            self.colorlist.append(QColor(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)))
        
        # 默认的图表指标
        self.chartIndicator = ['avol']

    def reset_chart(self):
        """重置图表状态"""
        self.stockcode = None
        self.prestockcode = None
        self.period = 0
        self.viewData = None
        self.kdata = OrderedDict()
        self.arraydata = np.array([])
        self.kdispdataArr = np.array([])
        self.colsDict = dict()
        self.resourceData = pd.DataFrame()
        self.kdispdata = None
        self.weightdata = None
        self.kdispcount = 0
        self.ktotalcount = 0
        self.mouseposx = 0
        self.mouseposy = 0
        self.indicatorpos = 0
        self.crossline = True
        self.helperlinepos = None
        self.helperlinekindex = None
        self.zoombase = 1  # 初始值
        self.zoom = self.zoombase
        self.lastzoom = self.zoom
        self.zoominmax = 3
        self.canzoomout = True
        self.mousepos = None
        self.mouseglobalpos = None
        self.pricehigh = 0
        self.pricelow = 100000
        self.pricerange = self.pricehigh - self.pricelow
        self.kdispstartInd = 0  # 当前界面第一根K线行索引
        self.endIdx = 10000000  # 当前界面最后一根K线行索引
        self.kleft = 0
        self.kindex = 0
        self.maintitle = []
        self.VerticalGridLinePosX = []
        self.dispdataPosX = []

    def normalizeKdata(self):
        """标准化K线数据"""
        if len(self.resourceData):
            x = self.viewData.data
            self.kdata = []
            # 需要处理的列
            cols_to_process = ['volp', 'c', 'date', 'h', 'l', 'o', 'volume', 'hsl', 'chg']

            for i in x.index:
                x1 = OrderedDict()
                for col in cols_to_process:
                    x1[col] = x.loc[i, col]
                self.kdata.append(x1)
        else:
            return self.kdata

class Chart(chartBase):
    DataUpdatefinished = pyqtSignal()
    emitKwidthSig = pyqtSignal(float)
    emitChartSig = pyqtSignal(object,object)

    def __init__(self):
        super(chartBase).__init__()
        super(Chart, self).__init__()
        self.log = True #是否对数坐标
        self.dateHeight = 10
        # realtime stockdata update
        self.periodSelect = QComboBox(self)
        self.periodSelect.setMaximumHeight(20)
        self.periodSelect.setMinimumHeight(20)
        self.periodSelect.setHidden(True)
        self.periodSelect.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.periodSelect.currentIndexChanged.connect(self.periodChanged)
        periodlist = ['日', '周', '月', '季', '半年', '年']
        self.periodSelect.addItems(periodlist)
        self.krange = 300
        # self.rt_timer = QTimer()
        # self.rt_timer.setInterval(10000)
        # self.rt_data = {}
        # self.rt_timer.timeout.connect(self.rtStockdataUpdate)
        # self.rt_timer.start()
        # indicators.volma.Volma([20, 50,245,750])
        self.stockcode = None
        self.mainIndicator = []#['avolma']
        self.mainIndAddActLst = []
        #self.mainIndicator = indicators.Avolma.Avolma(['avolma'])
        self.DataUpdatefinished.connect(self.calculatePriceRangeBasedOnKData)
        self.createContextMenu()
        self.RectX,self.RectY = self.rect().width(),self.rect().height()
        self.lines = ['avolma']
        self.menuCreate = True
        self.americK = False

    def rtStockdataUpdate(self):
        if(not self.stockcode):
            return
        if(globals.realtime):
            if(self.rt_data.get('working')):
                return
            self.rt_data['working'] = True
            hqinfo, _resourcedata = stock.getHq(self.stockcode)
            self.rt_data['data'] = hqinfo
            if(hqinfo['code'] != self.stockcode):
                return
            if(self.kdata[-1]['date'] == hqinfo['date']):
                self.kdata[-1] = hqinfo
                self.resourceData = pd.concat(
                    [self.resourceData[:-1], _resourcedata])
            else:
                self.kdata.append(hqinfo)
                self.resourceData = pd.concat(
                    [self.resourceData, _resourcedata])
            self.rt_data['working'] = False
            self.resetchartscrollbar.emit(len(self.kdata), 1)
            if(self.rt_data.get('status') != 'realtime' or self.rt_data.get('stockcode') != self.stockcode):
                self.scrollbartriggerSig.emit()
                self.rt_data['stockcode'] = self.stockcode
                self.rt_data['status'] = 'realtime'
            self.update()
    #@engine._async

    def paintEvent(self, event):
        try:
            if len(self.arraydata):
                if self.menuCreate:
                    self.createContextMenu()
                    self.menuCreate = False
                painter = QPainter(self)
                # fill background
                #painter.fillRect(self.rect(), backgroundColor)
                #painter.setPen(QColor(128, 128, 128))
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setFont(QFont(self.font, self.fontsize))
                QToolTip.setFont(QFont(self.font, self.fontsize))
                #painter.drawRect(QRect(self.rect().width()-self.rightMarkwidth, 0, self.rect().width()-3, self.rect().height()))
        #        painter.drawLine(self.rect().width()-2, 0, self.rect().width()-2, self.rect().height())
                painter.drawLine(self.RectX-self.rightMarkwidth, self.maintitleHeight,
                                 self.RectX-self.rightMarkwidth, self.RectY)
                painter.drawLine(self.RectX-1, 0,
                                 self.RectX-1, self.RectY)
                # draw nothing when there is no data
                # update data for display
                # self.handleDataUpdate()
                self.handleDataUpdateSig.emit()
                # calculate pricehigh, pricelow and pricerange
                self.calculatePriceRangeBasedOnKData()
                # update mainIndicator
    #            self.cal_kdispcount()
    #            self.cal_kdispdata()
                if(self.mainIndicator):
                    # utils.feedstockdata(self.mainIndicator)
                    self.feedstockkdataSig.emit([self.mainIndicator])
                    self.mainIndicator.updateDataAndPriceRange()
                # draw price and date grid
                self.drawPriceAndDateGrid(painter)
                # draw candle sticks
                self.drawCandleSticks(painter)
                #self.drawFibonacci(painter)
                # draw helper line
                self.drawHelperline(painter)        
                if hasattr(self,'indMouseMove'):
                    self.drawHelperlineAct(painter)
                else:
                    self.drawHelperline(painter)
                # draw main chart title
                self.drawMainChartTitle(painter)
                # draw cross line
                self.drawCrossline(painter)
                # draw price and date tips
                self.updateStockInfoSig.emit()
                self.emitChartSig.emit(self,'xxx')
        except Exception as e:
            print(f'119:{e}')
            #self.secreen = QApplication.primaryScreen().grabWindow(QApplication.desktop().winId())
#    def paintAct2(self,event):
#        if self.canselfdrawing:            
#            self.Wincreen.update()    

    def drawFibonacci(self,painter):
        """
        画斐波那契线
        """
        try:
            painter.setPen(Qt.DashLine)
            painter.setPen(QColor(255, 0, 0))
            cache = self.kdispdataArr[:,self.colsDict['c']]
            if len(cache):
                cache = cache[np.argmax(cache):]
                llv = np.min(cache)
                priceRange = cache[0] - llv
                #self.FibonacciArr = [llv*i for i in [1.382,1.5,1.618]]
                #压力线
                for fibonacci in [0.382,0.5,0.618]:
                    Fibonacci_ypos = self.topMarginheight + self.krange * (1 - (priceRange*fibonacci+llv - self.pricelow) / self.pricerange)
                    painter.drawLine(QPointF(self.chartwidth, Fibonacci_ypos), QPointF(self.chartwidth+self.kmarginw, Fibonacci_ypos))
                #支撑线
                painter.setPen(QColor(0, 0, 0))
                cache = cache[np.argmin(cache):]
                hhv = np.max(cache)
                priceRange = hhv - cache[0] 
                for fibonacci in [0.382,0.5,0.618]:
                    Fibonacci_ypos = self.topMarginheight + self.krange * (1 - (hhv-priceRange*fibonacci - self.pricelow) / self.pricerange)
                    painter.drawLine(QPointF(self.chartwidth, Fibonacci_ypos), QPointF(self.chartwidth+self.kmarginw, Fibonacci_ypos))
        except Exception as e:
            print(f'111:{e}')
    def updateKdispData(self):
        try:
            self.kdispdataArr = self.arraydata[range(self.kdispstartInd,self.endIdx+1),:]
            self.calculatePriceRangeBasedOnKData()
        except Exception as e:
            print(f'112:{e}')

    def calculatePriceRangeBasedOnKData(self):
        # calculate pricehigh, pricelow and pricerange
        try:
            if self.colsDict.get('avolma'):
                if len(self.kdispdataArr[:,[self.colsDict['l'],self.colsDict.get('avolma')]]):
                    self.pricelow = np.nanmin(self.kdispdataArr[:,[self.colsDict['l'],self.colsDict.get('avolma')]])
                    self.pricehigh = np.nanmax(self.kdispdataArr[:,[self.colsDict['h'],self.colsDict.get('avolma')]])
    #                if self.pricehigh>=0:
    #                    self.hasGreatZero = True
    #                else:
    #                    self.hasGreatZero = False
    #                if self.pricelow<=0:
    #                    self.hasLessZero = True
    #                else:
    #                    self.hasLessZero = False
    #                    
                    if self.pricehigh<=0:
                        self.pricerange = np.abs(self.pricelow - self.pricehigh)
                    else:
                         self.pricerange = self.pricehigh - self.pricelow
                    self.priceGridHelper()
    #                if not self.log:
    #                    self.priceGridHelper()
    #                    self.pricerange = np.log2(self.pricerange)
                    self.calculatePriceRangeBasedOnKDataFinished.emit(self.pricerange)
            else:
                if len(self.kdispdataArr[:,self.colsDict['l']]):
                    self.pricelow = np.nanmin(self.kdispdataArr[:,self.colsDict['l']])
                    self.pricehigh = np.nanmax(self.kdispdataArr[:,self.colsDict['h']])
    #                if self.pricehigh>=0:
    #                    self.hasGreatZero = True
    #                else:
    #                    self.hasGreatZero = False
    #                if self.pricelow<=0:
    #                    self.hasLessZero = True
    #                else:
    #                    self.hasLessZero = False
    #                    
                    if self.pricehigh<=0:
                        self.pricerange = np.abs(self.pricelow - self.pricehigh)
                    else:
                         self.pricerange = self.pricehigh - self.pricelow
                    self.priceGridHelper()
    #                if not self.log:
    #                    self.priceGridHelper()
    #                    self.pricerange = np.log2(self.pricerange)
                    self.calculatePriceRangeBasedOnKDataFinished.emit(self.pricerange)
        except Exception as e:
            print(f'113:{e}')

    def priceGridHelper(self):
        if self.log:
            llv = np.exp2(self.pricelow)
            hhv = np.exp2(self.pricehigh)
            pricegrid = [llv]
            while pricegrid[-1]<hhv:
                pricegrid.append(1.1*pricegrid[-1])
            if pricegrid[-1]<hhv:
                pricegrid += [hhv]
            else:
                pricegrid[-1] = hhv
            pricegrid = np.log2(pricegrid)
        else:
            pricegrid = [self.pricelow]
            while pricegrid[-1]<self.pricehigh:                        
                pricegrid.append(1.1*pricegrid[-1])
            if pricegrid[-1]<self.pricehigh:
                pricegrid += [self.pricehigh]
            else:
                pricegrid[-1] = self.pricehigh
        self.pricegrid = pricegrid
        self.pricegridposy = [self.cac_posy(p) for p in pricegrid]

    def drawPriceAndDateGrid(self, painter):
        try:
            print('xxxxxxxxx')
            # draw price grid
            painter.setPen(Qt.DashLine)
            for posy in self.pricegridposy:
                painter.drawLine(0, posy, self.chartwidth, posy)
    #        painter.setPen(Qt.SolidLine)  
    #        painter.setPen(QColor(0,0,238))
            for posy,p in zip(self.pricegridposy,self.pricegrid):
                painter.drawLine(self.chartwidth+self.whiteKwidth, posy,
                                 self.chartwidth+self.whiteKwidth+4, posy) #画右侧短横线
                painter.drawText(self.chartwidth+self.whiteKwidth+8, posy+5, '{:.2f}'.format(np.exp2(p))) #辅助线价格标示
            # 顶部显示栏
            #painter.setBrush(QColor(255, 255, 255, 100))
    #        painter.drawRect(0, 0, self.rect().width(), kposy_y)
    #        painter.setBrush(QColor(255, 255, 240, 60))
            painter.setPen(Qt.SolidLine)
            painter.drawLine(0, self.maintitleHeight, self.RectX-self.rightMarkwidth, self.maintitleHeight) #顶部显示栏分割线
            self.periodSelect.setGeometry(self.RectX-self.periodSelect.width()-self.rightMarkwidth-1, self.rect(
            ).height()-self.periodSelect.height(), self.periodSelect.width(), self.periodSelect.height())
            # draw date grid
            kcnt = len(self.kdispdataArr)
            if kcnt:
                self.kdispdatakcnt = kcnt
                for i in range(0, self.chartwidth, 200):
                    idx = math.floor((i-self.kleft)/self.kwidth+0.5)  #kdispdataArr的行索引
                    if(idx < 0):
                        idx = 0
                    if(idx >= kcnt):
                        idx = kcnt - 1
                    date = self.ta.dateArr[self.kdispstartInd:
                                self.kdispstartInd+self.kdispcount]
                    if(i == self.chartwidth):
                        date = '{}/{}'.format(date[4:6], date[6:])
                    else:
                        date = '{}/{}/{}'.format(date[:4], date[4:6], date[6:])
                indexrange = [i for i in range(kcnt+1)]
    #            painter.fillRect(0, 0, self.rect().width() -
    #                             self.rightMarkwidth, kposy_y, QColor(0, 0, 0, 60))
        #        painter.setPen(QColor(128, 128, 128))
                #painter.setPen(QColor(0, 0, 0))
                painter.setPen(Qt.DotLine)
                posy0 = self.topMarginheight
                posy1 = self.RectY-self.bottomMarkHeight
                margin = 144
                if (self.zoom > 0.3) & (self.zoom < 1):
                    margin = 20
                elif self.zoom < 0.1:
                    margin = 245
                elif self.zoom >= 1:
                    margin = 5
                year = []
                self.VerticalGridLinePosX = []
                for cnt in indexrange:
                    kposx = self.kleft + cnt*self.kwidth
                    if (np.mod(cnt, margin) == 0) & ((kcnt-cnt)*self.kwidth >= margin*self.kwidth):
                        painter.drawLine(QPointF(kposx, posy0), QPointF(kposx, posy1))
                        self.VerticalGridLinePosX.append(kposx)
                        try:
                            date = self.ta.dateArr[self.kdispstartInd:
                                self.kdispstartInd+self.kdispcount][cnt]
                            #date = '20200102'
                            yearflag = date[:4]
                            if yearflag in year:
                                date = date[4:]
                            else:
                                year.append(yearflag)
                            painter.drawText(kposx, self.Rect.height(
                            )-self.bottomMarkHeight+self.dateHeight, date)
                        except Exception as e:
                            print(f'114:{e}')
                    elif cnt == (kcnt-1):
                        painter.drawLine(QPointF(kposx, posy0), QPointF(kposx, posy1))
                        self.VerticalGridLinePosX.append(kposx)
                        try:
                            date = self.ta.dateArr[cnt]
                            #date = '20200102'
                            painter.drawText(kposx-self.kwidth-self.kleft, self.rect(
                            ).height()-self.bottomMarkHeight+self.dateHeight, date)
                        except Exception as e:
                            print(f'115:{e}')
    #            painter.setPen(Qt.SolidLine)
    #            #draw date tips
    #            tipwidth = 72
    #            tipleft = self.helperlinepos.x()+self.kwidth*0.45
    #            if(tipleft + tipwidth>self.chartwidth):
    #                tipleft =self.helperlinepos.x() - self.kwidth*0.45 - tipwidth
    #            painter.fillRect(tipleft, self.rect().height()-2,tipleft+tipwidth, self.rect().height()-self.bottomMarkHeight, QColor(225,255,240))
    #
    #
    #            date = self.kdata[self.helperlinekindex]['date']
    #            date = '{}/{}/{}'.format(date[:4],date[4:6],date[6:])
    #            painter.drawText(tipleft+4, self.rect().height()-self.bottomMarkHeight+self.dateHeight+6, date)
        except Exception as e:
            print(f'116:{e}')
            
    def cac_posy(self,data,**kwargs):
        #drawCandleSticks helper
        if self.log:
            posy = self.topMarginheight + (1 - (data - self.pricelow)/self.pricerange) * self.krange
        else:
            posy = self.topMarginheight + (1 - (data - self.pricelow)/self.pricerange) * self.krange
        return posy
#    def cac_posy(self,data,**kwargs):
#        if self.hasLessZero & self.hasGreatZero:
#            zeroposy = self.krange * (self.pricehigh/self.pricerange)
#        if not self.hasLessZero:
#            posy = self.krange * (1-data/self.pricerange) + self.topMarginheight
#        elif not self.hasGreatZero:
#            posy = self.krange *(abs(data)+self.pricehigh)/self.pricerange + self.topMarginheight
#        elif data>=0:
#            posy = zeroposy * (1-data/self.pricerange)+self.topMarginheight
#        else:
#            posy = self.krange * (abs(data)+self.pricehigh)/self.pricerange + self.topMarginheight
#        return posy
#    

    def drawCandleSticks_log(self,painter):
        cnt = 0
        self.dispdataPosX = []
        prev_avolma = None
        prev_rzrq = None
        buy = False
        sell = True
        flag2 = False
        if len(self.kdispdataArr):
            for row in self.kdispdataArr:
                kposx = self.kleft + cnt*self.kwidth
                self.dispdataPosX.append(kposx)
                o = row[self.colsDict['o']]
                kposy_open = self.cac_posy(o)
                kposy_high = self.cac_posy(row[self.colsDict['h']])
                kposy_low = self.cac_posy(row[self.colsDict['l']])
                c = row[self.colsDict['c']]
                kposy_close = self.cac_posy(c)
                kcolor = 'black'
                painter.setPen(QColor(0, 0, 0))
                kspan = 0.6
                painter.drawLine(QPointF(kposx, kposy_high),
                                 QPointF(kposx, kposy_low))
                if c > o:
                    kcolor = 'red'
                    painter.setPen(QColor(255, 0, 0))
                else:
                    kcolor = 'green'
                    painter.setPen(QColor(0, 128, 0))
                if self.americK:
                    if(self.zoom > 0.3):
                        if True:
                            painter.drawLine(
                                QPointF(kposx-self.kwidth*kspan/2, kposy_open), QPointF(kposx, kposy_open))
                            painter.drawLine(QPointF(kposx, kposy_close), QPointF(
                                kposx+self.kwidth*kspan/2, kposy_close))
                            painter.drawLine(
                                QPointF(kposx, kposy_low), QPointF(kposx, kposy_high))
                else:
                    if(self.zoom > 0.3):
                        if(kcolor == 'black'):
                            painter.drawLine(QPointF(
                                kposx-self.kwidth*kspan/2, kposy_open), QPointF(kposx+self.kwidth*kspan/2, kposy_close))
                        elif(kcolor == 'green'):
                            painter.fillRect(QRectF(QPointF(kposx-self.kwidth*kspan/2, kposy_open), QPointF(
                                kposx+self.kwidth*kspan/2, kposy_close)), QColor(0, 128, 0))
                            painter.drawRect(QRectF(QPointF(
                                kposx-self.kwidth*kspan/2, kposy_open), QPointF(kposx+self.kwidth*kspan/2, kposy_close)))
                        elif(kcolor == 'red'):
                            painter.fillRect(QRectF(QPointF(kposx-self.kwidth*kspan/2, kposy_close), QPointF(
                                kposx+self.kwidth*kspan/2, kposy_open)), QColor(255, 255, 240))
                            painter.drawRect(QRectF(QPointF(
                                kposx-self.kwidth*kspan/2, kposy_close), QPointF(kposx+self.kwidth*kspan/2, kposy_open)))
                if self.colsDict.get('avolma'):    
                    avolma = row[self.colsDict.get('avolma')]
                    painter.setPen(QColor(255, 0, 0))
                    if(prev_avolma and prev_avolma != None and prev_avolma != np.NAN):
                        kposxprev = self.dispdataPosX[-2]
                        kposy = self.cac_posy(avolma)
                        kposyprev = self.cac_posy(prev_avolma)
                        painter.drawLine(QPointF(kposxprev, kposyprev),
                                         QPointF(kposx, kposy))
                        flag2 = avolma > prev_avolma
                    prev_avolma = avolma
                # if self.colsDict.get('rzrq'):    
                #     rzrq = row[self.colsDict.get('rzrq')]
                #     painter.setPen(QColor(255, 0, 0))
                #     if(prev_rzrq and prev_rzrq != None and prev_rzrq != np.NAN):
                #         kposxprev = self.dispdataPosX[-2]
                #         kposy = self.cac_posy(rzrq)
                #         kposyprev = self.cac_posy(prev_rzrq)
                #         painter.drawLine(QPointF(kposxprev, kposyprev),
                #                          QPointF(kposx, kposy))
                #     prev_rzrq = rzrq
                # if self.colsDict.get('flag'):
                #     flag = row[self.colsDict['flag']]
                #     flag1 = 1.3*avolma < c
                #     self.setMask(pic[1].mask())
                #     if (flag == 1) & sell & flag2:
                #         buy = True
                #         sell = False
                #         # painter.drawText(kposx,int(kposy_low+20),'B')
                #         painter.drawPixmap(int(kposx-pic[1].width()/2), int(
                #             kposy_low+pic[1].height()), int(pic[1].width()), int(pic[2].height()), pic[1])
                #     if buy & flag1:
                #         painter.setPen(QColor(0, 255, 0))
                #         painter.drawText(kposx, int(kposy_low+20), 'S')
                #         sell = True
                #         buy = False
                #     elif buy & (flag == -1):
                #         painter.setPen(QColor(0, 255, 0))
                #         # painter.drawText(kposx,int(kposy_low+20),'S')
                #         painter.drawPixmap(int(kposx-pic[2].width()/2), int(
                #             kposy_low+pic[2].height()), int(pic[2].width()), int(pic[2].height()), pic[2])
                #         sell = True
                #         buy = False
                cnt += 1
            if self.colsDict.get('holdday'):
                holdday = int(row[self.colsDict['holdday']])
                brush = QBrush(Qt.Dense6Pattern)
                painter.setBrush(brush)
                #painter.setPen(QColor(220, 122, 122, 20))
                painter.setPen(QColor(10, 12, 20, 20))
                if holdday <= len(self.dispdataPosX):
                    h_price = self.kdispdataArr[-holdday:][:,self.colsDict['h']]
                    l_price = self.kdispdataArr[-holdday:][:,self.colsDict['l']]
                    avolma_price = self.kdispdataArr[-holdday:][:,self.colsDict['avolma']]
                    hhp = np.max([np.nanmax(h_price),np.nanmax(avolma_price)])
                    llp = np.min([np.nanmin(l_price),np.nanmin(avolma_price)])
                    if self.ktotalcount >= self.dispdataPosX[-holdday]:
                        kposyllp = self.topMarginheight + (1 - (llp - self.pricelow)/self.pricerange) * self.krange
                        kposyhhp = self.topMarginheight + (1 - (hhp - self.pricelow)/self.pricerange) * self.krange
                        painter.drawRect(QRectF(QPointF(self.dispdataPosX[-holdday], kposyllp), QPointF(self.chartwidth, kposyhhp)))
                # update title
            #self.updateDistpText()

    def drawCandleSticks(self, painter):
        if self.log:
            self.drawCandleSticks_log(painter)
        else:
            self.drawCandleSticks_liner(painter)

    def drawCandleSticks_liner(self,painter):
        cnt = 0
        self.dispdataPosX = []
        prev_avolma = None
        prev_rzrq = None
        buy = False
        sell = True
        flag2 = False
        if len(self.kdispdataArr):
            for row in self.kdispdataArr:
                kposx = self.kleft + cnt*self.kwidth
                self.dispdataPosX.append(kposx)
                o = row[self.colsDict['o']]
                kposy_open = self.cac_posy(o)
                kposy_high = self.cac_posy(row[self.colsDict['h']])
                kposy_low = self.cac_posy(row[self.colsDict['l']])
                c = row[self.colsDict['c']]
                kposy_close = self.cac_posy(c)
                kcolor = 'black'
                painter.setPen(QColor(0, 0, 0))
                kspan = 0.6
                painter.drawLine(QPointF(kposx, kposy_high),
                                 QPointF(kposx, kposy_low))
                if c > o:
                    kcolor = 'red'
                    painter.setPen(QColor(255, 0, 0))
                else:
                    kcolor = 'green'
                    painter.setPen(QColor(0, 128, 0))
                if self.americK:
                    if(self.zoom > 0.3):
                        if True:
                            painter.drawLine(
                                QPointF(kposx-self.kwidth*kspan/2, kposy_open), QPointF(kposx, kposy_open))
                            painter.drawLine(QPointF(kposx, kposy_close), QPointF(
                                kposx+self.kwidth*kspan/2, kposy_close))
                            painter.drawLine(
                                QPointF(kposx, kposy_low), QPointF(kposx, kposy_high))
                else:
                    if(self.zoom > 0.3):
                        if(kcolor == 'black'):
                            painter.drawLine(QPointF(
                                kposx-self.kwidth*kspan/2, kposy_open), QPointF(kposx+self.kwidth*kspan/2, kposy_close))
                        elif(kcolor == 'green'):
                            painter.fillRect(QRectF(QPointF(kposx-self.kwidth*kspan/2, kposy_open), QPointF(
                                kposx+self.kwidth*kspan/2, kposy_close)), QColor(0, 128, 0))
                            painter.drawRect(QRectF(QPointF(
                                kposx-self.kwidth*kspan/2, kposy_open), QPointF(kposx+self.kwidth*kspan/2, kposy_close)))
                        elif(kcolor == 'red'):
                            painter.fillRect(QRectF(QPointF(kposx-self.kwidth*kspan/2, kposy_close), QPointF(
                                kposx+self.kwidth*kspan/2, kposy_open)), QColor(255, 255, 240))
                            painter.drawRect(QRectF(QPointF(
                                kposx-self.kwidth*kspan/2, kposy_close), QPointF(kposx+self.kwidth*kspan/2, kposy_open)))
                if self.colsDict.get('avolma'):    
                    avolma = row[self.colsDict.get('avolma')]
                    painter.setPen(QColor(255, 0, 0))
                    if(prev_avolma and prev_avolma != None and prev_avolma != np.NAN):
                        kposxprev = self.dispdataPosX[-2]
                        kposy = self.cac_posy(avolma)
                        kposyprev = self.cac_posy(prev_avolma)
                        painter.drawLine(QPointF(kposxprev, kposyprev),
                                         QPointF(kposx, kposy))
                        flag2 = avolma > prev_avolma
                    prev_avolma = avolma
                # if self.colsDict.get('rzrq'):    
                #     rzrq = row[self.colsDict.get('rzrq')]
                #     painter.setPen(QColor(255, 0, 0))
                #     if(prev_rzrq and prev_rzrq != None and prev_rzrq != np.NAN):
                #         kposxprev = self.dispdataPosX[-2]
                #         kposy = self.cac_posy(rzrq)
                #         kposyprev = self.cac_posy(prev_rzrq)
                #         painter.drawLine(QPointF(kposxprev, kposyprev),
                #                          QPointF(kposx, kposy))
                #     prev_rzrq = rzrq
                # if self.colsDict.get('flag'):
                #     flag = row[self.colsDict['flag']]
                #     flag1 = 1.3*avolma < c
                #     self.setMask(pic[1].mask())
                #     if (flag == 1) & sell & flag2:
                #         buy = True
                #         sell = False
                #         # painter.drawText(kposx,int(kposy_low+20),'B')
                #         painter.drawPixmap(int(kposx-pic[1].width()/2), int(
                #             kposy_low+pic[1].height()), int(pic[1].width()), int(pic[2].height()), pic[1])
                #     if buy & flag1:
                #         painter.setPen(QColor(0, 255, 0))
                #         painter.drawText(kposx, int(kposy_low+20), 'S')
                #         sell = True
                #         buy = False
                #     elif buy & (flag == -1):
                #         painter.setPen(QColor(0, 255, 0))
                #         # painter.drawText(kposx,int(kposy_low+20),'S')
                #         painter.drawPixmap(int(kposx-pic[2].width()/2), int(
                #             kposy_low+pic[2].height()), int(pic[2].width()), int(pic[2].height()), pic[2])
                #         sell = True
                #         buy = False
                cnt += 1
            if self.colsDict.get('holdday'):
                holdday = int(row[self.colsDict['holdday']])
                brush = QBrush(Qt.Dense6Pattern)
                painter.setBrush(brush)
                #painter.setPen(QColor(220, 122, 122, 20))
                painter.setPen(QColor(10, 12, 20, 20))
                if holdday <= len(self.dispdataPosX):
                    h_price = self.kdispdataArr[-holdday:][:,self.colsDict['h']]
                    l_price = self.kdispdataArr[-holdday:][:,self.colsDict['l']]
                    avolma_price = self.kdispdataArr[-holdday:][:,self.colsDict['avolma']]
                    hhp = np.max([np.nanmax(h_price),np.nanmax(avolma_price)])
                    llp = np.min([np.nanmin(l_price),np.nanmin(avolma_price)])
                    if self.ktotalcount >= self.dispdataPosX[-holdday]:
                        kposyllp = self.topMarginheight + (1 - (llp - self.pricelow)/self.pricerange) * self.krange
                        kposyhhp = self.topMarginheight + (1 - (hhp - self.pricelow)/self.pricerange) * self.krange
                        painter.drawRect(QRectF(QPointF(self.dispdataPosX[-holdday], kposyllp), QPointF(self.chartwidth, kposyhhp)))
                # update title
            #self.updateDistpText()

    def drawMainInd(self, item, painter, row, n):
        pass
        # if self.colsDict.get('avolma'):
        #     avolma = row[self.colsDict['avolma']]
        #     if(prev_avolma and prev_avolma != None and prev_avolma != np.NAN):
        #         kposxprev = self.dispdataPosX[-2]
        #         kposy = self.topMarginheight + \
        #             (1 - (avolma - self.pricelow)/self.pricerange) * self.krange
        #         kposyprev = self.topMarginheight + \
        #             (1 - (prev_avolma - self.pricelow)/self.pricerange) * self.krange
        #         painter.drawLine(QPointF(kposxprev, kposyprev),
        #                           QPointF(kposx, kposy))

    def updateDistpText(self):
        maintitle = '{}'.format(self.stockcode)
        stockname = getName.getName(self.stockcode)
        if(stockname):
            maintitle = '{} {}'.format(stockname, self.stockcode)
        self.maintitle = []
        self.maintitle.append(
            {'x': self.maintitlePox['x'], 'y': self.maintitlePox['y'], 'text': maintitle, 'color': QColor(0, 0, 0)})

    def drawMainChartTitle(self, painter):
        for txtinfo in self.maintitle:
            painter.setPen(txtinfo['color'])
            painter.drawText(txtinfo['x'], txtinfo['y'], txtinfo['text'])
        # if not painter.isActive():
        #     painter.end()
#    def set_codelist(self, codelist):
#        self.codelist = codelist

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if not self.canselfdrawing:
            key = event.key()
            if (key == Qt.Key_Escape):
                self.ChangeSLayoutSig.emit()
            elif (key == Qt.Key_Left):
                self.resetchartscrollbar.emit(999, 4)
    #            self.endIdx -= 1
    #            self.cal_kdispdata()
    #            self.update()
    #            self.emitChartSig.emit(self)
            elif (key == Qt.Key_Right):
                self.resetchartscrollbar.emit(999, 5)
            elif(key == Qt.Key_PageUp):
                self.resetchartscrollbar.emit(999, 6)
            elif(key == Qt.Key_PageDown):
                self.resetchartscrollbar.emit(999, 7)
            elif (self.zoom < self.zoominmax and key == Qt.Key_Up):
                self.zoom *= 1.1
                self.update()
                self.emitChartSig.emit(self,'xxx')
            elif (self.canzoomout and key == Qt.Key_Down):
                self.zoom /= 1.1
                self.update()
                self.emitChartSig.emit(self,'xxx')
            elif (key == Qt.Key_Backspace):
                self.zoom = self.zoombase
                self.update()
                self.emitChartSig.emit(self,'xxx')
            elif (key == Qt.Key_Space):
                if(not self.crossline):
                    self.crossline = True
                else:
                    self.crossline = False
                self.update()
            elif (key == Qt.Key_C):
                self.crossline = False
                self.helperlinepos = None
                self.update()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if (event.button() == Qt.LeftButton):
            if(not self.helperlinepos):
                self.helperlinepos = event.pos()
            else:
                self.helperlinepos = None
        elif (event.button() == Qt.RightButton):
            self.releaseMouse()
            if(not self.helperlinepos):                    
                self.helperlinepos = event.pos()
            else:
                self.helperlinepos = None
        self.mousepos = event.localPos()
        self.mouseglobalpos = event.globalPos()
        self.clickpos = event.localPos()
        self.update()
        self.emitChartSig.emit(self,'xxx')

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        # self.helperlinepos = None
        # painter = QPainter(self)
        # painter.fillRect(
        #     QRect(self.clickpos.x(), self.clickpos.y(), 100, 300), QColor(0, 0, 0))
        # self.update()

    def mouseDoubleClickEvent(self, event):
        #super().mouseMoveEvent(event)
        if not self.canselfdrawing:
            self.showStockInfoDlgSig.emit()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if not self.canselfdrawing:
            self.mousepos = event.localPos()
            self.mouseglobalpos = event.globalPos()
            self.update()
            self.emitChartSig.emit(self,'xxx')
#    def mouseMoveEventAct(self, x,y):
#        if not self.canselfdrawing:
#            self.mouseposx = x
#            self.mouseposy = y
#            self.update()
#            self.emitChartSig.emit(self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.Rect = self.rect()
        self.RectX,self.RectY = self.rect().width(),self.rect().height()
        self.chartwidth = self.RectX - self.rightMarkwidth-self.whiteKwidth
        self.resetchartscrollbar.emit(int(self.chartwidth/1000)-1, 3)
        self.emitChartSig.emit(self,'xxx')

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.crossline = False

    def wheelEventAct(self, y):
        if y > 0:  # up
            if(self.zoom < self.zoominmax):
                self.zoom *= 1.01
                self.update()
                self.emitChartSig.emit(self,'xxx')
        else:  # down
            if(self.canzoomout):
                self.zoom /= 1.01
                self.update()
                self.emitChartSig.emit(self,'xxx')

    def cal_kdispcount(self):
        self.kwidth = self.kwidth*self.zoom
        self.kleft = self.chartwidth - self.kmarginw/2 - self.kdispcount * self.kwidth
        # self.krange is the area for drawing candle sticks
        self.krange = self.RectY - self.bottomMarkHeight - self.topMarginheight 
        self.kdispcount = int((self.chartwidth - self.kmarginw*2)/self.kwidth)

    def cal_kdispdata(self):
        if self.endIdx >= (len(self.arraydata)-1):
            self.ktotalcount = len(self.arraydata)
            self.endIdx = self.ktotalcount-1
        self.kdispstartInd = self.endIdx - self.kdispcount+1
        if self.kdispstartInd < 0:
            self.kdispstartInd = 0
        self.kdispdataArr = self.arraydata[self.kdispstartInd:
                            self.kdispstartInd+self.kdispcount]
        self.update()

    def handleDataUpdate(self, chartscroballvalue):
        self.cal_kdispcount()
        self.ktotalcount = len(self.arraydata)
        # calculate kwidth and kdispcount
        self.kwidth = 10
        self.kwidth = self.kwidth*self.zoom
        self.kdispcount = int((self.chartwidth - self.kmarginw*2)/self.kwidth)
        self.kleft = self.chartwidth - self.kmarginw/2 - self.kdispcount * self.kwidth
        # self.krange is the area for drawing candle sticks
        self.krange = self.RectY -self.topMarginheight - self.bottomMarkHeight 
        # normal zoom
        # globals.mainwin.chartscrollbar.value() - self.kdispcount
        self.kdispstartInd = chartscroballvalue-self.kdispcount
        self.canzoomout = True
        if(self.kdispstartInd < 0):
            self.kdispstartInd = 0
            self.canzoomout = False
        if self.kdispstartInd >= (self.ktotalcount-1):
            self.kdispstartInd = self.ktotalcount-self.dispcount-1
            self.canzoomout = False
        # zoom and move candle sticks based on helperline
        if(self.helperlinepos and self.helperlinekindex and self.lastzoom != self.zoom):  # zoom
            if(self.kdispstartInd != 0):  # can zoom
                idxdiff = math.floor(
                    (self.helperlinepos.x()-self.kleft)/self.kwidth+0.5)
                self.kdispstartInd = self.helperlinekindex - idxdiff
                if(self.kdispstartInd + self.kdispcount > self.ktotalcount):
                    self.kdispstartInd = self.ktotalcount - self.kdispcount
                    self.scrollbarsetValueSig.emit(self.ktotalcount)
                else:
                    if(self.kdispstartInd < 0):
                        self.kdispstartInd = 0
                    self.scrollbarsetValueSig.emit(
                        self.kdispstartInd + self.kdispcount)
        if(self.helperlinepos and self.helperlinekindex):  # move
            if(self.helperlinekindex < self.kdispstartInd):  # left border
                self.kdispstartInd = self.helperlinekindex
                self.scrollbarsetValueSig.emit(
                    self.kdispstartInd + self.kdispcount)
            if((self.helperlinekindex + 1) > (self.kdispstartInd + self.kdispcount)):  # right border
                self.kdispstartInd = self.helperlinekindex + 1 - self.kdispcount
                self.scrollbarsetValueSig.emit(self.helperlinekindex+1)
            # update helperlinepos
            idx = self.helperlinekindex - self.kdispstartInd
            posx = self.kleft + idx*self.kwidth
            self.helperlinepos.setX(posx)
        self.lastzoom = self.zoom
        self.kdispdataArr = self.arraydata[self.kdispstartInd:
                            self.kdispstartInd+self.kdispcount]
        # calculate helperlinekindex based on helperline pos
        if(self.helperlinepos):
            if(not self.helperlinekindex):
                kcnt = len(self.arraydata)
                self.helperlinekindex = math.floor(
                    (self.helperlinepos.x()-self.kleft)/self.kwidth+0.5)
                if(self.helperlinekindex < 0):
                    self.helperlinekindex = 0
                if(self.helperlinekindex >= kcnt):
                    self.helperlinekindex = kcnt - 1
                # update self.helperlinepos, move it to the center of the candle stick
                kposx = self.kleft + self.helperlinekindex*self.kwidth
                self.helperlinepos.setX(kposx)
                self.helperlinekindex += self.kdispstartInd
        if(not self.helperlinepos):
            self.helperlinekindex = None
        # calculate index of self.kdispdata
        self.kindex = 0
        if(self.mousepos):
            kcnt = len(self.arraydata)
            self.kindex = math.floor(
                (self.mousepos.x()-self.kleft)/self.kwidth+0.5)
            if(self.kindex < 0):
                self.kindex = 0
            if(self.kindex >= kcnt):
                self.kindex = kcnt - 1
        # update scrollbar status
        if(self.ktotalcount >= self.kdispcount):
            self.resetchartscrollbar.emit(self.kdispcount, 2)
        else:
            self.resetchartscrollbar.emit(self.ktotalcount, 2)
        self.DataUpdatefinished.emit()
    # def handleDataUpdate(self, chartscroballvalue):
    #     self.cal_kdispcount()
    
    #     # 更新kdispcount, kwidth等
    #     self.kwidth = 10 * self.zoom
    #     self.kdispcount = int((self.chartwidth - self.kmarginw*2) / self.kwidth)
    #     self.kleft = self.chartwidth - self.kmarginw / 2 - self.kdispcount * self.kwidth
    #     self.krange = self.RectY - self.topMarginheight - self.bottomMarkHeight
    
    #     # 更新kdispstartInd
    #     self.kdispstartInd = self.update_kdispstartInd(chartscroballvalue - self.kdispcount)
    
    #     # 根据helperline位置和缩放调整显示
    #     if self.helperlinepos and self.helperlinekindex and self.lastzoom != self.zoom:
    #         idxdiff = math.floor((self.helperlinepos.x() - self.kleft) / self.kwidth + 0.5)
    #         self.kdispstartInd = self.helperlinekindex - idxdiff
    #         self.kdispstartInd = self.update_kdispstartInd(self.kdispstartInd)
    
    #     # 更新helperline
    #     self.update_helperline()
    
    #     # 更新kdispdataArr
    #     self.kdispdataArr = self.arraydata[self.kdispstartInd:self.kdispstartInd + self.kdispcount]
    
    #     # 计算鼠标位置的蜡烛索引
    #     if self.mousepos:
    #         kcnt = len(self.arraydata)
    #         self.kindex = max(0, min(math.floor((self.mousepos.x() - self.kleft) / self.kwidth + 0.5), kcnt - 1))
    
    #     # 更新滚动条状态
    #     self.resetchartscrollbar.emit(min(self.ktotalcount, self.kdispcount), 2)
    
    #     # 完成数据更新
    #     self.DataUpdatefinished.emit()

    def updateStockInfoDlg(self, labels):
        if (self.mousepos):
            try:
                self._updateStockInfoDlg(labels)
            except Exception as e:
                print(f'117:{e}')

    def _updateStockInfoDlg(self, labels):
        try:
            mousex = self.mousepos.x()
            mousey = self.mousepos.y()
            if len(self.kdispdataArr)>self.kindex:
                # #date = str(self.kdispdataArr[self.kindex][self.colsDict['date']])
                # date = self.ta.dateArr[self.kdispstartInd:
                #             self.kdispstartInd+self.kdispcount][self.kindex]
                # d = datetime.date(int(date[:4]), int(date[4:6]), int(date[6:8]))
                # day = self.daylist[d.weekday()]
                # date = '{}/{}/{}({})'.format(date[:4], date[4:6], date[6:], day)
                date='20200102'
                self.updateStockInfoTitleSig.emit(date)
                labels[0].setText(date)  # 日期
                idx = self.kdispstartInd + self.kindex - 1
                if(idx < 0):
                    idx = 0
                prev_row = self.kdispdataArr[self.kindex]
                row = self.kdispdataArr[self.kindex]
                labels[0].setText('{:.2f}'.format(
                    (1-(mousey-self.topMarginheight)/self.krange)*self.pricerange + self.pricelow))  # 数值
                if(row[self.colsDict['o']] > prev_row[self.colsDict['c']]):
                    labels[1].setStyleSheet('color: red')
                elif(row[self.colsDict['o']] < prev_row[self.colsDict['c']]):
                    labels[1].setStyleSheet('color: green')
                else:
                    labels[1].setStyleSheet('color: black')
                labels[1].setText('{:.2f}'.format(row[self.colsDict['o']]))  # 开盘
                if(row[self.colsDict['h']] > prev_row[self.colsDict['c']]):
                    labels[2].setStyleSheet('color: red')
                elif(row[self.colsDict['h']] < prev_row[self.colsDict['c']]):
                    labels[2].setStyleSheet('color: green')
                else:
                    labels[2].setStyleSheet('color: black')
                labels[2].setText('{:.2f}'.format(row[self.colsDict['h']]))  # 最高
                if(row[self.colsDict['l']] > prev_row[self.colsDict['c']]):
                    labels[3].setStyleSheet('color: red')
                elif(row[self.colsDict['l']] < prev_row[self.colsDict['c']]):
                    labels[3].setStyleSheet('color: green')
                else:
                    labels[3].setStyleSheet('color: black')
                labels[3].setText('{:.2f}'.format(row[self.colsDict['l']]))  # 最低
                if(row[self.colsDict['c']] > prev_row[self.colsDict['c']]):
                    labels[4].setStyleSheet('color: red')
                    labels[6].setStyleSheet('color: red')
                    labels[7].setStyleSheet('color: red')
                elif(row[self.colsDict['c']] < prev_row[self.colsDict['c']]):
                    labels[4].setStyleSheet('color: green')
                    labels[6].setStyleSheet('color: green')
                    labels[7].setStyleSheet('color: green')
                else:
                    labels[4].setStyleSheet('color: black')
                    labels[6].setStyleSheet('color: black')
                    labels[7].setStyleSheet('color: green')
                labels[4].setText('{:.2f}'.format(row[self.colsDict['c']]))  # 收盘
                labels[5].setText('{:,.2f}亿'.format(
                    np.true_divide(row[self.colsDict['volp']], 1e8)))  # 成交额
                zd = row[self.colsDict['c']] - prev_row[self.colsDict['c']]
                chg = zd/prev_row[self.colsDict['c']]
                # labels[6].setText('{:-.2f} {:-.2%}'.format(zd, zd_p))  #涨跌
                labels[6].setText('{:-.2f}%'.format(row[self.colsDict['chg']]))
                labels[7].setText('{:-.2f}%'.format(row[self.colsDict['hsl']]))
                labels[8].setText('{:.2%}'.format(
                    (row[self.colsDict['h']] - row[self.colsDict['l']])/prev_row[self.colsDict['c']]))  # 振幅
        except Exception as e:
            print(f'118:{e}')
    def drawCrosslineWithInd(self, x):
        painter = QPainter(self)
        painter.setPen(Qt.DashLine)
        painter.drawLine(QPointF(x, self.topMarginheight), QPointF(
            x, self.RectY))
        self.update()

    def drawCrossline(self, painter):
        if(self.crossline and self.mousepos):
            painter.drawLine(QPointF(self.mousepos.x(), self.topMarginheight), QPointF(
                self.mousepos.x(), self.RectY))
            if self.mousepos.y()>=self.topMarginheight: #超出范围，不画横线
                painter.setPen(Qt.DashLine)
                painter.drawLine(QPointF(0, self.mousepos.y()), QPointF(
                    self.RectX, self.mousepos.y()))

    def createContextMenu(self):
        print('*'*30)
        '''''
        创建右键菜单
        '''
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        # 创建QMenu
        self.contextMenu = QMenu(self)
        self.addfavStock = self.contextMenu.addAction(
            QIcon("./icon/star.png"), '加自选')
        self.actionNext = self.contextMenu.addAction(
            QIcon("./icon/next.png"), 'Next')
        self.actionPre = self.contextMenu.addAction(
            QIcon("./icon/pre.png"), 'Pre')
        self.MainIndMenu = self.contextMenu.addMenu(
            QIcon("./icon/setting.png"), '主图指标')
        self.actionAddInd = self.MainIndMenu.addMenu(
            QIcon("./icon/setting.png"), '叠加')
        self.actionAddInd1 = self.actionAddInd.addAction(
            QIcon("images/0.png"), 'avolma')
        self.mainIndAddActLst.append(self.actionAddInd1)
        self.actionAddInd2 = self.actionAddInd.addAction(
            QIcon("images/0.png"), 'ma')
        self.mainIndAddActLst.append(self.actionAddInd2)
        self.chartStyleMenu = self.contextMenu.addMenu(
            QIcon("./icon/setting.png"), 'K线类型')
        self.chartStyle1 = self.chartStyleMenu.addAction('蜡烛图')
        self.chartStyle2 = self.chartStyleMenu.addAction('美国线')
        self.chartStyle1.triggered.connect(self.changeChartStyle)
        self.chartStyle2.triggered.connect(self.changeChartStyle)
        self.actionChgInd = self.MainIndMenu.addMenu(
            QIcon("./icon/setting.png"), '切换')
        self.realtimeAct = QAction('realtime')
        self.realtimeAct.setCheckable(True)
        self.actionChgInd.addAction(self.realtimeAct)
        self.actionRemoveInd = self.MainIndMenu.addMenu(
            QIcon("./icon/setting.png"), '移除')

        def creatAct(name):
            self.ActDict.update({name: self.actionAddInd.addAction(name)})
        self.ActDict = {}
        if len(self.arraydata):
            for i in [i for i in self.colsDict.keys()]:
                creatAct(i)
            for key, act in self.ActDict.items():
                act.triggered.connect(self.changeItem)
        # 添加二级菜单
        self.second = self.contextMenu.addMenu(QIcon("./icon/time.png"), "周期")
        self.actionPeriod1 = self.second.addAction(
            QIcon("images/0.png"), ' 1分')
        self.actionPeriod5 = self.second.addAction(
            QIcon("images/0.png"), ' 5分')
        self.actionPeriod15 = self.second.addAction(
            QIcon("images/0.png"), '15分')
        self.actionPeriod30 = self.second.addAction(
            QIcon("images/0.png"), '30分')
        self.actionPeriod60 = self.second.addAction(
            QIcon("images/0.png"), '60分')
        self.actionPeriodDay = self.second.addAction(
            QIcon("images/0.png"), '日线')
        self.actionPeriodMonth = self.second.addAction(
            QIcon("images/0.png"), '周线')
        self.actionPeriodWeek = self.second.addAction(
            QIcon("images/0.png"), '月线')
        self.actionPeriodQuater = self.second.addAction(
            QIcon("images/0.png"), '季线')
        self.actionPeriodYear = self.second.addAction(
            QIcon("images/0.png"), '年线')
        self.reTurn = self.second.addAction(QIcon("images/0.png"), '返回')
        self.actionNext.triggered.connect(self.update)
        self.actionPre.triggered.connect(self.update)
        self.actionPeriod1.triggered.connect(self.update)
        self.actionPeriod5.triggered.connect(self.update)
        self.actionPeriod15.triggered.connect(self.update)
        self.actionPeriod30.triggered.connect(self.update)
        self.actionPeriod60.triggered.connect(self.update)
        self.actionPeriodDay.triggered.connect(self.update)
        self.actionPeriodWeek.triggered.connect(self.update)
        self.actionPeriodMonth.triggered.connect(self.update)
        self.actionPeriodQuater.triggered.connect(self.update)
        self.actionPeriodQuater.triggered.connect(self.update)
        self.actionPeriodYear.triggered.connect(self.update)
        self.reTurn.triggered.connect(lambda: self.ChangeSLayoutSig.emit())

    def changeChartStyle(self):
        sender = self.sender()
        if sender.text() == '美国线':
            self.americK = True
            self.update()
        else:
            self.americK = False
            self.update()

    def changeItem(self):  # ,key):
        self.item = self.sender().text()
        self.lines.append(self.item)
        self.update()

    def showContextMenu(self, pos):
        ''''
        右键点击时调用的函数
        '''
        # 菜单显示前，将它移动到鼠标点击的位置
        self.contextMenu.exec_(QCursor.pos())  # 在鼠标位置显示

    def drawHelperline(self, painter):
        if(self.helperlinepos):
            pen = QPen(QColor(128, 128, 255))
            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            if(self.zoom > 0.3) & (self.helperlinepos.x()<self.chartwidth):
                painter.drawLine(QPointF(self.helperlinepos.x()-self.kwidth*0.45, self.topMarginheight), QPointF(
                    self.helperlinepos.x()-self.kwidth*0.45, self.RectY-self.bottomMarkHeight))
                painter.drawLine(QPointF(self.helperlinepos.x()+self.kwidth*0.45, self.topMarginheight), QPointF(
                    self.helperlinepos.x()+self.kwidth*0.45, self.RectY-self.bottomMarkHeight))
            elif (self.helperlinepos.x()<self.chartwidth):
                painter.drawLine(QPointF(self.helperlinepos.x(), self.topMarginheight), QPointF(
                    self.helperlinepos.x(), self.RectY-self.bottomMarkHeight))
            self.drawHelperlineFineshed.emit()

    def drawHelperlineAct(self, painter):
        pen = QPen(QColor(128, 128, 255))
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        if(self.zoom > 0.3) & (self.ind.mouseglobalpos.x()<self.chartwidth):
            painter.drawLine(QPointF(self.ind.mouseglobalpos.x()-self.kwidth*0.45, self.topMarginheight), QPointF(
                self.ind.mouseglobalpos.x()-self.kwidth*0.45, self.RectY-self.bottomMarkHeight))
            painter.drawLine(QPointF(self.helperlinepos.x()+self.kwidth*0.45, self.topMarginheight), QPointF(
                self.ind.mouseglobalpos.x()+self.kwidth*0.45, self.RectY-self.bottomMarkHeight))
        elif (self.ind.mouseglobalpos.x()<self.chartwidth):
            painter.drawLine(QPointF(self.ind.mouseglobalpos.x(), self.topMarginheight), QPointF(
                self.ind.mouseglobalpos.x(), self.RectY-self.bottomMarkHeight))
        self.drawHelperlineFineshed.emit()

    def indMouseMoveAct(self,x):
        self.ind = x

    def optimize(self):
        jsxgDlg = parameterSettingDlg.parameterSettingDlg()

class ChartFrame(chartBase):

    def __init__(self):
        # super(Chart,self).__init__()
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.Chart = Chart()
#        self.splitter = QSplitter(Qt.Vertical)
#        self.splitter.addWidget(self.Chart)
#        self.splitter.setStretchFactor(0,4)
#        self.splitter.setStretchFactor(1,1)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.addWidget(self.Chart)
        self.setLayout(hbox)
        self.setContentsMargins(0,0,0,0)
