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
        self.database = database(isHistory=True)
        self.log = []


    def initDataBase(self):
        self.database.initDataBase()



    def loadHistory(self,withAlbums=True):
        self.log = []
        if withAlbums: self.loadAlbumHistory()
        self.loadTrackHistory()
        self.loadRadioHistory()
        self.log = sorted(self.log , key=attrgetter('playDate','historyType'), reverse=True)


    def insertAlbumHistory(self,albumID):
        ''' Insert album in history '''
        sql = """    INSERT INTO playHistoryAlbum ({columns})
                        VALUES ('{albumID}',datetime('now','localtime'));
                  """.format(columns="albumID, playDate",albumID=albumID)
        return self.database.insert(sql)


    def loadAlbumHistory(self):
        req = """ 
        SELECT albumID, playDate 
        FROM playHistoryAlbum
        """
        
        for rowHisto in self.database.getSelect(req):
            histo = historyItem(rowHisto[1])
            histo.initHistoAlbum(rowHisto[0])
            histo.data.getAlbum(self.musicBase)
            self.log.append(histo)


    def insertTrackHistory(self,albumID,fileName):
        ''' Insert track in history '''

        self.database.createConnection()
        sql = """    INSERT INTO playHistoryTrack ({columns})
                        VALUES ('{albumID}','{fileName}',datetime('now','localtime'));
                  """.format(columns="albumID, fileName, playDate",albumID=albumID,fileName=fileName)
        return self.database.insert(sql)


    def loadTrackHistory(self):
        req = """ 
        SELECT albumID, fileName, playDate 
        FROM playHistoryTrack
        """
        
        for rowHisto in self.database.getSelect(req):
            histo = historyItem(rowHisto[2])
            histo.initHistoTrack(rowHisto[0],rowHisto[1])
            histo.data.getAlbum(self.musicBase)
            self.log.append(histo)



    def insertRadioHistory(self,radioName,title):
        ''' Insert radio title in history '''
        sql = """    INSERT INTO playHistoryRadio ({columns})
                        VALUES ('{radioName}','{title}',datetime('now','localtime'));"""
        sql = sql.format(columns="radioName, title, playDate",radioName=radioName,title=title)
        return self.database.insert(sql)



    def loadRadioHistory(self):
        req = """ 
        SELECT radioName, title, playDate 
        FROM playHistoryRadio
        """
        
        for rowHisto in self.database.getSelect(req):
            histo = historyItem(rowHisto[2])
            histo.initHistoRadio(rowHisto[0],rowHisto[1])
            self.log.append(histo)


    def printAll(self):
        for histo in self.log:
            histo.printData()





if __name__ == "__main__":
    from musicBase import *

    #print('musicBase')
    mb = musicBase()
    #print('loadMusicBase')
    mb.loadMusicBase(False)

    history = historyManager(mb)
    #history.loadHistory()
    history.printAll()

    sql = """    INSERT INTO playHistoryRadio ({columns})
                    VALUES ('{radioName}','{title}',datetime('now','localtime'));
              """.format(columns="radioName, title, playDate",radioName="testRad",title="MyTitle")
    print(sql)
 