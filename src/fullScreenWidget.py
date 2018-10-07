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
        self.setWindowFlags(
                            Qt.Window | 
                            Qt.WindowStaysOnTopHint | 
                            Qt.MaximizeUsingFullscreenGeometryHint | 
                            Qt.FramelessWindowHint )


        self.initUI()

        self.shortcutClose = QShortcut(QKeySequence("Escape"), self)
        self.shortcutClose.activated.connect(self.close)

        self.setCurrentTrack()
        self.cover.show()

    def show(self):
        self.showFullScreen()


    def initUI(self):

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)

        self.vLayout = QVBoxLayout()
        self.vLayout.setContentsMargins(6, 6, 6, 6)
        self.setLayout(self.vLayout)


        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        
        self.cover = QLabel()
        self.cover.setSizePolicy(sizePolicy)
        self.cover.setMinimumSize(QSize(400, 400))
        #self.cover.setMaximumSize(QSize(200, 200))
        self.cover.setAlignment(Qt.AlignCenter)
        self.coverPixmap = QPixmap()

        self.cover.setPixmap(self.coverPixmap)
        self.vLayout.addWidget(self.cover)

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
        trk = self.player.getCurrentTrackPlaylist()
        if trk:
            self.coverPixmap = trk.getCoverPixmap()

        if not self.coverPixmap.isNull():
            print("Pic size="+str(self.cover.size()))
            scaledCover = self.coverPixmap.scaled(self.cover.size(),
                                                    Qt.KeepAspectRatio,
                                                    Qt.SmoothTransformation)
            self.cover.setPixmap(scaledCover)
        else:
            self.cover.setPixmap(QtGui.QPixmap())
        self.cover.show()


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


    #fs.showFullScreen()

    #tempPath = "/tmp/tmp8mfrufdl"
    #fs.setCoverPic(tempPath)


    #url = "C:\\Users\\MP05~1.OCT\\AppData\\Local\\Temp\\tmpp9wk96vu"
    #playlist.onPicDownloaded(url)


    sys.exit(app.exec_())
