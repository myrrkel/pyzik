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

    def __init__(self,musicBase):

        self.musicBase = musicBase
        self.albumCol = albumCollection(self.musicBase)
        self.artistCol = artistCollection(self.musicBase)
        self.dirPath = ""
        self.musicDirectoryID = 0
        self.styleID = 0
        self.dirName = ""
        self.albums = []
        self.dirType = 0
        self.status = 0 # -1=Error ,0=Unknown , 1=OK



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



    def exploreDirectory(self,progressChanged=None):
            if self.dirType in (0,None) : self.exploreAlbumsDirectory(progressChanged)
            elif self.dirType == 1 : self.exploreArtistsDirectory(progressChanged)
            elif self.dirType == 2 : print("Dirty directory not managed yet!")
        

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
            curAlb.dirPath = dir

            if curAlb.toVerify == False:
                #Artist name et album title has been found
                curArt = self.artistCol.getArtist(curAlb.artistName)
                #GetArtist return a new artist if if doesn't exists in artistsCol
                if curArt:                
                    curAlb.artistID = curArt.artistID
                    curAlb.artistName = curArt.name

                    albumList = self.albumCol.findAlbums(curAlb.title,curAlb.artistID)
                    if len(albumList)==0:
                        print("Add "+curAlb.title+" in "+curArt.name+" discography. ArtID="+str(curArt.artistID))
                        self.albumCol.addAlbum(curAlb)
                        curArt.albums.append(curAlb)
                    #else:
                        #print("Album "+curAlb.title+" already exists for "+curArt.name+" ArtistID="+str(curArt.artistID))
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
            #GetArtist return a new artist if if doesn't exists in artistsCol

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

                albumList = self.albumCol.findAlbums(curAlb.title,curAlb.artistID)
                if len(albumList)==0:
                    print("Add "+curAlb.title+" in "+artist.name+" discography. ArtID="+str(artist.artistID))
                    self.albumCol.addAlbum(curAlb)
                    artist.albums.append(curAlb)


        return 


    def updateMusicDirectoryDB(self):
        if self.musicDirectoryID > 0 :
            try:
                c = self.db.connection.cursor()
                sqlInsertMusicDirectory = """    UPDATE musicDirectories SET dirPath=?, dirName=?, styleID=?
                            WHERE musicDirectoryID=?;
                              """
                print("save idStyle="+str(self.styleID))
                c.execute(sqlInsertMusicDirectory,
                    (self.dirPath,
                    self.dirName,
                    self.styleID,
                    self.musicDirectoryID))

                self.db.connection.commit()

            except sqlite3.Error as e:
                print(e)
        

