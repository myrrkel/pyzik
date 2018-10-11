#!/usr/bin/env python3
# -*- coding: utf-8 -*-


print("Import modules...")

import sys
#import vlc

from historyManager import *
#from PyQt5 import QtWidgets, QtGui, QtCore
from darkStyle import *
from playerVLC import *
from musicBase import *
from translators import *
from mainWindowLoader import * 


def main():
    print("Pyzik starting...")
    app = QtWidgets.QApplication(sys.argv)

    print("Loading translations...")
    tr = translators(app)      
    localeLanguage = QtCore.QLocale.system().name()
    tr.installTranslators(localeLanguage)


    #Load & Set the DarkStyleSheet
    print("Loading DarkStyleSheet...")
    app.setStyleSheet(darkStyle.darkStyle.load_stylesheet_pyqt5())
    #print("Available system styles: ",QtWidgets.QStyleFactory.keys())
    #myStyle = QtWidgets.QStyleFactory.create('Windows')
    #app.setStyle(myStyle)

    print("Checking history file...")
    histoManager = historyManager()
    histoManager.database.checkHistoryInMainDB()


    mb = musicBase()
    print('Loading musicBase...')
    mb.loadMusicBase()
    print('Loading VLC player...')
    player = playerVLC()

    print('Showing main window...')
    window = MainWindowLoader(None,app,mb,player,tr)
    window.show()

    print("Go!")
    app.exec()
    window.threadStreamObserver.stop()

    player.release()

    db = database()
    db.vacuum()

    sys.exit()



if __name__ == "__main__":
    main()

