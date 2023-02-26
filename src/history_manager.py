#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from operator import itemgetter, attrgetter
from typing import List
from database import Database
from history_item import HistoryItem


class HistoryManager:
    """
    Read and write playing history
    """

    def __init__(self, music_base=None):
        self.music_base = music_base
        self.database = Database(is_history=True)
        self.history: List[HistoryItem] = list()

    def init_data_base(self):
        self.database.init_data_base()

    def load_history(self, with_albums=True):
        self.history = []
        if with_albums:
            self.load_album_history()
        self.load_track_history()
        self.load_radio_history()
        self.history = sorted(self.history, key=attrgetter("play_date", "history_type"),
                              reverse=True)

    def insert_album_history(self, album_id):
        """Insert album in history"""
        self.database.insert_album_history(album_id)

    def load_album_history(self):
        req = """ 
        SELECT albumID, playDate 
        FROM playHistoryAlbum
        """

        for rowHisto in self.database.get_select(req):
            histo = HistoryItem(rowHisto[1])
            histo.init_histo_album(rowHisto[0])
            histo.data.get_album(self.music_base)
            self.history.append(histo)

    def insert_track_history(self, album_id, file_name):
        """Insert track in history"""
        self.database.insert_track_history(album_id, file_name)

    def load_track_history(self):
        req = """ 
        SELECT albumID, fileName, playDate 
        FROM playHistoryTrack
        """

        for rowHisto in self.database.get_select(req):
            histo = HistoryItem(rowHisto[2])
            histo.init_histo_track(rowHisto[0], rowHisto[1])
            histo.data.get_album(self.music_base)
            self.history.append(histo)

    def insert_radio_history(self, radio_name, title):
        """Insert radio title in history"""
        self.database.insert_radio_history(radio_name, title)

    def load_radio_history(self):
        req = """ 
        SELECT radioName, title, playDate 
        FROM playHistoryRadio
        """

        for rowHisto in self.database.get_select(req):
            histo = HistoryItem(rowHisto[2])
            histo.init_histo_radio(rowHisto[0], rowHisto[1])
            self.history.append(histo)

    def print_all(self):
        for histo in self.history:
            histo.print_data()


if __name__ == "__main__":
    from music_base import MusicBase

    mb = MusicBase()
    mb.load_music_base(False)

    history = HistoryManager(mb)
    history.print_all()

    sql = """    INSERT INTO playHistoryRadio ({columns})
                    VALUES ('{radioName}','{title}',datetime('now','localtime'));
              """.format(
        columns="radioName, title, playDate", radioName="testRad", title="MyTitle"
    )
    print(sql)
