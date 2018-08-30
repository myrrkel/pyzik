from appdirs import *
import os
import sys

global appName
appName = "pyzik"
global appAuthor
appAuthor = "myrrkel"

global musicFilesExtension
musicFilesExtension = ["mp3","ogg","mpc","flac","m4a","wma"]
global pictureFilesExtension
imageFilesExtension = ["jpg","jpeg","png"]

global dataDir
dataDir = user_data_dir(appName, appAuthor)

global appDir
if os.path.basename(sys.executable) == "pyzik":
    appDir = os.path.dirname(os.path.realpath(sys.executable))
else:
    appDir = os.path.dirname(os.path.realpath(sys.argv[0]))


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


def keyToString2(key):
    skey = ""
    chars = key.split("-")
    for char in chars:
        #print(char)
        skey = skey + chr(int(char))

    return skey

def stringToKey2(s):
    """
    Get your oun dev api key at https://console.developers.google.com/apis
    """
    key = ""

    for c in s:
        n = ord(c)
        if key != "": key =key+'-'
        key = key+str(n)

    return key

dirbleAPIKey = stringToKey("HcFaFbIfICffGcffFGHGCCBddD")
darAPIKey = stringToKey("EDJFIIGAFA")
ytubeAPIKey = keyToString2("65-73-122-97-83-121-67-83-57-56-121-119-72-111-118-101-83-98-109-109-115-107-82-51-50-97-68-65-120-117-73-100-97-121-78-108-95-98-89")