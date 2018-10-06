#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PyQt5.QtCore import Qt, pyqtSignal, QCoreApplication
from PyQt5.QtWidgets import QShortcut, QAction, QWidget, QMainWindow
from PyQt5.QtGui import QPixmap, QIcon

from historyManager import *


class customControlsWidget(QWidget):


    def __init__(self,parent=None):
        QWidget.__init__(self,parent=parent)

        lay = QHBoxLayout(self)
        
        _translate = QCoreApplication.translate

        self.refreshButton = QtWidgets.QPushButton(_translate("custom", "Refresh"))
        lay.addWidget(self.refreshButton)


class fullScreenWidget(QtWidgets.QDialog):
    

    def __init__(self,parent=None):
        QtWidgets.QDialog.__init__(self)
        self.parent = parent
        self.setWindowFlags(
                            QtCore.Qt.Window | 
                            QtCore.Qt.WindowStaysOnTopHint | 
                            QtCore.Qt.MaximizeUsingFullscreenGeometryHint | 
                            QtCore.Qt.FramelessWindowHint )
     

        self.shortcutClose = QShortcut(QtGui.QKeySequence("Escape"), self)
        self.shortcutClose.activated.connect(self.close)

        self.initUI()

        self.showFullScreen()

        #self.showTableItems(self.mainItem.items)
        #self.initColumnHeaders()

    def initUI(self):

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

    def mousePressEvent(self, event):
        print("clicked")
        self.close()

    def show(self):
        self.showFullScreen()