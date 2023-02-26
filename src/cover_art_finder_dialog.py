#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QSize, QCoreApplication
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QDialog,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)

from pic_from_url_thread import PicFromUrlThread
from thumbnail_viewer_widget import ThumbnailViewerWidget
from cover_art_finder import CoverArtFinder
from svg_icon import *
import logging

logger = logging.getLogger(__name__)

_translate = QCoreApplication.translate

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
from wait_overlay_widget import WaitOverlay


class CoverFinderSearchThread(QThread):
    """Read datas from files in the album folder"""

    doStop = False
    music_base = None
    resultFound = pyqtSignal(int, name="resultFound")

    coverFinder = None
    keyword = ""

    def run(self):
        try:
            self.coverFinder.search(self.keyword)
        except Exception as err:
            logger.error(err)
            pass
        self.resultFound.emit(1)
        self.quit()


class CoverArtFinderDialog(QDialog):
    signalCoverSaved = pyqtSignal(int, name="coverSaved")
    picFromUrlThread = None

    def __init__(self, album=None, parent=None):
        QDialog.__init__(self, parent)
        self.items = []
        self.album = album
        self.keyword = ""
        self.coverSaved = False

        self.coverFinder = CoverArtFinder()
        self.coverFinderThread = CoverFinderSearchThread()
        self.coverFinderThread.coverFinder = self.coverFinder
        self.coverFinderThread.resultFound.connect(self.onCoverFinderResult)

        if self.picFromUrlThread is None:
            self.picFromUrlThread = PicFromUrlThread()
        self.picFromUrlThread.downloadCompleted.connect(self.onSelectedPicDownloaded)

        self.setWindowFlags(Qt.Window)
        self.initUI()

    def initUI(self):
        # self.resize(650,400)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)

        self.centralWidget = QWidget(self)

        self.overlay = WaitOverlay(self)

        self.vLayout = QVBoxLayout()
        # self.vLayout = QGridLayout()
        self.vLayout.setContentsMargins(6, 6, 6, 6)
        self.centralWidget.setLayout(self.vLayout)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        self.centralWidget.setSizePolicy(sizePolicy)
        self.centralWidget.resize(652, 400)

        self.thumbViewer = ThumbnailViewerWidget(self.items)
        self.thumbViewer.thumbWidget.setSpacing(4)

        self.vLayout.addWidget(self.thumbViewer)

        self.btWidget = QWidget()
        self.vLayout.addWidget(self.btWidget)
        layBt = QHBoxLayout(self.btWidget)

        self.saveButton = QPushButton(_translate("coverArtFinder", "Save cover"))
        self.saveButton.setIcon(get_svg_icon("save.svg"))
        self.saveButton.clicked.connect(self.saveCover)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.saveButton.setSizePolicy(sizePolicy)

        layBt.addStretch()
        layBt.addWidget(self.saveButton)
        layBt.addStretch()

        self.thumbViewer.reset_selection()

        self.retranslateUi()

        self.overlay.showOverlay()

    def resizeEvent(self, event):
        self.overlay.resize(event.size())
        self.centralWidget.resize(event.size())

        event.accept()

    def showEvent(self, event):
        self.search()

    def search(self):
        if self.album is not None:
            self.keyword = self.album.get_cover_search_text()

        keyword = self.keyword

        print("CoverArtFinder search=" + keyword)

        self.coverFinderThread.coverFinder = self.coverFinder
        self.coverFinderThread.keyword = keyword
        self.coverFinderThread.start()

    def saveCover(self):
        url = self.thumbViewer.selectedURL
        if url != "":
            self.selectedFile = self.thumbViewer.selectedFile
            if self.selectedFile == "":
                self.picFromUrlThread.url = url
                self.picFromUrlThread.start()
            else:
                self.saveSelectedCover()

    def onSelectedPicDownloaded(self, uri):
        self.selectedFile = uri
        self.saveSelectedCover()

    def saveSelectedCover(self):
        self.album.cutCoverFromPath(self.selectedFile)
        self.coverSaved = True
        self.signalCoverSaved.emit(1)
        print("saveSelectedCover")
        self.close()

    def onCoverFinderResult(self, result):
        if not self.coverFinder.items:
            return
        self.items = self.coverFinder.items
        logger.debug("ITEMS : %s", self.items)
        self.showThumbnails()
        self.overlay.hide()

    def closeEvent(self, event):
        self.thumbViewer.thumbWidget.clear()
        self.thumbViewer.remove_temp_files(self.coverSaved)
        self.thumbViewer.reset_selection()
        self.close()

    def addThumbnailItem(self, url, thumbURL, name):
        self.thumbViewer.add_thumbnail_item(url, thumbURL, name)

    def showThumbnails(self):
        for thumb in self.items:
            thumbURL = thumb["image_thumbnail_url"]
            url = thumb["image_link"]
            height = thumb["image_height"]
            width = thumb["image_width"]
            name = str(height) + "x" + str(width)
            print("thumbURL=" + thumbURL)
            self.addThumbnailItem(url, thumbURL, name)

    def retranslateUi(self):
        self.saveButton.setText(_translate("coverArtFinder", "Save cover"))
        self.setWindowTitle(_translate("coverArtFinder", "Cover finder"))


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    caf = CoverArtFinderDialog()

    caf.show()

    sys.exit(app.exec_())
