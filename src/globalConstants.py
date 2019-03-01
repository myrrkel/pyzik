from appdirs import *
import os
import sys

from limbo import *

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
