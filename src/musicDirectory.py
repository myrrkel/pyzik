#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sqlite3
from explore_event import *
from database import Database
from album import Album
from albumCollection import AlbumCollection
from artistCollection import ArtistCollection
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
from filesUtils import *

logger = logging.getLogger(__name__)


class ImportAlbumsThread(QThread):
    """Read datas from files in the album folder"""

    alb_dict_list = []
    musicbase = None

    album_import_progress = pyqtSignal(int, name="album_import_progress")
    album_import_started_signal = pyqtSignal(str, name="album_imported_signal")
    file_copy_started_signal = pyqtSignal(str, name="file_copied_signal")
    import_completed_signal = pyqtSignal(int, name="import_completed_signal")

    def run(self):
        self.musicbase.db = Database()
        self.musicbase.import_albums(
            self.alb_dict_list,
            self.album_import_started_signal,
            self.file_copy_started_signal,
            self.album_import_progress,
        )
        self.import_completed_signal.emit(1)
        return


class MusicDirectory:
    """
    musicDirectory contains albums or artist's directories.
    It have a style: Various (default), Rock, Jazz...
    All his albums heritates of this style on import
    """

    explore_events = ExploreEventList()

    def __init__(self, music_base=None, dirPath=""):
        self.music_base = music_base
        if music_base:
            self.albumCol = music_base.albumCol
            self.artistCol = music_base.artistCol
        else:
            self.albumCol = AlbumCollection(self.music_base)
            self.artistCol = ArtistCollection(self.music_base)
        self.dir_path = dirPath
        self.music_directory_id = 0
        self.styleID = -1
        self.dirName = ""
        self.albums = []
        self.dirType = 0
        self.status = 0  # -1=Error ,0=Unknown , 1=OK

    def load(self, row):
        # musicDirectoryID, dirPath, dirName, styleID
        self.music_directory_id = row[0]
        self.dir_path = row[1]
        self.dirName = row[2]
        self.styleID = row[3]
        self.dirType = row[4]

    def getDirPath(self):
        return self.dir_path

    def getStatus(self, verify=True):
        if self.status == 0 or verify:
            exist = os.path.exists(self.dir_path)
            if exist:
                self.status = 1
            else:
                self.status = -1
        return self.status

    def addExploreEvent(self, explEvent):
        self.explore_events.append(explEvent)
        logger.info(
            "ExploreEvent " + explEvent.event_code + " : " + explEvent.get_text()
        )

    def exploreDirectory(self, progressChanged=None):
        self.explore_events = []
        if self.dirType in (0, None):
            self.exploreAlbumsDirectory(progressChanged)
        elif self.dirType == 1:
            self.exploreArtistsDirectory(progressChanged)
        elif self.dirType == 2:
            logger.info("Song directory not managed yet!")
        elif self.dirType == 3:
            self.exploreAlbumsDirectory(progressChanged, forceTAGCheck=True)

    def exploreAlbumsDirectory(self, progressChanged=None, forceTAGCheck=False):
        if self.getStatus() == -1:
            return

        dirlist = next(os.walk(self.dir_path))[1]
        for i, dir in enumerate(dirlist):
            iProgress = round((i / len(dirlist)) * 100)
            progressChanged.emit(iProgress)
            curAlb = Album(dir, self)

            if not curAlb.to_verify or forceTAGCheck:
                if forceTAGCheck:
                    curAlb.get_tags_from_first_file()
                    if not (curAlb.artist_name and curAlb.title):
                        self.addExploreEvent(
                            ExploreEvent("ALBUM_TO_VERIFY_NO_TAG", curAlb.get_album_dir())
                        )

                # Artist name and album title has been found
                curArt = self.artistCol.get_artist(curAlb.artist_name)
                # GetArtist return a new artist if it doesn't exists in artistsCol
                if curArt:
                    curAlb.artist_id = curArt.artist_id
                    curAlb.artist_name = curArt.name.upper()
                    curAlb.add_style({self.styleID})

                    albumList = curArt.find_albums(curAlb.title)
                    if not albumList:
                        logger.info(
                            "Add "
                            + curAlb.title
                            + " in "
                            + curArt.name
                            + " discography. ArtID= %s",
                            curArt.artist_id,
                        )
                        self.addExploreEvent(
                            ExploreEvent("ALBUM_ADDED", curAlb.get_album_dir())
                        )
                        # curAlb.getAlbumSize()
                        # curAlb.getLength()
                        self.albumCol.add_album(curAlb)
                        curArt.add_album(curAlb)
                    else:
                        for alb in albumList:
                            if alb.get_album_dir() != curAlb.get_album_dir():
                                self.addExploreEvent(
                                    ExploreEvent(
                                        "ALBUM_DUPLICATE",
                                        curAlb.get_album_dir(),
                                        alb.album_id,
                                        curArt.artist_id,
                                        alb,
                                    )
                                )

                else:
                    logger.info("exploreAlbumsDirectory - No artist for " + dir)
            else:
                self.addExploreEvent(
                    ExploreEvent("ALBUM_TO_VERIFY", curAlb.get_album_dir())
                )

        return

    def explore_albums_to_import(self, progressChanged=None, forceTAGCheck=False):
        self.explore_events = []
        res = []
        logger.info("explore %s", self.dir_path)
        dir_list = next(os.walk(self.dir_path))[1]

        for i, dir_path in enumerate(dir_list):
            dir_result = {}
            album_exists = False

            if progressChanged:
                iProgress = round((i / len(dir_list)) * 100)
                progressChanged.emit(iProgress)
            logger.debug("explore album %s", dir_path)
            curAlb = Album(dir_path, self)
            if curAlb.to_verify:
                curAlb.get_tags_from_first_file()
            if not curAlb.to_verify and curAlb.year in [0, 9999]:
                curAlb.get_year_from_first_file()
            artists = self.artistCol.find_artists(curAlb.artist_name)
            artist_exists = len(artists) > 0
            if artist_exists:
                dir_result["artist_name"] = artists[0].name
                curAlb.artist_id = artists[0].artist_id
                albums = artists[0].find_albums(curAlb.title)
                album_exists = len(albums) > 0
            else:
                logger.info("Artist don't exists %s", curAlb.artist_name)
                dir_result["artist_name"] = curAlb.artist_name

            dir_result["alb"] = curAlb
            dir_result["artist_exists"] = artist_exists
            dir_result["album_exists"] = album_exists
            dir_result["album_dir"] = dir_path
            dir_result["full_dir"] = os.path.join(self.dir_path, dir_path)
            res.append(dir_result)

        res = sorted(res, key=lambda k: k["alb"].artist_name + k["alb"].title)
        return res

    def import_album(self, album_to_import, album_path, file_copy_started_signal=None):
        new_dir_name = album_to_import.get_formatted_dir_name()
        album_to_import.dir_path = new_dir_name
        copy_path = os.path.join(self.dir_path, new_dir_name)
        logger.info("from: %s to: %s", album_path, copy_path)
        if os.path.exists(copy_path):
            logger.info("Directory already exists %s", copy_path)
            self.addExploreEvent(
                ExploreEvent(
                    "DIRECTORY_EXISTS",
                    album_to_import.get_album_dir(),
                    album_to_import.album_id,
                    album_to_import.artist_id,
                )
            )
            return False

        move_directory_file_by_file(
            album_path, copy_path, file_copy_started_signal, test_mode=False
        )

        curArt = self.artistCol.get_artist(album_to_import.artist_name)
        # GetArtist return a new artist if it doesn't exists in artistsCol
        if curArt:
            album_to_import.artist_id = curArt.artist_id
            album_to_import.music_directory_id = self.music_directory_id
            album_to_import.artist_name = curArt.name
            album_to_import.add_style({self.styleID})

            albumList = curArt.find_albums(album_to_import.title)
            if not albumList:
                logger.info(
                    "Add "
                    + album_to_import.title
                    + " in "
                    + curArt.name
                    + " discography. ArtID= %s",
                    curArt.artist_id,
                )
                self.addExploreEvent(
                    ExploreEvent("ALBUM_ADDED", album_to_import.get_album_dir())
                )
                self.albumCol.add_album(album_to_import)
                curArt.add_album(album_to_import)
                return True
        return False

    def exploreArtistsDirectory(self, progressChanged=None):
        if self.getStatus() == -1:
            return
        dirlist = next(os.walk(self.dir_path))[1]
        i = 0
        for dirArt in dirlist:
            i += 1
            iProgress = round((i / len(dirlist)) * 100)
            progressChanged.emit(iProgress)

            logger.info("exploreArtistsDirectory=" + dirArt)
            curArt = self.artistCol.get_artist(dirArt)
            # GetArtist return a new artist if it doesn't exists in artistsCol

            self.exploreAlbumsInArtistDirectory(curArt, dirArt, progressChanged)

        return

    def exploreAlbumsInArtistDirectory(self, artist, dirArt, progressChanged=None):
        artPath = os.path.join(self.dir_path, dirArt)
        dirlist = next(os.walk(artPath))[1]
        i = 0

        if len(dirlist) == 0:
            logger.info("This artist directory has no sub directory : " + artPath)
            return False

        for dirAlb in dirlist:
            i += 1
            iProgress = round((i / len(dirlist)) * 100)
            progressChanged.emit(iProgress)
            albPath = os.path.join(dirArt, dirAlb)
            curAlb = Album(albPath, self)

            curAlb.artist_id = artist.artist_id
            curAlb.artist_name = artist.name

            if curAlb.to_verify == False:
                # Artist name et album title has been found

                albumList = artist.find_albums(curAlb.title)
                if len(albumList) == 0:
                    logger.info(
                        "Add "
                        + curAlb.title
                        + " in "
                        + artist.name
                        + " discography. ArtID= %s",
                        artist.artist_id,
                    )
                    curAlb.get_album_size()
                    # curAlb.getLength()
                    self.albumCol.add_album(curAlb)
                    artist.add_album(curAlb)

        return True

    def updateMusicDirectoryDB(self):
        if self.music_directory_id > 0:
            try:
                c = self.music_base.db.connection.cursor()
                sqlInsertMusicDirectory = """    UPDATE musicDirectories SET dirPath=?, dirName=?, styleID=?, dirType=?
                            WHERE musicDirectoryID=?;
                              """
                c.execute(
                    sqlInsertMusicDirectory,
                    (
                        self.dir_path,
                        self.dirName,
                        self.styleID,
                        self.dirType,
                        self.music_directory_id,
                    ),
                )

                self.music_base.db.connection.commit()

            except sqlite3.Error as e:
                logger.info(e)
