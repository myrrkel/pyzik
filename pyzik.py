#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtGui, QtCore

from darkStyle import darkStyle
from playerVLC import *
from mainWindowLoader import * 
from musicBase import *



def main():

    app = QtWidgets.QApplication(sys.argv)

    #Load & Set the DarkStyleSheet
    app.setStyleSheet(darkStyle.darkStyle.load_stylesheet_pyqt5())

    mb = musicBase()
    print('loadMusicBase')
    mb.loadMusicBase()
    print('player')
    player = playerVLC()

    window = MainWindowLoader(None,app,mb,player)

    print('show')
    window.show()

    app.exec()
    window.threadStreamObserver.stop()

    player.release()

    sys.exit()


if __name__ == "__main__":
    main()

