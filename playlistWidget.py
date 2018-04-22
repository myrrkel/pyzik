#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from track import *

class playlistWidget(QtWidgets.QDialog):
    
    mediaList = None
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

        self.tableWidgetTracks = QtWidgets.QTableWidget(self)
        self.tableWidgetTracks.setGeometry(0, 0, 300, 250)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.tableWidgetTracks.sizePolicy().hasHeightForWidth())
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
        hHeader = self.tableWidgetTracks.horizontalHeader()
        vHeader = self.tableWidgetTracks.verticalHeader()
        vHeader.hide()
        hHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        hHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        hHeader.hideSection(4)

        layout.addWidget(self.tableWidgetTracks)

        self.tableWidgetTracks.cellDoubleClicked.connect(self.changeTrack)

        self.setWindowTitle("Playlist")
        self.show()



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
            print("track.albumObj.title:"+track.albumObj.title)
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
            #path = unquote(m.get_mrl())
            #t.setPath(path.replace("file://",""))
            t.setMRL(mrl)
            t.getMutagenTags()
            tracks.append(t)

        self.showAlbumTracks(tracks)


    def setCurrentTrack(self,track_media):
        index = self.mediaList.index_of_item(track_media)
        print("setCurrentTrack:"+str(index))
        #selModel = self.tableWidgetTracks.selectionModel()
        #selModel.reset()
        item = self.tableWidgetTracks.item(index,0)
        self.tableWidgetTracks.setCurrentItem(item)
        #selModel.select(item.index(), QtCore.QItemSelectionModel.Select)
        #self.showAlbums(item.artist)

        #self.tableWidgetTracks.selectRow(index)



    def changeTrack(self,item):
        i = self.tableWidgetTracks.currentRow()

        self.trackChanged.emit(i)
