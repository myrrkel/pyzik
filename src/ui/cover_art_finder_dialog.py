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

        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(100)
        size_policy.setVerticalStretch(100)

        self.central_widget = QWidget(self)

        self.overlay = WaitOverlay(self)

        self.vertical_layout = QVBoxLayout()
        # self.vLayout = QGridLayout()
        self.vertical_layout.setContentsMargins(6, 6, 6, 6)
        self.central_widget.setLayout(self.vertical_layout)

        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(100)
        size_policy.setVerticalStretch(100)
        self.central_widget.setSizePolicy(size_policy)
        self.central_widget.resize(652, 400)

        self.thumb_viewer = ThumbnailViewerWidget(self.items)
        self.thumb_viewer.thumbWidget.setSpacing(4)

        self.vertical_layout.addWidget(self.thumb_viewer)

        self.bottom_buttons_widget = QWidget()
        self.vertical_layout.addWidget(self.bottom_buttons_widget)
        bottom_buttons_layout = QHBoxLayout(self.bottom_buttons_widget)

        self.save_button = QPushButton(_translate("coverArtFinder", "Save cover"))
        self.save_button.setIcon(svg.get_svg_icon("save.svg"))
        self.save_button.clicked.connect(self.save_cover)
        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.save_button.setSizePolicy(size_policy)

        bottom_buttons_layout.addStretch()
        bottom_buttons_layout.addWidget(self.save_button)
        bottom_buttons_layout.addStretch()

        self.thumb_viewer.reset_selection()

        self.retranslateUi()

        self.overlay.show_overlay()

    def resizeEvent(self, event):
        self.overlay.resize(event.size())
        self.central_widget.resize(event.size())
        event.accept()

    def showEvent(self, event):
        self.search()

    def search(self, keyword=''):
        if keyword:
            self.keyword = keyword
        elif self.album:
            self.keyword = self.album.get_cover_search_text()
        self.cover_finder_thread.keyword = self.keyword
        self.cover_finder_thread.start()

    def save_cover(self):
        url = self.thumb_viewer.selected_url
        if url != "":
            self.selected_file = self.thumb_viewer.selected_file
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
        self.thumb_viewer.thumbWidget.clear()
        self.thumb_viewer.remove_temp_files(self.cover_saved)
        self.thumb_viewer.reset_selection()
        self.overlay.kill_timer()
        self.close()

    def add_thumbnail_item(self, url, thumbnail_url, name):
        self.thumb_viewer.add_thumbnail_item(url, thumbnail_url, name)

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
        self.save_button.setText(_translate("coverArtFinder", "Save cover"))
        self.setWindowTitle(_translate("coverArtFinder", "Cover finder"))


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    caf = CoverArtFinderDialog()

    caf.show()

    sys.exit(app.exec_())
