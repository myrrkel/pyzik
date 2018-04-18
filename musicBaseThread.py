import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
from database import *
from PyQt5 import QtCore, QtGui, QtWidgets


import time


class exploreAlbumsDirectoriesThread(QThread):


    """Read datas from files in the album folder"""

    doStop = False 
    musicbase = None
    progressChanged = pyqtSignal(int, name='progressChanged')
    exploreCompleted = pyqtSignal(int, name='exploreCompleted')


    def run(self):
        self.doStop = False

        self.wProgress = progressWidget()
        self.wProgress.show()
        #self.wProgress.exec_()


        self.musicbase.musicDirectoryCol.db = database()
        for mdir in self.musicbase.musicDirectoryCol.musicDirectories:
            mdir.db = database()

            print("Dir="+mdir.dirPath)
            mdir.artistCol = self.musicbase.artistCol
            mdir.albumCol = self.musicbase.albumCol
            mdir.artistCol.db = database()
            mdir.albumCol.db = database()
            mdir.exploreAlbumsDirectory()
            time.sleep(2)
            if self.doStop: return

        self.musicbase.artistCol.sortArtists()        
        
        


    def stop(self):
        self.doStop = True
        self.album.setDoStop()



class progressWidget(QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.initUI()

    def initUI(self):

        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setGeometry(0, 0, 250, 20)
        self.progress.setValue(50)
        self.button = QtWidgets.QPushButton('Start', self)
        self.button.move(0, 30)
        self.show()