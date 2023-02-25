#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from historyManager import HistoryManager


class CustomControlsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        lay = QtWidgets.QHBoxLayout(self)

        _translate = QtCore.QCoreApplication.translate

        self.refreshButton = QtWidgets.QPushButton(_translate("custom", "Refresh"))
        lay.addWidget(self.refreshButton)


class CustomWidget(QtWidgets.QDialog):
    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self)
        self.parent = parent
        self.setWindowFlags(QtCore.Qt.Window)

        self.initUI()

        # self.showTableItems(self.mainItem.items)
        # self.initColumnHeaders()

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
        # self.initTableWidgetItems()

        self.customControls = CustomControlsWidget()
        self.customControls.refreshButton.clicked.connect(self.onAction)

        # layout.addWidget(self.tableWidgetItems)
        layout.addWidget(self.customControls)

        # self.retranslateUi()

    def onAction(self, event):
        print("Action!")

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

    def showTableItems(self, items):
        self.tableWidgetItems.setStyleSheet(
            "selection-background-color: black;selection-color: white;"
        )
        self.tableWidgetItems.setColumnCount(4)
        self.tableWidgetItems.setRowCount(0)
        i = 0
        for item in items:
            self.tableWidgetItems.insertRow(i)
            titleItem = QtWidgets.QTableWidgetItem(item.getColumnText(0))
            titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetItems.setItem(i, 0, titleItem)

            artistItem = QtWidgets.QTableWidgetItem(item.getColumnText(1))
            artistItem.setFlags(artistItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetItems.setItem(i, 1, artistItem)

            albumItem = QtWidgets.QTableWidgetItem(item.getColumnText(2))
            albumItem.setFlags(albumItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetItems.setItem(i, 2, albumItem)

            durationItem = QtWidgets.QTableWidgetItem(item.getColumnText(3))
            durationItem.setFlags(durationItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetItems.setItem(i, 3, durationItem)

            i += 1


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    custWidget = CustomWidget(app)

    custWidget.show()
    sys.exit(app.exec_())
