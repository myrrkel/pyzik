#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from operator import itemgetter, attrgetter
import random
from album import *
import formatString as FS

def getSimplestTitle(title,char):
    simple =  title.replace(".",char)
    simple = simple.replace(",",char)
    simple = simple.replace("'",char)
    simple = simple.replace("!",char)
    simple = simple.replace(":",char)
    simple = simple.replace("?",char)
    simple = simple.replace("  "," ")
    simple = simple.strip()
    return simple
    
def getAlternativeTitle(title):
    alter = title
    if " & " in alter:
        alter = alter.replace(" & "," And ")
    else:
        alter = alter.replace(" And "," & ")
    return alter


def filterAlbumsByTitle(seq, title):
    title = FS.getSearchKey(title.upper())

    for el in seq:
        if el.getSearchKey() == title:
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
        self.styleIDSet = set()
        self.albums = []
        self.itemListViewArtist = None
        self.searchKey = ""
        

    def getName(self):
        return self.name

    def formatName(self,name):
        return name.upper()

    def getSearchKey(self):
        if self.searchKey =="":
            self.searchKey = FS.getSearchKey(self.name)
        return self.searchKey

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

    def addStyle(self,idSet):
        self.styleIDSet = self.styleIDSet.union(idSet)


    def findAlbums(self,stitle):
        albumList = []
        for alb in filterAlbumsByTitle(self.albums,stitle):
            albumList.append(alb)
        return albumList