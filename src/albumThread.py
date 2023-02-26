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
        self.album.get_images()
        if self.doStop:
            return
        self.album.get_cover()
        if self.doStop:
            return

        self.album.get_tracks()
        if self.doStop:
            return
        self.tracksLoaded.emit(1)
        self.imagesLoaded.emit(1)
        self.quit()

    def stop(self):
        self.doStop = True
        self.album.setDoStop()
