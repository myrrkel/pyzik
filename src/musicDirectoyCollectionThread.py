import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread

import time


class loadAlbumFilesThread(QThread):
    """Read datas from files in the album folder"""

    doStop = False
    album = None
    player = None
    imagesLoaded = pyqtSignal(int, name='imagesLoaded')
    tracksLoaded = pyqtSignal(int, name='tracksLoaded')

    def run(self):
        self.doStop = False
        self.album.getImages()
        if self.doStop: return
        self.album.getCover()
        self.imagesLoaded.emit(1)
        if self.doStop: return
        self.album.getTracks(self.player)
        self.tracksLoaded.emit(1)
        return

    def stop(self):
        self.doStop = True
        self.album.setDoStop()
