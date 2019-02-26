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
        self.path = ""
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
        self.parent.path = self.path
        self.parent.addTempFile(path)
        self.addFile(path)


class thumbnailViewerWidget(QDialog):
    
    def __init__(self,items):
        QDialog.__init__(self)
        self.items = items
        self.tempFiles = []
        self.selectedFile = ""
        self.selectedURL = ""
        self.isDownloading = False
        self.fullScreenCover = fullScreenCoverWidget()
        self.picFromUrlThread = picFromUrlThread()
        self.picFromUrlThread.downloadCompleted.connect(self.onPicDownloaded)

        self.setWindowFlags(Qt.Window)
        self.initUI()
        self.show()

    def resetSelection(self):
        self.selectedFile = ""
        self.selectedURL = ""


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
        #self.thumbWidget.setViewMode(QListWidget.IconMode)
        self.thumbWidget.setIconSize(QSize(200,200))

        self.vLayout.addWidget(self.thumbWidget)

        self.thumbWidget.itemDoubleClicked.connect(self.showItem)

        self.thumbWidget.itemClicked.connect(self.onSelectedItem)

    def onSelectedItem(self,item):
        print("SelectedURL="+item.url)
        self.selectedURL = item.url
        self.selectedFile = ""

    def showItem(self,item):
        if self.isDownloading == False:
            self.fullScreenCover.show()
            self.picFromUrlThread.run(item.getURL())


    def onPicDownloaded(self,uri):
        self.tempFiles.append(uri)
        self.selectedFile = uri
        self.isDownloading = False

        self.fullScreenCover.setPixmapFromUri(uri)
        self.fullScreenCover.show()

    def addTempFile(self,path):
        self.tempFiles.append(path)

    def removeTempFiles(self,fileSaved=False):
        print("Remove temp thumb files:"+str(range(len(self.tempFiles))))
        for i in reversed(range(len(self.tempFiles))):

            print("File n°"+str(i)+" ="+self.tempFiles[i])
            if not (self.tempFiles[i] == self.selectedFile and fileSaved):
                print("remove File="+self.tempFiles[i])
                os.remove(self.tempFiles[i])
                del self.tempFiles[i]
                


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
