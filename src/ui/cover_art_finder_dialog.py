#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QCoreApplication, pyqtSignal, QThread
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QDialog,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)

from src.pic_from_url_thread import PicFromUrlThread
from src.cover_art_finder import CoverArtFinder
import src.svg_icon as svg

from .wait_overlay_widget import WaitOverlay
from .thumbnail_viewer_widget import ThumbnailViewerWidget
import logging

logger = logging.getLogger(__name__)

_translate = QCoreApplication.translate


class CoverFinderSearchThread(QThread):
    """Search image"""

    do_stop = False
    music_base = None
    result_found = pyqtSignal(int, name="resultFound")

    cover_finder = CoverArtFinder()
    keyword = ""

    def run(self):
        try:
            self.cover_finder.search(self.keyword)
        except Exception as err:
            logger.error(err)
            pass
        self.result_found.emit(1)
        self.quit()


class CoverArtFinderDialog(QDialog):
    signal_cover_saved = pyqtSignal(int, name="coverSaved")
    pic_from_url_thread = None
    selected_file = ''

    def __init__(self, album=None, parent=None):
        QDialog.__init__(self, parent)
        self.items = []
        self.album = album
        self.keyword = ""
        self.cover_saved = False

        self.cover_finder_thread = CoverFinderSearchThread()
        self.cover_finder = self.cover_finder_thread.cover_finder
        self.cover_finder_thread.result_found.connect(self.on_cover_finder_result)

        if not self.pic_from_url_thread:
            self.pic_from_url_thread = PicFromUrlThread()
        self.pic_from_url_thread.download_completed.connect(self.on_selected_pic_downloaded)

        self.setWindowFlags(Qt.Window)
        self.init_ui()

    def init_ui(self):
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
        self.saveButton.setIcon(svg.get_svg_icon("save.svg"))
        self.saveButton.clicked.connect(self.save_cover)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.saveButton.setSizePolicy(sizePolicy)

        layBt.addStretch()
        layBt.addWidget(self.saveButton)
        layBt.addStretch()

        self.thumbViewer.reset_selection()

        self.retranslateUi()

        self.overlay.show_overlay()

    def resizeEvent(self, event):
        self.overlay.resize(event.size())
        self.centralWidget.resize(event.size())
        event.accept()

    def showEvent(self, event):
        self.search()

    def search(self):
        if self.album:
            self.keyword = self.album.get_cover_search_text()
        self.cover_finder_thread.keyword = self.keyword
        self.cover_finder_thread.start()

    def save_cover(self):
        url = self.thumbViewer.selected_url
        if url != "":
            self.selected_file = self.thumbViewer.selected_file
            if self.selected_file == "":
                self.pic_from_url_thread.url = url
                self.pic_from_url_thread.start()
            else:
                self.album.cover = ''
                self.save_selected_cover()

    def on_selected_pic_downloaded(self, uri):
        self.selected_file = uri
        self.save_selected_cover()

    def save_selected_cover(self):
        self.album.cut_cover_from_path(self.selected_file)
        self.cover_saved = True
        self.album.cover_saved = True
        self.album.cover = ''
        self.signal_cover_saved.emit(1)
        self.close()

    def on_cover_finder_result(self, result):
        if not self.cover_finder.items:
            return
        self.items = self.cover_finder.items
        logger.debug("ITEMS : %s", self.items)
        self.show_thumbnails()
        self.overlay.hide()

    def closeEvent(self, event):
        self.thumbViewer.thumbWidget.clear()
        self.thumbViewer.remove_temp_files(self.cover_saved)
        self.thumbViewer.reset_selection()
        self.overlay.kill_timer()
        self.close()

    def add_thumbnail_item(self, url, thumbnail_url, name):
        self.thumbViewer.add_thumbnail_item(url, thumbnail_url, name)

    def show_thumbnails(self):
        for thumb in self.items:
            thumbnail_url = thumb["image_thumbnail_url"]
            url = thumb["image_link"]
            height = thumb["image_height"]
            width = thumb["image_width"]
            name = str(height) + "x" + str(width)
            print("thumbnail_url=" + thumbnail_url)
            self.add_thumbnail_item(url, thumbnail_url, name)

    def retranslateUi(self):
        self.saveButton.setText(_translate("coverArtFinder", "Save cover"))
        self.setWindowTitle(_translate("coverArtFinder", "Cover finder"))


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    caf = CoverArtFinderDialog()

    caf.show()

    sys.exit(app.exec_())
