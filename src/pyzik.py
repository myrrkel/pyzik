#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtGui, QtCore
from darkStyle import darkStyle
from playerVLC import *
from mainWindowLoader import * 
from musicBase import *
from translators import *



def main():

    app = QtWidgets.QApplication(sys.argv)

    tr = translators(app)      
    localeLanguage = QtCore.QLocale.system().name()
    tr.installTranslators(localeLanguage)


    #Load & Set the DarkStyleSheet
    app.setStyleSheet(darkStyle.darkStyle.load_stylesheet_pyqt5())
    print("Available system styles: ",QtWidgets.QStyleFactory.keys())
    #myStyle = QtWidgets.QStyleFactory.create('Windows')
    #app.setStyle(myStyle)

    print('musicBase')
    mb = musicBase()
    print('loadMusicBase')
    mb.loadMusicBase()
    print('player')
    player = playerVLC()
    print('MainWindowLoader')
    window = MainWindowLoader(None,app,mb,player,tr)

    print('show')
    window.show()

    app.exec()
    window.threadStreamObserver.stop()

    player.release()

    sys.exit()






if __name__ == "__main__":
    main()

