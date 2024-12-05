# cython: language_level=3
# -*- coding: utf-8 -*-


import sys
sys.path.insert(0,'/var/workspace/QUANTPI')








import os
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QScrollBar
from modules import utils

class ScrollBar(QScrollBar):
    ScrollbarmousePressEvent = pyqtSignal()
    # cbValueChangedSig=pyqtSignal(int)

    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
#        self.valueChanged.connect(self.cbValueChanged)
#
#
#    def cbValueChanged(self, value):
#        self.cbValueChangedSig.emit(value)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.ScrollbarmousePressEvent.emit()
