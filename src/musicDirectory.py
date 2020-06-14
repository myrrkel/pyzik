#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from albumCollection import *
from artistCollection import *
import logging
import shutil

logger = logging.getLogger(__name__)


class musicDirectory:
    """
    musicDirectory contains albums or artist's directories.
    It have a style: Various (default), Rock, Jazz...
    All his albums heritates of this style on import
    """

    def __init__(self, musicBase=None, dirPath=""):

        self.musicBase = musicBase
        if musicBase:
            self.albumCol = musicBase.albumCol
            self.artistCol = musicBase.artistCol
        else:
            self.albumCol = albumCollection(self.musicBase)
            self.artistCol = artistCollection(self.musicBase)
        self.dirPath = dirPath
        self.musicDirectoryID = 0
        self.styleID = -1
        self.dirName = ""
        self.albums = []
        self.dirType = 0
        self.status = 0  # -1=Error ,0=Unknown , 1=OK
        self.exploreEvents = []

    def load(self, row):
        # musicDirectoryID, dirPath, dirName, styleID
        self.musicDirectoryID = row[0]
        self.dirPath = row[1]
        self.dirName = row[2]
        self.styleID = row[3]
        self.dirType = row[4]

    def getDirPath(self):
        return self.dirPath

    def getStatus(self, verify=True):
        if self.status == 0 or verify:
            exist = os.path.exists(self.dirPath)
            if exist:
                self.status = 1
            else:
                self.status = -1
        return self.status

    def addExploreEvent(self, explEvent):
        self.exploreEvents.append(explEvent)
        logger.info("ExploreEvent " + explEvent.eventCode + " : " + explEvent.getText())

    def exploreDirectory(self, progressChanged=None):
        self.exploreEvents = []
        if self.dirType in (0, None):
            self.exploreAlbumsDirectory(progressChanged)
        elif self.dirType == 1:
            self.exploreArtistsDirectory(progressChanged)
        elif self.dirType == 2:
            logger.info("Song directory not managed yet!")
        elif self.dirType == 3:
            self.exploreAlbumsDirectory(progressChanged, forceTAGCheck=True)

    def exploreAlbumsDirectory(self, progressChanged=None, forceTAGCheck=False):

        if self.getStatus() == -1: return

        dirlist = next(os.walk(self.dirPath))[1]
        for i, dir in enumerate(dirlist):
            iProgress = round((i / len(dirlist)) * 100)
            progressChanged.emit(iProgress)
            curAlb = album(dir, self)

            if not curAlb.toVerify or forceTAGCheck:

                if forceTAGCheck:
                    curAlb.getTagsFromFirstFile()
                    if not (curAlb.artistName and curAlb.title):
                        self.addExploreEvent(exploreEvent("ALBUM_TO_VERIFY_NO_TAG", curAlb.getAlbumDir()))

                # Artist name and album title has been found
                curArt = self.artistCol.getArtist(curAlb.artistName)
                # GetArtist return a new artist if it doesn't exists in artistsCol
                if curArt:
                    curAlb.artistID = curArt.artistID
                    curAlb.artistName = curArt.name
                    curAlb.addStyle({self.styleID})

                    albumList = curArt.findAlbums(curAlb.title)
                    if not albumList:
                        logger.info("Add " + curAlb.title + " in " + curArt.name + " discography. ArtID= %s", curArt.artistID)
                        self.addExploreEvent(exploreEvent("ALBUM_ADDED", curAlb.getAlbumDir()))
                        # curAlb.getAlbumSize()
                        # curAlb.getLength()
                        self.albumCol.addAlbum(curAlb)
                        curArt.addAlbum(curAlb)
                    else:
                        for alb in albumList:
                            if alb.getAlbumDir() != curAlb.getAlbumDir():
                                self.addExploreEvent(
                                    exploreEvent("ALBUM_DUPLICATE", curAlb.getAlbumDir(), alb.albumID, curArt.artistID))

                else:
                    logger.info("exploreAlbumsDirectory - No artist for " + dir)
            else:
                self.addExploreEvent(exploreEvent("ALBUM_TO_VERIFY", curAlb.getAlbumDir()))

        return

    def explore_albums_to_import(self, progressChanged=None, forceTAGCheck=False):
        self.exploreEvents = []
        res = []
        logger.info("explore %s", self.dirPath)
        dir_list = next(os.walk(self.dirPath))[1]

        for i, dir_path in enumerate(dir_list):
            dir_result = {}
            album_exists = False

            if progressChanged:
                iProgress = round((i / len(dir_list)) * 100)
                progressChanged.emit(iProgress)

            curAlb = album(dir_path, self)
            if curAlb.toVerify:
                curAlb.getTagsFromFirstFile()
            artists = self.artistCol.findArtists(curAlb.artistName)
            artist_exists = len(artists) > 0
            if artist_exists:
                curAlb.artistID = artists[0].artistID
                albums = artists[0].findAlbums(curAlb.title)
                album_exists = len(albums) > 0
            else:
                logger.info("Artist don't exists %s", curAlb.artistName)

            dir_result['alb'] = curAlb
            dir_result['artist_exists'] = artist_exists
            dir_result['album_exists'] = album_exists
            dir_result['album_dir'] = dir_path
            dir_result['full_dir'] = os.path.join(self.dirPath, dir_path)
            res.append(dir_result)

        res = sorted(res, key=lambda k: k['alb'].artistName+k['alb'].title)
        return res

    def import_album(self, album_to_import, album_path):
        copy_path = os.path.join(self.dirPath, album_to_import.get_formatted_dir_name())
        logger.info("from: %s to: %s", album_path, copy_path)
        if os.path.exists(copy_path):
            logger.info("Directory already exists %s", copy_path)
            self.addExploreEvent(exploreEvent("DIRECTORY_EXISTS", album_to_import.getAlbumDir(),
                                              album_to_import.albumID, album_to_import.artistID))
            return False

        shutil.move(album_path, copy_path)

        curArt = self.artistCol.getArtist(album_to_import.artistName)
        # GetArtist return a new artist if it doesn't exists in artistsCol
        if curArt:
            album_to_import.artistID = curArt.artistID
            album_to_import.musicDirectoryID = self.musicDirectoryID
            album_to_import.artistName = curArt.name
            album_to_import.addStyle({self.styleID})

            albumList = curArt.findAlbums(album_to_import.title)
            if not albumList:
                logger.info("Add " + album_to_import.title + " in " + curArt.name + " discography. ArtID= %s", curArt.artistID)
                self.addExploreEvent(exploreEvent("ALBUM_ADDED", album_to_import.getAlbumDir()))
                self.albumCol.addAlbum(album_to_import)
                curArt.addAlbum(album_to_import)
                return True
        return False

    def exploreArtistsDirectory(self, progressChanged=None):
        if self.getStatus() == -1: return
        dirlist = next(os.walk(self.dirPath))[1]
        i = 0
        for dirArt in dirlist:
            i += 1
            iProgress = round((i / len(dirlist)) * 100)
            progressChanged.emit(iProgress)

            logger.info('exploreArtistsDirectory=' + dirArt)
            curArt = self.artistCol.getArtist(dirArt)
            # GetArtist return a new artist if it doesn't exists in artistsCol

            self.exploreAlbumsInArtistDirectory(curArt, dirArt, progressChanged)

        return

    def exploreAlbumsInArtistDirectory(self, artist, dirArt, progressChanged=None):

        artPath = os.path.join(self.dirPath, dirArt)
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
            curAlb = album(albPath, self)
            # curAlb.musicDirectoryID = self.musicDirectoryID
            # curAlb.musicDirectory = self
            # curAlb.dirPath = dirArt

            curAlb.artistID = artist.artistID
            curAlb.artistName = artist.name

            if curAlb.toVerify == False:
                # Artist name et album title has been found

                albumList = artist.findAlbums(curAlb.title)
                if len(albumList) == 0:
                    logger.info("Add " + curAlb.title + " in " + artist.name + " discography. ArtID= %s", artist.artistID)
                    curAlb.getAlbumSize()
                    # curAlb.getLength()
                    self.albumCol.addAlbum(curAlb)
                    artist.addAlbum(curAlb)

        return True

    def updateMusicDirectoryDB(self):
        if self.musicDirectoryID > 0:
            try:
                c = self.musicBase.db.connection.cursor()
                sqlInsertMusicDirectory = """    UPDATE musicDirectories SET dirPath=?, dirName=?, styleID=?, dirType=?
                            WHERE musicDirectoryID=?;
                              """
                c.execute(sqlInsertMusicDirectory,
                          (self.dirPath,
                           self.dirName,
                           self.styleID,
                           self.dirType,
                           self.musicDirectoryID))

                self.musicBase.db.connection.commit()

            except sqlite3.Error as e:
                logger.info(e)


class exploreEvent:

    def __init__(self, code, dirpath, albumID=0, artistID=0):
        self.eventCode = code
        self.dirPath = dirpath
        self.artistID = artistID
        self.albumID = albumID

    def getText(self):
        if self.eventCode == "ALBUM_DUPLICATE":
            return "Album in " + self.dirPath + " already exists for this artist."
        if self.eventCode == "ALBUM_TO_VERIFY":
            return "Album in " + self.dirPath + " must be verified"
        if self.eventCode == "ALBUM_TO_VERIFY_NO_TAG":
            return "Album in " + self.dirPath + " must be verified. No tag found."
        if self.eventCode == "ALBUM_ADDED":
            return "Album in " + self.dirPath + " added."
        return ""
