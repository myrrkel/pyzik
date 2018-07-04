#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from database import *
from albumCollection import *
from artistCollection import *
from musicDirectoryCollection import *
from musicGenres import *
from historyManager import *
from radioManager import *

import os.path
from PyQt5 import QtWidgets, QtGui, QtCore





class musicBase:
    """
    musicBase manage albums and artists from
    the music directories to the database'''
    """

    def __init__(self):
        self.db = database()
        self.db.initDataBase()
        self.albumCol = albumCollection(self)
        self.artistCol = artistCollection(self)
        self.musicDirectoryCol = musicDirectoryCollection(self)
        self.genres = musicGenres()
        self.styleIDSet = set()
        self.availableGenres = set()
        self.history = historyManager()
        self.radioMan = radioManager(self)

    def loadMusicBase(self,memoryDB=True):
        if memoryDB: self.db.initMemoryDB()
        self.musicDirectoryCol.loadMusicDirectories()
        self.artistCol.loadArtists()
        self.albumCol.loadAlbums()
        self.addGenresDirToAlbums()
        self.addAlbumsToArtists()
        self.radioMan.loadFavRadios()

        self.styleIDSet = self.musicDirectoryCol.getStyleIDSet()

        #print("styleIDSet=",self.styleIDSet)
        self.availableGenres = self.genres.getAvailableGenresFormIDSet(self.styleIDSet)


    def addGenresDirToAlbums(self):
        for alb in self.albumCol.albums:
            md = self.musicDirectoryCol.getMusicDirectory(alb.musicDirectoryID)
            if md.styleID >=0:
                alb.addStyle({md.styleID})

    def addAlbumsToArtists(self):
        for alb in self.albumCol.albums:
            artistFound = self.artistCol.getArtistByID(alb.artistID)
            if artistFound is not None:
                alb.artistName = artistFound.name
                artistFound.addStyle(alb.styleIDSet)
                artistFound.albums.append(alb)


    def emptyDatas(self):
        self.artistCol.artists = set()
        self.albumCol.albums = []






        