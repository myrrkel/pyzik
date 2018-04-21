#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from urllib.parse import unquote
from track import *

class playlistWidget(QtWidgets.QDialog):
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
        self.tableWidgetTracks.setColumnCount(3)
        self.tableWidgetTracks.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(2, item)

        _translate = QtCore.QCoreApplication.translate
        item = self.tableWidgetTracks.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Title"))
        item = self.tableWidgetTracks.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Duration"))
        item = self.tableWidgetTracks.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "ID"))

        self.tableWidgetTracks.setRowCount(0)
        hHeader = self.tableWidgetTracks.horizontalHeader()
        vHeader = self.tableWidgetTracks.verticalHeader()
        vHeader.hide()
        hHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        hHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        hHeader.hideSection(2)

        layout.addWidget(self.tableWidgetTracks)

        self.setWindowTitle("Playlist")
        self.show()



    def showAlbumTracks(self,tracks):        
        self.tableWidgetTracks.setColumnCount(1)
        self.tableWidgetTracks.setRowCount(0)
        i=0
        for track in tracks:
            self.tableWidgetTracks.insertRow(i)
            titleItem = QtWidgets.QTableWidgetItem(track.title)
            titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetTracks.setItem(i,0,titleItem)
            i+=1


    def showMediaList(self,ml):
        tracks = []
        for i in range(ml.count()):
            m = ml.item_at_index(i)
            t = track("","")
            path = unquote(m.get_mrl())
            t.setPath(path.replace("file://",""))
            t.getMutagenTags()
            tracks.append(t)

        self.showAlbumTracks(tracks)
