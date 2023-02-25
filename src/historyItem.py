#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class HistoryItem:
    """
    Defines different types of history items
    """

    def __init__(self, playDate):
        self.playDate = playDate
        self.historyType = 0  # 2=Album, 1=Track, 3=Radio
        self.data = None

    def initHistoAlbum(self, albumID):
        self.historyType = 1
        self.data = dataHistoAlbum(albumID)

    def initHistoTrack(self, albumID, fileName):
        self.historyType = 2
        self.data = dataHistoTrack(albumID, fileName)

    def initHistoRadio(self, radioName, title):
        self.historyType = 3
        self.data = dataHistoRadio(radioName, title)

    def printData(self):
        print(str(self.playDate) + " " + self.data.getInfo())

    def getColumnText(self, colID):
        if colID == 0:
            return str(self.playDate)
        else:
            return self.data.getColumnText(colID)


class dataHistoAlbum:
    def __init__(self, albumID):
        self.albumID = albumID
        self.album = None

    def getAlbum(self, music_base):
        self.album = music_base.albumCol.getAlbum(self.albumID)

    def getInfo(self):
        return "Artist: " + self.album.artist_name + " Album: " + self.album.title

    def getColumnText(self, colID):
        if colID == 1:
            return ""
        if colID == 2:
            return self.album.artist_name
        elif colID == 3:
            return self.album.title
        else:
            return ""


class dataHistoTrack(dataHistoAlbum):
    def __init__(self, albumID, fileName):
        self.albumID = albumID
        self.fileName = fileName

    def getInfo(self):
        return (
            "Artist: "
            + self.album.artist_name
            + " Album: "
            + self.album.title
            + " File: "
            + self.fileName
        )

    def getColumnText(self, colID):
        if colID == 1:
            return self.fileName
        elif colID == 2:
            return self.album.artist_name
        elif colID == 3:
            return self.album.title
        else:
            return ""


class dataHistoRadio:
    def __init__(self, radioName, title):
        self.radioName = radioName
        self.title = title

    def getInfo(self):
        return "Radio: " + self.radioName + " Title: " + self.title

    def getColumnText(self, colID):
        if colID == 1:
            return self.title
        elif colID == 2:
            return self.radioName
        elif colID == 3:
            return self.radioName
        else:
            return ""
