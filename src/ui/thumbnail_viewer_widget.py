#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize, QCoreApplication
from PyQt5.QtWidgets import (
    QWidget,
    QListWidget,
    QVBoxLayout,
    QSizePolicy,
    QListWidgetItem,
)
from src.pic_from_url_thread import PicFromUrlThread
from .full_screen_cover_widget import FullScreenCoverWidget
import logging

logger = logging.getLogger(__name__)
_translate = QCoreApplication.translate


class ThumbnailItem(QListWidgetItem):
    def __init__(self, parent, url, thumb_url, name):
        self.url = url
        self.path = ""
        self.parent = parent
        self.title = name
        self.thumbIcon = ThumbnailIcon(self, thumb_url)
        QListWidgetItem.__init__(self, self.thumbIcon, "")
        self.setHidden(True)
        self.setSizeHint(QSize(200, 220))

    def get_url(self):
        return self.url

    def add_temp_file(self, path):
        self.parent.add_temp_file(path)

    def set_title(self):
        self.setText(self.title)


class ThumbnailIcon(QtGui.QIcon):
    def __init__(self, parent, url):
        QtGui.QIcon.__init__(self)
        self.parent = parent
        self.path = ""
        self.picFromUrlThread = PicFromUrlThread()
        self.picFromUrlThread.download_completed.connect(self.on_pic_downloaded)
        self.picFromUrlThread.url = url
        self.picFromUrlThread.start()

    def on_pic_downloaded(self, path):
        self.path = path
        if self.parent:
            try:
                self.parent.path = self.path
                self.parent.add_temp_file(path)
                self.addFile(path)
                self.parent.setIcon(self)
                self.parent.set_title()
                self.parent.setHidden(False)
            except Exception as err:
                logger.error(err)


class ThumbnailViewerWidget(QWidget):
    def __init__(self, items):
        QWidget.__init__(self)
        self.items = items
        self.temp_files = []
        self.selected_file = ""
        self.selected_url = ""
        self.is_downloading = False
        self.full_screen_cover = FullScreenCoverWidget()
        self.pic_from_url_thread = PicFromUrlThread()
        self.pic_from_url_thread.download_completed.connect(self.on_pic_downloaded)

        self.setWindowFlags(Qt.Window)
        self.init_ui()

    def reset_selection(self):
        self.selected_file = ""
        self.selected_url = ""

    def init_ui(self):
        self.vLayout = QVBoxLayout()
        self.vLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vLayout)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        self.setSizePolicy(sizePolicy)
        self.resize(600, 400)

        self.thumbWidget = QListWidget(self)
        self.thumbWidget.setViewMode(QListWidget.IconMode)
        self.thumbWidget.setResizeMode(QListWidget.Adjust)
        self.thumbWidget.setIconSize(QSize(200, 200))
        self.thumbWidget.setMovement(QListWidget.Static)

        self.vLayout.addWidget(self.thumbWidget)

        self.thumbWidget.itemDoubleClicked.connect(self.show_item)

        self.thumbWidget.itemClicked.connect(self.on_selected_item)

    def on_selected_item(self, item):
        print("SelectedURL=" + item.url)
        self.selected_url = item.url
        self.selected_file = ""

    def show_item(self, item):
        if not self.is_downloading:
            self.full_screen_cover.show()
            self.full_screen_cover.init_cover()
            self.pic_from_url_thread.url = item.get_url()
            self.pic_from_url_thread.start()

    def on_pic_downloaded(self, uri):
        self.temp_files.append(uri)
        self.selected_file = uri
        self.is_downloading = False

        self.full_screen_cover.set_pixmap_from_uri(uri)
        # self.fullScreenCover.setBackgroundBlack()
        self.full_screen_cover.showFullScreen()
        # self.fullScreenCover.show()

    def add_temp_file(self, path):
        self.temp_files.append(path)

    def remove_temp_files(self, file_saved=False):
        for i in reversed(range(len(self.temp_files))):
            uri = self.temp_files[i]
            if not (uri == self.selected_file and file_saved):
                if os.path.isfile(uri):
                    os.remove(uri)
                del self.temp_files[i]

    def add_thumbnail_item(self, url, thumbnail_url, name):
        self.thumbWidget.addItem(ThumbnailItem(self, url, thumbnail_url, name))

    # def showThumbnails(self):
    #     for thumb in self.items:
    #         thumbURL = thumb["image_thumbnail_url"]
    #         url = thumb["image_link"]
    #         height = thumb["image_height"]
    #         width = thumb["image_width"]
    #         name = str(height)+"x"+str(width)
    #         print("thumbURL="+thumbURL)
    #         self.addThumbnailItem(url,thumbURL,name)
