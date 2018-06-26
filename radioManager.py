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
        darRadios = None
        idList = self.searchDarRadiosID(search)

        for id in idList:
            darStream = self.getDarStream(id)
            print(darStream)
            stream = self.getRedirection(darStream)
            print(stream)

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


    def getDarStream(self,id):
        stream = ""

        try:
            url = "http://www.dar.fm/uberstationurlxml.php?station_id="+str(id)+"&partner_token="+darAPIKey
            r = requests.get(url)
            print(r.text)
            tree = ET.fromstring(r.text)

        except requests.exceptions.HTTPError as err:  
            print(err)

        for child in tree:
            if child.tag == "url":
                stream = child.text.strip()
                print(stream)

        return stream            


    def searchDirbleRadios(self,search):
        dirbleRadios = None
        search = urllib.parse.quote_plus(search)

        try:
            r = requests.post("http://api.dirble.com/v2/search?token="+dirbleAPIKey, data={'query': search, 'page': 1})
            dirbleRadios = json2obj(r.text)
        except requests.exceptions.HTTPError as err:  
            print(err)

        return dirbleRadios

    def search(self,search):
        resRadios = []
        dradios = self.searchDarRadios(search)
        if dradios:
            for dr in dradios:
                for strm in dr.streams:
                        rad = radio()
                        rad.initWithDirbleRadio(dr,strm.stream)
                        resRadios.append(rad)

        return resRadios



if __name__ == "__main__":

    rm = radioManager()

    radios = rm.search("FIP")
    for rad in radios:
        rad.printData()

    rm.getDarStream(110777)
