#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import logging
import getopt

print("Import modules...")

from darkStyle import *
from playerVLC import *
from musicBase import *
from translators import *
from mainWindowLoader import *

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
    localeLanguage = QtCore.QLocale.system().name()
    tr.installTranslators(localeLanguage)

    # Load & Set the DarkStyleSheet
    if style_name:
        logger.info("Available system styles: %s", QtWidgets.QStyleFactory.keys())
        try:
            q_style = QtWidgets.QStyleFactory.create(style_name)
            app.setStyle(q_style)
        except Exception as e:
            logger.error(e)
    else:
        logger.info("Loading DarkStyleSheet...")
        ds = darkStyle.darkStyle()
        app.setStyleSheet(ds.load_stylesheet_pyqt5())

    mb = MusicBase(db_path=db_path)
    logger.info("Loading musicBase...")
    mb.loadMusicBase()
    logger.info("Loading VLC player...")
    player = PlayerVLC()

    logger.info("Showing main window...")
    window = MainWindowLoader(None, app, mb, player, tr)
    window.show()

    logger.info("Go!")
    app.exec()
    window.threadStreamObserver.stop()

    player.release()

    db = Database()
    db.vacuum()

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
