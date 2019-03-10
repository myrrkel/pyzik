#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random

from album import *




def filterByTitle_ArtistID(seq, title, art_id):
    ''' not used any more, use artist.findAlbum() '''
    for el in seq:
        if el.artistID == art_id:
            if el.title == el.formatTitle(title):
                yield el
                break
            elif el.title.replace("And","&") == el.formatTitle(title).replace("And","&"):
                yield el
                break

def findByAlbumID2(seq, alb_id):
    return next(el for el in seq if int(el.albumID) == int(alb_id))
   



def findByAlbumID(seq, alb_id):
    return next((el for el in seq if int(el.albumID) == int(alb_id)),None)      

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
        for rowAlb in self.musicBase.db.getSelect("SELECT albumID, title, year, dirPath, artistID, musicDirectoryID, size, length FROM albums"):
            alb = album("")
            alb.load(rowAlb)
            self.addAlbum(alb)


    def findAlbums(self,stitle,artID):
        albumList = []
        for alb in filterByTitle_ArtistID(self.albums,stitle,artID):
            albumList.append(alb)
        return albumList


    def getAlbum(self,albID):
        return findByAlbumID(self.albums,albID) or album("")


    def getRandomAlbum(self,styleID=-2):

        if styleID > -2:
            albList = [alb for alb in self.albums if styleID in alb.styleIDSet]
        else:
            albList = self.albums

        nbAlbum = len(albList)
        if(nbAlbum > 0):
            irandom  = random.randint(0, nbAlbum-1)
            resAlb = albList[irandom]
            return resAlb

    def getAlbumsSize(self):
        for alb in self.albums:
            alb.getAlbumSize()
    

    
if __name__ == '__main__':
    from musicBase import *
    ac = albumCollection()
    ac.musicBase = musicBase()
    ac.musicBase.loadMusicBase()
    ac.loadAlbums()
    ac.printAlbums()

