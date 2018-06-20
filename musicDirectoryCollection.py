#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from musicDirectory import *


def filterByID(seq, id):
    for el in seq:
        if el.musicDirectoryID==id : yield el


class musicDirectoryCollection:
    """
    MusicDirectoryCollection class
    """

    def __init__(self,mainMusicBase):
        self.musicDirectories = [] #MusicDirectory Collection
        self.musicBase = mainMusicBase
        

    def addMusicDirectory(self,musicDirectory):
        if musicDirectory.musicDirectoryID == 0:
            musicDirectory.musicDirectoryID = self.insertMusicDirectoryDB(musicDirectory)

        self.musicDirectories.append(musicDirectory)
        return musicDirectory.musicDirectoryID

    def printMusicDirectories(self):
        for dir in self.musicDirectories:
            dir.printInfos()



    def insertMusicDirectoryDB(self,musicDirectory):

        try:
            c = self.musicBase.db.connection.cursor()
            sqlInsertMusicDirectory = """    INSERT INTO musicDirectories (dirPath, dirName)
                                VALUES (?,?);
                          """
            c.execute(sqlInsertMusicDirectory,(musicDirectory.dirPath,musicDirectory.dirName))
            self.musicBase.db.connection.commit()
            musicDirectory.musicDirectoryID = c.lastrowid
        except sqlite3.Error as e:
            print(e)
        

        return musicDirectory.musicDirectoryID


    def loadMusicDirectories(self):
        req = "SELECT musicDirectoryID, dirPath, dirName, styleID, ifnull(dirType,0) as dirType FROM musicDirectories"
        for row_dir in self.musicBase.db.getSelect(req):
            print('{0} : {1}'.format(row_dir[0], row_dir[1]))
            dir = musicDirectory(self.musicBase)
            dir.load(row_dir)
            self.addMusicDirectory(dir)


    def getMusicDirectory(self,id):
        resMB = None
        for mdir in filterByID(self.musicDirectories,id):
            resMB = mdir
        return resMB


    
    def getStyleIDSet(self):
        styleIDSet = set()
        for md in self.musicDirectories:
            styleIDSet.add(md.styleID)
        return styleIDSet
