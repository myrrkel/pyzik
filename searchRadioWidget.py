#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from radioManager import *
from searchRadioThread import *
from progressWidget import *


class searchControlsWidget(QtWidgets.QWidget):


    def __init__(self,parent=None):
        QtWidgets.QWidget.__init__(self,parent=parent)

        lay = QtWidgets.QHBoxLayout(self)
        
        _translate = QtCore.QCoreApplication.translate

        self.searchEdit = QtWidgets.QLineEdit()
        self.searchEdit.setText("")

        self.searchButton = QtWidgets.QPushButton("Search")
        lay.addWidget(self.searchEdit)
        lay.addWidget(self.searchButton)

class playControlsWidget(QtWidgets.QWidget):


    def __init__(self,parent=None):
        QtWidgets.QWidget.__init__(self,parent=parent)

        lay = QtWidgets.QHBoxLayout(self)
        
        _translate = QtCore.QCoreApplication.translate


        self.playButton = QtWidgets.QPushButton("Play")
        lay.addWidget(self.playButton)

        self.addButton = QtWidgets.QPushButton("Add")
        lay.addWidget(self.addButton)


class searchRadioWidget(QtWidgets.QDialog):
    

    def __init__(self,musicBase):
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(QtCore.Qt.Window)
        
        self.radios = []
        self.radioManager = radioManager(musicBase)
        self.searchRadioThread = searchRadioThread()
                

        self.initUI()


        self.initColumnHeaders()

    def initUI(self):

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        self.setSizePolicy(sizePolicy)
        self.resize(550,400)
        self.initTableWidgetItems()

        self.searchControls = searchControlsWidget()
        self.searchControls.searchButton.clicked.connect(self.onSearch)

        self.playControls = playControlsWidget()
        self.playControls.playButton.clicked.connect(self.onSearch)

        layout.addWidget(self.searchControls)
        layout.addWidget(self.tableWidgetItems)
        layout.addWidget(self.playControls)

        self.retranslateUi()
        


    def onSearch(self,event):
        #self.radios = self.radioManager.search()
        search = self.searchControls.searchEdit.text()


        self.wProgress = progressWidget()
        self.searchRadioThread.searchProgress.connect(self.wProgress.setValue)
        self.searchRadioThread.searchCurrentMachine.connect(self.wProgress.setDirectoryText)
        self.searchRadioThread.searchCompleted.connect(self.onSearchComplete)
        self.wProgress.progressClosed.connect(self.searchRadioThread.stop)
        self.searchRadioThread.search = search
        self.searchRadioThread.start()


    def onSearchComplete(self,event):
        self.showItems(self.searchRadioThread.resRadios)
        self.initColumnHeaders()
        self.wProgress.close()


    def initTableWidgetItems(self):

        self.tableWidgetItems = QtWidgets.QTableWidget(self)

        self.tableWidgetItems.setGeometry(0, 0, 550, 300)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
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
        item.setText(_translate("searchRadio", "Name"))
        item = self.tableWidgetItems.horizontalHeaderItem(1)
        item.setText(_translate("searchRadio", "Country"))
        item = self.tableWidgetItems.horizontalHeaderItem(2)
        item.setText(_translate("searchRadio", "Genre"))
        item = self.tableWidgetItems.horizontalHeaderItem(3)
        item.setText(_translate("searchRadio", "Stream"))

        self.setWindowTitle(_translate("searchRadio", "Search radio"))
        self.searchControls.searchButton.setText(_translate("searchRadio", "Search"))

    def showItems(self,items):      
        self.tableWidgetItems.setStyleSheet("selection-background-color: black;selection-color: white;") 
        self.tableWidgetItems.setColumnCount(4)
        self.tableWidgetItems.setRowCount(0)
        i=0
        for item in items:
            self.tableWidgetItems.insertRow(i)
            titleItem = QtWidgets.QTableWidgetItem(item.name)
            titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetItems.setItem(i,0,titleItem)
            
            artistItem = QtWidgets.QTableWidgetItem(item.country)
            artistItem.setFlags(artistItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetItems.setItem(i,1,artistItem)

            albumItem = QtWidgets.QTableWidgetItem(item.getCategoriesText())
            albumItem.setFlags(albumItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetItems.setItem(i,2,albumItem)

            durationItem = QtWidgets.QTableWidgetItem(item.stream)
            durationItem.setFlags(durationItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetItems.setItem(i,3,durationItem)
          

            i+=1

   


if __name__ == "__main__":
    import sys
    from musicBase import *

    print('musicBase')
    mb = musicBase()
    print('loadMusicBase')
    mb.loadMusicBase(False)


    app = QtWidgets.QApplication(sys.argv)

    searchWidget = searchRadioWidget(mb)

    searchWidget.show()
    sys.exit(app.exec_())


    
