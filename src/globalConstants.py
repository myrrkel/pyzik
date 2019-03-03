from appdirs import *
import os
import sys

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QColor
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



global settings
settings = QSettings('pyzik', 'pyzik')

global theme_color

if settings.contains('theme_color'):
    theme_color = settings.value('theme_color', type=str)
else:
    theme_color = ""

global orange
orange = QColor(216, 119, 0)