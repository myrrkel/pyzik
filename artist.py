#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from operator import itemgetter, attrgetter
import random




def filterAlbumsByTitle(seq, title):
    for el in seq:
        if el.title == el.formatTitle(title):
            yield el
            break
        elif el.title.replace("And","&") == el.formatTitle(title):
            yield el
            break
        elif el.title == el.formatTitle(title).replace("And","&"):
            yield el
            break

class artist:
    """
    Artist's class, the have 
    """

    def __init__(self,name,id):
        self.artistID = id
        self.name = self.formatName(name)
        self.countryID = 0
        self.categoryID = 0
        self.albums = []
        self.itemListViewArtist = None
        

    def getName(self):
        return self.name

    def formatName(self,name):
        return name.upper()



    def printInfos(self):
        print(self.name+" id="+str(self.artistID))

    def sortAlbums(self):
        self.albums = sorted(self.albums, key=attrgetter('year','title'))

    def getRandomAlbum(self):
        nbAlbum = len(self.albums)
        if(nbAlbum > 0):
            irandom  = random.randint(0, nbAlbum-1)
            resAlb = self.albums[irandom]
            return resAlb

    def addAlbum(self,alb):
        self.albums.append(alb)


    def findAlbums(self,stitle):
        albumList = []
        for alb in filterAlbumsByTitle(self.albums,stitle):
            albumList.append(alb)
        return albumList