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
        if self.doStop: self.quit()
        self.album.getCover()
        if self.doStop: self.quit()
        self.imagesLoaded.emit(1)
        self.album.getTracks(self.player)
        if self.doStop: self.quit()
        self.tracksLoaded.emit(1)
        self.quit()
        
         
        


    def stop(self):
        self.doStop = True
        self.album.setDoStop()
