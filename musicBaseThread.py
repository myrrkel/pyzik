import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
from database import *
from progressWidget import *



import time


class exploreAlbumsDirectoriesThread(QThread):


    """Read datas from files in the album folder"""

    doStop = False 
    musicBase = None
    progressChanged = pyqtSignal(int, name='progressChanged')
    directoryChanged = pyqtSignal(str, name='directoryChanged')
    exploreCompleted = pyqtSignal(int, name='exploreCompleted')


    def run(self):
        self.doStop = False
        db = database()
        db.initMemoryDB()
        self.musicBase.db = db
        self.musicBase.musicDirectoryCol.db = db
       
        for mdir in self.musicBase.musicDirectoryCol.musicDirectories:
            print("explore="+mdir.dirName)
            self.directoryChanged.emit(mdir.dirName)
            mdir.db = db
            mdir.artistCol = self.musicBase.artistCol
            mdir.albumCol = self.musicBase.albumCol
            mdir.artistCol.db = db
            mdir.albumCol.db = db

            mdir.exploreDirectory(self.progressChanged)


            if self.doStop: break
        self.directoryChanged.emit("Saving datas..")
        self.musicBase.db.saveMemoryToDisc()
        #self.musicBase.artistCol.sortArtists()        
        self.exploreCompleted.emit(1)
        self.quit()      
        


    def stop(self):
        self.doStop = True
        



