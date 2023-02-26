#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from typing import List
from explore_event import *
from database import Database
from album import Album
from album_collection import AlbumCollection
from artist_collection import ArtistCollection
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
from files_utils import *

logger = logging.getLogger(__name__)


class ImportAlbumsThread(QThread):
    """Read datas from files in album folder"""

    alb_dict_list = []
    music_base = None

    album_import_progress = pyqtSignal(int, name="album_import_progress")
    album_import_started_signal = pyqtSignal(str, name="album_imported_signal")
    file_copy_started_signal = pyqtSignal(str, name="file_copied_signal")
    import_completed_signal = pyqtSignal(int, name="import_completed_signal")

    def run(self):
        self.music_base.db = Database()
        self.music_base.import_albums(
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

    def __init__(self, music_base=None, dir_path=""):
        self.music_base = music_base
        if music_base:
            self.albumCol = music_base.albumCol
            self.artistCol = music_base.artistCol
        else:
            self.albumCol = AlbumCollection(self.music_base)
            self.artistCol = ArtistCollection(self.music_base)
        self.dir_path = dir_path
        self.music_directory_id = 0
        self.styleID = -1
        self.dirName = ""
        self.albums: List[Album] = list()
        self.dirType = 0
        self.status = 0  # -1=Error ,0=Unknown , 1=OK

    def load(self, row):
        # musicDirectoryID, dirPath, dirName, styleID
        self.music_directory_id = row[0]
        self.dir_path = row[1]
        self.dirName = row[2]
        self.styleID = row[3]
        self.dirType = row[4]

    def get_dir_path(self):
        return self.dir_path

    def get_status(self, verify=True):
        if self.status == 0 or verify:
            exist = os.path.exists(self.dir_path)
            if exist:
                self.status = 1
            else:
                self.status = -1
        return self.status

    def add_explore_event(self, expl_event):
        self.explore_events.append(expl_event)
        logger.info(
            "ExploreEvent " + expl_event.event_code + " : " + expl_event.get_text()
        )

    def explore_directory(self, progress_changed=None):
        self.explore_events = []
        if self.dirType in (0, None):
            self.explore_albums_directory(progress_changed)
        elif self.dirType == 1:
            self.explore_artists_directory(progress_changed)
        elif self.dirType == 2:
            logger.info("Song directory not managed yet!")
        elif self.dirType == 3:
            self.explore_albums_directory(progress_changed, force_tag_check=True)

    def explore_albums_directory(self, progress_changed=None, force_tag_check=False):
        if self.get_status() == -1:
            return

        dirlist = next(os.walk(self.dir_path))[1]
        for i, directory in enumerate(dirlist):
            progress = round((i / len(dirlist)) * 100)
            progress_changed.emit(progress)
            album = Album(directory, self)

            if not album.to_verify or force_tag_check:
                if force_tag_check:
                    album.get_tags_from_first_file()
                    if not (album.artist_name and album.title):
                        self.add_explore_event(
                            ExploreEvent("ALBUM_TO_VERIFY_NO_TAG", album.get_album_dir())
                        )

                # Artist name and album title has been found
                cur_art = self.artistCol.get_artist(album.artist_name)
                # GetArtist return a new artist if it doesn't exists in artistsCol
                if cur_art:
                    album.artist_id = cur_art.artist_id
                    album.artist_name = cur_art.name.upper()
                    album.add_style({self.styleID})

                    album_list = cur_art.find_albums(album.title)
                    if not album_list:
                        logger.info(
                            "Add "
                            + album.title
                            + " in "
                            + cur_art.name
                            + " discography. ArtID= %s",
                            cur_art.artist_id,
                        )
                        self.add_explore_event(
                            ExploreEvent("ALBUM_ADDED", album.get_album_dir())
                        )
                        # curAlb.getAlbumSize()
                        # curAlb.getLength()
                        self.albumCol.add_album(album)
                        cur_art.add_album(album)
                    else:
                        for alb in album_list:
                            if alb.get_album_dir() != album.get_album_dir():
                                self.add_explore_event(
                                    ExploreEvent(
                                        "ALBUM_DUPLICATE",
                                        album.get_album_dir(),
                                        alb.album_id,
                                        cur_art.artist_id,
                                        alb,
                                    )
                                )

                else:
                    logger.info("exploreAlbumsDirectory - No artist for " + directory)
            else:
                self.add_explore_event(
                    ExploreEvent("ALBUM_TO_VERIFY", album.get_album_dir())
                )

        return

    def explore_albums_to_import(self, progress_changed=None, force_tag_check=False):
        self.explore_events = []
        res = []
        logger.info("explore %s", self.dir_path)
        dir_list = next(os.walk(self.dir_path))[1]

        for i, dir_path in enumerate(dir_list):
            dir_result = {}
            album_exists = False

            if progress_changed:
                progress = round((i / len(dir_list)) * 100)
                progress_changed.emit(progress)
            logger.debug("explore album %s", dir_path)
            cur_alb = Album(dir_path, self)
            if cur_alb.to_verify:
                cur_alb.get_tags_from_first_file()
            if not cur_alb.to_verify and cur_alb.year in [0, 9999]:
                cur_alb.get_year_from_first_file()
            artists = self.artistCol.find_artists(cur_alb.artist_name)
            artist_exists = len(artists) > 0
            if artist_exists:
                dir_result["artist_name"] = artists[0].name
                cur_alb.artist_id = artists[0].artist_id
                albums = artists[0].find_albums(cur_alb.title)
                album_exists = len(albums) > 0
            else:
                logger.info("Artist don't exists %s", cur_alb.artist_name)
                dir_result["artist_name"] = cur_alb.artist_name

            dir_result["alb"] = cur_alb
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
            self.add_explore_event(
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

        cur_art = self.artistCol.get_artist(album_to_import.artist_name)
        # GetArtist return a new artist if it doesn't exist in artistsCol
        if cur_art:
            album_to_import.artist_id = cur_art.artist_id
            album_to_import.music_directory_id = self.music_directory_id
            album_to_import.artist_name = cur_art.name
            album_to_import.add_style({self.styleID})

            album_list = cur_art.find_albums(album_to_import.title)
            if not album_list:
                logger.info(
                    "Add "
                    + album_to_import.title
                    + " in "
                    + cur_art.name
                    + " discography. ArtID= %s",
                    cur_art.artist_id,
                )
                self.add_explore_event(
                    ExploreEvent("ALBUM_ADDED", album_to_import.get_album_dir())
                )
                self.albumCol.add_album(album_to_import)
                cur_art.add_album(album_to_import)
                return True
        return False

    def explore_artists_directory(self, progress_changed=None):
        if self.get_status() == -1:
            return
        dirlist = next(os.walk(self.dir_path))[1]
        i = 0
        for dir_art in dirlist:
            i += 1
            progress = round((i / len(dirlist)) * 100)
            progress_changed.emit(progress)

            logger.info("exploreArtistsDirectory=" + dir_art)
            cur_art = self.artistCol.get_artist(dir_art)
            # GetArtist return a new artist if it doesn't exist in artistsCol

            self.explore_albums_in_artist_directory(cur_art, dir_art, progress_changed)

        return

    def explore_albums_in_artist_directory(self, artist, dir_art, progress_changed=None):
        art_path = os.path.join(self.dir_path, dir_art)
        dir_list = next(os.walk(art_path))[1]
        i = 0

        if len(dir_list) == 0:
            logger.info("This artist directory has no sub directory : " + art_path)
            return False

        for dirAlb in dir_list:
            i += 1
            progress = round((i / len(dir_list)) * 100)
            progress_changed.emit(progress)
            alb_path = os.path.join(dir_art, dirAlb)
            album = Album(alb_path, self)

            album.artist_id = artist.artist_id
            album.artist_name = artist.name

            if not album.to_verify:
                # Artist name et album title has been found

                album_list = artist.find_albums(album.title)
                if len(album_list) == 0:
                    logger.info(
                        "Add "
                        + album.title
                        + " in "
                        + artist.name
                        + " discography. ArtID= %s",
                        artist.artist_id,
                    )
                    album.get_album_size()
                    # album.getLength()
                    self.albumCol.add_album(album)
                    artist.add_album(album)

        return True

    def update_music_directory_db(self):
        if self.music_directory_id > 0:
            try:
                c = self.music_base.db.connection.cursor()
                request = """    UPDATE musicDirectories SET dirPath=?, dirName=?, styleID=?, dirType=?
                            WHERE musicDirectoryID=?;
                              """
                c.execute(request, (self.dir_path,
                                    self.dirName,
                                    self.styleID,
                                    self.dirType,
                                    self.music_directory_id))

                self.music_base.db.connection.commit()

            except sqlite3.Error as e:
                logger.info(e)
