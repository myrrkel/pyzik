#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import requests
import urllib.parse
import json
from collections import namedtuple

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())

def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

class radio:
    '''
    Radio Stream
    '''
    def __init__(self):
        self.radioID = 0
        self.name = ""
        self.country = ""
        self.image = ""
        self.thumb = ""
        self.categories = []
        self.stream = ""
        self.streamLink = ""
        self.searchID = ""
        self.sortID = 0


    def load(self,row):
        self.radioID = row[0]
        self.name = row[1]
        self.stream = row[2]
        self.image = row[3]
        self.thumb = row[4]
        self.categoryID = row[5]
        self.sortID = row[6]


    def addCategorie(self,cat):
        self.categories.append(cat)

    def addStream(self,stream):
        self.streams.append(stream)

    def getCategorieID(self):
        return 0



    def insertRadio(self,db):
        db.createConnection()

        try:
            c = db.connection.cursor()
            sqlInsertHistory = """    INSERT INTO radios (name, stream)
                                      VALUES (?,?);
                          """
            c.execute(sqlInsertHistory,(self.name,self.stream))
            db.connection.commit()
            self.radioID = c.lastrowid

        except sqlite3.Error as e:
            print(e)

    def saveRadio(self,db):
        if self.radioID == 0:
            self.insertRadio(db)

        db.createConnection()

        try:
            c = db.connection.cursor()
            sqlInsertHistory = """    UPDATE radios SET name=?, stream=?,image=?,thumb=?,categoryID=?,sortID=?
                                      WHERE radioID = ?;
                          """
            c.execute(sqlInsertHistory,(self.name,self.stream,self.image,self.thumb,self.getCategorieID(),self.sortID,self.radioID,))
            db.connection.commit()


        except sqlite3.Error as e:
            print(e)





    def initWithDirbleRadio(self,dRadio,stream):
        self.name = dRadio.name
        self.country = dRadio.country

        #print(str(dRadio))

        if hasattr(dRadio,'image'):
            if len(dRadio.image) > 0:
                self.image = dRadio.image[0]
                if hasattr(dRadio.image,'thumb'): 
                    self.thumb = dRadio.image.thumb[0]

        self.stream = stream
        for cat in dRadio.categories:
            self.addCategorie(cat.title)

    
    def initWithTuneinRadio(self,tRadio):
        self.name = tRadio.Title
        self.country = tRadio.Subtitle
        self.searchID = tRadio.GuideId


    def getRFID(self):
        id = -1
        if self.name.upper() == "FIP":
            id = 7
        elif "FIP " in self.name.upper():
            key = "webradio"
            iwr = self.stream.find(key)+len(key)
            if iwr > 0:
                nwr = self.stream[iwr]
                id = 63+int(nwr)

        return id

    def isFIP(self):
        return (self.name.upper() == "FIP" or "FIP " in self.name.upper())


    def getCurrentTrackRF(self):

        """
        Get live title from RF
        """ 
        trackTitle =""

        try:
            if self.isFIP(): liveUrl = "https://www.fip.fr/livemeta/"+str(self.getRFID())
            r = requests.post(liveUrl)
            print(r.text)
            datas = json2obj(r.text)
        except requests.exceptions.HTTPError as err:  
            print(err)

        if datas:
            pos = datas.levels[0].position
            stepID = datas.levels[0].items[pos]
            step = datas.steps.find(stepID)
            if step is not None:
                trackTitle = step.authors+" - "+step.title

        prin("trackTitle="+trackTitle)
        return trackTitle 

    
    def printData(self):
        print(self.name+" # "+self.stream+" # "+str(self.image)+" # "+str(self.thumb))

    def getCategoriesText(self):
        txt = ""
        for cat in self.categories:
            if txt != "": txt = txt +"; "
            txt = txt + cat
        return txt
