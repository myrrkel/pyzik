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
        self.album_col = AlbumCollection(self)
        self.artist_col = ArtistCollection(self)
        self.music_directory_col = MusicDirectoryCollection(self)
        self.genres = MusicGenres()
        self.style_ids = set()
        self.available_genres = set()
        self.history = HistoryManager()
        self.radio_manager = RadioManager(self)

    def load_music_base(self, memory_db=True):
        if memory_db:
            self.db.init_memory_db()
        self.music_directory_col.load_music_directories()
        self.artist_col.load_artists()
        self.album_col.load_albums()
        self.add_genres_dir_to_albums()
        self.add_albums_to_artists()
        self.radio_manager.load_fav_radios()
        self.init_available_genres()
        self.history.init_data_base()

    def refresh(self):
        self.add_genres_dir_to_albums()
        self.add_albums_to_artists()
        self.init_available_genres()

    def init_available_genres(self):
        self.style_ids = self.music_directory_col.get_style_id_set()
        self.available_genres = self.genres.get_available_genres_form_id_set(self.style_ids)

    def add_genres_dir_to_albums(self):
        for album in self.album_col.albums:
            music_directory = self.music_directory_col.get_music_directory(album.music_directory_id)
            if music_directory is not None:
                if music_directory.style_id >= -1:
                    album.add_style({music_directory.style_id})

    def add_albums_to_artists(self):
        for album in self.album_col.albums:
            artist_found = self.artist_col.get_artist_by_id(album.artist_id)
            if artist_found is not None:
                album.artist_name = artist_found.name
                artist_found.add_style(album.style_ids)
                artist_found.albums.append(album)

    def delete_music_directory(self, music_directory):
        self.music_directory_col.delete_music_directory(music_directory)

    def empty_datas(self):
        self.artist_col.artists = set()
        self.album_col.albums = []

    def generate_random_album_list(self, nb_alb=20, style_id=-2):
        random_alb_list = []

        for i in range(nb_alb):
            try_count = 0
            album = self.album_col.get_random_album(style_id)
            while album in random_alb_list and try_count < 3:
                album = self.album_col.get_random_album(style_id)
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
