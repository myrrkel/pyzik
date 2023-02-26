#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from music_directory import MusicDirectory
from explore_event import ExploreEventList


def filter_by_id(seq, id):
    for el in seq:
        if el.music_directory_id == id:
            yield el


class MusicDirectoryCollection:
    """
    MusicDirectoryCollection class
    """

    def __init__(self, main_music_base):
        self.musicDirectories = []  # MusicDirectory Collection
        self.music_base = main_music_base

    def add_music_directory(self, music_directory):
        if music_directory.music_directory_id == 0:
            music_directory.music_directory_id = self.insert_music_directory_db(
                music_directory
            )

        self.musicDirectories.append(music_directory)
        return music_directory.music_directory_id

    def delete_music_directory(self, music_directory):
        self.music_base.db.updateValue(
            "albums",
            "musicDirectoryID",
            "0",
            "musicDirectoryID",
            music_directory.music_directory_id,
        )

        if self.music_base.db.deleteWithID(
            "musicDirectories", "musicDirectoryID", music_directory.music_directory_id
        ):
            self.musicDirectories.remove(music_directory)
            print("Directory removed")
        else:
            print("deleteMusicDirectory - Error")

    def print_music_directories(self):
        for dir in self.musicDirectories:
            dir.printInfos()

    def get_explore_events(self):
        events = ExploreEventList()
        for md in self.musicDirectories:
            events.extend(md.explore_events)
        return events

    def insert_music_directory_db(self, music_directory):
        try:
            c = self.music_base.db.connection.cursor()
            sqlInsertMusicDirectory = """    INSERT INTO musicDirectories (dirPath, dirName)
                                VALUES (?,?);
                          """
            c.execute(
                sqlInsertMusicDirectory,
                (music_directory.dir_path, music_directory.dirName),
            )
            self.music_base.db.connection.commit()
            music_directory.music_directory_id = c.lastrowid
        except sqlite3.Error as e:
            print(e)

        return music_directory.music_directory_id

    def load_music_directories(self):
        req = "SELECT musicDirectoryID, dirPath, dirName, ifnull(styleID,0), ifnull(dirType,0) as dirType FROM musicDirectories"
        for rowDir in self.music_base.db.getSelect(req):
            # print('{0} : {1}'.format(rowDir[0], rowDir[1]))
            dir = MusicDirectory(self.music_base)
            dir.load(rowDir)
            self.add_music_directory(dir)

    def get_music_directory(self, id):
        resMB = None
        for mdir in filter_by_id(self.musicDirectories, id):
            resMB = mdir
        return resMB

    def get_style_id_set(self):
        style_ids = set()
        for md in self.musicDirectories:
            style_ids.add(md.styleID)
        return style_ids
