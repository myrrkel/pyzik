#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import Database
from album_collection import AlbumCollection
from artist_collection import ArtistCollection
from music_directory_collection import MusicDirectoryCollection
from music_genres import MusicGenres
from history_manager import HistoryManager
from radio_manager import RadioManager
import logging

logger = logging.getLogger(__name__)


class MusicBase:
    """
    musicBase manage albums and artists from
    the music directories to the database'''
    """

    def __init__(self, db_path=""):
        self.db = Database(db_path=db_path)
        self.db.initDataBase()
        self.albumCol = AlbumCollection(self)
        self.artistCol = ArtistCollection(self)
        self.musicDirectoryCol = MusicDirectoryCollection(self)
        self.genres = MusicGenres()
        self.style_ids = set()
        self.availableGenres = set()
        self.history = HistoryManager()
        self.radioMan = RadioManager(self)

    def load_music_base(self, memoryDB=True):
        if memoryDB:
            self.db.initMemoryDB()
        self.musicDirectoryCol.load_music_directories()
        self.artistCol.load_artists()
        self.albumCol.load_albums()
        self.add_genres_dir_to_albums()
        self.add_albums_to_artists()
        self.radioMan.load_fav_radios()
        self.init_available_genres()
        self.history.initDataBase()

    def refresh(self):
        self.add_genres_dir_to_albums()
        self.add_albums_to_artists()
        self.init_available_genres()

    def init_available_genres(self):
        self.style_ids = self.musicDirectoryCol.get_style_id_set()
        self.availableGenres = self.genres.getAvailableGenresFormIDSet(self.style_ids)

    def add_genres_dir_to_albums(self):
        for alb in self.albumCol.albums:
            md = self.musicDirectoryCol.get_music_directory(alb.music_directory_id)
            if md != None:
                if md.styleID >= -1:
                    alb.add_style({md.styleID})

    def add_albums_to_artists(self):
        for alb in self.albumCol.albums:
            artistFound = self.artistCol.get_artist_by_id(alb.artist_id)
            if artistFound is not None:
                alb.artist_name = artistFound.name
                artistFound.add_style(alb.style_ids)
                artistFound.albums.append(alb)

    def delete_music_directory(self, musicDirectory):
        self.musicDirectoryCol.deleteMusicDirectory(musicDirectory)

    def empty_datas(self):
        self.artistCol.artists = set()
        self.albumCol.albums = []

    def generate_random_album_list(self, nb_alb=20, styleID=-2):
        randomAlbList = []

        for i in range(nb_alb):
            try_count = 0
            alb = self.albumCol.get_random_album(styleID)
            while alb in randomAlbList and try_count < 3:
                alb = self.albumCol.get_random_album(styleID)
                try_count += 1

            if alb not in randomAlbList:
                randomAlbList.append(alb)

        return randomAlbList

    def import_albums(
        self,
        alb_dict_list={},
        album_import_started_signal=None,
        file_copy_started_signal=None,
        album_import_progress=None,
    ):
        for i, alb_dict in enumerate(alb_dict_list):
            if album_import_progress:
                if i != 0:
                    album_import_progress.emit((100 / len(alb_dict_list)) * i)
                else:
                    album_import_progress.emit(0)

            if not alb_dict["album_exists"]:
                logger.debug("import_album %s", alb_dict)
                album_import_started_signal.emit(
                    alb_dict["alb"].get_formatted_dir_name()
                )
                alb_dict["to_dir"].import_album(
                    alb_dict["alb"], alb_dict["full_dir"], file_copy_started_signal
                )


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    mb = MusicBase()
    mb.load_music_base()
    randAlbumList = mb.generate_random_album_list(20)

    for alb in randAlbumList:
        print(alb.title)

    sys.exit(app.exec_())
