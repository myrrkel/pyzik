#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PyQt5.QtCore import Qt, pyqtSignal, QCoreApplication, QSize
from PyQt5.QtWidgets import QDialog, QWidget, QShortcut, QAction, QWidget, QMainWindow, \
    QSizePolicy, QLabel, QFrame, QVBoxLayout, QHBoxLayout, QApplication, QPushButton
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence, QFont, QKeySequence

from track import Track
from history_manager import HistoryManager
from pic_from_url_thread import PicFromUrlThread
from global_constants import *


class CustomControlsWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        lay = QHBoxLayout(self)

        _translate = QCoreApplication.translate

        self.refreshButton = QPushButton(_translate("custom", "Refresh"))
        lay.addWidget(self.refreshButton)


class FullScreenWidget(QDialog):
    coverPixmap = None
    picFromUrlThread = None
    defaultPixmap = None

    def __init__(self, player=None):
        QDialog.__init__(self)
        self.player = player
        self.currentTrack = Track()
        self.currentCoverPath = ""
        self.picBufferManager = None
        self.setWindowFlags(
            Qt.Window
            | Qt.WindowStaysOnTopHint
            | Qt.MaximizeUsingFullscreenGeometryHint
            | Qt.FramelessWindowHint
        )

        self.initUI()

        if self.picFromUrlThread is None:
            self.picFromUrlThread = PicFromUrlThread()

        self.shortcutPause = QShortcut(QKeySequence("Space"), self)
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

        self.labelTitle = QLabel()
        sizePolicy = QSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelTitle.sizePolicy().hasHeightForWidth())
        self.labelTitle.setSizePolicy(sizePolicy)
        self.labelTitle.setMinimumSize(QSize(50, 70))
        font = QFont()
        font.setPointSize(12)
        self.labelTitle.setStyleSheet("color:white;")
        self.labelTitle.setFont(font)
        self.labelTitle.setAutoFillBackground(False)
        self.labelTitle.setFrameShape(QFrame.Box)
        self.labelTitle.setFrameShadow(QFrame.Raised)
        self.labelTitle.setLineWidth(1)
        self.labelTitle.setMidLineWidth(0)
        self.labelTitle.setTextFormat(Qt.RichText)
        self.labelTitle.setScaledContents(True)
        self.labelTitle.setAlignment(Qt.AlignCenter)

        self.vLayout.addWidget(self.labelTitle)

    def mousePressEvent(self, event):
        self.close()

    def connectPicDownloader(self, picDl):
        self.picFromUrlThread = picDl
        self.picFromUrlThread.downloadCompleted.connect(self.onPicDownloaded)

    def resizeEvent(self, event):
        self.resizeCover()

    def resizeCover(self):
        if not self.coverPixmap.isNull():
            scaledCover = self.coverPixmap.scaled(
                self.cover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.cover.setPixmap(scaledCover)

    def setCurrentTrack(self, title=""):
        if self.player is None:
            return

        if self.isVisible() == False:
            return

        self.currentTrack = self.player.get_current_track_playlist()

        self.showCover(self.currentTrack)

        self.setTitleLabel()

    def onPicDownloaded(self, path):
        print("fullscreenWidget onPicDownloaded=" + path)
        self.showCoverPixmap(path)

    def showCover(self, trk):
        if self.player.radioMode:
            coverUrl = self.player.get_live_cover_url()
            if coverUrl == "":
                rad = self.player.get_current_radio()
                if rad is not None:
                    coverUrl = rad.get_radio_pic()

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
                    coverPath = trk.parentAlbum.get_cover_path()
                    if self.currentCoverPath == coverPath:
                        return
                    self.currentCoverPath = coverPath
                    self.showCoverPixmap(coverPath)

    def showCoverPixmap(self, path):
        if self.picBufferManager is None:
            self.coverPixmap = QPixmap(path)
        else:
            self.coverPixmap = self.picBufferManager.getPic(path, "fullscreenWidget")

        scaledCover = self.coverPixmap.scaled(
            self.cover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.cover.setPixmap(scaledCover)
        self.cover.show()

    def setTitleLabel(self):
        artName = "Pyzik"
        albTitle = ""
        year = ""

        # orange = QtGui.QColor(216, 119, 0)
        colorName = orange.name()

        if self.currentTrack:
            if self.currentTrack.is_radio():
                artName = self.currentTrack.radio.name
                albTitle = self.currentTrack.radio.liveTrackTitle
                if albTitle == "":
                    albTitle = self.player.get_now_playing()
            else:
                artName = self.currentTrack.get_artist_name()
                albTitle = self.currentTrack.get_album_title()
                albTitle = albTitle + " - " + self.currentTrack.get_track_title()
                year = self.currentTrack.get_album_year()

        sAlbum = albTitle
        sYear = str(year)
        if not sYear in ["0", ""]:
            sAlbum += " (" + sYear + ")"
        sTitle = """<html><head/><body>
        <p><span style=\" color:{colorName}; font-size:28pt; text-shadow:white 0px 0px 4px; font-weight:600;\">{Artist}</span></p>
        <p><span style=\" color:{colorName}; font-size:20pt; font-style:italic;\">{Album}</span></p>
        </body></html>"""
        sTitle = sTitle.format(Artist=artName, Album=sAlbum, colorName=colorName)

        self.labelTitle.setText(sTitle)


if __name__ == "__main__":
    import sys
    from pic_downloader import PicDownloader

    app = QApplication(sys.argv)

    fs = FullScreenWidget()

    fs.show()

    url = "https://i3.radionomy.com/radios/400/ce7c17ce-4b4b-4698-8ed0-c2881eaf6e6b.png"
    pd = PicDownloader()
    tempPath = pd.getPic(url)
    fs.onPicDownloaded(tempPath)
    fs.setTitleLabel()

    # fs.showFullScreen()

    # tempPath = "/tmp/tmp8mfrufdl"
    # fs.setCoverPic(tempPath)

    # url = "C:\\Users\\MP05~1.OCT\\AppData\\Local\\Temp\\tmpp9wk96vu"
    # playlist.onPicDownloaded(url)

    sys.exit(app.exec_())
