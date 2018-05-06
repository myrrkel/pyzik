#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random

from album import *




def filterByTitle_ArtistID(seq, title, art_id):
    for el in seq:
        if el.artistID == art_id:
            if el.title == el.formatTitle(title):
                yield el
                break
            elif el.title.replace("And","&") == el.formatTitle(title):
                yield el
                break
            elif el.title == el.formatTitle(title).replace("And","&"):
                yield el
                break

def filterByAlbumID(seq, alb_id):
    for el in seq:
        if int(el.albumID) == int(alb_id):
            yield el
            break
            

class albumCollection:
    """
    AlbumCollection class
    """
    musicBase = None

    def __init__(self,mainMusicBase):
        self.albums = [] #Album Collection
        self.musicBase = mainMusicBase

        

    def addAlbum(self,album):
        if album.albumID == 0:
            album.albumID = self.musicBase.db.insertAlbum(album)

        album.musicDirectory = self.musicBase.musicDirectoryCol.getMusicDirectory(album.musicDirectoryID)
        self.albums.append(album)
        return album.albumID

    def printAlbums(self):
        for alb in self.albums:
            alb.printInfos()




    def loadAlbums(self):
        for row_alb in self.musicBase.db.getSelect("SELECT albumID, title, year, dirPath, artistID, musicDirectoryID FROM albums"):
            alb = album("")
            alb.load(row_alb)
            self.addAlbum(alb)


    def findAlbums(self,stitle,artID):
        albumList = []
        for alb in filterByTitle_ArtistID(self.albums,stitle,artID):
            albumList.append(alb)
        return albumList


    def getAlbum(self,albID):
        resAlb = album("")
        for alb in filterByAlbumID(self.albums,albID):
            resAlb = alb
        return resAlb


    def getRandomAlbum(self):
        nbAlbum = len(self.albums)
        if(nbAlbum > 0):
            irandom  = random.randint(0, nbAlbum-1)
            resAlb = self.albums[irandom]
            return resAlb


    
if __name__ == '__main__':
    from musicBase import *
    ac = albumCollection()
    ac.musicBase = musicBase()
    ac.musicBase.loadMusicBase()
    ac.loadAlbums()
    ac.printAlbums()

