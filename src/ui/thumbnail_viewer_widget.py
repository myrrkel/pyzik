#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize, QCoreApplication
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QListWidget,
    QDialog,
    QPushButton,
    QVBoxLayout,
    QHeaderView,
    QHBoxLayout,
    QSlider,
    QSizePolicy,
    QFrame,
    QLabel,
    QShortcut,
    QListWidgetItem,
)
import os
from src.pic_from_url_thread import PicFromUrlThread
from .full_screen_cover_widget import FullScreenCoverWidget

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
        self.parent.path = self.path
        self.parent.add_temp_file(path)
        self.addFile(path)
        self.parent.setIcon(self)
        self.parent.set_title()
        # self.parent.parent.thumbWidget.setSpacing(4)
        self.parent.setHidden(False)


class ThumbnailViewerWidget(QWidget):
    def __init__(self, items):
        QWidget.__init__(self)
        self.items = items
        self.tempFiles = []
        self.selectedFile = ""
        self.selectedURL = ""
        self.isDownloading = False
        self.fullScreenCover = FullScreenCoverWidget()
        self.picFromUrlThread = PicFromUrlThread()
        self.picFromUrlThread.download_completed.connect(self.on_pic_downloaded)

        self.setWindowFlags(Qt.Window)
        self.initUI()
        # self.show()

    def reset_selection(self):
        self.selectedFile = ""
        self.selectedURL = ""

    def initUI(self):
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
        self.selectedURL = item.url
        self.selectedFile = ""

    def show_item(self, item):
        if self.isDownloading == False:
            self.fullScreenCover.show()
            self.fullScreenCover.init_cover()
            self.picFromUrlThread.url = item.get_url()
            self.picFromUrlThread.start()

    def on_pic_downloaded(self, uri):
        self.tempFiles.append(uri)
        self.selectedFile = uri
        self.isDownloading = False

        self.fullScreenCover.set_pixmap_from_uri(uri)
        # self.fullScreenCover.setBackgroundBlack()
        self.fullScreenCover.showFullScreen()
        # self.fullScreenCover.show()

    def add_temp_file(self, path):
        self.tempFiles.append(path)

    def remove_temp_files(self, fileSaved=False):
        print("Remove temp thumb files:" + str(range(len(self.tempFiles))))
        for i in reversed(range(len(self.tempFiles))):
            uri = self.tempFiles[i]
            print("File n°" + str(i) + " =" + uri)
            if not (uri == self.selectedFile and fileSaved):
                if os.path.isfile(uri):
                    print("remove File=" + uri)
                    os.remove(uri)
                del self.tempFiles[i]

    def add_thumbnail_item(self, url, thumbURL, name):
        self.thumbWidget.addItem(ThumbnailItem(self, url, thumbURL, name))

    # def showThumbnails(self):
    #     for thumb in self.items:
    #         thumbURL = thumb["image_thumbnail_url"]
    #         url = thumb["image_link"]
    #         height = thumb["image_height"]
    #         width = thumb["image_width"]
    #         name = str(height)+"x"+str(width)
    #         print("thumbURL="+thumbURL)
    #         self.addThumbnailItem(url,thumbURL,name)
