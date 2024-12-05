# cython: language_level=3
# -*- coding: utf-8 -*-


import sys
sys.path.insert(0,'/var/workspace/QUANTPI')








from PyQt5.QtCore import (QCoreApplication, Qt, QTextCodec, QThread, QTimer,
                          pyqtSignal, pyqtSlot)
from PyQt5.QtGui import (QGuiApplication, QIcon, QKeySequence, QMovie,
                         QPalette, QPixmap, QWindow)
from PyQt5.QtWidgets import (QAbstractSlider, QAction, QApplication, QComboBox,
                             QDockWidget, QGridLayout, QMainWindow, QMenu,
                             QMessageBox, QShortcut, QStackedLayout,
                             QTableWidget, QTabWidget, QWidget,QFileDialog,QPushButton,QRadioButton,QCheckBox)
import guiSettings

class metaMainWin(QMainWindow):

    def __init__(self,parent=None):
        super(metaMainWin,self).__init__(parent=None)
        self.setWindowTitle(guiSettings.mainTitle)
        self.setWindowIcon(QIcon(QPixmap('./icon/logo.png')))
        self.setWindowState(Qt.WindowActive)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
###############################################################################
# The following are GUI shortcut tools
###############################################################################
    ## Create an action for GUIs

    def createAction(self, text, slot = None, shortcut = None, icon = None,
                     tip = None, checkable = False, signal = "triggered()"):
        action = QAction(text,self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)
    ## Create a button

    def createButton(self,text, kind= "push", checkable = False):
        if kind == "push":
            button = QPushButton(text)
        if kind == "radio":
            button = QRadioButton(text)
        if kind == "check":
            button = QCheckBox(text)
        if checkable:
            button.setEnabled(True)
        return button

    def threadRun(self,thread):
        Thd = QThread()
        thread.moveToThread(Thd)
        Thd.started.connect(lambda:thread.do())
        Thd.start()
        print(thread.ret)
        return thread
