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
        db.init_memory_db()
        self.explore_events = []
        self.music_base.db = db
        self.music_base.music_directory_col.db = db

        for mdir in self.music_base.music_directory_col.music_directories:
            logger.debug("explore=" + mdir.directory_name)
            self.directoryChanged.emit(mdir.directory_name)
            mdir.db = db
            mdir.artist_col = self.music_base.artist_col
            mdir.album_col = self.music_base.album_col
            mdir.artist_col.db = db
            mdir.album_col.db = db

            mdir.explore_directory(self.progressChanged)
            self.explore_events.extend(mdir.explore_events)

            if self.doStop:
                break
        self.directoryChanged.emit("Saving datas...")
        self.music_base.db.save_memory_to_disc()
        # self.music_base.artistCol.sortArtists()
        self.music_base.init_available_genres()
        self.exploreCompleted.emit(1)
        self.quit()

    def stop(self):
        self.doStop = True
