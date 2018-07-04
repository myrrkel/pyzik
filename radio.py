#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

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

        #print(str(tRadio))

        

    
    def printData(self):
        print(self.name+" # "+self.stream+" # "+str(self.image)+" # "+str(self.thumb))

    def getCategoriesText(self):
        txt = ""
        for cat in self.categories:
            if txt != "": txt = txt +"; "
            txt = txt + cat
        return txt
