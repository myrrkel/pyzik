#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from musicDirectory import MusicDirectory
from explore_event import ExploreEventList


def filterByID(seq, id):
    for el in seq:
        if el.music_directory_id == id:
            yield el


class MusicDirectoryCollection:
    """
    MusicDirectoryCollection class
    """

    def __init__(self, mainMusicBase):
        self.musicDirectories = []  # MusicDirectory Collection
        self.music_base = mainMusicBase

    def addMusicDirectory(self, musicDirectory):
        if musicDirectory.music_directory_id == 0:
            musicDirectory.music_directory_id = self.insertMusicDirectoryDB(
                musicDirectory
            )

        self.musicDirectories.append(musicDirectory)
        return musicDirectory.music_directory_id

    def deleteMusicDirectory(self, musicDirectory):
        self.music_base.db.updateValue(
            "albums",
            "musicDirectoryID",
            "0",
            "musicDirectoryID",
            musicDirectory.music_directory_id,
        )

        if self.music_base.db.deleteWithID(
            "musicDirectories", "musicDirectoryID", musicDirectory.music_directory_id
        ):
            self.musicDirectories.remove(musicDirectory)
            print("Directory removed")
        else:
            print("deleteMusicDirectory - Error")

    def printMusicDirectories(self):
        for dir in self.musicDirectories:
            dir.printInfos()

    def getExploreEvents(self):
        events = ExploreEventList()
        for md in self.musicDirectories:
            events.extend(md.explore_events)
        return events

    def insertMusicDirectoryDB(self, musicDirectory):
        try:
            c = self.music_base.db.connection.cursor()
            sqlInsertMusicDirectory = """    INSERT INTO musicDirectories (dirPath, dirName)
                                VALUES (?,?);
                          """
            c.execute(
                sqlInsertMusicDirectory,
                (musicDirectory.dir_path, musicDirectory.dirName),
            )
            self.music_base.db.connection.commit()
            musicDirectory.music_directory_id = c.lastrowid
        except sqlite3.Error as e:
            print(e)

        return musicDirectory.music_directory_id

    def load_music_directories(self):
        req = "SELECT musicDirectoryID, dirPath, dirName, ifnull(styleID,0), ifnull(dirType,0) as dirType FROM musicDirectories"
        for rowDir in self.music_base.db.getSelect(req):
            # print('{0} : {1}'.format(rowDir[0], rowDir[1]))
            dir = MusicDirectory(self.music_base)
            dir.load(rowDir)
            self.addMusicDirectory(dir)

    def get_music_directory(self, id):
        resMB = None
        for mdir in filterByID(self.musicDirectories, id):
            resMB = mdir
        return resMB

    def get_style_id_set(self):
        style_ids = set()
        for md in self.musicDirectories:
            style_ids.add(md.styleID)
        return style_ids
