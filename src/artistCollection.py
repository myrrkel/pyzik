#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from artist import *
import formatString as FS
from operator import itemgetter, attrgetter
from sortedcontainers import SortedKeyList


def filterByName(seq, value):
    value = FS.getSearchKey(value)
    return list(el for el in seq if el.getSearchKey() == value)
        



def findByID(seq, value):
    return next(el for el in seq if el.artistID==value)



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
        return filterByName(self.artists,sname)


    def getArtistByID(self,id):
        return findByID(self.artists,id)


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


