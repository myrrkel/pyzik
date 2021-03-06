#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PyQt5.QtCore import Qt, pyqtSignal, QCoreApplication, QSize
from PyQt5.QtWidgets import QDialog, QWidget, QShortcut, QAction, QWidget, QMainWindow, \
    QSizePolicy, QLabel, QFrame, QVBoxLayout, QHBoxLayout, QApplication
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence

from historyManager import *
from picFromUrlThread import *


class customControlsWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        lay = QHBoxLayout(self)

        _translate = QCoreApplication.translate

        self.refreshButton = QPushButton(_translate("custom", "Refresh"))
        lay.addWidget(self.refreshButton)


class fullScreenWidget(QDialog):
    coverPixmap = None
    picFromUrlThread = None

    def __init__(self, player=None):
        QDialog.__init__(self)
        self.player = player
        self.currentTrack = None
        self.currentCoverPath = ""
        self.picBufferManager = None
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowStaysOnTopHint |
            Qt.MaximizeUsingFullscreenGeometryHint |
            Qt.FramelessWindowHint)

        self.initUI()

        if self.picFromUrlThread is None:
            self.picFromUrlThread = picFromUrlThread()

        self.shortcutPause = QShortcut(QtGui.QKeySequence("Space"), self)
        if self.player is not None:
            self.shortcutPause.activated.connect(self.player.pause)
        self.shortcutClose = QShortcut(QKeySequence("Escape"), self)
        self.shortcutClose.activated.connect(self.close)

        # self.setCurrentTrack()
        # self.setBackgroundBlack()
        # self.setTitleLabel()
        # self.cover.show()

    def show(self):
        self.showFullScreen()
        self.setBackgroundBlack()
        self.setCurrentTrack()

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
        self.close()

    def connectPicDownloader(self, picDl):
        self.picFromUrlThread = picDl
        self.picFromUrlThread.downloadCompleted.connect(self.onPicDownloaded)

    def resizeEvent(self, event):
        self.resizeCover()

    def resizeCover(self):
        if (not self.coverPixmap.isNull()):
            scaledCover = self.coverPixmap.scaled(self.cover.size(),
                                                  Qt.KeepAspectRatio,
                                                  Qt.SmoothTransformation)
            self.cover.setPixmap(scaledCover)

    def setCurrentTrack(self, title=""):

        if self.player is None: return

        if self.isVisible() == False: return

        self.currentTrack = self.player.getCurrentTrackPlaylist()

        self.showCover(self.currentTrack)

        self.setTitleLabel()

    def onPicDownloaded(self, path):
        print("fullscreenWidget onPicDownloaded=" + path)
        self.showCoverPixmap(path)

    def showCover(self, trk):

        if self.player.radioMode:
            coverUrl = self.player.getLiveCoverUrl()
            if coverUrl == "":
                rad = self.player.getCurrentRadio()
                if rad is not None:
                    coverUrl = rad.getRadioPic()

            if self.currentCoverPath == coverUrl:
                return

            if coverUrl != "":
                self.currentCoverPath = coverUrl
                self.picFromUrlThread.url = coverUrl
                self.picFromUrlThread.start()

        else:
            # self.picFromUrlThread.resetLastURL()
            if trk is not None and trk.parentAlbum is not None:
                print("fullscreenWidget trk.parentAlbum.cover=" + trk.parentAlbum.cover)
                if trk.parentAlbum.cover == "" or trk.parentAlbum.cover is None:
                    self.coverPixmap = self.defaultPixmap
                else:
                    coverPath = trk.parentAlbum.getCoverPath()
                    if self.currentCoverPath == coverPath:
                        return
                    self.currentCoverPath = coverPath
                    self.showCoverPixmap(coverPath)

    def showCoverPixmap(self, path):
        if self.picBufferManager is None:
            self.coverPixmap = QPixmap(path)
        else:
            self.coverPixmap = self.picBufferManager.getPic(path, "fullscreenWidget")

        scaledCover = self.coverPixmap.scaled(self.cover.size(),
                                              Qt.KeepAspectRatio,
                                              Qt.SmoothTransformation)
        self.cover.setPixmap(scaledCover)
        self.cover.show()

    def setTitleLabel(self):
        artName = "Pyzik"
        albTitle = ""
        year = ""

        # orange = QtGui.QColor(216, 119, 0)
        colorName = orange.name()

        if self.currentTrack:
            if self.currentTrack.isRadio():
                artName = self.currentTrack.radio.name
                albTitle = self.currentTrack.radio.liveTrackTitle
                if albTitle == "":
                    albTitle = self.player.getNowPlaying()
            else:
                artName = self.currentTrack.getArtistName()
                albTitle = self.currentTrack.getAlbumTitle()
                albTitle = albTitle + " - " + self.currentTrack.getTrackTitle()
                year = self.currentTrack.getAlbumYear()

        sAlbum = albTitle
        sYear = str(year)
        if (not sYear in ["0", ""]): sAlbum += " (" + sYear + ")"
        sTitle = '''<html><head/><body>
        <p><span style=\" color:{colorName}; font-size:28pt; text-shadow:white 0px 0px 4px; font-weight:600;\">{Artist}</span></p>
        <p><span style=\" color:{colorName}; font-size:20pt; font-style:italic;\">{Album}</span></p>
        </body></html>'''
        sTitle = sTitle.format(Artist=artName, Album=sAlbum, colorName=colorName)

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

    # fs.showFullScreen()

    # tempPath = "/tmp/tmp8mfrufdl"
    # fs.setCoverPic(tempPath)

    # url = "C:\\Users\\MP05~1.OCT\\AppData\\Local\\Temp\\tmpp9wk96vu"
    # playlist.onPicDownloaded(url)

    sys.exit(app.exec_())
