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
        self.styleID = 0
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
        print("ExploreEvent "+explEvent.eventCode+" : "+explEvent.text)



    def exploreDirectory(self,progressChanged=None):
            if self.dirType in (0,None) : self.exploreAlbumsDirectory(progressChanged)
            elif self.dirType == 1 : self.exploreArtistsDirectory(progressChanged)
            elif self.dirType == 2 : print("Song directory not managed yet!")
        

    def exploreAlbumsDirectory(self,progressChanged=None):
        
        if self.getStatus() == -1: return

        dirlist = next(os.walk(self.dirPath))[1]
        i=0
        for dir in dirlist:
            i+=1
            iProgress = round((i/len(dirlist))*100)
            progressChanged.emit(iProgress)
            curAlb = album(dir)
            curAlb.musicDirectoryID = self.musicDirectoryID
            curAlb.musicDirectory = self
            curAlb.dirPath = dir

            if curAlb.toVerify == False:
                #Artist name and album title has been found
                curArt = self.artistCol.getArtist(curAlb.artistName)
                #GetArtist return a new artist if it doesn't exists in artistsCol
                if curArt:                
                    curAlb.artistID = curArt.artistID
                    curAlb.artistName = curArt.name

                    albumList = curArt.findAlbums(curAlb.title)
                    if len(albumList)==0:
                        print("Add "+curAlb.title+" in "+curArt.name+" discography. ArtID=",curArt.artistID)
                        self.albumCol.addAlbum(curAlb)
                        curArt.addAlbum(curAlb)
                    else:
                        for alb in albumList:
                            if alb.getAlbumDir() != curAlb.getAlbumDir():
                                self.addExploreEvent(exploreEvent("ALBUM_DUPLICATE",curAlb.getAlbumDir(),alb.albumID,curArt.artistID))

                else:
                    print("No artist for "+dir)

        return 

        

    def exploreArtistsDirectory(self,progressChanged=None):
        if self.getStatus() == -1: return
        dirlist = next(os.walk(self.dirPath))[1]
        i=0
        for dir in dirlist:
            i+=1
            iProgress = round((i/len(dirlist))*100)
            progressChanged.emit(iProgress)

            print('exploreArtistsDirectory='+dir)
            curArt = self.artistCol.getArtist(dir)
            #GetArtist return a new artist if it doesn't exists in artistsCol

            self.exploreAlbumsInArtistDirectory(curArt,dir,progressChanged)


        return 



    def exploreAlbumsInArtistDirectory(self,artist,artDir,progressChanged=None):
        
        artPath = os.path.join(self.dirPath,artDir)
        dirlist = next(os.walk(artPath))[1]
        i=0
        for dir in dirlist:
            i+=1
            iProgress = round((i/len(dirlist))*100)
            progressChanged.emit(iProgress)
            curAlb = album(dir)
            curAlb.musicDirectoryID = self.musicDirectoryID
            curAlb.dirPath = artDir

            curAlb.artistID = artist.artistID
            curAlb.artistName = artist.name

            if curAlb.toVerify == False:
                #Artist name et album title has been found

                albumList = artist.findAlbums(curAlb.title)
                if len(albumList)==0:
                    print("Add "+curAlb.title+" in "+artist.name+" discography. ArtID=",artist.artistID)
                    self.albumCol.addAlbum(curAlb)
                    artist.addAlbum(curAlb)


        return 


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
        self.text = ""
        self.dirPath = dirpath
        self.artistID = artistID
        self.albumID = albumID

    def getText(self):
        if code == "ALBUM_DUPLICATE":
            return "Album in "+self.dirpath+" already exists for this artist"