#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
import urllib.parse

import json
from collections import namedtuple

from radio import *



def keyToString(key):
    skey = ""
    for c in key:
        if c.isdigit():
            n = chr(96+int(c))
            skey = skey+n.upper()
        else:
            skey = skey+c

    return skey

def stringToKey(s):
    key = ""

    for c in s:
        if c == c.upper():
            n = ord(c.lower())-96
            key = key+str(n)
        else:
            key = key+c

    return key


def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())

def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

apiKey = stringToKey("GcEaEbHfHBffFcffEFGFBBAddC")



def searchDirbleRadios(search):
    dirbleRadios = None
    search = urllib.parse.quote_plus(search)

    try:
        r = requests.post("http://api.dirble.com/v2/search?token="+apiKey, data={'query': search, 'page': 1})
        dirbleRadios = json2obj(r.text)
    except:
    	print("No result")

    return dirbleRadios


radios = searchDirbleRadios("fuzzy groovy")


print("JSON")
print(radios[0])
print("JSON")
print(radios[0].streams[0])



