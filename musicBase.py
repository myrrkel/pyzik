#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from albumCollection import *
from artistCollection import *
from musicDirectoryCollection import *
import os.path
from PyQt5 import QtWidgets, QtGui, QtCore




class musicBase:
    """
    musicBase manage albums and artists from
     the music directories to the database'''
    """

    def __init__(self):
        self.albumCol = albumCollection(self)
        self.artistCol = artistCollection()
        self.musicDirectoryCol = musicDirectoryCollection()

    def loadMusicBase(self):
        self.musicDirectoryCol.loadMusicDirectories()
        self.artistCol.loadArtists()
        self.albumCol.loadAlbums()
        self.addAlbumsToArtists()


    def exploreAlbumsDirectories(self):
        for mdir in self.musicDirectoryCol.musicDirectories:
            print("Dir="+mdir.dirPath)
            mdir.artistCol = self.artistCol
            mdir.albumCol = self.albumCol
            mdir.exploreAlbumsDirectory()
        self.artistCol.sortArtists()



    def addAlbumsToArtists(self):
        for alb in self.albumCol.albums:
            artist_found = self.artistCol.getArtistByID(alb.artistID)
            if (artist_found != None):
                artist_found.albums.append(alb)


    def emptyDatas(self):
        self.artistCol.artists = []
        self.albumCol.albums = []
        #self.musicDirectoryCol.musicDirectories = []



class ProgressBarWidget(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(ProgressBarWidget, self).__init__(parent)
        layout = QtGui.QVBoxLayout(self)       

        self.progressBar = QtGui.QProgressBar(self)
        self.progressBar.setRange(0,100)
        button = QtGui.QPushButton("Start", self)
        layout.addWidget(self.progressBar)
        layout.addWidget(button)

        button.clicked.connect(self.onStart)

        self.myLongTask = TaskThread()
        self.myLongTask.notifyProgress.connect(self.onProgress)


    def onStart(self):
        self.myLongTask.start()

    def onProgress(self, i):
        self.progressBar.setValue(i)


class TaskThread(QtCore.QThread):
    notifyProgress = QtCore.pyqtSignal(int)
    def run(self):
        for i in range(101):
            self.notifyProgress.emit(i)
            time.sleep(0.1)