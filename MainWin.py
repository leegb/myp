# cython: language_level=3
# -*- coding: utf-8 -*-


import sys
sys.path.insert(0,'/var/workspace/QUANTPI')



from modules.hqTable import hqTable
from basefunc import sleep, int2str, partial, call
from SystemDir import configure_dir, gdrs_dir
from SystemDir import baseinfodir, configure_dir, datadir, getpath
from SystemDir import configure_dir, datadir
import qdarkstyle
from dbConstant import dayDB
from tdx.getCode import initCodeDB
from tdx.gn import *
from basedata.hyinfo import hyinfo
from modules.load_histData import load_histData
from modules.metaMainWin import metaMainWin
from modules.tradeLoginDlg import tradeLoginDlg
from modules.dateDlg import dateDlg
from dfViewer.dataFrameViewer import dataFrameViewer
from TAFunc import c_pos, cac_return
from TA_arr import TA_arr as TA
#from download_histData import download_histData
from modules.TreeBase import TreeBase
from modules.TableWidget2TablePage import TableWidget2TablePage
from modules.stockHolderDlg import stockHolderDlg
from modules.select_color import select_color
from modules.GdrsDock import GdrsTree
from modules.dfTableWidget import dfTable
from modules.DDZZTable import DDZZTable
from modules.data2dfTable import data2dfTable
from modules import (chart, cmdedit, globals, init, kchartPageWin, netState,
                     output, parameterSettingDlg, scrollbar, searchLine, stock,
                     stockfilterresultdlg, stockinfodlg, stockwatchdlg,
                     tablePageWin, utils, getName)
from Jrj.radar import radar_jrj
from Dfcf.yjyg import yjyg
from Dfcf.yjbb import yjbb
from Dfcf.gn_dfcf import gn_dfcf
from Dfcf.dfcfxgq import dfcfXgq
from basefunc import normalizeStockCode
from async_gui.toolkits.pyqt import PyQtEngine
from async_gui.engine import Task
from async_gui import MultiProcessTask
import indicators
import numpy as np
from tools.pandas_util import pd
from PyQt5.QtWidgets import (QAbstractSlider, QAction, QApplication, QComboBox,
                             QDockWidget, QGridLayout, QMainWindow, QMenu,
                             QMessageBox, QShortcut, QStackedLayout, QPushButton,
                             QTableWidget, QTabWidget, QWidget, QFileDialog)
from PyQt5.QtGui import (QGuiApplication, QIcon, QKeySequence, QMovie,
                         QPalette, QPixmap, QWindow, QColor, QImage)
from PyQt5.QtCore import (QCoreApplication, Qt, QTextCodec, QThread, QTimer,
                          pyqtSignal, pyqtSlot, QUrl)
import PIL
import os
from tools import reportperiodlist
from StockPool import *
from dfcf_data.stock import dfcfHQdbUpdate
codelist2chartdict = dict(zip(range(len(all_stocklist)), all_stocklist))
all_codelist2chart = np.array(all_stocklist)
reverse_codelist2chartdict = dict(
    zip(all_stocklist, range(len(all_stocklist))))
engine = PyQtEngine()
ta = TA()




# from modules.hqTable import hqTable
# from basefunc import sleep, int2str, partial, call
# from SystemDir import configure_dir, gdrs_dir
# from SystemDir import baseinfodir, configure_dir, datadir, getpath
# from SystemDir import configure_dir, datadir
# import qdarkstyle
# from dbConstant import dayDB
# from tdx.getCode import initCodeDB
# from tdx.gn import *
# from basedata.hyinfo import hyinfo
# from modules.load_histData import load_histData
# from modules.metaMainWin import metaMainWin
# from modules.tradeLoginDlg import tradeLoginDlg
# #from StockPool import all_stocklist
# from modules.dateDlg import dateDlg
# from dfViewer.dataFrameViewer import dataFrameViewer
# from TAFunc import c_pos, cac_return
# from TA_arr import TA_arr as TA
# from download_histData import download_histData
# from modules.TreeBase import TreeBase
# from modules.TableWidget2TablePage import TableWidget2TablePage
# from modules.stockHolderDlg import stockHolderDlg
# from modules.select_color import select_color
# from modules.GdrsDock import GdrsTree
# from modules.dfTableWidget import dfTable
# from modules.DDZZTable import DDZZTable
# from modules.data2dfTable import data2dfTable
# from modules import (chart, cmdedit, globals, init, kchartPageWin, netState,
#                      output, parameterSettingDlg, scrollbar, searchLine, stock,
#                      stockfilterresultdlg, stockinfodlg, stockwatchdlg,
#                      tablePageWin, utils, getName)
# from Jrj.radar import radar_jrj
# from Dfcf.yjyg import yjyg
# from Dfcf.yjbb import yjbb
# from Dfcf.gn_dfcf import gn_dfcf
# from Dfcf.dfcfxgq import dfcfXgq
# from basefunc import normalizeStockCode
# #from basedata.gbinfo import gbinfo_client
# from async_gui.toolkits.pyqt import PyQtEngine
# from async_gui.engine import Task
# from async_gui import MultiProcessTask
# import indicators
# import numpy as np
# from tools.pandas_util import pd
# from PyQt5.QtWidgets import (QAbstractSlider, QAction, QApplication, QComboBox,
#                              QDockWidget, QGridLayout, QMainWindow, QMenu,
#                              QMessageBox, QShortcut, QStackedLayout, QPushButton,
#                              QTableWidget, QTabWidget, QWidget, QFileDialog)
# from PyQt5.QtGui import (QGuiApplication, QIcon, QKeySequence, QMovie,
#                          QPalette, QPixmap, QWindow, QColor, QImage)
# from PyQt5.QtCore import (QCoreApplication, Qt, QTextCodec, QThread, QTimer,
#                           pyqtSignal, pyqtSlot, QUrl)
# import PIL
# import os
# from tools import reportperiodlist
# from StockPool import *
# from dfcf_data.stock import dfcfHQdbUpdate
# #from PyQt5.QtWebEngineWidgets import QWebEngineView
# #import THS
# # sys._enablelegacywindowsfsencoding()
# #from Ntes.wget_ntes import wget_ohlc_ntes
# #from TA import TA
# #from tdxCW import tdxCW
# #from tdx.quotes_tdx import quotes_tdx
# # codelist=gbinfo().load().code.tolist()
# #from Stock.Data.Ui.DyStockDataMainWindow import DyStockDataMainWindow
# # from modules.stockInfo import stockinfoDict #顶部显示股票代码和名称
# #from load_histData import histData

# codelist2chartdict = dict(zip(range(len(all_stocklist)), all_stocklist))
# all_codelist2chart = np.array(all_stocklist)
# reverse_codelist2chartdict = dict(
#     zip(all_stocklist, range(len(all_stocklist))))
# engine = PyQtEngine()
# # hdf_file=pd.HDFStore('/mnt/work/QUANTPI_Data/ntesCsv')
# #histData = hdf_file.select('ntes',where="code == 1",auto_close=True)
# #initCodeDB()

# #use_db = True
# # if use_db:
# #    colDict = {}
# #    if dayDB.col:
# #        [colDict.update({col:idx}) for idx,col in enumerate(dayDB.col)]
# #        #[colDict.update({col:idx}) for idx,col in enumerate(dayDB.loadArray({'code':'0000001'}).dtype.names)]
# # else:
# #    from load_histData import histData
# #    colDict = {}
# #    [colDict.update({col:idx}) for idx,col in enumerate(histData.columns)]
# #onMarketDay = histData.groupby('code',as_index=False).date.count()
# #onMarketDayDict = dict(zip(int2str(onMarketDay['code']),onMarketDay['date']))
# # onMarketDayDict.update(zip(onMarketDay['code'],onMarketDay['date']))
# ta = TA()
class DataFetchThread(QThread):
    """
    后台线程用于加载股票数据，避免阻塞主线程。
    """
    dataFetched = pyqtSignal(object)
    errorOccurred = pyqtSignal(str)

    def __init__(self, stockcode, chart):
        super(DataFetchThread, self).__init__()
        self.stockcode = stockcode
        self.chart = chart  # 传递chart对象以便在线程中进行数据操作
        print(stockcode)

    def run(self):
        """
        执行数据加载的操作
        """
        try:
            # 在这里模拟耗时操作，实际操作应该是调用self.chart.ta.set_data(stockcode)
            print(f"Fetching data for stock: {self.stockcode}")
            #time.sleep(10)  # 模拟数据加载的延时
            self.chart.ta.set_data(self.stockcode)  # 假设这个操作是耗时的
            self.chart.stockcode = self.stockcode
            # self.chart.ta.TSI()
            # self.chart.ta.AVOLMA()
            # #self.chart.ta.DMI()
            print('finished')
            # 数据加载完成，发射信号给主线程
            self.dataFetched.emit(self.chart.ta.data)

        except Exception as e:
            self.errorOccurred.emit(str(e))  # 如果发生异常，发射错误信号
class MainWindow(metaMainWin):
    emitStockInfoSig = pyqtSignal(list)
    emitchartscrollbarSig = pyqtSignal(int)
    downloadSig = pyqtSignal()

    @engine._async
    def __init__(self):
        #super(dataFrameViewer, self).__init__()
        super(MainWindow, self).__init__()
        #super(dataFrameViewer, self).__init__()
        # self.setMinimumSize(QApplication.desktop().width()//1.01,QApplication.desktop().height()//1.11)
        # self.setStyleSheet("background-color:rgb(255,255,244),")
        self.curPid = None
        self.reportPeriodSelect()
        # self.createStatusBar()
        self.toolbarlst = []
        self.SLayoutWinlist = []
        self.itemList = []
        self.gnstocklist = None
        #self.Data2dfTable = data2dfTable()  #表格窗口
        # self.resize(desktop.width(),desktop.height()-80)
        # self.move(-10,-10)
        self.expandCount = 0
        self.prevSLayoutind = 1
        self.initLayout()
        self.initWidget()
        self.initActions()
        self.createMenus()
        try:
            self.boundSig() #连接信号
        except:
            pass
        self.showMaximized()
        self.codelist2chart = dict()
        self.initTablepageWin()
        # self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    def initWidget(self):
        self.searchBox = searchLine.searchLine(self)
        self.searchBox.setFocusPolicy(Qt.ClickFocus)
        self.itemList.append(self.searchBox)
        self.createDockWindows()
        pass
        # self.gdrstree = GdrsTree() 
        # try:
        #     self.gdrstree.setDataFrame(
        #         pd.read_hdf(getpath('gdrs/gdrs_2018-03-31')))
        # except:
        #     pass
        # self.gdrsWin.setWidget(self.gdrstree)
        # self.itemList.append(self.gdrstree)


    def initTablepageWin(self):
        pass
        #self.tablePageWin.addTable(name='zs_tdx', df=zs_tdx().parse()[:10])
        df=pd.DataFrame(np.random.randn(10, 5), columns=['A', 'B', 'C', 'D', 'E'])
        self.tablePageWin.addTable(name='zs_tdx', df=df)
        #self.tablePageWin.addTable(name='dfcf_stockHQ', df=dfcfHQdbUpdate()[['code','c','hsl']])
        
        
#        self.tablePageWin.addTable(name='业绩预告',df=yjyg().parse('2019-06-30'))
#        self.tablePageWin.addTable(name='行业分类',df=hyinfo().load())
#        self.tablePageWin.addTable(name='股东人数',df=pd.read_hdf(configure_dir(gdrs_dir,np.sort(os.listdir(gdrs_dir))[-1])))

    def changeToolbar(self):
        if self.SLayout.currentIndex() == 0:
            for toolbar, action in self.toolbarDict.items():
                for _action in action:
                    toolbar.removeAction(_action)
            self.prevSLayoutind = 0
        else:
            for toolbar, action in self.toolbarDict.items():
                self.addActions(toolbar, action)
            self.prevSLayoutind = 1

    def stockChangeEventHelp(self, stocklist, **kwargs):
        """
        按键切换股票
        """
        if len(stocklist):
            self.codelist2chart = stocklist
        else:
            self.codelist2chart = all_codelist2chart
            self.stockid = np.argwhere(
                all_codelist2chart == self.chart.stockcode)

    def setStockId(self, stockid):
        self.stockid = stockid

    def boundSig(self):
        for i in self.itemList:
            if hasattr(i, 'showChartSig'):
                i.showChartSig.connect(self.showStockChart)
            if hasattr(i, 'ChangeSLayoutSig'):
                i.ChangeSLayoutSig.connect(self.do_ChangeSLayout)
            if hasattr(i, 'printSig'):
                pass
            if hasattr(i, 'codelist2chartsig'):
                i.codelist2chartsig.connect(self.stockChangeEventHelp)
            if hasattr(i, 'stockIdsig'):
                i.stockIdsig.connect(self.setStockId)
        for i in self.chart.mainIndAddActLst:
            i.triggered.connect(self.mainIndicatorAddAct)
        self.chart.updateStockInfoTitleSig.connect(
            lambda date: self.stockinfodlg.setWindowTitle(date))
        self.chart.updateStockInfoSig.connect(lambda: self.chart.updateStockInfoDlg(
            self.stockinfodlg.labels))  # self.emitStockInfoSig.emit(self.stockinfodlg.labels))
        self.chart.scrollbarsetValueSig.connect(
            lambda x: lambda value: self.chartscrollbar.setValue(value))
        self.chart.scrollbartriggerSig.connect(self.chartscrobartriggerAct)
        self.chart.resetchartscrollbar.connect(self.resetScrollbar)
        self.chart.periodChanged.connect(self.updateChart_period)
        self.chart.showStockInfoDlgSig.connect(
            lambda: self.stockinfodlg.show())
        self.chart.handleDataUpdateSig.connect(
            lambda: self.chart.handleDataUpdate(self.chartscrollbar.value()))
#        self.chart.feedstockkdataSig.connect(
#            lambda x: self.feedstockdata(x[0]))
        self.chart.emitChartSig.connect(self.handle_emitchartSig)
        self.chart.drawHelperlineFineshed.connect(
            self.handle_drawHelperlineFineshed)
        self.emitchartscrollbarSig.connect(self.chart.handleDataUpdate)
        self.SLayout.currentChanged.connect(self.changeToolbar)
        self.drawingBTN.clicked.connect(self.selfdrawing)
        #self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin1.kchartPageWin_Bottom_Left.holerlineposx.connect(lambda x:self.chart.drawCrosslineWithInd(x))
        for i in range(self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin1.count()):
            self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin1.indDict[self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin1.tabText(
                i)].helpline_x_Sig.connect(lambda x: self.chart.drawCrosslineWithInd(x))
        for i in range(self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin2.count()):
            self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin2.indDict[self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin2.tabText(
                i)].helpline_x_Sig.connect(lambda x: self.chart.drawCrosslineWithInd(x))
#        self.right2.ChangeSearchboxFocusedSig.connect(lambda x:self.searchBox.setFocusPolicy(x[0]))
        # for i in self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWinlst:
        #     for j in i.indlist:
        #         j.ind_mouseMoveSig.connect(lambda x:self.chart.mouseMoveEventAct(x))
        self.SLayout.setCurrentIndex(0)  # 初始界面:数据表界面
        self.prevSLayoutind = 1

    def selfdrawing(self):
        if self.drawingBTN.isChecked():
            self.chart.canselfdrawing = True
            self.chart.update()
        else:
            self.chart.canselfdrawing = False
            self.chart.update()

    def mainIndicatorAddAct(self):
        a = self.sender()
        print(a.text())

    def showHtml(self):
        pass
        view = QWebEngineView()
        url_string = "file:///mnt/HDD/QUANTPI/render.html"
        view.load(QUrl(url_string))
        view.show()
# ind_mouseMoveSig

    @engine._async
    def handle_emitchartSig(self, data, *args):
        """
        副图指标
        """
        pass
#        funcs = [self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin2.Vol.setData,
#                 self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin1.Vol.setData,
#                 self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin1.kchartPageWin_Bottom_Left.setData,
#                 self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin2.kchartPageWin_Bottom_Left.setData,
#                 self.kchartPageWin.kchartPageWin_Top.kchartPageWin_Top_Right.kchartPageWin_Top_Right_chou.setData]

        funcs = [self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin1.indDict[self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin1.tabText(i)].setData for i in range(
            self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin1.count())]  # self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin1.currentIndex()
        funcs += [self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin2.indDict[self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin2.tabText(
            i)].setData for i in range(self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin2.count())]
        funcs += [self.kchartPageWin.kchartPageWin_Top.kchartPageWin_Top_Right.kchartPageWin_Top_Right_chou.setData]
        if len(args):
            for i in args:
                yield [Task(partial(_func, data), i) for _func in funcs]
        else:
            yield [Task(_func, data) for _func in funcs]

#        for _func in funcs:
#            _func(None)
        # self.kchartPageWin.kchartPageWin_Top.kchartPageWin_Top_Right.drawExLines()

    @engine._async
    def handle_drawHelperlineFineshed(self):
        pass
        funcs = [self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin2.Vol.drawHelperline,
                self.kchartPageWin.kchartPageWin_Bottom.IndWin.IndWin1.kchartPageWin_Bottom_Left.drawHelperline]
        yield [Task(_func,True) for _func in funcs]
        for _func in funcs:
            _func(None)

    def initLayout(self):
        self.initRootWin()
        self.kchartPageItem()
        self.tablePage()
        self.registerPageWinToSLayout()

    def initRootWin(self):
        self.RootWin = QWidget()  # 主窗口
        self.RootWin.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.RootWin)
        self.SLayout = QStackedLayout()  # 主窗口容器
        self.SLayout.setSpacing(0)
        self.SLayout.setContentsMargins(0, 0, 0, 0)
        # #对主窗口进行布局
        Gridbox = QGridLayout(self.RootWin)
        Gridbox.setSpacing(0)
        Gridbox.setContentsMargins(0, 0, 0, 0)
        Gridbox.addLayout(self.SLayout, 0, 0)

    def createDockWindows(self):
        self.gdrsWin = QDockWidget('股东人数')
        self.itemList.append(self.gdrsWin)
        self.gdrsWin.setContentsMargins(0, 0, 0, 0)
        # self.gdrsWin.setStyleSheet("background-color:rgb(225,222,179)")
        self.gdrsWin.setFeatures(
            QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable)
        self.gdrsWin.setUpdatesEnabled(True)
        self.gdrsWin.setAllowedAreas(Qt.AllDockWidgetAreas)
        #self.addDockWidget(Qt.LeftDockWidgetArea, self.gdrsWin)

    def kchartPageItem(self):
        self.kchartPageWin = kchartPageWin.kchartPageWin()  # K线显示界面
        self.softInfo = self.kchartPageWin.kchartPageWin_Bottom.kchartPageWin_Bottom_Right.kchartPageWin_Bottom_Right1
        #self.softInfo.info('begin')  # 程序运行信息
        self.SLayoutWinlist.append(self.kchartPageWin)
        self.chart = self.kchartPageWin.kchartPageWin_Top.kchartPageWin_Top_Left  # .Chart
        self.itemList.append(self.chart)
        self.chart.setMinimumSize(self.chart.width(), self.chart.height())
        self.chart.setBackgroundRole(QPalette.Base)
        self.chart.setMouseTracking(True)
        self.chart.setFocusPolicy(Qt.ClickFocus)  # StrongFocus
        self.chartscrollbar = scrollbar.ScrollBar(
            Qt.Horizontal, self.chart)  # K线窗口滚动条
        self.chartscrollbar.ScrollbarmousePressEvent.connect(self.updateChart)
        self.chartscrollbar.setMaximum(100000)
        self.chartscrollbar.setHidden(True)
        self.chartscrollbar.setMinimumWidth(1600)
        self.stockinfodlg = stockinfodlg.StockInfoDlg(
            self.chart)  # 交易日交易情况提示窗口
        self.itemList.append(self.stockinfodlg)
        self.showStockChart('000001')
    def tablePage(self):
        self.tablePageWin = dataFrameViewer(self)
        self.tablePageWin.setTabsClosable(True)
        self.itemList.append(self.tablePageWin)
        self.tablePageWin.setTabPosition(QTabWidget.South)
        self.tablePageWinItem = {}
        self.SLayoutWinlist.append(self.tablePageWin)
        self.tablePageWin.setContentsMargins(0, 0, 0, 0)
        #self.tablePageWin.setStyleSheet("background-color:rgb(255,250,234)")
        #self.registerDfTable(['dfcf', 'gdrs'])

    def putData(self, i):
        print(self.sender().tabText(i))
        self.Data2dfTable.setData(self.sender().tabText(i))

    def registerPageWinToSLayout(self):
        """
        添加窗口
        """
        pass
        for win in self.SLayoutWinlist:
            self.SLayout.addWidget(win)

    def chartscrobartriggerAct(self):
        self.chartscrollbar.triggerAction(QAbstractSlider.SliderToMaximum)

    @pyqtSlot()
    def do_ChangeSLayout(self):
        if (self.prevSLayoutind == 1) & (self.chart.stockcode == None):
            self.showStockChart('600000')
        else:
            self.prevSLayoutind = int(np.mod(self.prevSLayoutind+1, 2))
            self.SLayout.setCurrentIndex(self.prevSLayoutind)
            self.changeToolbar()
        if self.prevSLayoutind != 0:
            self.stockinfodlg.close()

    def updateChart(self):
        self.chart.crossline = False
        self.chart.mousepos = None
        self.chart.update()

    @pyqtSlot(int, int)
    def resetScrollbar(self, kdatalenth, Flags):
        # super(chart.Chart).__init__()
        if Flags == 1:
            self.chartscrollbar.setMaximum(kdatalenth)
        elif Flags == 2:
            self.chartscrollbar.setMinimum(kdatalenth)
        elif Flags == 3:
            self.chartscrollbar.setPageStep(kdatalenth)
        elif Flags == 4:
            self.chartscrollbar.triggerAction(
                QAbstractSlider.SliderSingleStepSub)
        elif Flags == 5:
            self.chartscrollbar.triggerAction(
                QAbstractSlider.SliderSingleStepAdd)
        elif Flags == 6:
            self.chartscrollbar.triggerAction(
                QAbstractSlider.SliderPageStepSub)
        elif Flags == 7:
            self.chartscrollbar.triggerAction(
                QAbstractSlider.SliderPageStepAdd)

    def reportPeriodSelect(self):
        self.periodSelect = QComboBox()
        self.periodSelect.setMaximumHeight(100)
        self.periodSelect.setMinimumHeight(20)
        self.periodSelect.setHidden(True)
        self.periodSelect.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        #self.periodSelect.currentIndexChanged.connect(self.periodChanged)
        periodlist = reportperiodlist()
        periodlist.reverse()
        self.periodSelect.addItems(periodlist)

    def windowStockFilterResult(self):
        pass
#        self.stockfilterresultdlg.show()
#        self.stockfilterresultdlg.activateWindow()

    def windowWatchListDlg(self):
        self.stockwatchdlg.show()
        self.stockwatchdlg.activateWindow()

    def onDockListIndexChanged(self, index):  # 左侧导航栏
        item = self.NaviItems[index]
        self.right2.info(item)

    def connectTradecenter(self):
        tradeLoginDlg(self).show()

    def connectHqHost(self):
        QWidget(None, Qt.SplashScreen)
#    def contextMenuEvent(self):
#        pass

    def normalizeStockCode(self, stock_code):
        if isinstance(stock_code, (int, float)):
            stock_code = str(stock_code)
        if len(stock_code) < 6:
            padlen = 6 - len(stock_code)
            padlist = []
            for i in range(0, padlen):
                padlist.append('0')
            padstr = ''.join(padlist)
            stock_code = padstr + stock_code
        return stock_code

    def showStockChart(self, stockcode, **kwargs):
        #self.searchBox.clear()
        self.stockinfodlg.close()
        if isinstance(stockcode, list):
            stockcode = stockcode[0]
        if isinstance(stockcode, (str, float, int)):
            stockcode = self.normalizeStockCode(stockcode)
        if (self.chart.stockcode == stockcode) & (stockcode != '000001'):
            if self.SLayout.currentIndex() == 1:
                self.do_ChangeSLayout()
        else:
            self.chart.prestockcode = self.chart.stockcode
            self.chart.reset_chart()
            self.chart.stockcode = stockcode
            self.chart.periodSelect.setVisible(True)
            self.chart.periodSelect.setCurrentIndex(0)
            #taarr
            self.chart.ta = TA()
            #self.chart.ta.setDataFrameByCode(stockcode, fq=1)
           #self.chart.ta.set_data(stockcode)
            # 启动后台线程获取数据
            self.dataThread = DataFetchThread(stockcode, self.chart)
            self.dataThread.dataFetched.connect(self.update_chart_data)
            self.dataThread.errorOccurred.connect(self.handle_error)
            self.dataThread.start()  # 启动线程




    def update_chart_data(self, data):
        """更新图表数据"""
        if len(self.chart.ta.data):
            #            if self.chart.ta.dataprepared:
            #                if len(self.codelist2chart) == 0:
            #                    self.codelist2chart = codelist2chartdict
            #                    self.stockid = reverse_codelist2chartdict[self.chart.stockcode]
            #                else:
            #                    self.stockid = reverse_codelist2chartdict[self.chart.stockcode]
            self.chart.ta.multicode = False
            self.chart.ta.TSI()
            self.chart.ta.AVOLMA()
            self.chart.ta.DMI()
            # self.chart.ta.BuyOrSell()
            # self.chart.ta.toDisp()
#            c_pos(self.chart.ta.data)
            self.chart.resourceData = self.chart.ta.data
#            self.chart.resourceData.index = self.chart.resourceData.date
            self.chart.resourceData['涨跌比率'] = 0
#            self.chart.resourceData.update(zdbl)
            # self.chart.ta.toDisp()
#                for i in ['c', 'h', 'l', 'o', 'yc', 'avgp', 'avolma']:
#                    self.chart.ta.data[i] = np.log2(self.chart.ta.data[i])
            if not hasattr(self.chart.ta.data, 'avolma'):
                self.chart.ta.data['avolma'] = np.nan
            self.chart.ta.data[['c', 'h', 'l', 'o', 'yc', 'avgp', 'avolma']] = np.log2(
                self.chart.ta.data[['c', 'h', 'l', 'o', 'yc', 'avgp', 'avolma']])
            self.chart.arraydata = np.asarray(self.chart.ta.data)
            #self.chart.kdata = self.chart.ta.kdata
            # dict(zip(self.chart.ta.data.columns,range(len(self.chart.ta.data.columns))))
            self.chart.colsDict = self.chart.ta.colDict
            #self.chart.arraydata[:,self.colsDict['avolma']] = self.chart.arraydata[:,self.colsDict['avolma']].astype(np.int)
            self.chartscrollbar.setMinimum(0)
            ktotalcount = len(self.chart.arraydata)
            self.chartscrollbar.setMaximum(ktotalcount)
            self.chartscrollbar.setValue(ktotalcount)
            self.chartscrollbar.setSingleStep(10)
            globals.viewportclear = False
            #self.chart.mainIndicator = indicators.Avolma.Avolma(['avolma'])
#                self.chart.indicators = [indicators.amo.Amo(
#                ), indicators.macd.Macd(), indicators.kd.Kd()]
            self.chart.update()
            # if self.gdrsWin.isVisible():
            #     self.gdrsWin.setVisible(True)
            if self.SLayout.currentIndex() != 0:
                self.do_ChangeSLayout()
            self.chart.maintitle = [
                {'x': 5, 'y': 15, 'text': getName.getName(self.chart.stockcode), 'color': QColor(0, 0, 0)}]
#                self.rt_timer = QTimer()
#                self.rt_timer.setInterval(3000)
#                self.rt_timer.timeout.connect(self.rt_chart)
#                self.rt_timer.start()
        else:
            self.softInfo.info(stockcode+'  数据缺失')
            self.showStockChart('000001')

    def handle_error(self, error_message):
        """处理后台线程中的错误"""
        QMessageBox.warning(self, "错误", f"加载数据时发生错误：{error_message}")
        self.softInfo.info(f"错误：{error_message}")
    def rt_chart(self):
        try:
            self.chart.ta.updateData()
            self.chart.ta.TSI()
            self.chart.ta.AVOLMA()
            self.chart.ta.BuyOrSell()
            # self.chart.ta.toDisp()
    #            c_pos(self.chart.ta.data)
            self.chart.resourceData = self.chart.ta.data
    #            self.chart.resourceData.index = self.chart.resourceData.date
            self.chart.resourceData['涨跌比率'] = 0
    #            self.chart.resourceData.update(zdbl)
            # self.chart.ta.toDisp()
    #                for i in ['c', 'h', 'l', 'o', 'yc', 'avgp', 'avolma']:
    #                    self.chart.ta.data[i] = np.log2(self.chart.ta.data[i])
            self.chart.ta.Data[['c', 'h', 'l', 'o', 'yc', 'avgp', 'avolma']] = np.log2(
                self.chart.ta.Data[['c', 'h', 'l', 'o', 'yc', 'avgp', 'avolma']])
            self.chart.arraydata = np.array(self.chart.ta.Data)
            #self.chart.kdata = self.chart.ta.kdata
            # dict(zip(self.chart.ta.data.columns,range(len(self.chart.ta.data.columns))))
            self.chart.colsDict = self.chart.ta.colDict
            #self.chart.arraydata[:,self.colsDict['avolma']] = self.chart.arraydata[:,self.colsDict['avolma']].astype(np.int)
            self.chartscrollbar.setMinimum(0)
            ktotalcount = len(self.chart.arraydata)
            self.chartscrollbar.setMaximum(ktotalcount)
            self.chartscrollbar.setValue(ktotalcount)
            self.chartscrollbar.setSingleStep(10)
            globals.viewportclear = False
            #self.chart.mainIndicator = indicators.Avolma.Avolma(['avolma'])
    #                self.chart.indicators = [indicators.amo.Amo(
    #                ), indicators.macd.Macd(), indicators.kd.Kd()]
            self.chart.update()
            if self.gdrsWin.isVisible():
                self.gdrsWin.setVisible(True)
            if self.SLayout.currentIndex() != 0:
                self.do_ChangeSLayout()
            self.chart.maintitle = [{'x': 5, 'y': 15, 'text': getName.getName(
                self.chart.ta.code), 'color': QColor(0, 0, 0)}]
        except:
            pass

    def do_loadData(self, *args):
        #暂时未使用
        self.loadData = load_histData()
        self.dataThd = QThread()
        self.loadData.moveToThread(self.dataThd)
        self.dataThd.started.connect(lambda: self.loadData.load())

    def prepare_stockData(self):
        print('m'*30)
        if len(self.chart.ta.data):
            self.chart.ta.toDisp()
            self.chart.ta.multicode = False
            self.chart.ta.data['avolma'] = np.nan
            self.chart.ta.tsiArr = np.zeros(len(self.chart.ta.data))
#            self.chart.ta.TSI()
#            self.chart.ta.AVOLMA()
#            self.chart.ta.BuyOrSell()
    #            c_pos(self.chart.ta.data)
    #            self.chart.resourceData.index = self.chart.resourceData.date
#            self.chart.resourceData['涨跌比率'] = 0
    #            self.chart.resourceData.update(zdbl)
            # self.chart.ta.toDisp()
            self.chart.arraydata = np.asarray(self.chart.ta.data)
            #self.chart.kdata = self.chart.ta.kdata
            self.chart.colsDict = dict(
                zip(self.chart.ta.data.columns, range(len(self.chart.ta.data.columns))))
            #self.chart.arraydata[:,self.colsDict['avolma']] = self.chart.arraydata[:,self.colsDict['avolma']].astype(np.int)
            self.chartscrollbar.setMinimum(0)
            ktotalcount = len(self.chart.arraydata)
            self.chartscrollbar.setMaximum(ktotalcount)
            self.chartscrollbar.setValue(ktotalcount)
            self.chartscrollbar.setSingleStep(10)
            globals.viewportclear = False
            self.chart.update()
            if self.gdrsWin.isVisible():
                self.gdrsWin.setVisible(True)
            if self.SLayout.currentIndex() != 0:
                self.do_ChangeSLayout()

    @pyqtSlot(int)
    def updateChart_period(self, period):
        try:
            if period == 0:  # 日线
                self.chart.resourceData = self.chart.viewData.dayData()
            elif period == 1:  # 周
                self.chart.resourceData = self.chart.ta.toWeek()
            elif period == 2:  # 月
                self.chart.resourceData = self.chart.ta.toMonth()
                # self.chart.reset_chart()
                #self.chart.ta = TA()
                # self.chart.ta.set_df(data)
                # self.prepare_stockData()
            elif period == 3:
                self.chart.resourceData = self.chart.viewData.quarterData()
            elif period == 4:
                self.chart.resourceData = self.chart.viewData.quarterData()
            elif period == 5:
                self.chart.resourceData = self.chart.viewData.yearData()
#            self.chart.resourceData.index = self.chart.resourceData.date
#            self.chart.resourceData['涨跌比率'] = 0
#            # self.chart.resourceData.update(zdbl)
#
#            self.chart.periodSelect.setVisible(True)
#            self.chart.normalizeKdata()
#            self.chartscrollbar.setMinimum(0)
#            ktotalcount = len(self.chart.kdata)
#            self.chartscrollbar.setMaximum(ktotalcount)
#            self.chartscrollbar.setValue(ktotalcount)
#            self.chartscrollbar.setSingleStep(10)
#            #globals.viewportclear =True
#            self.chart.mainIndicator = indicators.volma.Volma(
#                [20, 50, 245, 3*245])
#            self.chart.indicators = [indicators.amo.Amo(
#            ), indicators.macd.Macd(), indicators.kd.Kd()]
#            self.chart.update()
#            self.chart.activateWindow()
#            self.gdrsWin.setVisible(False)
        except Exception as e:
            self.softInfo.info(e)

    @pyqtSlot(list)
    def feedstockdata(self, oneindicator):
        chart = self.chart
        if(not oneindicator.chart):
            oneindicator.chart = chart
            kdata = chart.kdata
        if(globals.realtime):
            #kdata = chart.kdata[-1000:]
            pass
        if(globals.realtime or (oneindicator.stockcode != chart.stockcode)):
            oneindicator.stockcode = chart.stockcode
            #oneindicator.data = oneindicator.calculateData(kdata)
            oneindicator.data = {'avolma': list(
                self.chart.resourceData['avolma'])}

    def createStatusBar(self):
        self.statusBar().showMessage('Ready')

    def initActions(self):
        #        def createAction(self, text, slot = None, shortcut = None, icon = None,
        #                         tip = None, checkable = False, signal = "triggered()"):
        ## Actions and shortcuts for mainwindow##################################

#        self.quitAct = QAction('&关闭', self, triggered=lambda: self.close())
#        self.quitAct.setShortcuts()
#        self.quitAct.setStatusTip('关闭软件')
        self.quitAct = self.createAction(
            '关闭', slot=self.close, shortcut=QKeySequence('Alt+Q'), tip="关闭软件")        
        self.quitAct.setIcon(QIcon(QPixmap('./icon/shutdown.png')))
        
        self.dateSelectAct = QAction('dateSelect', self)
        self.dateSelectAct.triggered.connect(self.dateSelect)
        
        
        self.reportPeriodSelectAct = QAction('reportSelectPeriod', self)
        self.reportPeriodSelectAct.triggered.connect(self.reportPeriodSelect)
        
        
        self.stockInfoAct = QAction(
            '&交易简况', self, triggered=lambda: self.stockinfodlg.show())
        self.stockInfoAct.setShortcuts(QKeySequence('Alt+I'))
        
        
        self.windowStockFilterResultAct = QAction(
            '&数据筛选', self, triggered=self.windowStockFilterResult)
        self.windowStockFilterResultAct.setShortcuts(QKeySequence('Ctrl+F'))
        self.windowWatchListAct = QAction(
            '&列表', self, triggered=self.windowWatchListDlg)
        self.windowWatchListAct.setShortcuts(QKeySequence('Ctrl+W'))
        self.colorsetAct = QAction('&颜色', self, triggered=select_color)
        
        # self.ntes_update = download_histData()
        # self.thd = QThread()
        # self.ntes_update.moveToThread(self.thd)
        # if not self.ntes_update.working:
        #     # self.ntes_update.download)
        #     self.thd.started.connect(self.downloadUI)
        # self.ntesdownloadAct = QAction(
        #     '&下载网易日线', self, triggered=self.thd.start)
        self.ntesupdateAct = QAction(
            '&预留', self, triggered=self.about)
        self.aboutAct = QAction('&系统版本', self, triggered=self.about)
        # self.showblockDfcfAct = QAction(
        #     '东方财富', self, triggered=lambda: self.naviDock.show())  # 左侧导航栏
#        self.showblockThsAct=QAction('同花顺', self, triggered=self.shownaviDock)  #左侧导航栏
#        self.showblockTdxAct=QAction('通达信', self, triggered=self.shownaviDock)  #左侧导航栏
#        self.showblockSseAct=QAction('证监会', self, triggered=self.shownaviDock)  #左侧导航栏
        self.hqAct = QAction(
            '全部A股', self, triggered=self.hqFunc)
        self.phfxAct = QAction(
            '盘后分析', self, triggered=self.phfx)
        self.connectTradecenterAct = QAction(
            '交易连接', self, triggered=self.connectTradecenter)
        self.connectTradecenterAct.setIcon(QIcon(QPixmap('./icon/trade.png')))
        self.connectTradecenterAct.setIconText('交易连接')
        self.connectHqHostAct = QAction(
            '行情连接', self, triggered=self.connectHqHost)
#        self.searchAct = QAction('搜索', self, triggered=self.search)
#        self.searchAct.setIcon(QIcon(QPixmap('./icon/explorer.png')))
        jsxgDlg = parameterSettingDlg.parameterSettingDlg()
        self.jsxgAct = QAction('技术选股', self, triggered=lambda: jsxgDlg.show())
        data = np.array(PIL.Image.open('./icon/jsxg.png'))
        # (QIcon(QPixmap('./icon/jsxg.png')))
        self.jsxgAct.setIcon(QIcon(self.pil2pixmap('./icon/jsxg.png')))
        self.jsxgAct.setToolTip('技术选股')
        self.top10Holder = QAction(
            '十大股东', self, triggered=self.showHtml)
        self.btn = QAction(
            'info', self, triggered=lambda: stockHolderDlg().excute(self.chart.stockcode))
        self.btn.setIcon(QIcon(QPixmap('./icon/jsxg.png')))
        self.btn.setToolTip('info')
        data = np.array(PIL.Image.open('./icon/add.jpeg'))
        self.btn.setIcon(
            QIcon(QPixmap(QImage(data, data.shape[0], data.shape[1], QImage.Format_RGB32))))
        
        
        ## Actions and shortcuts for table(s)##################################
        self.fileNewAction = self.createAction(
            "&新建", self.tablePageWin.fileNew, QKeySequence.New, "filenew", "Create a file")
        self.fileOpenAction = self.createAction("&打开...", self.tablePageWin.fileOpen,
                                                QKeySequence.Open, "fileopen",
                                                "Open an existing file")
        self.fileSaveAction = self.createAction("&保存", self.tablePageWin.fileSave,
                                                QKeySequence.Save, "filesave", "Save the file")
        self.fileSaveAsAction = self.createAction("保存&为...",
                                                  self.tablePageWin.fileSaveAs, icon="filesaveas",
                                                  tip="Save the file using a new filename")
        self.fileSaveAllAction = self.createAction("全部保存",
                                                   self.tablePageWin.fileSaveAll, icon="filesave",
                                                   tip="Save all the files")
        self.fileCloseTabAction = self.createAction("Close &Tab",
                                                    self.tablePageWin.fileCloseTab, QKeySequence.Close, "filequit",
                                                    "Close the active tab")
        self.fileQuitAction = self.createAction("&Quit", self.tablePageWin.close,
                                                "Ctrl+Q", "filequit", "Close the application")
        self.editEditableAction = self.createAction("E&ditable",
                                                    self.tablePageWin.enableEditing, icon="document-edit", checkable=True,
                                                    signal="toggled(bool)")
        self.editAddRowAction = self.createAction("Add Row", self.tablePageWin.addRow,
                                                  icon='edit-table-insert-row-below', tip="Add a new row")
        self.editAddColAction = self.createAction("Add Column",
                                                  self.tablePageWin.showAddColumnDialog, icon='edit-table-insert-column-right',
                                                  tip="Add a new column")
        self.editDelRowAction = self.createAction("Delete Row", self.tablePageWin.removeRow,
                                                  icon='edit-table-delete-row', tip="Delete a row")
        self.editDelColAction = self.createAction("Delete Column",
                                                  self.tablePageWin.showRemoveColumnDialog, icon='edit-table-delete-column',
                                                  tip="Delete a column")
        self.editUndoAction = self.createAction("Undo", self.tablePageWin.undoChange,
                                                shortcut='Ctrl+Z', icon='previous', tip="Undo last action")
        self.editRedoAction = self.createAction("Redo", self.tablePageWin.redoChange,
                                                shortcut='Ctrl+Y', icon='next', tip="Redo last action")
        self.mergeAction = self.createAction("Merge DataFrames",
                                             self.tablePageWin.showMergeDialog, icon='merge', tip="Merge Dataframes")
        self.groupByAction = self.createAction("聚合", self.tablePageWin.showGroupDialog,
                                               icon="group", tip="聚合")
        self.graphAction = self.createAction("画图",
                                             self.tablePageWin.showGraphDialog, icon="graph", tip="画图")
        self.describeAction = self.createAction("Describe Data",
                                                self.tablePageWin.showDescribeDialog, icon="describe", tip="Describe Data")
        QShortcut(QKeySequence.PreviousChild, self, self.tablePageWin.prevTab)
        QShortcut(QKeySequence.NextChild, self, self.tablePageWin.nextTab)
        self.tablePageWin.tabCloseRequested.connect(
            self.tablePageWin.fileCloseTab)
        #### end tablePageWin
        
        
        self.editEditableAction.setChecked(False)
        self.editAddRowAction.setEnabled(False)
        self.editAddColAction.setEnabled(False)
        self.editDelRowAction.setEnabled(False)
        self.editDelColAction.setEnabled(False)
        self.editUndoAction.setEnabled(False)
        self.editRedoAction.setEnabled(False)

        self.fullscreenAct = QAction('全屏显示', self, triggered=self.FullScreen)
        self.exitfullscreenAct = QAction(
            '退出全屏', self, triggered=self.exitFullScreen)
        self.drawingBTN = QPushButton('画线', self)
        self.drawingBTN.setCheckable(True)
        self.toolbar1 = self.addToolBar('组1')
        self.toolbar1.addAction(self.quitAct)
        self.toolbar1.addAction(self.connectTradecenterAct)
        self.toolbar1.addAction(self.connectHqHostAct)
        self.toolbar1.setContentsMargins(0, 0, 0, 0)
        self.toolbar1.addAction(self.fullscreenAct)
        self.toolbar1.addWidget(self.drawingBTN)
        self.toolbar1.addAction(self.phfxAct)
        self.toolbar3 = self.addToolBar('组3')
        self.toolbar3.addAction(self.jsxgAct)
        self.toolbar3.addAction(self.btn)
        self.toolbar3.addWidget(self.periodSelect)
        self.toolbar3.addAction(self.top10Holder)
        self.toolbar3.setContentsMargins(0, 0, 0, 0)
        self.toolbar2 = self.addToolBar('组2')
        self.toolbar2.setContentsMargins(0, 0, 0, 0)
        #self.toolbar2.addWidget(self.searchBox)
        self.toolbar2.addWidget(self.periodSelect)
        self.toolbar2.setContentsMargins(0, 0, 0, 0)
#        combox = QComboBox()
#        combox.addAction(self.aboutAct)
#        combox.addAction(self.filedlgAct)
#        self.toolbar1.addWidget(combox)
        # lambda:self.showFullScreen())
#        status = self.statusBar()
#        status.setSizeGripEnabled(False)
#        status.showMessage("Ready", 5000)

    def pil2pixmap(self, file_path):
        im = PIL.Image.open(fp=file_path)
        if im.mode == "RGB":
            pass
        elif im.mode == "L":
            im = im.convert("RGBA")
        data = im.tobytes('raw', "RGBA")
        qim = QImage(data, im.size[0], im.size[1], QImage.Format_ARGB32)
        pixmap = QPixmap.fromImage(qim)
        return pixmap

    def hqFunc(self):
        self.tablePageWin.addTable(name='沪深A股', df=hqTable(code=all_stocklist))

    def phfx(self):
        pass
#         from Jrj.quotes_jrj import quotes_jrj
#         df = quotes_jrj().parse()
# #        if 'code' in df.columns:
# #            df['上市天数'] = df['code'].map(onMarketDayDict)
#         self.tablePageWin.addTable(name='盘后分析', df=df)

    @engine._async
    def ntesdownload(self):
        yield Task(hist_ntes().download())

    def downloadUI(self):
        pass
        # DyStockDataMainWindow().show()

    def change_pageBtn(self):
        if self.SLayout.currentIndex() == 0:
            pass

    def _close(self):
        call('nohup kill -15 %s >/dev/null 2>log' % os.getpid(), shell=True)

    def dfcfgnActFunc(self):
        # 东方财富分类
        self.tablePageWin.addTable(
            name='东方财富板块', df=pd.read_hdf('dfcfgn'), table_category='x')

    def createMenus(self):
        #        self.fileMenu = self.menuBar().addMenu('&文件')
        #        self.fileMenu.addAction(self.quitAct)
        #        self.fileMenu_sub1 = self.fileMenu.addMenu(
        #            QMenu('Import', self))  # 添加三级菜单
        #        self.fileMenuOpenFile = self.fileMenu.addMenu(QMenu('打开文件', self))
        #        self.fileMenuOpenFile.triggered.connect(self.about)
        #        self.fileMenu.addAction(self.filedlgAct)
        self.windowMenu = self.menuBar().addMenu('&窗口')
        self.windowMenu.addAction(self.stockInfoAct)
        self.windowMenu.addAction(self.windowStockFilterResultAct)
        self.windowMenu.addAction(self.windowWatchListAct)
        self.dataMenu = self.menuBar().addMenu('&数据管理')
        #self.dataMenu.addAction(self.ntesdownloadAct)
        self.dataMenu.addAction(self.ntesupdateAct)
        self.naviMenu = self.menuBar().addMenu('&板块')
        self.gn_blockMenu = self.naviMenu.addMenu('&概念')
        self.gn_blockMenu.addAction(QAction(
            '&东方财富', self, triggered=self.dfcfgnActFunc))
        self.hy_blockMenu = self.naviMenu.addMenu('&行业')
#        self.hy_blockMenu.addAction(self.showblockSseAct)
#
        self.radarMenu = self.menuBar().addMenu('&雷达')
        self.hqMenu = self.menuBar().addMenu('&行情浏览')
        self.hqMenu.addAction(self.hqAct)
        self.setupMenu = self.menuBar().addMenu('&设置')
        self.setupMenu.addAction(self.dateSelectAct)
        self.setupMenu.addAction(self.colorsetAct)
        self.setupMenu.addAction(self.ntesupdateAct)
        self.helpMenu = self.menuBar().addMenu('&帮助')
        self.helpMenu.addAction(self.aboutAct)
        self.fileMenu = self.menuBar().addMenu("&File")
        self.editMenu = self.menuBar().addMenu("&Edit")
        self.dataMenu = self.menuBar().addMenu("&Data")
        self.graphMenu = self.menuBar().addMenu("&Graph")
        self.addActions(self.fileMenu, (self.fileNewAction, self.fileOpenAction,
                                        self.fileSaveAction, self.fileSaveAsAction, self.fileSaveAllAction,
                                        self.fileCloseTabAction, None, self.fileQuitAction))
        self.addActions(self.editMenu, (self.editEditableAction, self.editAddRowAction,
                                        self.editAddColAction, self.editDelRowAction, self.editDelColAction,
                                        None, self.editUndoAction, self.editRedoAction))
        self.addActions(self.dataMenu, (self.mergeAction, self.groupByAction,
                                        self.describeAction))
        self.addActions(self.graphMenu, (self.graphAction,))
#        self.addActions(self.toolbar1, (self.fileNewAction, self.fileOpenAction,
#                                      self.fileSaveAction))
        self.addActions(self.toolbar2, (self.tablePageWin.fillNaNAction, self.tablePageWin.updateHQAction))
        self.toolbarDict = {self.toolbar2: [self.tablePageWin.fillNaNAction, self.tablePageWin.fillNaNAction,
                                            self.tablePageWin.fillNaNAction, self.tablePageWin.fillNaNAction, self.tablePageWin.updateHQAction]}

    def FullScreen(self):
        self.showFullScreen()
        self.toolbar1.removeAction(self.fullscreenAct)
        self.toolbar1.addAction(self.exitfullscreenAct)

    def exitFullScreen(self):
        self.showMaximized()
        self.toolbar1.removeAction(self.exitfullscreenAct)
        self.toolbar1.addAction(self.fullscreenAct)

    def about(self):
        QMessageBox.about(self, '金黔投资',
                          "金黔投资出品\ncopyright 2016-2030"
                          )
    # @engine._async

    def closeEvent(self, event):
        if utils.confirm(self, '是否重启？', 'Quit'):
            call('kill %s & nohup /usr/bin/sh QUANTPI.sh >/dev/null 2>log' %
                 self.curPid, shell=True)
            event.accept()
#            self.stockinfodlg.close()
#            if self.ntes_update.working:
#                if utils.confirm(self, '网易数据更新未完成，强制退出？', 'Quit'):
#                    event.accept()
#            else:
#                event.ignore()
        else:
            event.accept()
            # event.accept()

    def setcodelist2chart(self, codelist):
        self.codelist2chart = codelist

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        key = event.key()
        if len(self.codelist2chart) == 0:
            self.codelist2chart = all_codelist2chart
            self.stockid = np.argwhere(
                all_codelist2chart == self.chart.stockcode)
            if len(self.stockid):
                self.stockid = self.stockid[0, 0]
        if (key == Qt.Key_N) & (len(self.codelist2chart) > 0):
            self.stockid += 1
            try:
                if self.stockid == (len(self.codelist2chart)-1):
                    self.showStockChart(self.codelist2chart[self.stockid])
                    self.stockid = -1
                else:
                    self.showStockChart(self.codelist2chart[self.stockid])
            except:
                if self.stockid == (len(self.codelist2chart)-1):
                    self.stockid = -1
        elif (key == Qt.Key_B) & (len(self.codelist2chart) > 0):
            self.stockid -= 1
            try:
                if self.stockid < 0:
                    self.showStockChart(self.codelist2chart[self.stockid])
                    self.stockid = len(self.codelist2chart)-1
                else:
                    self.showStockChart(self.codelist2chart[self.stockid])
            except:
                if self.stockid < 0:
                    self.stockid = len(self.codelist2chart)-1

    def CheckNetState(self):
        self.netState = netState.netState()
        self.netState.netStateSig.connect(self.StatusBarMessageShow)
        self.netStateThread = QThread()
        self.netState.moveToThread(self.netStateThread)
        self.netStateThread.started.connect(self.netState.checkNetstate)

    def WeChartInfo(self, messages):
        pass

    def StatusBarMessageShow(self, text):
        self.statusBar().showMessage(text)

    def dateSelect(self):
        _dateDlg = dateDlg(data=dict(), parent=self)
        _dateDlg.show()

    def wheelEvent(self, event):
        super().wheelEvent(event)
        if self.SLayout.currentIndex() == 0:
            y = event.angleDelta().y()
            self.chart.wheelEventAct(y)
    def mouseMoveEvent(self, x,y):
        super().mouseMoveEvent(event)
        if self.SLayout.currentIndex() == 0:
            self.chart.mouseMoveEventAct(event.globalPos().x(),event.globalPos().y())


# if __name__ == '__main__':
#     try:
#         #ta = TA(histData)
#         ta = TA()
#     except:
#         from load_histData import histData
#         ta = TA(histData)
#     QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
#     app = QApplication(sys.argv)
#     engine.main_app = app
#     # app.setStyle("fusion")
#     pic = {1: QPixmap('/mnt/HDD/QUANTPI/icon/buy.png', "0", Qt.AvoidDither | Qt.ThresholdDither | Qt.ThresholdAlphaDither), 2: QPixmap("/mnt/HDD/QUANTPI/icon/sell.png", "0", Qt.AvoidDither | Qt.ThresholdDither | Qt.ThresholdAlphaDither),
#           3: QPixmap('/mnt/HDD/QUANTPI/icon/minus.png', "0", Qt.AvoidDither | Qt.ThresholdDither | Qt.ThresholdAlphaDither), 4: QPixmap('/mnt/HDD/QUANTPI/icon/minus.png', "0", Qt.AvoidDither | Qt.ThresholdDither | Qt.ThresholdAlphaDither)}
#     codec = QTextCodec.codecForName('UTF8')
#     QTextCodec.setCodecForLocale(codec)

    # Mainwin = MainWindow()
    # Mainwin.show()
    #Mainwin.Data2dfTable.sendData.connect(Mainwin.tdxcw.addData)
    # try:
    #     DDZZ = THS.ddzz()
    #     DDZZ.dataUpdated.connect(lambda x: Mainwin.gdTable.addData(x))
    #     Mainwin.dfcfCwTable.addData(dfcfXgq().parse())
    # except Exception as e:
    #     print(e)
    # Mainwin.avolmaTable.addData(pd.read_hdf(
    #     getpath( 'avol_xg'), key='avolma_xg'))
    #Mainwin.searchBox.setFocus(Qt.OtherFocusReason)
    # sys.exit(app.exec_())
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     form = dataFrameViewer()
#     form.addTable(name='沪深A股', df=pd.DataFrame(np.random.randn(10, 5), columns=['A', 'B', 'C', 'D', 'E']))
#     form.show()
#     app.exec_()