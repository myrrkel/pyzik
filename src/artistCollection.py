#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from artist import *
import formatString as FS
from operator import itemgetter, attrgetter
from sortedcontainers import SortedKeyList


def filterByName(seq, value):
    value = FS.getSearchKey(value)

    for el in seq:
        if el.getSearchKey() == value:
            yield el
            break
        



def filterByID(seq, value):
    for el in seq:
        if el.artistID==value:
            yield el
            break




class artistCollection:
    """
    Artist's class, each album is in a directory.
    """

    def __init__(self,mainMusicBase):
        self.artists = SortedKeyList(key=attrgetter('name')) #[] #Artist Collection
        self.musicBase = mainMusicBase

        

    def addArtist(self,artist):
        #Add an artist in artists list, 


        if artist.artistID == 0:
            artist.artistID = self.musicBase.db.insertArtist(artist)

        self.artists.add(artist)

        return artist


    def getArtist(self,artistName):
        newArt = artist(artistName,0)
    
        artistList = self.findArtists(newArt.name)

        if len(artistList)==0:
            #If the artist is not found in artistCol, we add it and return the
            curArt = self.addArtist(newArt)
        elif len(artistList)==1:
            #If artists is found
            curArt = artistList[0]
        else:
            #If there is more than 1 artist, ask for the good one to user
            #For the moment, just return the first one
            curArt = artistList[0]

        return curArt



    def findArtists(self,sname):
        artistList = []

        for art in filterByName(self.artists,sname):
            artistList.append(art)
        return artistList

    def findSortedArtist(self,art):
        artistList = []
        if art in self.artists:
            print("findSortedArtist="+art.name)
            artistList.append(art)

        return artistList

    def getArtistByID(self,id):
        for art in filterByID(self.artists,id):
            return art


    def printArtists(self):
        for art in self.artists:
            art.printInfos()

    def loadArtists(self):
        for rowArt in self.musicBase.db.getSelect("SELECT artistID, name FROM artists ORDER BY name"):
            art = artist(rowArt[1],rowArt[0])
            self.addArtist(art)


    def artistCompare(art1,art2):
        return art1.name > art2.name

    def sortArtists(self): 
        self.artists = sorted(self.artists, key=attrgetter('name'))

