#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize, QCoreApplication
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QDialog, QPushButton, QVBoxLayout, \
QHeaderView, QHBoxLayout, QSlider, QSizePolicy, QFrame, QLabel, QShortcut, QListWidgetItem

from picFromUrlThread import *
from fullScreenCoverWidget import *
from thumbnailViewerWidget import *
from coverArtFinder import *
from svgIcon import *

_translate = QCoreApplication.translate


class coverArtFinderDialog(QDialog):
    
    def __init__(self,album=None):
        QDialog.__init__(self)
        self.items = []
        self.album = album
        self.selectedFile = ""
        self.coverFinder = CoverArtFinder()
        self.search()

        self.thumbViewer = thumbnailViewerWidget(self.items)

    
    
        self.setWindowFlags(Qt.Window)
        self.initUI()
        self.show()
        self.showThumbnails()

    def initUI(self):

        self.vLayout = QVBoxLayout()
        self.vLayout.setContentsMargins(6, 6, 6, 6)
        self.setLayout(self.vLayout)
        
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        self.setSizePolicy(sizePolicy)
        self.resize(550,400)

        self.vLayout.addWidget(self.thumbViewer)

        layBt = QHBoxLayout(self)
        
        #layBt.addStretch()
        self.saveButton = QPushButton(_translate("history", "Save cover"))
        self.saveButton.setIcon(getSvgIcon("save.svg"))
        self.vLayout.addWidget(self.saveButton)


    def saveCover(self):
        

    def search(self):

        if self.album is not None:
            keyword = self.album.getCoverSearchText()+ " album"
            self.coverFinder.search(keyword)
            self.items = self.coverFinder.items


    def close(self):
        self.removeTempFiles()

    def addThumbnailItem(self,url,thumbURL,name):
        self.thumbViewer.addThumbnailItem(url,thumbURL,name)


    def showThumbnails(self):
        for thumb in self.items:
            thumbURL = thumb["image_thumbnail_url"]
            url = thumb["image_link"]
            height = thumb["image_height"]
            width = thumb["image_width"]
            name = str(height)+"x"+str(width)
            print("thumbURL="+thumbURL)
            self.addThumbnailItem(url,thumbURL,name)




if __name__ == '__main__':

    import sys
    
    app = QApplication(sys.argv)
    caf = coverArtFinderDialog()

    caf.show()


    sys.exit(app.exec_())