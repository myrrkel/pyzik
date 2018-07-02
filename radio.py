#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


    def addCategorie(self,cat):
        self.categories.append(cat)

    def addStream(self,stream):
        self.streams.append(stream)


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
