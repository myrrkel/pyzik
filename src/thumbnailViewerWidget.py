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
    def __init__(self, parent, url, thumb_url, name):
        self.url = url
        self.path = ""
        self.parent = parent
        self.title = name
        self.thumbIcon = thumbnailIcon(self, thumb_url)
        QListWidgetItem.__init__(self, self.thumbIcon, "")
        self.setHidden(True)
        self.setSizeHint(QSize(200, 220))

    def getURL(self):
        return self.url

    def addTempFile(self, path):
        self.parent.addTempFile(path)

    def setTitle(self):
        self.setText(self.title)


class thumbnailIcon(QtGui.QIcon):

    def __init__(self, parent, url):
        QtGui.QIcon.__init__(self)
        self.parent = parent
        self.path = ""
        self.picFromUrlThread = picFromUrlThread()
        self.picFromUrlThread.downloadCompleted.connect(self.onPicDownloaded)
        self.picFromUrlThread.url = url
        self.picFromUrlThread.start()

    def onPicDownloaded(self, path):
        self.path = path
        self.parent.path = self.path
        self.parent.addTempFile(path)
        self.addFile(path)
        self.parent.setIcon(self)
        self.parent.setTitle()
        # self.parent.parent.thumbWidget.setSpacing(4)
        self.parent.setHidden(False)


class thumbnailViewerWidget(QWidget):

    def __init__(self, items):
        QWidget.__init__(self)
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
        # self.show()

    def resetSelection(self):
        self.selectedFile = ""
        self.selectedURL = ""

    def initUI(self):
        self.vLayout = QVBoxLayout()
        self.vLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vLayout)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        self.setSizePolicy(sizePolicy)
        self.resize(600, 400)

        self.thumbWidget = QListWidget(self)
        self.thumbWidget.setViewMode(QListWidget.IconMode)
        self.thumbWidget.setResizeMode(QListWidget.Adjust)
        self.thumbWidget.setIconSize(QSize(200, 200))
        self.thumbWidget.setMovement(QListWidget.Static)

        self.vLayout.addWidget(self.thumbWidget)

        self.thumbWidget.itemDoubleClicked.connect(self.showItem)

        self.thumbWidget.itemClicked.connect(self.onSelectedItem)

    def onSelectedItem(self, item):
        print("SelectedURL=" + item.url)
        self.selectedURL = item.url
        self.selectedFile = ""

    def showItem(self, item):
        if self.isDownloading == False:
            self.fullScreenCover.show()
            self.fullScreenCover.initCover()
            self.picFromUrlThread.url = item.getURL()
            self.picFromUrlThread.start()

    def onPicDownloaded(self, uri):
        self.tempFiles.append(uri)
        self.selectedFile = uri
        self.isDownloading = False

        self.fullScreenCover.setPixmapFromUri(uri)
        # self.fullScreenCover.setBackgroundBlack()
        self.fullScreenCover.showFullScreen()
        # self.fullScreenCover.show()

    def addTempFile(self, path):
        self.tempFiles.append(path)

    def removeTempFiles(self, fileSaved=False):
        print("Remove temp thumb files:" + str(range(len(self.tempFiles))))
        for i in reversed(range(len(self.tempFiles))):
            uri = self.tempFiles[i]
            print("File n°" + str(i) + " =" + uri)
            if not (uri == self.selectedFile and fileSaved):
                if os.path.isfile(uri):
                    print("remove File=" + uri)
                    os.remove(uri)
                del self.tempFiles[i]

    def addThumbnailItem(self, url, thumbURL, name):
        self.thumbWidget.addItem(thumbnailItem(self, url, thumbURL, name))

    # def showThumbnails(self):
    #     for thumb in self.items:
    #         thumbURL = thumb["image_thumbnail_url"]
    #         url = thumb["image_link"]
    #         height = thumb["image_height"]
    #         width = thumb["image_width"]
    #         name = str(height)+"x"+str(width)
    #         print("thumbURL="+thumbURL)
    #         self.addThumbnailItem(url,thumbURL,name)
