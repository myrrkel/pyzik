#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize, QCoreApplication
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QDialog, QPushButton, QVBoxLayout, \
QHeaderView, QHBoxLayout, QSlider, QSizePolicy, QFrame, QLabel, QShortcut, QListWidgetItem

from picFromUrlThread import *
from fullScreenCoverWidget import *

_translate = QCoreApplication.translate


class thumbnailItem(QListWidgetItem):
    def __init__(self,parent,url,thumb_url,name):
        self.url = url
        self.parent = parent
        self.thumbIcon = thumbnailIcon(self,thumb_url)
        QListWidgetItem.__init__(self,self.thumbIcon,name)

    def getURL(self):
        return self.url

    def addTempFile(self,path):
        self.parent.addTempFile(path)
        

class thumbnailIcon(QtGui.QIcon):

    def __init__(self,parent,url):
        QtGui.QIcon.__init__(self)
        self.parent = parent
        self.path = ""
        self.picFromUrlThread = picFromUrlThread()
        self.picFromUrlThread.downloadCompleted.connect(self.onPicDownloaded)
        self.picFromUrlThread.run(url)

    def onPicDownloaded(self,path):
        self.path = path
        self.parent.addTempFile(path)
        self.addFile(path)


class thumbnailViewerWidget(QDialog):
    
    def __init__(self,items):
        QDialog.__init__(self)
        self.items = items
        self.tempFiles = []
        self.selectedFile = ""
        self.fullScreenCover = fullScreenCoverWidget()
        self.picFromUrlThread = picFromUrlThread()
        self.picFromUrlThread.downloadCompleted.connect(self.onPicDownloaded)

        self.setWindowFlags(Qt.Window)
        self.initUI()
        self.show()


    def initUI(self):

        self.vLayout = QVBoxLayout()
        self.vLayout.setContentsMargins(6, 6, 6, 6)
        self.setLayout(self.vLayout)
        
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        self.setSizePolicy(sizePolicy)
        self.resize(550,400)

        self.thumbWidget = QListWidget(self)
        self.thumbWidget.setViewMode(QListWidget.IconMode)
        self.thumbWidget.setIconSize(QSize(200,200))

        self.vLayout.addWidget(self.thumbWidget)

        self.thumbWidget.itemDoubleClicked.connect(self.showItem)

        self.thumbWidget.itemSelected.connect(self.showItem)

    def onSelectedItem(self,item):
        self.selectedFile = item.path

    def showItem(self,item):
        self.fullScreenCover.show()
        self.picFromUrlThread.run(item.getURL())

    def onPicDownloaded(self,uri):
        self.fullScreenCover.setPixmapFromUri(uri)

    def addTempFile(self,path):
        self.tempFiles.append(path)

    def removeTempFiles(self):
        for i in range(len(self.tempFiles)-1,0):
            if tempFiles[i] != self.selectedFile:
                self.tempFiles.remove(i)

    def close(self):
        self.removeTempFiles()

    def addThumbnailItem(self,url,thumbURL,name):
        self.thumbWidget.addItem(thumbnailItem(self,url,thumbURL,name))

    # def showThumbnails(self):
    #     for thumb in self.items:
    #         thumbURL = thumb["image_thumbnail_url"]
    #         url = thumb["image_link"]
    #         height = thumb["image_height"]
    #         width = thumb["image_width"]
    #         name = str(height)+"x"+str(width)
    #         print("thumbURL="+thumbURL)
    #         self.addThumbnailItem(url,thumbURL,name)
