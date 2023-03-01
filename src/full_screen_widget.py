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

    def show(self):
        self.showFullScreen()
        self.set_background_black()
        self.set_current_track()

    def set_background_black(self):
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

    def connect_pic_downloader(self, picDl):
        self.picFromUrlThread = picDl
        self.picFromUrlThread.download_completed.connect(self.on_pic_downloaded)

    def resizeEvent(self, event):
        self.resize_cover()

    def resize_cover(self):
        if not self.coverPixmap.isNull():
            scaledCover = self.coverPixmap.scaled(
                self.cover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.cover.setPixmap(scaledCover)

    def set_current_track(self, title=""):
        if self.player is None:
            return

        if self.isVisible() == False:
            return

        self.currentTrack = self.player.get_current_track_playlist()

        self.show_cover(self.currentTrack)

        self.set_title_label()

    def on_pic_downloaded(self, path):
        print("fullscreenWidget onPicDownloaded=" + path)
        self.show_cover_pixmap(path)

    def show_cover(self, trk):
        if self.player.radio_mode:
            cover_url = self.player.get_live_cover_url()
            if cover_url == "":
                rad = self.player.get_current_radio()
                if rad is not None:
                    cover_url = rad.get_radio_pic()

            if self.currentCoverPath == cover_url:
                return

            if cover_url != "":
                self.currentCoverPath = cover_url
                self.picFromUrlThread.url = cover_url
                self.picFromUrlThread.start()

        else:
            if trk is not None and trk.parentAlbum is not None:
                print("fullscreenWidget trk.parentAlbum.cover=" + trk.parentAlbum.cover)
                if trk.parentAlbum.cover == "" or trk.parentAlbum.cover is None:
                    self.coverPixmap = self.defaultPixmap
                else:
                    cover_path = trk.parentAlbum.get_cover_path()
                    if self.currentCoverPath == cover_path:
                        return
                    self.currentCoverPath = cover_path
                    self.show_cover_pixmap(cover_path)

    def show_cover_pixmap(self, path):
        if self.picBufferManager is None:
            self.coverPixmap = QPixmap(path)
        else:
            self.coverPixmap = self.picBufferManager.get_pic(path, "fullscreenWidget")

        scaled_cover = self.coverPixmap.scaled(
            self.cover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.cover.setPixmap(scaled_cover)
        self.cover.show()

    def set_title_label(self):
        art_name = "Pyzik"
        alb_title = ""
        year = ""

        # orange = QtGui.QColor(216, 119, 0)
        color_name = ORANGE.name()

        if self.currentTrack:
            if self.currentTrack.is_radio():
                art_name = self.currentTrack.radio.name
                alb_title = self.currentTrack.radio.live_track_title
                if alb_title == "":
                    alb_title = self.player.get_now_playing()
            else:
                art_name = self.currentTrack.get_artist_name()
                alb_title = self.currentTrack.get_album_title()
                alb_title = alb_title + " - " + self.currentTrack.get_track_title()
                year = self.currentTrack.get_album_year()

        album = alb_title
        year = str(year)
        if year not in ["0", ""]:
            album += " (" + year + ")"
        title = f"""<html><head/><body>
        <p><span style=\" color:{color_name}; font-size:28pt; text-shadow:white 0px 0px 4px; font-weight:600;\">{art_name}</span></p>
        <p><span style=\" color:{color_name}; font-size:20pt; font-style:italic;\">{album}</span></p>
        </body></html>"""

        self.labelTitle.setText(title)


if __name__ == "__main__":
    import sys
    from pic_downloader import PicDownloader

    app = QApplication(sys.argv)

    fs = FullScreenWidget()

    fs.show()

    url = "https://i3.radionomy.com/radios/400/ce7c17ce-4b4b-4698-8ed0-c2881eaf6e6b.png"
    pd = PicDownloader()
    tempPath = pd.get_pic(url)
    fs.on_pic_downloaded(tempPath)
    fs.set_title_label()

    sys.exit(app.exec_())
