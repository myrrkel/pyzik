#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from albumCollection import *
from artistCollection import *

class musicDirectory:
    """
    musicDirectory contains albums or artist's directories.
    It have a style: Various (default), Rock, Jazz...
    All his albums heritates of this style on import
    """

    def __init__(self,musicBase,dirPath=""):

        self.musicBase = musicBase
        self.albumCol = albumCollection(self.musicBase)
        self.artistCol = artistCollection(self.musicBase)
        self.dirPath = dirPath
        self.musicDirectoryID = 0
        self.styleID = -1
        self.dirName = ""
        self.albums = []
        self.dirType = 0
        self.status = 0 # -1=Error ,0=Unknown , 1=OK
        self.exploreEvents = []



    def load(self,row):
        #musicDirectoryID, dirPath, dirName, styleID
        self.musicDirectoryID = row[0]
        self.dirPath = row[1]
        self.dirName = row[2]
        self.styleID = row[3]
        self.dirType = row[4]
        

    def getDirPath(self):
        return self.dirPath

    def getStatus(self,verify=True):
        if self.status == 0 or verify:
            exist = os.path.exists(self.dirPath)
            if exist:
                self.status = 1
            else:
                self.status = -1
        return self.status

    def addExploreEvent(self,explEvent):
        self.exploreEvents.append(explEvent)
        print("ExploreEvent "+explEvent.eventCode+" : "+explEvent.getText())



    def exploreDirectory(self,progressChanged=None):
            if self.dirType in (0,None) : self.exploreAlbumsDirectory(progressChanged)
            elif self.dirType == 1 : self.exploreArtistsDirectory(progressChanged)
            elif self.dirType == 2 : print("Song directory not managed yet!")
        

    def exploreAlbumsDirectory(self,progressChanged=None):
        
        if self.getStatus() == -1: return

        dirlist = next(os.walk(self.dirPath))[1]
        for i, dir in enumerate(dirlist):
            iProgress = round((i/len(dirlist))*100)
            progressChanged.emit(iProgress)
            curAlb = album(dir,self)

            if not curAlb.toVerify:
                #Artist name and album title has been found
                curArt = self.artistCol.getArtist(curAlb.artistName)
                #GetArtist return a new artist if it doesn't exists in artistsCol
                if curArt:                
                    curAlb.artistID = curArt.artistID
                    curAlb.artistName = curArt.name
                    curAlb.addStyle({self.styleID})

                    albumList = curArt.findAlbums(curAlb.title)
                    if not albumList:
                        print("Add "+curAlb.title+" in "+curArt.name+" discography. ArtID=",curArt.artistID)
                        #curAlb.getAlbumSize()
                        #curAlb.getLength()
                        self.albumCol.addAlbum(curAlb)
                        curArt.addAlbum(curAlb)
                    else:
                        for alb in albumList:
                            if alb.getAlbumDir() != curAlb.getAlbumDir():
                                self.addExploreEvent(exploreEvent("ALBUM_DUPLICATE",curAlb.getAlbumDir(),alb.albumID,curArt.artistID))

                else:
                    print("exploreAlbumsDirectory - No artist for "+dir)
            else:
                self.addExploreEvent(exploreEvent("ALBUM_TO_VERIFY",curAlb.getAlbumDir()))

        return 

        

    def exploreArtistsDirectory(self,progressChanged=None):
        if self.getStatus() == -1: return
        dirlist = next(os.walk(self.dirPath))[1]
        i=0
        for dirArt in dirlist:
            i+=1
            iProgress = round((i/len(dirlist))*100)
            progressChanged.emit(iProgress)

            print('exploreArtistsDirectory='+dirArt)
            curArt = self.artistCol.getArtist(dirArt)
            #GetArtist return a new artist if it doesn't exists in artistsCol

            self.exploreAlbumsInArtistDirectory(curArt,dirArt,progressChanged)


        return 



    def exploreAlbumsInArtistDirectory(self,artist,dirArt,progressChanged=None):
        
        artPath = os.path.join(self.dirPath,dirArt)
        dirlist = next(os.walk(artPath))[1]
        i=0

        if len(dirlist)==0 :
            print("This artist directory has no sub directory : "+artPath)
            return False

        for dirAlb in dirlist:
            i+=1
            iProgress = round((i/len(dirlist))*100)
            progressChanged.emit(iProgress)
            albPath = os.path.join(dirArt,dirAlb)
            curAlb = album(albPath,self)
            #curAlb.musicDirectoryID = self.musicDirectoryID
            #curAlb.musicDirectory = self
            #curAlb.dirPath = dirArt

            curAlb.artistID = artist.artistID
            curAlb.artistName = artist.name

            if curAlb.toVerify == False:
                #Artist name et album title has been found

                albumList = artist.findAlbums(curAlb.title)
                if len(albumList)==0:
                    print("Add "+curAlb.title+" in "+artist.name+" discography. ArtID=",artist.artistID)
                    curAlb.getAlbumSize()
                    #curAlb.getLength()
                    self.albumCol.addAlbum(curAlb)
                    artist.addAlbum(curAlb)


        return True


    def updateMusicDirectoryDB(self):
        if self.musicDirectoryID > 0 :
            try:
                c = self.musicBase.db.connection.cursor()
                sqlInsertMusicDirectory = """    UPDATE musicDirectories SET dirPath=?, dirName=?, styleID=?, dirType=?
                            WHERE musicDirectoryID=?;
                              """
                c.execute(sqlInsertMusicDirectory,
                    (self.dirPath,
                    self.dirName,
                    self.styleID,
                    self.dirType,
                    self.musicDirectoryID))

                self.musicBase.db.connection.commit()

            except sqlite3.Error as e:
                print(e)
   

class exploreEvent:

    def __init__(self,code,dirpath,albumID=0,artistID=0):
        self.eventCode = code
        self.dirPath = dirpath
        self.artistID = artistID
        self.albumID = albumID

    def getText(self):
        if self.eventCode == "ALBUM_DUPLICATE":
            return "Album in "+self.dirPath+" already exists for this artist"
        if self.eventCode == "ALBUM_TO_VERIFY":
            return "Album in "+self.dirPath+" must be verified"