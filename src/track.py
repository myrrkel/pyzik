#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import sys
import time
import platform
from mutagen.id3 import ID3
from mutagen.id3 import ID3NoHeaderError
from mutagen import MutagenError
from mutagen import File
from urllib.parse import unquote
from PyQt5.QtCore import pyqtSignal
import logging
from utils import *

logger = logging.getLogger(__name__)


class Track:
    """
    Track's class, each track is music a file such mp3, ogg, wma (sic), mpc, flac...
    """

    def __init__(self, fileName="", extension="", subPath=""):
        self.trackID = 0
        self.title = ""
        self.album = ""
        self.artist = ""
        self.year = 0
        self.trackNumber = 0
        self.trackCount = 0
        self.discNumber = 0
        self.discCount = 0
        self.position = 0
        self.duration = 0  # in ms
        self.bitrate = 0
        self.fileName = fileName
        self.subPath = subPath
        self.path = ""
        self.extension = extension
        self.musicDirectoryID = ""
        self.mrl = ""
        self.parentAlbum = None
        self.radioName = ""
        self.radioStream = ""
        self.radioID = 0
        self.radio = None
        # self.coverDownloaded = pyqtSignal(str, name='coverDownloaded')

    def printInfos(self):
        txt = "TrackTitle=" + self.title + " No=" + str(self.trackNumber) + " DiscNo=" + str(self.discNumber)
        txt += " TrackCount=" + str(self.trackCount) + " DiscCount=" + str(self.discCount)
        logger.debug(txt)

    def getName(self):
        return self.fileName + self.extension

    def getFilePathInAlbumDir(self):
        return os.path.join(self.subPath, self.getName())

    def getFilePath(self):
        # return os.path.join(self.path, self.getFilePathInAlbumDir())
        return os.path.join(self.path, self.getName())

    def getFullFilePath(self):
        return os.path.join(self.path, self.getName())

    def setPath(self, path):
        self.subPath = ""
        self.path = os.path.dirname(path)
        basename = os.path.basename(path)
        self.fileName, self.extension = os.path.splitext(basename)

    def getArtistName(self):
        if self.parentAlbum is not None:
            return self.parentAlbum.artist_name
        else:
            return self.artist

    def getAlbumYear(self):
        if self.parentAlbum is not None and self.year == 0:
            return self.parentAlbum.year
        else:
            return self.year

    def getAlbumTitle(self):
        if self.parentAlbum is not None:
            return self.parentAlbum.title
        else:
            return self.album

    def getFullTitle(self):
        title = self.getTrackTitle()
        if not self.isRadio():
            if self.artist != "": title = title + " - " + self.artist

        return title

    def getTrackTitle(self):
        if self.radioName != "":
            if self.title != "":
                return self.title
            return self.radioName
        else:
            return self.title

    def getDuration(self, player, dir):
        media = player.getParsedMedia(os.path.join(dir, self.getFilePathInAlbumDir()))
        self.duration = media.get_duration()
        print("Duration=", self.duration)
        return self.duration

    def getDurationText(self):
        return time.strftime('%H:%M:%S', time.gmtime(self.duration))

    def isRadio(self):
        return self.radioName != ""

    def extractDataFromTagsWithVLC(self, player, dir):
        """
        Extract ID3 metadatas with VLC
        Using Mutagen is faster
        """
        parsedMedia = player.getParsedMedia(os.path.join(dir, self.getFilePathInAlbumDir()))
        self.title = parsedMedia.get_meta(0)
        self.album = parsedMedia.get_meta(4)
        self.artist = parsedMedia.get_meta(1)
        self.trackNumber = parsedMedia.get_meta(5)
        self.year = parsedMedia.get_meta(8)

    def setMRL(self, mrl):
        self.mrl = mrl
        path = unquote(mrl)
        if platform.system() == "Windows":
            path = path.replace("file:///", "")
        else:
            path = path.replace("file://", "")
        self.setPath(path)

    def getValidTrackNumberFromTAG(self, sTrackNo):
        if sTrackNo in ["", "None"]: return
        if "/" in sTrackNo:
            pos = sTrackNo.index("/")
            self.trackNumber = int(sTrackNo[:pos])
            self.trackCount = int(sTrackNo[pos + 1:])
        else:
            self.trackNumber = int(sTrackNo)

    def getValidDiscNumberFromTAG(self, sDiscNo):
        if sDiscNo in ["", "None"]: return
        if "/" in sDiscNo:
            pos = sDiscNo.index("/")
            self.discNumber = int(sDiscNo[:pos])
            self.discCount = int(sDiscNo[pos + 1:])
        else:
            self.discNumber = int(sDiscNo)

    def getMutagenTags(self, dir=""):
        """Extract ID3 metadatas, bitrate and duration with Mutagen"""
        try:
            if dir != "":
                trackPath = os.path.join(dir, self.getFilePathInAlbumDir())
            else:
                trackPath = self.getFilePath()

            audio = File(trackPath)

            if audio.info:
                self.duration = audio.info.length
                self.bitrate = audio.info.bitrate

            if audio.tags:
                self.title = str(audio.tags.get("TIT2"))
                self.artist = str(audio.tags.get('TPE1'))
                self.album = str(audio.tags.get('TALB'))
                self.year = self.get_year_from_tag_dict(audio.tags)
                self.getValidTrackNumberFromTAG(str(audio.tags.get("TRCK")))
                self.getValidDiscNumberFromTAG(str(audio.tags.get("TPOS")))


        except ID3NoHeaderError:
            logger.info("No tags")

        except MutagenError:
            logger.error("MutagenError:" + trackPath)

        except Exception as e:
            logger.error("getMutagenTags Exception mutagen: %s", e)

        if self.title in ("", "None"): self.title = self.fileName
        self.printInfos()

    def get_year_from_tags(self, dir=""):
        """Extract year with Mutagen"""
        try:
            if dir != "":
                trackPath = os.path.join(dir, self.getFilePathInAlbumDir())
            else:
                trackPath = self.getFilePath()
            logger.debug("get_year_from_tags track path %s", trackPath)
            audio = File(trackPath)

            if audio.tags:
                self.year = self.get_year_from_tag_dict(audio.tags)
                return self.year
        except Exception as e:
            logger.error("get_year_from_tags exception mutagen: %s", e)
            return 0

    def get_year_from_tag_dict(self, tag_dict):
        if tag_dict:
            y = tag_dict.get("TYER")
            if y:
                return year(y)
            else:
                y = tag_dict.get("TDRC")
                if y:
                    str_y = str(y)
                    if len(str_y) > 4:
                        logger.debug("datas: %s", str_y)
                        str_y = str_y[:4]
                    return year(str_y)

        return 0

    def get_pic_from_tags(self, dir=""):
        """Extract cover pic with Mutagen"""
        try:
            if dir != "":
                trackPath = os.path.join(dir, self.getFilePathInAlbumDir())
            else:
                trackPath = self.getFilePath()
            logger.debug("get_pic_from_tags track path %s", trackPath)
            audio = File(trackPath)
            logger.debug("get_pic_from_tags track tags %s", audio.tags)
            if audio.tags:
                pic = audio.tags.get("APIC:")
                if pic:
                    alb_dir = os.path.dirname(trackPath)
                    img_path = os.path.join(alb_dir, 'cover.jpg')
                    img_short_path = os.path.join(dir, 'cover.jpg')
                    logger.debug("get_pic_from_tags track img %s", img_path)
                    f = open(img_path, 'w+b')
                    data = pic.data
                    f.write(data)
                    f.close()
                    return img_path
            return ""
        except Exception as e:
            logger.error("get_pic_from_tags exception mutagen: %s", e)
            return ""

    def getMutagenFastTags(self, dir=""):
        """Extract ID3 metadatas with Mutagen"""
        try:
            if dir != "":
                trackPath = os.path.join(dir, self.getFilePathInAlbumDir())
            else:
                trackPath = self.getFilePath()

            audio = ID3(trackPath)
            if audio.tags:
                self.artist = str(audio.tags.get('TPE1'))
                self.album = str(audio.tags.get('TALB'))
                self.title = str(audio.tags.get("TIT2"))
                self.year = self.get_year_from_tag_dict(audio.tags)

                self.trackNumber = str(audio.get("TRCK"))

        except ID3NoHeaderError:
            logger.debug("No tags")

        except MutagenError:
            logger.error("MutagenError:" + trackPath)

        except Exception as e:
            logger.error("getMutagenFastTags exception mutagen: %s", e)

        if self.title in ("", "None"): self.title = self.fileName

    def onCoverDownloaded(self, cover):
        self.setCover(cover)
        self.coverDownloaded.emit(cover)


if __name__ == '__main__':
    import sys
    from pyzik import *
    from musicBase import *

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(darkStyle.darkStyle.load_stylesheet_pyqt5())
    mb = musicBase()
    mb.loadMusicBase()
    trk = Track("09. Not Suitable For Life", ".mp3", "/home/Documents/TEST/")
    trk.path = "/home/Documents/TEST/"
    logger.debug(trk)
    trk.get_pic_from_tags()
