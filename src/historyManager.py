#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from operator import itemgetter, attrgetter

from album import *
from database import *
from historyItem import *


class HistoryManager:
    """
    Read and write playing history
    """

    def __init__(self, music_base=None):
        self.music_base = music_base
        self.database = Database(isHistory=True)
        self.log = []

    def initDataBase(self):
        self.database.initDataBase()

    def loadHistory(self, withAlbums=True):
        self.log = []
        if withAlbums:
            self.loadAlbumHistory()
        self.loadTrackHistory()
        self.loadRadioHistory()
        self.log = sorted(
            self.log, key=attrgetter("playDate", "historyType"), reverse=True
        )

    def insertAlbumHistory(self, albumID):
        """Insert album in history"""
        self.database.insertAlbumHistory(albumID)

    def loadAlbumHistory(self):
        req = """ 
        SELECT albumID, playDate 
        FROM playHistoryAlbum
        """

        for rowHisto in self.database.getSelect(req):
            histo = HistoryItem(rowHisto[1])
            histo.initHistoAlbum(rowHisto[0])
            histo.data.getAlbum(self.music_base)
            self.log.append(histo)

    def insertTrackHistory(self, albumID, fileName):
        """Insert track in history"""
        self.database.insertTrackHistory(albumID, fileName)

    def loadTrackHistory(self):
        req = """ 
        SELECT albumID, fileName, playDate 
        FROM playHistoryTrack
        """

        for rowHisto in self.database.getSelect(req):
            histo = HistoryItem(rowHisto[2])
            histo.initHistoTrack(rowHisto[0], rowHisto[1])
            histo.data.getAlbum(self.music_base)
            self.log.append(histo)

    def insertRadioHistory(self, radioName, title):
        """Insert radio title in history"""
        self.database.insertRadioHistory(radioName, title)

    def loadRadioHistory(self):
        req = """ 
        SELECT radioName, title, playDate 
        FROM playHistoryRadio
        """

        for rowHisto in self.database.getSelect(req):
            histo = HistoryItem(rowHisto[2])
            histo.initHistoRadio(rowHisto[0], rowHisto[1])
            self.log.append(histo)

    def printAll(self):
        for histo in self.log:
            histo.printData()


if __name__ == "__main__":
    from musicBase import *

    mb = MusicBase()
    mb.loadMusicBase(False)

    history = HistoryManager(mb)
    history.printAll()

    sql = """    INSERT INTO playHistoryRadio ({columns})
                    VALUES ('{radioName}','{title}',datetime('now','localtime'));
              """.format(
        columns="radioName, title, playDate", radioName="testRad", title="MyTitle"
    )
    print(sql)
