#!/usr/bin/env python3
# -*- coding: utf-8 -*-




import sys
import logging

print("Import modules...")

from darkStyle import *
from playerVLC import *
from musicBase import *
from translators import *
from mainWindowLoader import * 

logger = logging.getLogger(__name__)
logger.setLevel("INFO")



def main():
    logger.info("Pyzik starting...")
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Pyzik")


    logger.info("Loading translations...")
    tr = translators(app)      
    localeLanguage = QtCore.QLocale.system().name()
    tr.installTranslators(localeLanguage)


    #Load & Set the DarkStyleSheet
    logger.info("Loading DarkStyleSheet...")
    app.setStyleSheet(darkStyle.darkStyle.load_stylesheet_pyqt5())
    #logger.info("Available system styles: ",QtWidgets.QStyleFactory.keys())
    #myStyle = QtWidgets.QStyleFactory.create('Windows')
    #app.setStyle(myStyle)


    mb = musicBase()
    logger.info('Loading musicBase...')
    mb.loadMusicBase()
    logger.info('Loading VLC player...')
    player = playerVLC()

    logger.info('Showing main window...')
    window = MainWindowLoader(None, app, mb, player, tr)
    window.show()

    logger.info("Go!")    
    app.exec()
    window.threadStreamObserver.stop()

    player.release()

    db = database()
    db.vacuum()

    sys.exit()



if __name__ == "__main__":
    main()

