#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
import urllib.parse
import json

import xml.etree.ElementTree as ET

from collections import namedtuple

from radio import *
from globalConstants import *



def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())

def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

def filterByRadioID(seq, RadID):
    for el in seq:
        if int(el.radioID) == int(RadID):
            yield el
            break




class radioManager():
    """radioManager search and save web radio streams"""
    def __init__(self,musicBase=None):
        self.musicBase = musicBase
        self.machines = ['RadioBrowser','Dirble','Dar','Tunein']
        self.favRadios = []
    
            

    def getFavRadio(self,radioID):

        resRad = None
        for rad in filterByRadioID(self.favRadios,radioID):
            resRad = rad
        return resRad


    def getRedirection(self,url):
        redirection = ""
        try:
            r = requests.get(url, allow_redirects=False)
            redirection = r.headers['Location']
            

        except requests.exceptions.HTTPError as err:  
            print(err)

        return redirection


    def searchDarRadios(self,search):
        darRadios = []

        idList = self.searchDarRadiosID(search)

        for id in idList:
            print("IDDar="+str(id))
            darStation = radio()
            darStation.stream, darStation.name = self.getDarStation(id)
            darStation.stream = self.getRedirection(darStation.stream)
            #print(darStation.stream)
            darRadios.append(darStation)

        return darRadios                 


    def searchDarRadiosID(self,search):
        radIDList = []
        search = urllib.parse.quote_plus("*"+search+"*")
        try:
            url = "http://api.dar.fm/playlist.php?q=@callsign "+search
            r = requests.get(url)
            tree = ET.fromstring(r.text)

        except requests.exceptions.HTTPError as err:  
            print(err)

        for child in tree:
            if child.tag == "station":
                id = child.find("station_id")
                radIDList.append(int(id.text))

        return radIDList        


    def getDarStation(self,id):
        radio_url = ""
        name = ""

        try:
            url = "http://www.dar.fm/uberstationurlxml.php?station_id="+str(id)+"&partner_token="+darAPIKey
            print(url)
            r = requests.get(url)
            rtxt = r.text.encode('utf-8')
            tree = ET.fromstring(rtxt)

        except requests.exceptions.HTTPError as err:  
            print(err)

        if tree.find("url") is not None:
            radioUrl = tree.find("url").text.strip()
            name = tree.find("callsign").text.strip()
         
        return (radioUrl,name)         


    def searchDirbleRadios(self,search):
        dirbleRadios = []
        search = urllib.parse.quote_plus(search)
        try:
            r = requests.post("http://api.dirble.com/v2/search?token="+dirbleAPIKey, data={'query': search}, timeout = 2)
            dradios = json2obj(r.text)
            print("Dirble results="+str(dradios))
            print("Status code="+str(r.status_code))
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:  
            print(err)
            return []
        except requests.exceptions.ReadTimeout as err:
            print("searchDirbleRadios Timeout")
            return []

        if dradios:
            for dr in dradios:
                if dr.streams is None: return []
                for strm in dr.streams:
                        rad = radio()
                        rad.initWithDirbleRadio(dr,strm.stream)
                        dirbleRadios.append(rad)

        return dirbleRadios


    def searchRadioBrower(self,search):
        """
        Get radios from RadioBrowser open-source project
        http://www.radio-browser.info/webservice
        """ 
        rbRadios = []
        search = urllib.parse.quote_plus(search.replace(" ","_"))

        try:
            headers = {'User-Agent': 'pyzik 0.1b',}
            searchUrl = "http://www.radio-browser.info/webservice/json/stations/byname/"+search
            r = requests.post(searchUrl,headers=headers)
            #print(r.text)
            tradios = json2obj(r.text)
        except requests.exceptions.HTTPError as err:  
            print(err)

        if tradios:
            for tr in tradios:
                rad = radio()
                rad.name = tr.name
                rad.stream = tr.url
                rad.coutry = tr.country
                rad.image = tr.favicon
                rad.addCategorie(tr.tags)
                rbRadios.append(rad)

        return rbRadios



    def searchTuneinRadios(self,search):
        tuneinRadios = []
        search = urllib.parse.quote_plus(search)

        try:
            r = requests.post("https://api.radiotime.com/profiles?query="+search+"&filter=s!&fullTextSearch=true&limit=20&formats=mp3,aac,ogg")
            tradios = json2obj(r.text)
        except requests.exceptions.HTTPError as err:  
            print(err)

        if tradios:
            for tr in tradios.Items:
                rad = radio()
                rad.initWithTuneinRadio(tr)
                rad.stream = self.getTuneinStream(rad.searchID)
                tuneinRadios.append(rad)

        return tuneinRadios


    def getTuneinStream(self,id):

        try:
            url = "https://opml.radiotime.com/Tune.ashx?id="+id+"&render=json"
            print(url)
            r = requests.get(url)
            #print(r.text)
            station = json2obj(r.text)

        except requests.exceptions.HTTPError as err:  
            print(err)

        if hasattr(station,'body'):
            if len(station.body) > 0:
                radioUrl = station.body[0].url
         
        return radioUrl     

    def getFuzzyGroovy(self):
        fg = radio()
        fg.name = "Fuzzy & Groovy Rock Radio"
        fg.stream = "http://listen.radionomy.com/fuzzy-and-groovy.m3u"
        fg.image = "https://i3.radionomy.com/radios/400/ce7c17ce-4b4b-4698-8ed0-c2881eaf6e6b.png"
        fg.adblock = True
        return fg




    def search(self,search,machine=""):
        resRadios = []
        if machine=="" or machine=="Dar": resRadios.extend(self.searchDarRadios(search))
        if machine=="" or machine=="Dirble": resRadios.extend(self.searchDirbleRadios(search))
        if machine=="" or machine=="Tunein": resRadios.extend(self.searchTuneinRadios(search))
        if machine=="" or machine=="RadioBrowser": resRadios.extend(self.searchRadioBrower(search))
        

        return resRadios


    def loadFavRadios(self):
        self.favRadios = []
        for row in self.musicBase.db.getSelect("""
            SELECT radioID, name, stream, image, thumb, categoryID, sortID
            FROM radios ORDER BY sortID"""):
            rad = radio()
            rad.load(row)
            #rad.printData()
            self.favRadios.append(rad)


if __name__ == "__main__":

    rm = radioManager()


    rm.searchDirbleRadios("fip")

    #radios = rm.searchRadioBrower("fip")
    #for rad in radios:
    #    rad.printData()



    
 