#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from radioManager import *
from searchRadioThread import *
from progressWidget import *
from svgIcon import *
from waitOverlayWidget import *

class searchControlsWidget(QtWidgets.QWidget):


    def __init__(self,parent=None):
        QtWidgets.QWidget.__init__(self,parent=parent)

        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        
        _translate = QtCore.QCoreApplication.translate

        self.searchEdit = QtWidgets.QLineEdit()
        self.searchEdit.setText("")

        self.searchButton = QtWidgets.QPushButton("Search")
        self.searchButton.setIcon(getSvgIcon("radio-tower.svg"))
        lay.addWidget(self.searchEdit)
        lay.addWidget(self.searchButton)

        



class machineSelectorControlsWidget(QtWidgets.QWidget):


    def __init__(self,parent=None,machines=[]):
        QtWidgets.QWidget.__init__(self,parent=parent)
        self.checks = []
        self.lay = QtWidgets.QHBoxLayout(self)
        self.lay.setContentsMargins(0, 0, 0, 9)
        
        for i, machine in enumerate(machines):

            check = QtWidgets.QCheckBox(machine)
            if i==0: check.setChecked(True)
            self.checks.append(check)
            self.lay.addWidget(check)

    def getSelectedMAchines(self):
        machines = []
        for check in self.checks:
            if check.isChecked():
                print("Checked="+check.text())
                machines.append(check.text())

        return machines

class playControlsWidget(QtWidgets.QWidget):


    def __init__(self,parent=None):
        QtWidgets.QWidget.__init__(self,parent=parent)

        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        
        _translate = QtCore.QCoreApplication.translate


        self.playButton = QtWidgets.QPushButton("Play")
        self.playButton.setIcon(getSvgIcon("play.svg"))
        lay.addWidget(self.playButton)

        self.addButton = QtWidgets.QPushButton("Add")
        self.addButton.setIcon(getSvgIcon("plus.svg"))
        lay.addWidget(self.addButton)


class searchRadioWidget(QtWidgets.QDialog):
    
    radioAdded = pyqtSignal(int, name='radioAdded')

    def __init__(self, musicBase, player, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowFlags(QtCore.Qt.Window)
        
        self.radios = []
        self.radioManager = radioManager(musicBase)
        self.player = player
        self.searchRadioThread = searchRadioThread()
        
                

        self.initUI()


        self.initColumnHeaders()

        self.searchControls.searchEdit.setFocus()
        self.setTabOrder(self.searchControls.searchEdit, self.searchControls.searchButton)

    def initUI(self):

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        self.setSizePolicy(sizePolicy)
        self.resize(600,400)
        self.initTableWidgetItems()

        self.searchControls = searchControlsWidget()
        self.searchControls.searchButton.clicked.connect(self.onSearch)

        self.playControls = playControlsWidget()
        self.playControls.playButton.clicked.connect(self.onClickPlayPadio)
        self.playControls.addButton.clicked.connect(self.onAddPadio)

        self.machineSelectorControls = machineSelectorControlsWidget(None,self.radioManager.machines)

        self.mainLayout.addWidget(self.searchControls)
        self.mainLayout.addWidget(self.machineSelectorControls)
        self.mainLayout.addWidget(self.tableWidgetItems)
        self.mainLayout.addWidget(self.playControls)

        self.overlay = waitOverlay(self)
        self.overlay.hide()

        self.retranslateUi()
        

    def resizeEvent(self, event):
    
        self.overlay.resize(event.size())

    def onSearch(self,event):
        self.overlay.showOverlay()
        search = self.searchControls.searchEdit.text()

        self.wProgress = progressWidget(self)
        self.searchRadioThread.searchProgress.connect(self.wProgress.setValue)
        self.searchRadioThread.searchCurrentMachine.connect(self.wProgress.setDirectoryText)
        self.searchRadioThread.searchCompleted.connect(self.onSearchComplete)
        self.wProgress.progressClosed.connect(self.searchRadioThread.stop)
        self.searchRadioThread.search = search
        self.searchRadioThread.machines = self.machineSelectorControls.getSelectedMAchines()
        self.searchRadioThread.start()

    def onPlayPadio(self,item):
        self.player.playRadio(self.radios[item])

    def onClickPlayPadio(self,event):
        i = self.tableWidgetItems.currentRow()
        self.player.playRadio(self.radios[i])

    def onAddPadio(self,item):
        i = self.tableWidgetItems.currentRow()
        rad = self.radios[i]
        rad.saveRadio(self.radioManager.musicBase.db)
        self.radioAdded.emit(1)


    def onSearchComplete(self,event):
        self.radios = self.searchRadioThread.resRadios
        self.showItems(self.radios)
        self.initColumnHeaders()
        self.wProgress.close()
        self.overlay.hide()


    def initTableWidgetItems(self):

        self.tableWidgetItems = QtWidgets.QTableWidget(self)

        self.tableWidgetItems.setGeometry(0, 0, 600, 300)
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

        self.tableWidgetItems.cellDoubleClicked.connect(self.onPlayPadio)

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
        self.playControls.playButton.setText(_translate("searchRadio", "Play"))
        self.playControls.addButton.setText(_translate("searchRadio", "Add"))

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
    from playerVLC import *

    app = QtWidgets.QApplication(sys.argv)

    print('musicBase')
    mb = musicBase()
    print('loadMusicBase')
    mb.loadMusicBase(False)

    player = playerVLC()


    

    searchWidget = searchRadioWidget(mb,player)

    searchWidget.show()
    sys.exit(app.exec_())


    
