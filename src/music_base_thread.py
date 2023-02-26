import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
from explore_event import ExploreEventList
from database import Database
import logging

logger = logging.getLogger(__name__)


class ExploreAlbumsDirectoriesThread(QThread):
    """Read datas from files in the album folder"""

    doStop = False
    music_base = None
    progressChanged = pyqtSignal(int, name="progressChanged")
    directoryChanged = pyqtSignal(str, name="directoryChanged")
    exploreCompleted = pyqtSignal(int, name="exploreCompleted")
    explore_events = ExploreEventList()

    def run(self):
        self.doStop = False
        db = Database()
        db.initMemoryDB()
        self.explore_events = []
        self.music_base.db = db
        self.music_base.musicDirectoryCol.db = db

        for mdir in self.music_base.musicDirectoryCol.musicDirectories:
            logger.debug("explore=" + mdir.dirName)
            self.directoryChanged.emit(mdir.dirName)
            mdir.db = db
            mdir.artistCol = self.music_base.artistCol
            mdir.albumCol = self.music_base.albumCol
            mdir.artistCol.db = db
            mdir.albumCol.db = db

            mdir.exploreDirectory(self.progressChanged)
            self.explore_events.extend(mdir.explore_events)

            if self.doStop:
                break
        self.directoryChanged.emit("Saving datas...")
        self.music_base.db.saveMemoryToDisc()
        # self.music_base.artistCol.sortArtists()
        self.music_base.init_available_genres()
        self.exploreCompleted.emit(1)
        self.quit()

    def stop(self):
        self.doStop = True
