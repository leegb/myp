# cython: language_level=3
# -*- coding: utf-8 -*-


import sys
sys.path.insert(0,'/var/workspace/QUANTPI')








import os
import re
from PyQt5.QtCore import pyqtSignal, QStringListModel, Qt
from PyQt5.QtWidgets import QLineEdit, QCompleter
from PyQt5.QtGui import QIcon
from basefunc import normalizeStockCode,pd
from modules import globals
from modules import utils
from SystemDir import getpath
#from chart import Chart
pat = re.compile(r'\d+')
from SystemDir import gdrs_dir,configure_dir
import numpy as np
from webData.cninfo import stockshortname
from basefunc import int2str

def create_searchline_data():
    a = pd.read_hdf(configure_dir(gdrs_dir,np.sort(os.listdir(gdrs_dir))[-1]))
    a.rename({'名称':'简称'},axis=1,inplace=True)
    b = pd.read_hdf(getpath('jrj_data'),key='jrj')
    b = pd.concat([a,b.query('code not in %s'%a.code.tolist())])
    b['f'] = b.简称.apply(lambda x:isinstance(x,str))
    b = b[b.f]
    ret = (b.code+':'+b.name).tolist()
    ret += (b.简称+':'+b.name+':'+b.code).tolist()
    ret += (b.简称.apply(lambda x: x.lower())+':'+b.name+':'+b.code).tolist()
    return ret

def create_searchline_data():
    b = pd.DataFrame(stockshortname().db.collection.find({'PYJC':{'$nin':[None]}},{'ZQJC','code','PYJC'}))
    ret = (b.code+':'+b['ZQJC']).tolist()
    ret += (b['PYJC']+':'+b['ZQJC']+':'+b.code).tolist()
    ret += (b['PYJC'].apply(lambda x: x.lower())+':'+b['ZQJC']+':'+b.code).tolist()
    return ret

class searchLine(QLineEdit):
    showChartSig = pyqtSignal(str)
    printSig = pyqtSignal(list)
    ChangeSLayoutSig = pyqtSignal()

    def __init__(self, parent=None):
        super(searchLine, self).__init__(parent)
        self.setMaximumWidth(120)
        self.setWindowIcon(QIcon('./icon/explorer.png'))
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        try:
            user_completion_list = create_searchline_data()
        except:
            user_completion_list = ['payh:平安银行:600000']
        user_completer_model = QStringListModel()
        user_completer_model.setStringList(sorted(user_completion_list))
        self.user_completion = QCompleter()
        self.user_completion.setModel(user_completer_model)
        self.setCompleter(self.user_completion)
        self.user_completion.setCaseSensitivity(Qt.CaseSensitive)
        self.user_completion.setMaxVisibleItems(20)
        # self.returnPressed.connect(lambda:self.showChart())
        self.user_completion.activated.connect(self.showChart)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clear()

    def showChart(self, text):
        self.clear()
        text = pat.findall(text)
        self.showChartSig.emit(self.normalizeStockCode(text[0]))
        self.clear()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        key = event.key()
        text = pat.findall(self.text())
        if (key == Qt.Key_Return):
            if len(text):
                self.showChartSig.emit(self.normalizeStockCode(text[0]))
                self.clear()
        if (key == Qt.Key_Escape):
            self.ChangeSLayoutSig.emit()

    def normalizeStockCode(self, stock_code):
        if isinstance(stock_code, (int, float)):
            stock_code = int2str(stock_code)
        elif isinstance(stock_code, str):
            if(len(stock_code) < 6):
                padlen = 6 - len(stock_code)
                padlist = []
                for i in range(0, padlen):
                    padlist.append('0')
                padstr = ''.join(padlist)
                stock_code = padstr + stock_code
        return stock_code

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.clear()
#        elif(key == Qt.Key_U):
#            if(event.modifiers() == Qt.ControlModifier):
#                pos = self.cursorPosition()
#                txt = self.text()[pos:]
#                self.setText(txt)
#                self.setCursorPosition(0)
#
#        elif(key == Qt.Key_K):
#            if(event.modifiers() == Qt.ControlModifier):
#                pos = self.cursorPosition()
#                txt = self.text()[:pos]
#                self.setText(txt)
#
#        elif(key == Qt.Key_Up):
#            idx = self.cmdHistoryIdx - 1
#            if(idx < 0):
#                idx = len(self.cmdHistory) - 1
#
#            try:
#                self.setText(self.cmdHistory[idx])
#                self.cmdHistoryIdx = idx
#            except:
#                pass
#
#        elif(key == Qt.Key_Down):
#            idx = self.cmdHistoryIdx + 1
#            if(idx > len(self.cmdHistory) -1):
#                idx = 0
#
#            try:
#                self.setText(self.cmdHistory[idx])
#                self.cmdHistoryIdx = idx
#            except:
#                pass
