import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
from database import *
from progressWidget import *



import time


class exploreAlbumsDirectoriesThread(QThread):


    """Read datas from files in the album folder"""

    doStop = False 
    musicbase = None
    progressChanged = pyqtSignal(int, name='progressChanged')
    directoryChanged = pyqtSignal(str, name='directoryChanged')
    exploreCompleted = pyqtSignal(int, name='exploreCompleted')


    def run(self):
        self.doStop = False

        self.musicbase.musicDirectoryCol.db = database()
       
        for mdir in self.musicbase.musicDirectoryCol.musicDirectories:
            self.directoryChanged.emit(mdir.dirName)
            mdir.db = database()
            mdir.artistCol = self.musicbase.artistCol
            mdir.albumCol = self.musicbase.albumCol
            mdir.artistCol.db = database()
            mdir.albumCol.db = database()
            mdir.exploreAlbumsDirectory(self.progressChanged)
            if self.doStop: break

        self.musicbase.artistCol.sortArtists()        
        self.exploreCompleted.emit(1)
        self.quit()      
        


    def stop(self):
        self.doStop = True
        self.album.setDoStop()



