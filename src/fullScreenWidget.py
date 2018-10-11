#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PyQt5.QtCore import Qt, pyqtSignal, QCoreApplication, QSize
from PyQt5.QtWidgets import QDialog, QWidget, QShortcut, QAction, QWidget, QMainWindow, \
                            QSizePolicy, QLabel, QFrame, QVBoxLayout, QHBoxLayout, QApplication
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence

from historyManager import *


class customControlsWidget(QWidget):


    def __init__(self,parent=None):
        QWidget.__init__(self,parent=parent)

        lay = QHBoxLayout(self)
        
        _translate = QCoreApplication.translate

        self.refreshButton = QPushButton(_translate("custom", "Refresh"))
        lay.addWidget(self.refreshButton)


class fullScreenWidget(QDialog):
    

    def __init__(self,player=None):
        QDialog.__init__(self)
        self.player = player
        self.currentTrack = None
        self.setWindowFlags(
                            Qt.Window | 
                            Qt.WindowStaysOnTopHint | 
                            Qt.MaximizeUsingFullscreenGeometryHint | 
                            Qt.FramelessWindowHint )


        self.initUI()

        self.shortcutClose = QShortcut(QKeySequence("Escape"), self)
        self.shortcutClose.activated.connect(self.close)

        self.setCurrentTrack()
        self.setBackgroundBlack()
        self.setTitleLabel()
        #self.cover.show()

    def show(self):
        self.showFullScreen()
        self.setBackgroundBlack()


    def setBackgroundBlack(self):
        self.setStyleSheet("background-color:black;")

    def initUI(self):

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)

        self.vLayout = QVBoxLayout()
        self.vLayout.setContentsMargins(6, 6, 6, 6)
        self.vLayout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.vLayout)


        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        
        self.cover = QLabel()
        self.cover.setSizePolicy(sizePolicy)
        self.cover.setMinimumSize(QSize(300, 300))
        self.cover.setAlignment(Qt.AlignCenter)
        self.coverPixmap = QPixmap()

        self.cover.setPixmap(self.coverPixmap)
        self.vLayout.addWidget(self.cover)

        self.labelTitle = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelTitle.sizePolicy().hasHeightForWidth())
        self.labelTitle.setSizePolicy(sizePolicy)
        self.labelTitle.setMinimumSize(QtCore.QSize(50, 70))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelTitle.setStyleSheet("color:white;")
        self.labelTitle.setFont(font)
        self.labelTitle.setAutoFillBackground(False)
        self.labelTitle.setFrameShape(QtWidgets.QFrame.Box)
        self.labelTitle.setFrameShadow(QtWidgets.QFrame.Raised)
        self.labelTitle.setLineWidth(1)
        self.labelTitle.setMidLineWidth(0)
        self.labelTitle.setTextFormat(QtCore.Qt.RichText)
        self.labelTitle.setScaledContents(True)
        self.labelTitle.setAlignment(QtCore.Qt.AlignCenter)

        self.vLayout.addWidget(self.labelTitle)


    def mousePressEvent(self, event):
        print("clicked")
        self.close()


    def resizeEvent(self,event):
        self.resizeCover()


    def resizeCover(self):
        if (not self.coverPixmap.isNull()):
            scaledCover = self.coverPixmap.scaled(self.cover.size(),
                                                    Qt.KeepAspectRatio,
                                                    Qt.SmoothTransformation)
            self.cover.setPixmap(scaledCover)


    def setCurrentTrack(self,title=""):

        if self.player is None : return 

        #index = self.player.getCurrentIndexPlaylist()
        self.currentTrack = self.player.getCurrentTrackPlaylist()
        if self.currentTrack:
            self.coverPixmap = self.currentTrack.getCoverPixmap()

        if not self.coverPixmap.isNull():
            print("Pic size="+str(self.cover.size()))
            scaledCover = self.coverPixmap.scaled(self.cover.size(),
                                                    Qt.KeepAspectRatio,
                                                    Qt.SmoothTransformation)
            self.cover.setPixmap(scaledCover)
        else:
            self.cover.setPixmap(QtGui.QPixmap())
        self.cover.show()
        self.setTitleLabel()


    def onPicDownloaded(self,path):
        
        self.coverPixmap = QtGui.QPixmap(path)
        if not self.coverPixmap.isNull():
            print("onPicDownloaded="+path)
            print("Pic size="+str(self.cover.size()))
            scaledCover = self.coverPixmap.scaled(self.cover.size(),
                                                    Qt.KeepAspectRatio,
                                                    Qt.SmoothTransformation)
            self.cover.setPixmap(scaledCover)
        else:
            self.cover.setPixmap(QtGui.QPixmap())
        self.cover.show()


    def setTitleLabel(self):
        artName="ARTIST"
        albTitle="Album"
        year=""

        orange = QtGui.QColor(216, 119, 0)
        colorName = orange.name()

        if self.currentTrack:
            if self.currentTrack.isRadio():
                artName = self.currentTrack.radio.name
                albTitle = self.currentTrack.radio.liveTrackTitle
            else:
                artName = self.currentTrack.getArtistName()
                albTitle = self.currentTrack.getAlbumTitle()
                albTitle = albTitle + " - " + self.currentTrack.getTrackTitle()
                year = self.getAlbumYear()


        sAlbum = albTitle
        sYear =str(year)
        if(not sYear in ["0",""]): sAlbum += " ("+sYear+")"
        sTitle = '''<html><head/><body>
        <p><span style=\" color:{colorName}; font-size:28pt; font-weight:600;\">{Artist}</span></p>
        <p><span style=\" color:{colorName}; font-size:20pt; font-style:italic;\">{Album}</span></p>
        </body></html>'''
        sTitle = sTitle.format(Artist=artName,Album=sAlbum, colorName=colorName)
        
        self.labelTitle.setText(sTitle)

if __name__ == "__main__":
    import sys
    from picDownloader import *

    app = QApplication(sys.argv)


    fs = fullScreenWidget()

    fs.show()

    url = "https://i3.radionomy.com/radios/400/ce7c17ce-4b4b-4698-8ed0-c2881eaf6e6b.png"
    pd = picDownloader()
    tempPath = pd.getPic(url)
    fs.onPicDownloaded(tempPath)
    fs.setTitleLabel()

    #fs.showFullScreen()

    #tempPath = "/tmp/tmp8mfrufdl"
    #fs.setCoverPic(tempPath)


    #url = "C:\\Users\\MP05~1.OCT\\AppData\\Local\\Temp\\tmpp9wk96vu"
    #playlist.onPicDownloaded(url)


    sys.exit(app.exec_())
