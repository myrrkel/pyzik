#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import Database
from albumCollection import AlbumCollection
from artistCollection import ArtistCollection
from musicDirectoryCollection import MusicDirectoryCollection
from musicGenres import MusicGenres
from historyManager import HistoryManager
from radioManager import RadioManager
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
        self.styleIDSet = set()
        self.availableGenres = set()
        self.history = HistoryManager()
        self.radioMan = RadioManager(self)

    def loadMusicBase(self, memoryDB=True):
        if memoryDB:
            self.db.initMemoryDB()
        self.musicDirectoryCol.loadMusicDirectories()
        self.artistCol.load_artists()
        self.albumCol.load_albums()
        self.addGenresDirToAlbums()
        self.addAlbumsToArtists()
        self.radioMan.loadFavRadios()
        self.initAvailableGenres()
        self.history.initDataBase()

    def refresh(self):
        self.addGenresDirToAlbums()
        self.addAlbumsToArtists()
        self.initAvailableGenres()

    def initAvailableGenres(self):
        self.styleIDSet = self.musicDirectoryCol.getStyleIDSet()
        self.availableGenres = self.genres.getAvailableGenresFormIDSet(self.styleIDSet)

    def addGenresDirToAlbums(self):
        for alb in self.albumCol.albums:
            md = self.musicDirectoryCol.getMusicDirectory(alb.musicDirectoryID)
            if md != None:
                if md.styleID >= -1:
                    alb.addStyle({md.styleID})

    def addAlbumsToArtists(self):
        for alb in self.albumCol.albums:
            artistFound = self.artistCol.get_artist_by_id(alb.artistID)
            if artistFound is not None:
                alb.artist_name = artistFound.name
                artistFound.addStyle(alb.styleIDSet)
                artistFound.albums.append(alb)

    def deleteMusicDirectory(self, musicDirectory):
        self.musicDirectoryCol.deleteMusicDirectory(musicDirectory)

    def emptyDatas(self):
        self.artistCol.artists = set()
        self.albumCol.albums = []

    def generateRandomAlbumList(self, nb_alb=20, styleID=-2):
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
    mb.loadMusicBase()
    randAlbumList = mb.generateRandomAlbumList(20)

    for alb in randAlbumList:
        print(alb.title)

    sys.exit(app.exec_())
