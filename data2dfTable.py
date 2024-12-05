# cython: language_level=3
# -*- coding: utf-8 -*-


import sys
sys.path.insert(0,'/var/workspace/QUANTPI')



from PyQt5.QtCore import pyqtSignal,QObject
from basefunc import pd

class data2dfTable(QObject):
    sendData = pyqtSignal(object)

    def __init__(self):
        super(data2dfTable,self).__init__()
        pass

    def setData(self, data):
        #data += '1'
        ret = pd.read_hdf(data)
        ret.index = range(len(ret))
        self.sendData.emit(ret)
