#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import requests
import urllib.parse
import json
from bs4 import BeautifulSoup
from collections import namedtuple
#import datetime
from datetime import datetime
from datetime import timedelta
import time
import pytz
import email.utils as eut


def _json_object_hook(d): 
    for k in d.keys():
        k = k.replace("-","_")    
    for v in d.values():
        if isinstance(v,str): v = v.replace("-","_")
    return namedtuple('X', d.keys(),rename=True)(*d.values())

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
        self.adblock = False

        self.liveID = -1
        self.liveTrackStart = None
        self.liveTrackEnd = None
        self.liveTrackTitle = ""
        self.liveCoverUrl = ""


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


    def getFIPLiveID(self):
        fipID = -1
        if self.isFIP(strict=True):
            fipID = 7
        elif "FIP " in self.name.upper():
            key = "webradio"
            iwr = self.stream.find(key)+len(key)
            if iwr > 0:
                nwr = self.stream[iwr]
                if int(nwr) == 4:
                    fipID = 69
                elif int(nwr) == 5:
                    fipID = 70
                elif int(nwr) == 6:
                    fipID = 71
                elif int(nwr) == 8:
                    fipID = 74
                else:
                    fipID = 63+int(nwr)

        return fipID

    def isFIP(self,strict=False):
        radName = "FIP"
        if strict:
            return (self.name.upper() == radName)
        else:
            return (self.name.upper() == radName or radName+" " in self.name.upper())

    def isFranceMusique(self,strict=False):
        radName = "FRANCE MUSIQUE"
        if strict:
            return (self.name.upper() == radName)
        else:
            return (self.name.upper() == radName or radName+" " in self.name.upper())

    def isFranceInter(self,strict=False):
        radName = "FRANCE INTER"
        return (self.name.upper() == radName)

    def isFranceCulture(self):
        radName = "FRANCE CULTURE"
        return (self.name.upper() == radName)

    def isFranceInfo(self):
        radName = "FRANCE INFO"
        return (self.name.upper() == radName)

    def isTSFJazz(self):
        radName = "TSF JAZZ"
        return (self.name.upper() == radName)

    def isKEXP(self):
        radName = "KEXP"
        return (self.name.upper() == radName or radName+" " in self.name.upper())


    def getFranceMusiqueLiveID(self,rurl):
        if self.isFranceMusique(strict=True):
            return 4

        try:
            url = "http://www.francemusique.fr"
            r = requests.get(url)
            html = r.text

        except requests.exceptions.HTTPError as err:  
            print(err)
            return -1

        soup = BeautifulSoup(html,"html.parser")
    
        #for p in soup.findAll("div", {"class": "web-radio-header-wrapper-content"}):
        for radiolist in soup.findAll("ul", {"class": "web-radio-header-wrapper-list"}):
            #print("radiolist="+str(radiolist))    
            for rad in radiolist.findAll("li"):
                url = rad.get("data-live-url")
                print(url)
                liveID = rad.get("data-station-id")
                print(str(liveID))

                if rurl.replace("http://","").replace("https://","") in url:
                    return liveID

        return -1


    def getCurrentTrack(self):
        title = ""
        if self.isFIP():
            liveUrl = "https://www.fip.fr/livemeta/"+str(self.getFIPLiveID())
            title = self.getCurrentTrackRF(liveUrl)

        elif self.isFranceMusique():
            if self.liveID < 0:
                self.liveID = int(self.getFranceMusiqueLiveID(self.stream))
            if self.liveID < 0: return ""
            liveUrl = "https://www.francemusique.fr/livemeta/pull/" + str(self.liveID)
            title = self.getCurrentTrackRF(liveUrl)

        elif self.isFranceInter():
            liveUrl = "https://www.francemusique.fr/livemeta/pull/1"
            title = self.getCurrentTrackRF(liveUrl)

        elif self.isFranceCulture():
            liveUrl = "https://www.francemusique.fr/livemeta/pull/5"
            title = self.getCurrentTrackRF(liveUrl)

        elif self.isFranceInfo():
            liveUrl = "https://www.francemusique.fr/livemeta/pull/2"
            title = self.getCurrentTrackRF(liveUrl)

        elif self.isTSFJazz():
            title = self.getCurrentTrackTSFJazz()

        elif self.isKEXP():
            title = self.getCurrentTrackKEXP()

        else: title = ""

        title = self.cleanTitle(title)
        self.liveTrackTitle = title

        return title


    def cleanTitle(self,title):
        clean = title.strip()
        if clean =="|": clean = ""
        if clean =="-": clean = ""
        if "targetspot" in clean.lower(): clean = ""
        return clean

    def isTimeout(self,nbSec=10):
        res = True
        tsNow =  time.time()
        if self.liveTrackEnd is not None:
            if self.liveTrackEnd > tsNow:
                res = False
            else:
                res = True
                self.liveTrackEnd = tsNow+10
        else: 
            self.liveTrackEnd = tsNow

        return res


    def getCurrentTrackTSFJazz(self):

        if not self.isTimeout(): return self.liveTrackTitle

        url = "http://www.tsfjazz.com/getSongInformations.php"
        r = requests.get(url)
        track = r.text.replace("|"," - ")
        return track


    def getCurrentTrackKEXP(self):
        
        if not self.isTimeout(): return self.liveTrackTitle

        currentTrack = ""
        try:
            liveUrl = "https://legacy-api.kexp.org/play/?format=json&limit=1"
            print("LiveUrl="+liveUrl)
            r = requests.get(liveUrl)
            if r.text == "": return ""
            if len(r.text) > 0 and r.text[0] != "{" : return ""
            #print(r.text) 
            dateRequest = r.headers.__getitem__("Date")
            dateSrv = datetime(*eut.parsedate(dateRequest)[:6])
            print("dateSrv= "+str(dateSrv))
            #print("Headers="+str(r.headers)) 
            datas = json2obj(r.text)
        except requests.exceptions.HTTPError as err:  
            print(err)

        if datas:
            if datas.results[0].playtype.playtypeid == 1:
                currentTrack = str(datas.results[0].artist.name) + " - " + str(datas.results[0].track.name)
            else:
                currentTrack = self.getCurrentShowKEXP()

        return currentTrack


    def getCurrentShowKEXP(self):
        currentShow = ""

        try:
            liveUrl = "https://legacy-api.kexp.org/show/?format=json&limit=1"
            print("LiveShowUrl="+liveUrl)
            r = requests.get(liveUrl)
            if r.text == "": return ""
            if len(r.text) > 0 and r.text[0] != "{" : return ""
            datas = json2obj(r.text)
        except requests.exceptions.HTTPError as err:  
            print(err)

        if datas:
            currentShow = str(datas.results[0].program.name) + " - " + str(datas.results[0].hosts[0].name)

        return currentShow



    def getCurrentTrackRF(self,liveUrl):

        """
        Get live title from RF
        """ 

        if self.liveTrackEnd is not None:
            tsNow =  time.time()
            #print("ts="+str(tsNow)+" - end="+str(self.liveTrackEnd))
            if self.liveTrackEnd > tsNow:
                return self.liveTrackTitle

        try:
            print("LiveUrl="+liveUrl)
            r = requests.get(liveUrl)
            if r.text == "": return ""
            if len(r.text) > 0 and r.text[0] != "{" : return ""
            #print(r.text) 
            dateRequest = r.headers.__getitem__("Date")
            dateSrv = datetime(*eut.parsedate(dateRequest)[:6])
            print("dateSrv= "+str(dateSrv))
            #print("Headers="+str(r.headers)) 
            datas = json2obj(r.text)
        except requests.exceptions.HTTPError as err:  
            print(err)

        #print(str(datas))
        if datas:
            if self.isFranceInfo():
                level = 1
            else:
                level = 0
            pos = datas.levels[level].position
            stepID = datas.levels[level].items[pos]
            #print("stepID="+str(stepID))
            #print(str(datas.steps))
            for stp in datas.steps:
                if stp.stepId == stepID:
                    self.liveTrackStart = stp.start
                    self.liveTrackEnd = stp.end

                    dateEnd = datetime.fromtimestamp(self.liveTrackEnd)
                    print("dateEnd="+str(dateEnd))
                    currentTrack = ""
                    if self.isFIP() or self.isFranceMusique():
                        if hasattr(stp,"visual") and stp.visual[:4].lower()=="http":
                            self.liveCoverUrl = stp.visual
                            print("visual="+self.liveCoverUrl)

                        if hasattr(stp,"authors") and isinstance(stp.authors,str):
                            if stp.authors != "":
                                currentTrack = stp.authors

                        if hasattr(stp,"composers") and isinstance(stp.composers,str):
                            if stp.composers != "":
                                currentTrack = stp.composers

                        if currentTrack != "":
                            currentTrack = currentTrack+" - "+stp.title
                        else:
                            currentTrack = stp.title

                    if self.isFranceInter() or self.isFranceInfo() or self.isFranceCulture():
                        if hasattr(stp,"visual") and stp.visual[:3].lower()=="http":
                            self.liveCoverUrl = stp.visual
                            print("visual="+self.liveCoverUrl)

                        if hasattr(stp,"titleConcept") and isinstance(stp.titleConcept,str):
                            currentTrack = stp.titleConcept
                            if stp.titleConcept != "":
                                currentTrack = currentTrack+" - "+stp.title
                        else:
                            currentTrack = stp.title



        print("trackTitle="+str(currentTrack))
        return currentTrack 

    
    def printData(self):
        print(self.name+" # "+self.stream+" # "+str(self.image)+" # "+str(self.thumb))

    def getRadioPic(self):
        url = self.image
        if url == "": 
            url = self.thumb
        return url

    def getCategoriesText(self):
        txt = ""
        for cat in self.categories:
            if txt != "": txt = txt +"; "
            txt = txt + cat
        return txt




if __name__ == "__main__":

    utc = datetime.utcnow()
    print(str(utc))
    dnow = datetime.now()
    print(str(dnow))
    print(time.mktime(dnow.timetuple()))


    local = pytz.timezone ("Europe/Paris")
    print(str(local))

    #datetime.fromtimestamp

    local_dt = local.localize(utc, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    print("local_dt="+str(local_dt)+" utc_dt="+str(utc_dt))

    rad = radio()
    rad.stream = "https://direct.francemusique.fr/live/francemusiquelajazz-hifi.mp3"
    rad.name = "France Musique La Jazz"
    print("Rad="+rad.getCurrentTrack())

