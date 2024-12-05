# cython: language_level=3
# -*- coding: utf-8 -*-


import sys
sys.path.insert(0,'/var/workspace/QUANTPI')








from PyQt5.QtWidgets import (QWidget, QPushButton, QFrame, 
    QColorDialog, QApplication,QDialog)
from PyQt5.QtGui import QColor

class Query_color(QDialog):     

    def __init__(self):
        super().__init__()      

    def color_name(self):      
        col =QColorDialog.getColor()
        return col.name()     

def select_color():
    return Query_color().color_name()
