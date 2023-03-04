#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, pyqtSignal, QCoreApplication, QSize
from PyQt5.QtWidgets import (
    QDialog,
    QWidget,
    QShortcut,
    QAction,
    QWidget,
    QMainWindow,
    QSizePolicy,
    QLabel,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QApplication,
)
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence


class FullScreenCoverWidget(QDialog):
    coverPixmap = None

    def __init__(self):
        QDialog.__init__(self)

        self.currentCoverPath = ""
        self.picBufferManager = None

        self.setWindowFlags(
            Qt.Window
            | Qt.WindowStaysOnTopHint
            | Qt.MaximizeUsingFullscreenGeometryHint
            | Qt.FramelessWindowHint
        )

        # self.shortcutPause = QShortcut(QtGui.QKeySequence("Space"), self)
        # self.shortcutPause.activated.connect(self.player.pause)
        self.shortcutClose = QShortcut(QKeySequence("Escape"), self)
        self.shortcutClose.activated.connect(self.close)

        self.vLayout = QVBoxLayout()
        self.vLayout.setContentsMargins(6, 6, 6, 6)
        self.vLayout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.vLayout)

        self.initUI()

        self.set_background_black()

    def show(self):
        self.set_background_black()
        self.showFullScreen()

    def set_background_black(self):
        self.setStyleSheet("background-color:black;")

    def initUI(self):
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

    def mousePressEvent(self, event):
        self.close()

    def resizeEvent(self, event):
        self.resize_cover()

    def resize_cover(self):
        if not self.coverPixmap.isNull():
            scaled_cover = self.coverPixmap.scaled(self.cover.size(),
                                                   Qt.KeepAspectRatio,
                                                   Qt.SmoothTransformation)
            self.cover.setPixmap(scaled_cover)

    def set_pixmap_from_uri(self, path):
        if self.picBufferManager is None:
            self.coverPixmap = QPixmap(path)
        else:
            self.coverPixmap = self.picBufferManager.get_pic(path)

        self.show_cover()

    def show_cover(self):
        if not self.coverPixmap.isNull():
            print("Pic size=" + str(self.cover.size()))
            scaled_cover = self.coverPixmap.scaled(
                self.cover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.cover.setPixmap(scaled_cover)
        else:
            self.cover.setPixmap(QPixmap())
        self.cover.show()

    def init_cover(self):
        self.coverPixmap = QPixmap()
        self.show_cover()


if __name__ == "__main__":
    import sys
    from pic_downloader import PicDownloader

    app = QApplication(sys.argv)

    fs = FullScreenCoverWidget()

    fs.show()

    url = "https://i3.radionomy.com/radios/400/ce7c17ce-4b4b-4698-8ed0-c2881eaf6e6b.png"
    pd = PicDownloader()
    tempPath = pd.get_pic(url)
    fs.set_pixmap_from_uri(tempPath)

    sys.exit(app.exec_())
