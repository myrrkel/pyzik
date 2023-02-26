#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
import sqlite3
from music_directory import MusicDirectory
from explore_event import ExploreEventList


def filter_by_id(seq, music_directory_id):
    for el in seq:
        if el.music_directory_id == music_directory_id:
            yield el


class MusicDirectoryCollection:
    """
    MusicDirectoryCollection class
    """

    def __init__(self, main_music_base):
        self.music_directories: List[MusicDirectory] = list()
        self.music_base = main_music_base

    def add_music_directory(self, music_directory):
        if music_directory.music_directory_id == 0:
            music_directory.music_directory_id = self.insert_music_directory_db(
                music_directory
            )

        self.music_directories.append(music_directory)
        return music_directory.music_directory_id

    def delete_music_directory(self, music_directory):
        self.music_base.db.update_value(
            "albums",
            "musicDirectoryID",
            "0",
            "musicDirectoryID",
            music_directory.music_directory_id,
        )

        if self.music_base.db.delete_with_id(
            "musicDirectories", "musicDirectoryID", music_directory.music_directory_id
        ):
            self.music_directories.remove(music_directory)
            print("Directory removed")
        else:
            print("deleteMusicDirectory - Error")

    def get_explore_events(self):
        events = ExploreEventList()
        for music_directory in self.music_directories:
            events.extend(music_directory.explore_events)
        return events

    def insert_music_directory_db(self, music_directory):
        try:
            c = self.music_base.db.connection.cursor()
            req = """INSERT INTO musicDirectories (dirPath, dirName)
                                VALUES (?,?);
                          """
            c.execute(req, (music_directory.dir_path, music_directory.dirName))
            self.music_base.db.connection.commit()
            music_directory.music_directory_id = c.lastrowid
        except sqlite3.Error as e:
            print(e)

        return music_directory.music_directory_id

    def load_music_directories(self):
        req = '''SELECT musicDirectoryID, dirPath, dirName, ifnull(styleID,0), ifnull(dirType,0) as dirType 
        FROM musicDirectories'''
        for rowDir in self.music_base.db.get_select(req):

            music_directory = MusicDirectory(self.music_base)
            music_directory.load(rowDir)
            self.add_music_directory(music_directory)

    def get_music_directory(self, music_directory_id):
        for music_directory in filter_by_id(self.music_directories, music_directory_id):
            return music_directory

    def get_style_id_set(self):
        style_ids = set()
        for md in self.music_directories:
            style_ids.add(md.styleID)
        return style_ids
