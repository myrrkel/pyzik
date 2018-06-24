#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from operator import itemgetter, attrgetter

from album import *
from database import *
from historyItem import *



class historyManager():
    '''
    Read and write playing history

    '''

    def __init__(self,musicBase=None):
        self.musicBase = musicBase
        self.database = database()
        self.log = []


    def loadHistory(self,withAlbums=True):
        self.log = []
        if withAlbums: self.loadAlbumHistory()
        self.loadTrackHistory()
        self.loadRadioHistory()
        self.log = sorted(self.log , key=attrgetter('playDate','historyType'), reverse=True)



    def insertAlbumHistory(self,albumID):
        self.database.createConnection()
        print("historyAlbum=",albumID)

        try:
            c = self.database.connection.cursor()
            sqlInsertHistory = """    INSERT INTO playHistoryAlbum (albumID, playDate)
                                VALUES (?,datetime('now','localtime'));
                          """
            c.execute(sqlInsertHistory,(albumID,))
            self.database.connection.commit()
            print("New historyAlbum:",c.lastrowid)

        except sqlite3.Error as e:
            print(e)



    def loadAlbumHistory(self):
        req = """ 
        SELECT albumID, playDate 
        FROM playHistoryAlbum
        """
        
        for rowHisto in self.database.getSelect(req):
            print('AlbumID={0} Date={1}'.format(rowHisto[0], rowHisto[1]))
            histo = historyItem(rowHisto[1])
            histo.initHistoAlbum(rowHisto[0])
            histo.data.getAlbum(self.musicBase)
            self.log.append(histo)


    def insertTrackHistory(self,albumID,fileName):
        self.database.createConnection()
        print("historyTrack="+fileName+" albID=",albumID)

        try:
            c = self.database.connection.cursor()
            sqlInsertHistory = """    INSERT INTO playHistoryTrack (albumID, fileName, playDate)
                                VALUES (?,?,datetime('now','localtime'));
                          """
            c.execute(sqlInsertHistory,(albumID,fileName))
            self.database.connection.commit()
            print("New historyTrack:",c.lastrowid)

        except sqlite3.Error as e:
            print(e)



    def loadTrackHistory(self):
        req = """ 
        SELECT albumID, fileName, playDate 
        FROM playHistoryTrack
        """
        
        for rowHisto in self.database.getSelect(req):
            print('AlbumID={0} file={1} Date={2}'.format(rowHisto[0], rowHisto[1], rowHisto[2]))
            histo = historyItem(rowHisto[2])
            histo.initHistoTrack(rowHisto[0],rowHisto[1])
            histo.data.getAlbum(self.musicBase)
            self.log.append(histo)



    def insertRadioHistory(self,radioName,title):
        self.database.createConnection()
        print("historyRadio="+radioName+" title=",title)

        try:
            c = self.database.connection.cursor()
            sqlInsertHistory = """    INSERT INTO playHistoryRadio (radioName, title, playDate)
                                VALUES (?,?,datetime('now','localtime'));
                          """
            c.execute(sqlInsertHistory,(radioName,title))
            self.database.connection.commit()
            print("New historyRadio:",c.lastrowid)

        except sqlite3.Error as e:
            print(e)



    def loadRadioHistory(self):
        req = """ 
        SELECT radioName, title, playDate 
        FROM playHistoryRadio
        """
        
        for rowHisto in self.database.getSelect(req):
            print('radioName={0} title={1} Date={2}'.format(rowHisto[0], rowHisto[1], rowHisto[2]))
            histo = historyItem(rowHisto[2])
            histo.initHistoRadio(rowHisto[0],rowHisto[1])
            self.log.append(histo)


    def printAll(self):
        print("*** ALL HISTORY ***")
        for histo in self.log:
            histo.printData()





if __name__ == "__main__":
    from musicBase import *

    print('musicBase')
    mb = musicBase()
    print('loadMusicBase')
    mb.loadMusicBase(False)

    history = historyManager(mb)
    history.loadHistory()
    history.printAll()