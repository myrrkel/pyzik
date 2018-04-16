import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
from database import *

import time


class exploreAlbumsDirectoriesThread(QThread):


    """Read datas from files in the album folder"""

    doStop = False 
    musicbase = None
    progressChanged = pyqtSignal(int, name='progressChanged')
    exploreCompleted = pyqtSignal(int, name='exploreCompleted')


    def run(self):
        self.doStop = False

        self.musicbase.musicDirectoryCol.db = database()
        for mdir in self.musicbase.musicDirectoryCol.musicDirectories:
            mdir.db = database()

            print("Dir="+mdir.dirPath)
            mdir.artistCol = self.musicbase.artistCol
            mdir.albumCol = self.musicbase.albumCol
            mdir.artistCol.db = database()
            mdir.albumCol.db = database()
            mdir.exploreAlbumsDirectory()
            if self.doStop: return

        self.artistCol.sortArtists()        
        
        


    def stop(self):
        self.doStop = True
        self.album.setDoStop()
