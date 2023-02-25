import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread

import time


class LoadAlbumFilesThread(QThread):
    """Read datas from files in the album folder"""

    doStop = False
    album = None

    imagesLoaded = pyqtSignal(int, name="imagesLoaded")
    tracksLoaded = pyqtSignal(int, name="tracksLoaded")

    def run(self):
        self.doStop = False
        self.album.getImages()
        if self.doStop:
            return
        self.album.getCover()
        if self.doStop:
            return

        self.album.getTracks()
        if self.doStop:
            return
        self.tracksLoaded.emit(1)
        self.imagesLoaded.emit(1)
        self.quit()

    def stop(self):
        self.doStop = True
        self.album.setDoStop()
