#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
import getopt

from PyQt5 import QtWidgets, Qt
from PyQt5.QtGui import QPalette
import qdarktheme
from player_vlc import PlayerVLC
from database import Database
from music_base import MusicBase
from translators import *
from main_window_loader import MainWindowLoader

logger = logging.getLogger(__name__)
root_logger = logging.getLogger()
root_logger.setLevel("INFO")
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root_logger.addHandler(handler)


def main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "hdp:s:", ["help", "debug", "db-path=", "style="]
        )
    except getopt.GetoptError as e:
        logger.error(e)
        print_help()
        sys.exit(2)

    db_path = ""
    style_name = ""
    for opt, arg in opts:
        if opt in ("-d", "--debug"):
            root_logger.setLevel("DEBUG")
            logger.debug("Debug mode ON")
        elif opt in ("-p", "--db-path"):
            db_path = arg
        elif opt in ("-s", "--style"):
            style_name = arg
        elif opt in ("-h", "--help"):
            print_help()
            sys.exit()

    sys.argv = [sys.argv[0]]
    logger.info("Pyzik starting...")
    app = QtWidgets.QApplication(sys.argv)

    app.setApplicationName("Pyzik")

    logger.info("Loading translations...")
    tr = Translators(app)
    locale_language = QtCore.QLocale.system().name()
    tr.install_translators(locale_language)

    # Load & Set the DarkStyleSheet
    logger.info("Available system styles: %s", QtWidgets.QStyleFactory.keys())
    if style_name:
        try:
            q_style = QtWidgets.QStyleFactory.create(style_name)
            app.setStyle(q_style)
        except Exception as e:
            logger.error(e)

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(palette)
    else:
        logger.info("Loading DarkStyleSheet...")

        app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    mb = MusicBase(db_path=db_path)
    logger.info("Loading musicBase...")
    mb.load_music_base()
    logger.info("Loading VLC player...")
    player = PlayerVLC()

    logger.info("Showing main window...")
    window = MainWindowLoader(None, app, mb, player, tr)
    window.show()

    logger.info("Go!")
    app.exec()
    window.threadStreamObserver.stop()

    db = Database()
    db.vacuum()

    player.release()

    sys.exit()


def print_help():
    help_str = """
    
#########################    
#      Pyzik Help       #
#########################

    Parameters:
        -d, --debug:       Enable debug mode
        -s, --style:       Set Qt Style (Windows, Fusion...)
        -p, --db-path:     Set the database file path (~/.local/share/pyzik/data/pyzik.db)
        -h, --help:        Display help
        
    """
    logger.info(help_str)


if __name__ == "__main__":
    main()
