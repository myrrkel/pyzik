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
        self.db.init_data_base()
        self.albumCol = AlbumCollection(self)
        self.artistCol = ArtistCollection(self)
        self.musicDirectoryCol = MusicDirectoryCollection(self)
        self.genres = MusicGenres()
        self.style_ids = set()
        self.availableGenres = set()
        self.history = HistoryManager()
        self.radioMan = RadioManager(self)

    def load_music_base(self, memory_db=True):
        if memory_db:
            self.db.init_memory_db()
        self.musicDirectoryCol.load_music_directories()
        self.artistCol.load_artists()
        self.albumCol.load_albums()
        self.add_genres_dir_to_albums()
        self.add_albums_to_artists()
        self.radioMan.load_fav_radios()
        self.init_available_genres()
        self.history.init_data_base()

    def refresh(self):
        self.add_genres_dir_to_albums()
        self.add_albums_to_artists()
        self.init_available_genres()

    def init_available_genres(self):
        self.style_ids = self.musicDirectoryCol.get_style_id_set()
        self.availableGenres = self.genres.get_available_genres_form_id_set(self.style_ids)

    def add_genres_dir_to_albums(self):
        for album in self.albumCol.albums:
            music_directory = self.musicDirectoryCol.get_music_directory(album.music_directory_id)
            if music_directory is not None:
                if music_directory.styleID >= -1:
                    album.add_style({music_directory.styleID})

    def add_albums_to_artists(self):
        for album in self.albumCol.albums:
            artist_found = self.artistCol.get_artist_by_id(album.artist_id)
            if artist_found is not None:
                album.artist_name = artist_found.name
                artist_found.add_style(album.style_ids)
                artist_found.albums.append(album)

    def delete_music_directory(self, music_directory):
        self.musicDirectoryCol.delete_music_directory(music_directory)

    def empty_datas(self):
        self.artistCol.artists = set()
        self.albumCol.albums = []

    def generate_random_album_list(self, nb_alb=20, style_id=-2):
        random_alb_list = []

        for i in range(nb_alb):
            try_count = 0
            album = self.albumCol.get_random_album(style_id)
            while album in random_alb_list and try_count < 3:
                album = self.albumCol.get_random_album(style_id)
                try_count += 1

            if album not in random_alb_list:
                random_alb_list.append(album)

        return random_alb_list

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
