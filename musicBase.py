#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from database import *
from albumCollection import *
from artistCollection import *
from musicDirectoryCollection import *
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

    def loadMusicBase(self):
        self.db.initMemoryDB()
        self.musicDirectoryCol.loadMusicDirectories()
        self.artistCol.loadArtists()
        self.albumCol.loadAlbums()
        self.addAlbumsToArtists()




    def addAlbumsToArtists(self):
        for alb in self.albumCol.albums:
            artist_found = self.artistCol.getArtistByID(alb.artistID)
            if artist_found is not None:
                alb.artistName = artist_found.name
                artist_found.albums.append(alb)


    def emptyDatas(self):
        self.artistCol.artists = []
        self.albumCol.albums = []

        