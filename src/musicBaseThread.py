import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
from database import *
import logging

logger = logging.getLogger(__name__)

import time
from explore_event import *


class exploreAlbumsDirectoriesThread(QThread):
    """Read datas from files in the album folder"""

    doStop = False
    musicBase = None
    progressChanged = pyqtSignal(int, name='progressChanged')
    directoryChanged = pyqtSignal(str, name='directoryChanged')
    exploreCompleted = pyqtSignal(int, name='exploreCompleted')
    explore_events = ExploreEventList()

    def run(self):
        self.doStop = False
        db = database()
        db.initMemoryDB()
        self.explore_events = []
        self.musicBase.db = db
        self.musicBase.musicDirectoryCol.db = db

        for mdir in self.musicBase.musicDirectoryCol.musicDirectories:
            logger.debug("explore=" + mdir.dirName)
            self.directoryChanged.emit(mdir.dirName)
            mdir.db = db
            mdir.artistCol = self.musicBase.artistCol
            mdir.albumCol = self.musicBase.albumCol
            mdir.artistCol.db = db
            mdir.albumCol.db = db

            mdir.exploreDirectory(self.progressChanged)
            self.explore_events.extend(mdir.explore_events)

            if self.doStop: break
        self.directoryChanged.emit("Saving datas...")
        self.musicBase.db.saveMemoryToDisc()
        # self.musicBase.artistCol.sortArtists()
        self.musicBase.initAvailableGenres()
        self.exploreCompleted.emit(1)
        self.quit()

    def stop(self):
        self.doStop = True
