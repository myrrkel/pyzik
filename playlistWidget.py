#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from track import *

class playlistWidget(QtWidgets.QDialog):
    
    mediaList = None
    player = None
    trackChanged = pyqtSignal(int, name='trackChanged')

    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.initUI()

    def initUI(self):

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        self.setSizePolicy(sizePolicy)
        self.resize(400,250)
        self.initTableWidgetTracks()

        layout.addWidget(self.tableWidgetTracks)

        self.tableWidgetTracks.cellDoubleClicked.connect(self.changeTrack)

        self.setWindowTitle("Playlist")

        #self.resizeEvent = self.onResize

    def onResize(self,event):
        hHeader = self.tableWidgetTracks.horizontalHeader()
        hHeader.resizeSections(QtWidgets.QHeaderView.Stretch)
        

    def initTableWidgetTracks(self):
         self.tableWidgetTracks = QtWidgets.QTableWidget(self)
        self.tableWidgetTracks.setGeometry(0, 0, 400, 250)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        #sizePolicy.setHeightForWidth(self.tableWidgetTracks.sizePolicy().hasHeightForWidth())
        self.tableWidgetTracks.setSizePolicy(sizePolicy)
        self.tableWidgetTracks.setMinimumSize(QtCore.QSize(50, 0))
        self.tableWidgetTracks.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidgetTracks.setObjectName("tableWidgetTracks")
        self.tableWidgetTracks.setColumnCount(5)
        self.tableWidgetTracks.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(4, item)

        _translate = QtCore.QCoreApplication.translate
        item = self.tableWidgetTracks.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Title"))
        item = self.tableWidgetTracks.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Artist"))
        item = self.tableWidgetTracks.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Album"))
        item = self.tableWidgetTracks.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Duration"))
        item = self.tableWidgetTracks.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "ID"))

        self.tableWidgetTracks.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidgetTracks.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidgetTracks.setRowCount(0)

        self.initColumnHeaders()

    def initColumnHeaders(self):

        hHeader = self.tableWidgetTracks.horizontalHeader()
        vHeader = self.tableWidgetTracks.verticalHeader()
        vHeader.hide()

        hHeader.resizeSections(QtWidgets.QHeaderView.ResizeToContents)
        hHeader.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        hHeader.hideSection(4)


    def showAlbumTracks(self,tracks):        
        self.tableWidgetTracks.setColumnCount(3)
        self.tableWidgetTracks.setRowCount(0)
        i=0
        for track in tracks:
            self.tableWidgetTracks.insertRow(i)
            titleItem = QtWidgets.QTableWidgetItem(track.title)
            titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetTracks.setItem(i,0,titleItem)
            
            artistItem = QtWidgets.QTableWidgetItem(track.albumObj.artistName)
            artistItem.setFlags(artistItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetTracks.setItem(i,1,artistItem)

            albumItem = QtWidgets.QTableWidgetItem(track.albumObj.title)
            albumItem.setFlags(albumItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetTracks.setItem(i,2,albumItem)

            i+=1


    def showMediaList(self,ml,player):
        tracks = []
        self.mediaList = ml
        for i in range(ml.count()):
            m = ml.item_at_index(i)
            t = track("","")
            mrl = m.get_mrl()
            t.albumObj = player.getTrackAlbum(mrl)
            t.setMRL(mrl)
            t.getMutagenTags()
            tracks.append(t)

        self.showAlbumTracks(tracks)

    def showMediaList(self,player):
        tracks = []

        self.mediaList = player.mediaList
        self.player = player
        for i in range(self.mediaList.count()):
            m = self.mediaList.item_at_index(i)
            if m == None:
                print("BREAK ShowMediaList media="+str(i))
                break
            t = track("","")
            mrl = m.get_mrl()
            t.albumObj = player.getTrackAlbum(mrl)
            t.setMRL(mrl)
            t.getMutagenTags()
            tracks.append(t)

        self.showAlbumTracks(tracks)
        
        self.setCurrentTrack()

        self.initColumnHeaders()


    def setCurrentTrack(self):
        index = self.player.getCurrentIndexPlaylist()
        print("setCurrentTrack:"+str(index))
        for i in range(self.mediaList.count()):

            item = self.tableWidgetTracks.item(i,0)
            if item == None:
                print("BREAK setCurrentTrack item="+str(i))
                break

            f = item.font()
            if i == index:
                f.setBold(True)
                f.setItalic(True)
            else:
                f.setBold(False)
                f.setItalic(False)
            item.setFont(f)
            self.tableWidgetTracks.item(i,1).setFont(f)
            self.tableWidgetTracks.item(i,2).setFont(f)
            if i == index: self.tableWidgetTracks.setCurrentItem(item)




    def changeTrack(self,item):
        i = self.tableWidgetTracks.currentRow()

        self.trackChanged.emit(i)
