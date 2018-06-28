#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
import urllib.parse

import xml.etree.ElementTree as ET

import json
from collections import namedtuple

from radio import *



def keyToString(key):
    skey = ""
    for c in key:
        if c.isdigit():
            n = chr(97+int(c))
            skey = skey+n.upper()
        else:
            skey = skey+c

    return skey

def stringToKey(s):
    """
    Get your oun dev api key at https://dirble.com/users/sign_in
    """
    key = ""

    for c in s:
        if c == c.upper():
            n = ord(c.lower())-97
            key = key+str(n)
        else:
            key = key+c

    return key


def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())

def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

dirbleAPIKey = stringToKey("HcFaFbIfICffGcffFGHGCCBddD")
darAPIKey = stringToKey("EDJFIIGAFA")

class radioManager():
    """radioManager search and save web radio streams"""
    def __init__(self,musicBase=None):
        self.musicBase = musicBase
    
            

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
            print(darStation.stream)
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
            print(r.text)
            tree = ET.fromstring(r.text)

        except requests.exceptions.HTTPError as err:  
            print(err)

        if tree.find("url") is not None:
            radio_url = tree.find("url").text.strip()
            name = tree.find("callsign").text.strip()
         
        return (radio_url,name)         


    def searchDirbleRadios(self,search):
        dirbleRadios = []
        search = urllib.parse.quote_plus(search)

        try:
            r = requests.post("http://api.dirble.com/v2/search?token="+dirbleAPIKey, data={'query': search, 'page': 1})
            dradios = json2obj(r.text)
        except requests.exceptions.HTTPError as err:  
            print(err)

        if dradios:
            for dr in dradios:
                for strm in dr.streams:
                        rad = radio()
                        rad.initWithDirbleRadio(dr,strm.stream)
                        dirbleRadios.append(rad)

        return dirbleRadios

    def search(self,search):
        resRadios = []
        resRadios = self.searchDarRadios(search)
        resRadios.extend(self.searchDirbleRadios(search))
        

        return resRadios



if __name__ == "__main__":

    rm = radioManager()

    radios = rm.search("FIP")
    for rad in radios:
        rad.printData()

    rm.getDarStation(110777)
