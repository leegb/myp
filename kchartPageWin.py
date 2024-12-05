# cython: language_level=3
# -*- coding: utf-8 -*-


import sys
sys.path.insert(0,'/var/workspace/QUANTPI')



from PyQt5.QtCore import (QCoreApplication, QPointF, QRectF, Qt, QTextCodec,
                          QTimer, pyqtSignal, pyqtSlot)
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPalette, QPen, QPixmap
from PyQt5.QtWidgets import (QAbstractSlider, QAction, QApplication, QFrame,
                             QGridLayout, QHBoxLayout, QLabel, QMenu,
                             QSplitter, QTableWidget, QTabWidget, QToolTip,
                             QWidget)
import indicators
from basefunc import np, pd
from indicators.DMI import DMI
from indicators.IndBase import Indbase
from indicators.Vol import Vol
from indicators.TSI import TSI
from indicators.Volp import Volp
from modules import chart, output

class kchartPageWin(QFrame):
    """
    主窗口
    """
    pressed = pyqtSignal()

    def __init__(self):
        super(kchartPageWin, self).__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.kchartPageWin_Bottom = kchartPageWin_Bottom()
        self.kchartPageWin_Top = kchartPageWin_Top()
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setContentsMargins(0, 0, 0, 0)
        self.splitter.setLineWidth(0)
        self.splitter.setMaximumWidth(0)
        self.splitter.addWidget(self.kchartPageWin_Top)
        self.splitter.addWidget(self.kchartPageWin_Bottom)
        self.kchartPageWin_Top.splitter.splitterMoved.connect(
            self.kchartPageWin_Bottom.splitter.moveSplitter)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.addWidget(self.splitter)
        self.setLayout(hbox)
        # 同步宽度
        self.kchartPageWin_Bottom.kchartPageWin_Bottom_Right.resize(
            self.kchartPageWin_Top.kchartPageWin_Top_Right.width(), self.kchartPageWin_Bottom.kchartPageWin_Bottom_Right.height())
        self.kchartPageWin_Top.kchartPageWin_Top_Right.resize(
            self.kchartPageWin_Bottom.kchartPageWin_Bottom_Right.width(), self.kchartPageWin_Top.kchartPageWin_Top_Right.height())
        self.setContentsMargins(0, 0, 0, 0)
from PyQt5.QtWidgets import QFrame, QSplitter, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal

class kchartPageWin(QFrame):
    """
    主窗口：包括上下两个面板，使用 QSplitter 来控制它们的大小。
    """
    pressed = pyqtSignal()  # 自定义信号，可用于后续的交互事件

    def __init__(self):
        super(kchartPageWin, self).__init__()

        # 创建上下两个面板
        self.kchartPageWin_Top = kchartPageWin_Top()  # 上面板
        self.kchartPageWin_Bottom = kchartPageWin_Bottom()  # 下面板

        # 创建垂直的 QSplitter，允许上下面板之间的大小调整
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setContentsMargins(0, 0, 0, 0)  # 只调用一次来设置边距
        self.splitter.setLineWidth(0)
        self.splitter.setMaximumWidth(0)
        self.splitter.addWidget(self.kchartPageWin_Top)
        self.splitter.addWidget(self.kchartPageWin_Bottom)

        # 连接信号，使得上下面板的尺寸同步
        self.kchartPageWin_Top.splitter.splitterMoved.connect(self.kchartPageWin_Bottom.splitter.moveSplitter)

        # 设置伸缩因子，确保两个面板在初始化时具有相同的空间分配
        self.splitter.setStretchFactor(0, 1)  # 上面板占1份空间
        self.splitter.setStretchFactor(1, 1)  # 下面板占1份空间

        # 创建主布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 设置边距
        layout.setSpacing(0)  # 设置间距
        layout.addWidget(self.splitter)  # 将 QSplitter 添加到布局中
        self.setLayout(layout)

        # 同步右侧面板的宽度
        self.syncPanelWidths()

    def syncPanelWidths(self):
        """
        同步上面板和下面板右侧部分的宽度，使其保持一致。
        """
        topRightWidth = self.kchartPageWin_Top.kchartPageWin_Top_Right.width()  # 获取上面板右侧宽度
        bottomRightWidth = self.kchartPageWin_Bottom.kchartPageWin_Bottom_Right.width()  # 获取下面板右侧宽度

        # 调整两个面板右侧部分的宽度，使它们保持一致
        self.kchartPageWin_Bottom.kchartPageWin_Bottom_Right.resize(topRightWidth, self.kchartPageWin_Bottom.kchartPageWin_Bottom_Right.height())
        self.kchartPageWin_Top.kchartPageWin_Top_Right.resize(topRightWidth, self.kchartPageWin_Top.kchartPageWin_Top_Right.height())

        # 如果需要在分隔条调整时动态同步宽度，可以通过连接信号来实现。

class kchartPageWin_Top(QFrame):
    """
    顶部窗口
    """

    def __init__(self):
        super(kchartPageWin_Top, self).__init__()
        self.kchartPageWin_Top_Left = chart.Chart()  # Chart()  #k线窗口
        # self.kchartPageWin_Top_Right=QLabel("预留窗口")
        self.kchartPageWin_Top_Right = kchartPageWin_Top_Right()  # 顶部右边窗口
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setContentsMargins(0, 0, 0, 0)
        self.splitter.setLineWidth(0)
        self.splitter.setMaximumWidth(0)
#        self.splitter.setStretchFactor(0,8)
#        self.splitter.setStretchFactor(1,2)
#        self.kchartPageWin_Bottom.setFrameStyle(QFrame.Box | QFrame.Plain)
#        self.kchartPageWin_Top.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.splitter.addWidget(self.kchartPageWin_Top_Left)
        self.splitter.addWidget(self.kchartPageWin_Top_Right)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.addWidget(self.splitter)
        self.setLayout(hbox)
        self.setMinimumHeight(600)
        self.setContentsMargins(0, 0, 0, 0)
from PyQt5.QtWidgets import QFrame, QSplitter, QHBoxLayout
from PyQt5.QtCore import Qt

class kchartPageWin_Top(QFrame):
    """
    顶部窗口：包括左右两个区域，使用 QSplitter 来控制它们的大小。
    """
    def __init__(self):
        super(kchartPageWin_Top, self).__init__()

        # 左侧区域：例如 K线图
        self.kchartPageWin_Top_Left = chart.Chart()  # K线窗口（示例）

        # 右侧区域：例如一些辅助信息或其他控件
        self.kchartPageWin_Top_Right = kchartPageWin_Top_Right()  # 顶部右侧窗口

        # 设置外框样式
        self.setFrameStyle(QFrame.Box | QFrame.Plain)

        # 创建水平 QSplitter，允许左右面板之间大小可调整
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setContentsMargins(0, 0, 0, 0)  # 设置边距
        self.splitter.setLineWidth(0)  # 分隔线宽度
        self.splitter.setMaximumWidth(0)  # 禁用最大宽度限制
        self.splitter.addWidget(self.kchartPageWin_Top_Left)  # 将左侧组件添加到 QSplitter
        self.splitter.addWidget(self.kchartPageWin_Top_Right)  # 将右侧组件添加到 QSplitter

        # 创建主布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 设置边距
        layout.setSpacing(0)  # 设置间距
        layout.addWidget(self.splitter)  # 将 QSplitter 添加到布局中
        self.setLayout(layout)

        # 设置最小高度
        self.setMinimumHeight(600)

        # 可选：如果需要初始化右侧和左侧面板的宽度比例，可以使用 setStretchFactor
        # self.splitter.setStretchFactor(0, 8)  # 设定左边区域占 80%
        # self.splitter.setStretchFactor(1, 2)  # 设定右边区域占 20%

        # 如果需要更多个性化的调整，可以在这里做进一步的扩展

class kchartPageWin_Top_Right(QTabWidget):
    """
    #顶部右边窗口
    """

    def __init__(self):
        super(kchartPageWin_Top_Right, self).__init__()
        self.kchartPageWin_Top_Right_chou = kchartPageWin_Top_Right_chou()
        self.addTab(self.kchartPageWin_Top_Right_chou, '筹')
        self.setTabPosition(QTabWidget.South)
        self.setStyleSheet('QTabBar::tab{height:9}')
        self.tabBarClicked.connect(self.tabBarclickedFunc)
        self.setMaximumWidth(400)
        self.setMinimumWidth(0)
        self.setContentsMargins(0, 0, 0, 0)

    def tabBarclickedFunc(self, i):
        sender = self.sender()

class kchartPageWin_Top_Right_chou(Indbase):
    """
    #顶部右边窗口:筹码分布
    """

    def __init__(self):
        super(kchartPageWin_Top_Right_chou, self).__init__()
        self.setMaximumWidth(400)
        self.setMinimumWidth(0)
        self.acquired = False
        self.setContentsMargins(0, 0, 0, 0)

    def displayData(self, painter):
        if self.acquired:
            self.dispdata = self.mainchart.arraydata
            if len(self.dispdata):
                self.colsDict = self.mainchart.colsDict
                n = int(self.dispdata[-1, :]
                        [self.mainchart.colsDict.get('holdday')])
                if (n >= len(self.dispdata)) | (n == 0):
                    n = len(self.dispdata)
                ret = self.dispdata[range(
                    int(-n), 0), :][:, self.mainchart.colsDict['avolma']]
                self.freq, self.price = np.histogram(ret, bins=50)
                self.freq = np.concatenate([np.array([0]), self.freq])
                linerange = self.rect().width()-10
                freqrange = np.max(self.freq)
                for freq, price in zip(self.freq, self.price):
                    painter.setPen(QColor(240, 0, 0))
                    if price > self.dispdata[-1, self.mainchart.colsDict['c']]:
                        painter.setPen(QColor(0, 0, 200))
                    posy = self.mainchart.topMarginheight + \
                        (1 - (price - self.mainchart.pricelow)/self.mainchart.pricerange) * \
                        self.mainchart.krange
                    painter.drawLine(QPointF(0, posy), QPointF(
                        freq*linerange/freqrange-10, posy))
                if not painter.isActive():
                    painter.end()
                del n, ret

    def paintEvent(self, event):
        if self.acquired:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            #painter.fillRect(self.rect(), QColor(255, 255, 240))
            painter.setPen(QColor(0, 0, 0))
            self.displayData(painter)

    def drawExLines(self):
        painter = QPainter(self)
        self.drawhelperline(painter)
        self.drawVerticalGridLine(painter)
        self.drawHorizontalGridLine(painter)
        self.drawCrossline(painter)
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QPointF
import numpy as np

class kchartPageWin_Top_Right_chou(Indbase):
    """
    顶部右边窗口: 显示筹码分布的图表。
    """

    def __init__(self):
        super(kchartPageWin_Top_Right_chou, self).__init__()
        self.setMaximumWidth(400)  # 设置最大宽度
        self.setMinimumWidth(0)    # 设置最小宽度
        self.acquired = False      # 是否获取数据标志
        self.setContentsMargins(0, 0, 0, 0)  # 设置窗口的内容边距

    def displayData(self, painter):
        """绘制筹码分布图的主要数据"""
        if self.acquired:
            # 获取需要显示的数据
            self.dispdata = self.mainchart.arraydata
            if len(self.dispdata) > 0:
                self.colsDict = self.mainchart.colsDict
                # 获取持有天数数据
                n = int(self.dispdata[-1, :][self.mainchart.colsDict.get('holdday')])
                
                # 检查持有天数是否有效
                if n >= len(self.dispdata) or n == 0:
                    n = len(self.dispdata)
                
                # 获取成交量数据
                ret = self.dispdata[range(int(-n), 0), :][:, self.mainchart.colsDict['avolma']]
                
                # 计算频率和价格的直方图
                self.freq, self.price = np.histogram(ret, bins=50)
                self.freq = np.concatenate([np.array([0]), self.freq])  # 添加一个0，避免绘制问题

                # 设置绘制区域的范围
                linerange = self.rect().width() - 10
                freqrange = np.max(self.freq)

                # 绘制频率线条
                for freq, price in zip(self.freq, self.price):
                    painter.setPen(QColor(240, 0, 0))  # 设置画笔颜色为红色
                    if price > self.dispdata[-1, self.mainchart.colsDict['c']]:
                        painter.setPen(QColor(0, 0, 200))  # 如果价格大于当前收盘价，设置为蓝色

                    # 计算Y轴位置
                    posy = self.mainchart.topMarginheight + \
                        (1 - (price - self.mainchart.pricelow) / self.mainchart.pricerange) * self.mainchart.krange
                    
                    # 绘制直线（根据成交量和价格绘制图形）
                    painter.drawLine(QPointF(0, posy), QPointF(freq * linerange / freqrange - 10, posy))

                # 绘制完毕，释放资源
                if not painter.isActive():
                    painter.end()
                del n, ret

    def paintEvent(self, event):
        """在绘制事件中调用绘制数据的方法"""
        if self.acquired:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)  # 开启反锯齿
            painter.setPen(QColor(0, 0, 0))  # 设置画笔颜色为黑色
            self.displayData(painter)  # 绘制数据

    def drawExLines(self):
        """绘制额外的辅助线"""
        painter = QPainter(self)
        self.drawhelperline(painter)         # 绘制辅助线
        self.drawVerticalGridLine(painter)   # 绘制垂直网格线
        self.drawHorizontalGridLine(painter) # 绘制水平网格线
        self.drawCrossline(painter)          # 绘制交叉线

class kchartPageWin_Bottom(QFrame):
    """
    底部窗口
    """

    def __init__(self):
        super(kchartPageWin_Bottom, self).__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.IndWin = IndWin()
        self.kchartPageWin_Bottom_Right = kchartPageWin_Bottom_Right()
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setContentsMargins(0, 0, 0, 0)
        self.splitter.setLineWidth(0)
        self.splitter.setMaximumWidth(0)
        self.splitter.addWidget(self.IndWin)
        self.splitter.addWidget(self.kchartPageWin_Bottom_Right)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.addWidget(self.splitter)
        self.setLayout(hbox)
        self.setMaximumHeight(480)
        self.setContentsMargins(0, 0, 0, 0)

class IndWin(QFrame):
    """
    底部左边窗口:副图窗口，指标窗口
    """

    def __init__(self):
        super(IndWin, self).__init__()
        self.IndWin2 = IndWin2()
        self.IndWin1 = IndWin1()
        self.IndWinlst = [self.IndWin2, self.IndWin1]
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setContentsMargins(0, 0, 0, 0)
        self.splitter.setLineWidth(0)
        self.splitter.setMaximumWidth(0)
        self.splitter.addWidget(self.IndWin2)
        self.splitter.addWidget(self.IndWin1)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.addWidget(self.splitter)
        self.setLayout(hbox)
        self.setContentsMargins(0, 0, 0, 0)
from PyQt5.QtWidgets import QFrame, QSplitter, QHBoxLayout
from PyQt5.QtCore import Qt

class kchartPageWin_Bottom(QFrame):
    """
    底部窗口: 包含副图窗口和指标窗口。
    主要通过QSplitter进行布局管理，水平分割副图窗口和右侧的内容窗口。
    """

    def __init__(self):
        super(kchartPageWin_Bottom, self).__init__()
        
        # 设置边框样式
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        
        # 初始化子窗口
        self.IndWin = IndWin()  # 指标窗口
        self.kchartPageWin_Bottom_Right = kchartPageWin_Bottom_Right()  # 右侧窗口
        
        # 设置分割器
        self.splitter = QSplitter(Qt.Horizontal)  # 水平分割器
        self.splitter.setContentsMargins(0, 0, 0, 0)
        self.splitter.setLineWidth(0)
        self.splitter.setMaximumWidth(0)  # 不限制最大宽度
        
        # 将子窗口添加到分割器中
        self.splitter.addWidget(self.IndWin)
        self.splitter.addWidget(self.kchartPageWin_Bottom_Right)
        
        # 创建并设置布局
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.addWidget(self.splitter)
        self.setLayout(hbox)
        
        # 设置窗口高度
        self.setMaximumHeight(480)
        self.setContentsMargins(0, 0, 0, 0)

class IndWin(QFrame):
    """
    底部左边窗口: 用于显示副图和指标窗口。
    将副图窗口（IndWin2）和指标窗口（IndWin1）垂直布局。
    """

    def __init__(self):
        super(IndWin, self).__init__()
        
        # 初始化两个子窗口
        self.IndWin2 = IndWin2()  # 副图窗口
        self.IndWin1 = IndWin1()  # 指标窗口
        
        # 将窗口加入到一个列表中，方便管理
        self.IndWinlst = [self.IndWin2, self.IndWin1]
        
        # 设置垂直分割器
        self.splitter = QSplitter(Qt.Vertical)  # 垂直分割器
        self.splitter.setContentsMargins(0, 0, 0, 0)
        self.splitter.setLineWidth(0)
        self.splitter.setMaximumWidth(0)  # 不限制最大宽度
        
        # 将子窗口添加到分割器中
        self.splitter.addWidget(self.IndWin2)
        self.splitter.addWidget(self.IndWin1)
        
        # 设置分割器的伸缩因子，使得两个子窗口可以等比例缩放
        self.splitter.setStretchFactor(0, 1)  # 设置第一个子窗口的伸缩因子
        self.splitter.setStretchFactor(1, 1)  # 设置第二个子窗口的伸缩因子
        
        # 创建并设置布局
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.addWidget(self.splitter)
        self.setLayout(hbox)
        
        # 设置窗口的内容边距
        self.setContentsMargins(0, 0, 0, 0)

class IndWin1(QTabWidget):
    """
    指标窗口，底部左边窗口
    """

    def __init__(self):
        super(IndWin1, self).__init__()
        # Volp()#Kd()#Example.Example()#QLabel("保留窗口1")
#        self.kchartPageWin_Bottom_Left = TSI()#DMI()
#        self.addTab(self.kchartPageWin_Bottom_Left, 'DMI')
#        #self.Vol = Vol()
#        self.addTab(Vol(), 'vol')
        self.indlist = [Vol, TSI]
        self.indDict = {}
        {self.indDict.update({i.__name__: i()})for i in self.indlist}
        for name, ind in self.indDict.items():
            self.addTab(ind, name)
        self.setTabPosition(QTabWidget.South)
        self.setStyleSheet('QTabBar::tab{height:9}')
        self.tabBarClicked.connect(self.tabBarclickedFunc)
        self.setContentsMargins(0, 0, 0, 0)

    def setInd(self, ind, name):
        self.addTab(ind, name)

    def tabBarclickedFunc(self, i):
        sender = self.sender()
        print(self.sender().tabText(i))

class IndWin2(QTabWidget):
    """
    指标窗口，底部左边窗口
    """

    def __init__(self):
        super(IndWin2, self).__init__()
        # Volp()#Kd()#Example.Example()#QLabel("保留窗口1")
#        self.kchartPageWin_Bottom_Left = TSI()#DMI()
#        self.addTab(self.kchartPageWin_Bottom_Left, 'DMI')
#        #self.Vol = Vol()
#        self.addTab(Vol(), 'vol')
        self.indlist = [Vol, TSI, DMI]
        self.indDict = {}
        {self.indDict.update({i.__name__: i()})for i in self.indlist}
        for name, ind in self.indDict.items():
            self.addTab(ind, name)
        self.setTabPosition(QTabWidget.South)
        self.setStyleSheet('QTabBar::tab{height:9}')
        self.tabBarClicked.connect(self.tabBarclickedFunc)
        self.setContentsMargins(0, 0, 0, 0)

    def setInd(self, ind, name):
        self.addTab(ind, name)

    def tabBarclickedFunc(self, i):
        sender = self.sender()
        print(self.sender().tabText(i))

class kchartPageWin_Bottom_Right(QTabWidget):
    """
    #底部右边窗口
    """

    def __init__(self):
        super(kchartPageWin_Bottom_Right, self).__init__()
        self.setMaximumWidth(400)
        self.setMinimumWidth(10)
        self.kchartPageWin_Bottom_Right1 = output.Output()
        self.addTab(self.kchartPageWin_Bottom_Right1, 'info')
        #self.Vol = Vol()
        #self.addTab(self.Vol, 'vol')
        self.setTabPosition(QTabWidget.South)
        self.setStyleSheet('QTabBar::tab{height:9}')
        self.tabBarClicked.connect(self.tabBarclickedFunc)
        self.setContentsMargins(0, 0, 0, 0)

    def tabBarclickedFunc(self, i):
        sender = self.sender()

class kchartPageWin_Bottom_Right1(QLabel):
    """
    底部右边窗口:子窗口
    """

    def __init__(self):
        super(kchartPageWin_Bottom_Right1, self).__init__()
        self.setText("预留窗口1")
        self.setAlignment(Qt.AlignCenter)
        self.setMaximumWidth(400)
        self.setMinimumWidth(10)
        self.setContentsMargins(0, 0, 0, 0)
from PyQt5.QtWidgets import QFrame, QSplitter, QHBoxLayout, QTabWidget, QLabel
from PyQt5.QtCore import Qt

class kchartPageWin_Bottom(QFrame):
    """
    底部窗口：包含副图窗口和右侧内容窗口。
    使用 QSplitter 来进行水平分割布局，左侧为 IndWin（副图与指标窗口），右侧为 kchartPageWin_Bottom_Right（信息窗口）。
    """
    def __init__(self):
        super(kchartPageWin_Bottom, self).__init__()

        # 设置窗口样式
        self.setFrameStyle(QFrame.Box | QFrame.Plain)

        # 初始化子窗口
        self.IndWin = IndWin()  # 左侧副图与指标窗口
        self.kchartPageWin_Bottom_Right = kchartPageWin_Bottom_Right()  # 右侧信息窗口

        # 设置水平分割器
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setContentsMargins(0, 0, 0, 0)
        self.splitter.setLineWidth(0)
        self.splitter.setMaximumWidth(0)

        # 将子窗口加入到分割器
        self.splitter.addWidget(self.IndWin)
        self.splitter.addWidget(self.kchartPageWin_Bottom_Right)

        # 创建布局并添加分割器
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.addWidget(self.splitter)
        self.setLayout(hbox)

        # 设置窗口最大高度
        self.setMaximumHeight(480)
        self.setContentsMargins(0, 0, 0, 0)


class IndWin(QFrame):
    """
    底部左侧窗口: 包含副图窗口（IndWin2）和指标窗口（IndWin1）。
    使用 QSplitter 来进行垂直分割布局。
    """
    def __init__(self):
        super(IndWin, self).__init__()

        # 初始化副图和指标窗口
        self.IndWin2 = IndWin2()  # 副图窗口
        self.IndWin1 = IndWin1()  # 指标窗口

        # 使用 QSplitter 进行垂直布局
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setContentsMargins(0, 0, 0, 0)
        self.splitter.setLineWidth(0)
        self.splitter.setMaximumWidth(0)

        # 将子窗口添加到分割器
        self.splitter.addWidget(self.IndWin2)
        self.splitter.addWidget(self.IndWin1)

        # 设置分割器的伸缩因子
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)

        # 创建并设置布局
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.addWidget(self.splitter)
        self.setLayout(hbox)

        # 设置窗口的内容边距
        self.setContentsMargins(0, 0, 0, 0)


class IndWin1(QTabWidget):
    """
    底部左侧窗口: 显示指标窗口（例如 Vol, TSI等）。
    使用 QTabWidget 管理多个标签页，用户可以在不同的指标之间切换。
    """
    def __init__(self):
        super(IndWin1, self).__init__()

        # 初始化指标列表
        self.indlist = [Vol, TSI]
        self.indDict = {}

        # 为每个指标添加标签页
        {self.indDict.update({i.__name__: i()}) for i in self.indlist}
        for name, ind in self.indDict.items():
            self.addTab(ind, name)

        # 设置标签位置和样式
        self.setTabPosition(QTabWidget.South)
        self.setStyleSheet('QTabBar::tab {height: 9px;}')

        # 连接标签栏点击事件
        self.tabBarClicked.connect(self.tabBarclickedFunc)
        self.setContentsMargins(0, 0, 0, 0)

    def tabBarclickedFunc(self, i):
        """
        处理标签栏点击事件，打印当前选中的标签名
        """
        sender = self.sender()
        print(sender.tabText(i))


class IndWin2(QTabWidget):
    """
    底部左侧窗口: 显示副图窗口（例如 Vol, TSI, DMI等）。
    使用 QTabWidget 管理多个标签页，用户可以在不同的副图之间切换。
    """
    def __init__(self):
        super(IndWin2, self).__init__()

        # 初始化副图列表
        self.indlist = [Vol, TSI, DMI]
        self.indDict = {}

        # 为每个副图添加标签页
        {self.indDict.update({i.__name__: i()}) for i in self.indlist}
        for name, ind in self.indDict.items():
            self.addTab(ind, name)

        # 设置标签位置和样式
        self.setTabPosition(QTabWidget.South)
        self.setStyleSheet('QTabBar::tab {height: 9px;}')

        # 连接标签栏点击事件
        self.tabBarClicked.connect(self.tabBarclickedFunc)
        self.setContentsMargins(0, 0, 0, 0)

    def tabBarclickedFunc(self, i):
        """
        处理标签栏点击事件，打印当前选中的副图标签名
        """
        sender = self.sender()
        print(sender.tabText(i))


class kchartPageWin_Bottom_Right(QTabWidget):
    """
    底部右侧窗口: 用于显示相关信息或其他内容。
    通过 QTabWidget 管理多个标签页，右侧显示不同的内容窗口。
    """
    def __init__(self):
        super(kchartPageWin_Bottom_Right, self).__init__()

        # 设置宽度限制
        self.setMaximumWidth(400)
        self.setMinimumWidth(10)

        # 初始化右侧窗口的子标签页
        self.kchartPageWin_Bottom_Right1 = kchartPageWin_Bottom_Right1()
        self.addTab(self.kchartPageWin_Bottom_Right1, 'Info')

        # 设置标签位置和样式
        self.setTabPosition(QTabWidget.South)
        self.setStyleSheet('QTabBar::tab {height: 9px;}')

        # 连接标签栏点击事件
        self.tabBarClicked.connect(self.tabBarclickedFunc)
        self.setContentsMargins(0, 0, 0, 0)

    def tabBarclickedFunc(self, i):
        """
        处理右侧窗口的标签点击事件
        """
        sender = self.sender()


class kchartPageWin_Bottom_Right1(QLabel):
    """
    右侧底部窗口中的子窗口，用于显示简单信息或占位。
    """
    def __init__(self):
        super(kchartPageWin_Bottom_Right1, self).__init__()

        # 设置标签内容和对齐方式
        self.setText("预留窗口1")
        self.setAlignment(Qt.AlignCenter)

        # 设置宽度和边距
        self.setMaximumWidth(400)
        self.setMinimumWidth(10)
        self.setContentsMargins(0, 0, 0, 0)
