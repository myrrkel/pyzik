#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from history_manager import HistoryManager
from svg_icon import *


class historyControlsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        lay = QtWidgets.QHBoxLayout(self)

        _translate = QtCore.QCoreApplication.translate
        lay.addStretch()
        self.refreshButton = QtWidgets.QPushButton(_translate("history", "Refresh"))
        self.refreshButton.setIcon(get_svg_icon("refresh.svg"))
        lay.addWidget(self.refreshButton)
        lay.addStretch()


class HistoryWidget(QtWidgets.QDialog):
    def __init__(self, music_base, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowFlags(QtCore.Qt.Window)

        self.history = HistoryManager(music_base)
        self.history.load_history(False)

        self.initUI()

        self.showHistoryItems(self.history.history)
        self.initColumnHeaders()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        self.setSizePolicy(sizePolicy)
        self.resize(550, 400)
        self.initTableWidgetItems()

        self.historyControls = historyControlsWidget()
        self.historyControls.refreshButton.clicked.connect(self.onRefresh)

        layout.addWidget(self.tableWidgetItems)
        layout.addWidget(self.historyControls)

        self.retranslateUi()

    def onRefresh(self, event):
        self.history.load_history(False)
        self.showHistoryItems(self.history.history)

    def initTableWidgetItems(self):
        self.tableWidgetItems = QtWidgets.QTableWidget(self)

        self.tableWidgetItems.setGeometry(0, 0, 550, 300)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)

        self.tableWidgetItems.setSizePolicy(sizePolicy)
        self.tableWidgetItems.setMinimumSize(QtCore.QSize(50, 0))
        self.tableWidgetItems.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tableWidgetItems.setObjectName("tableWidgetItems")
        self.tableWidgetItems.setColumnCount(5)
        self.tableWidgetItems.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetItems.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetItems.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetItems.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetItems.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetItems.setHorizontalHeaderItem(4, item)

        self.initColumnHeaders()

    def initColumnHeaders(self):
        hHeader = self.tableWidgetItems.horizontalHeader()
        vHeader = self.tableWidgetItems.verticalHeader()
        vHeader.hide()

        hHeader.resizeSections(QtWidgets.QHeaderView.ResizeToContents)
        hHeader.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        item = self.tableWidgetItems.horizontalHeaderItem(0)
        item.setText(_translate("history", "Date"))
        item = self.tableWidgetItems.horizontalHeaderItem(1)
        item.setText(_translate("history", "Title"))
        item = self.tableWidgetItems.horizontalHeaderItem(2)
        item.setText(_translate("history", "Artist"))
        item = self.tableWidgetItems.horizontalHeaderItem(3)
        item.setText(_translate("history", "Album"))

        self.setWindowTitle(_translate("history", "History"))
        self.historyControls.refreshButton.setText(_translate("history", "Refresh"))

    def showHistoryItems(self, items):
        self.tableWidgetItems.setStyleSheet(
            "selection-background-color: black;selection-color: white;"
        )
        self.tableWidgetItems.setColumnCount(4)
        self.tableWidgetItems.setRowCount(0)
        i = 0
        for item in items:
            self.tableWidgetItems.insertRow(i)
            titleItem = QtWidgets.QTableWidgetItem(item.get_column_text(0))
            titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetItems.setItem(i, 0, titleItem)

            artistItem = QtWidgets.QTableWidgetItem(item.get_column_text(1))
            artistItem.setFlags(artistItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetItems.setItem(i, 1, artistItem)

            albumItem = QtWidgets.QTableWidgetItem(item.get_column_text(2))
            albumItem.setFlags(albumItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetItems.setItem(i, 2, albumItem)

            durationItem = QtWidgets.QTableWidgetItem(item.get_column_text(3))
            durationItem.setFlags(durationItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetItems.setItem(i, 3, durationItem)

            i += 1


if __name__ == "__main__":
    import sys
    from music_base import MusicBase
    mb = MusicBase()

    mb.load_music_base(False)

    app = QtWidgets.QApplication(sys.argv)

    histoWidget = HistoryWidget(mb)

    histoWidget.show()
    sys.exit(app.exec_())
