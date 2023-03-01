import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
from explore_event import ExploreEventList
from database import Database
import logging

logger = logging.getLogger(__name__)


class ExploreAlbumsDirectoriesThread(QThread):
    """Read datas from files in the album folder"""

    do_stop = False
    music_base = None
    progress_changed = pyqtSignal(int, name="progressChanged")
    directory_changed = pyqtSignal(str, name="directoryChanged")
    explore_completed = pyqtSignal(int, name="exploreCompleted")
    explore_events = ExploreEventList()

    def run(self):
        self.do_stop = False
        db = Database()
        db.init_memory_db()
        self.explore_events = []
        self.music_base.db = db
        self.music_base.music_directory_col.db = db

        for mdir in self.music_base.music_directory_col.music_directories:
            logger.debug("explore=" + mdir.directory_name)
            self.directory_changed.emit(mdir.directory_name)
            mdir.db = db
            mdir.artist_col = self.music_base.artist_col
            mdir.album_col = self.music_base.album_col
            mdir.artist_col.db = db
            mdir.album_col.db = db

            mdir.explore_directory(self.progress_changed)
            self.explore_events.extend(mdir.explore_events)

            if self.do_stop:
                break
        self.directory_changed.emit("Saving datas...")
        self.music_base.db.save_memory_to_disc()
        # self.music_base.artistCol.sortArtists()
        self.music_base.init_available_genres()
        self.explore_completed.emit(1)
        self.quit()

    def stop(self):
        self.do_stop = True
