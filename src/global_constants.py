from appdirs import *
import os
import sys

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QColor

APP_NAME = "pyzik"
APP_AUTHOR = "myrrkel"
MUSIC_FILE_EXTENSIONS = ["mp3", "ogg", "mpc", "flac", "m4a", "wma"]
IMAGE_FILE_EXTENSIONS = ["jpg", "jpeg", "png"]
DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)

if os.path.basename(sys.executable) == "pyzik":
    APP_DIR = os.path.dirname(os.path.realpath(sys.executable))
else:
    APP_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))

settings = QSettings("pyzik", "pyzik")

if settings.contains("theme_color"):
    THEME_COLOR = settings.value("theme_color", type=str)
else:
    THEME_COLOR = ""

ORANGE = QColor(216, 119, 0)
