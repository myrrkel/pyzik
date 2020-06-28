#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os

import shutil
import fnmatch
from track import *
from filesUtils import *
from utils import *
from globalConstants import *
import formatString as FS
from database import *
from PyQt5.QtGui import QPixmap
import logging

logger = logging.getLogger(__name__)


def unvalidAlbumName():
    return ['Unknown album',
            'Album inconnu', ]


def unvalidArtistName():
    return ['Unknown artist',
            'Artiste inconnu', ]

def titleExcept(title):
    exceptions = ['a', 'an', 'of', 'the', 'is', 'in', 'to']
    word_list = re.split(' ', title)

    final = [capitaliseWord(word_list[0])]
    for word in word_list[1:]:
        if str.lower(word) in exceptions:
            final.append(word.lower())
        else:
            final.append(capitaliseWord(word))
    return " ".join(final)

def replaceSpecialChars(text):
    # Replace strings in given text according to the dictionary 'rep'

    rep = {"_": " ", "  ": " ", "#": "@",
           "-(": "@", ")-": "@", "- (": "@", ") -": "@",
           "-[": "@", "]-": "@", "- [": "@", "] -": "@",
           "(": "@", ")": "@", "[": "@", "]": "@",
           " - ": "@", "@ @": "@", "@@": "@"}

    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    return pattern.sub(lambda match: rep[re.escape(match.group(0))], text)


class album:
    """
    Album's class, each album is in a directory name.
    """

    def __init__(self, dirname="", musicDirectory=None):
        self.albumID = 0
        self.title = ""
        self.dirName = dirname
        self.dirPath = dirname
        self.artistID = ""
        self.artistName = ""
        self.year = 0
        self.cover = ""
        self.size = 0
        self.length = 0
        self.toVerify = False
        self.tracks = []
        self.images = []
        self.styleIDSet = set()
        self.doStop = False
        self.musicDirectory = musicDirectory
        self.coverPixmap = None  # QPixmap()
        if musicDirectory:
            self.musicDirectoryID = musicDirectory.musicDirectoryID
        else:
            self.musicDirectoryID = 0
        self.searchKey = ""

        if dirname != "":
            self.extractDataFromDirName()

    def load(self, row):
        self.albumID = row[0]
        self.title = row[1]
        self.year = row[2]
        self.dirPath = row[3]
        self.artistID = row[4]
        self.musicDirectoryID = row[5]
        self.size = row[6]
        self.length = row[7]

    def formatTitle(self, title):
        return titleExcept(title)

    def getCoverSearchText(self):
        txt = self.artistName
        if int(self.year) > 0 and int(self.year) != 9999:
            txt = txt + " " + str(self.year)
        txt = txt + " " + self.title
        return txt

    def getSearchKey(self):
        if self.searchKey == "":
            self.searchKey = FS.getSearchKey(self.title.upper())
        return self.searchKey

    def printInfos(self):
        print("Title: " + self.title + "  # Artist: " + self.artistName
              + "  # ArtistID: " + str(self.artistID)
              + "  # Year: " + str(self.year)
              + "  # musicDirectoryID: " + str(self.musicDirectoryID)
              + "  # dirPath: " + str(self.dirPath))

    def extractDataFromDirName(self):
        pos1 = self.dirName.find(" - [")
        pos2 = self.dirName.find("] - ")

        if 0 < pos1 and pos1 < pos2:
            # The name of the directory is correct like 'DEEP PURPLE - [1972] - Machine Head'
            self.title = self.dirName[pos2 + 4:]
            self.artistName = self.dirName[:pos1]
            self.year = year(self.dirName[pos1 + 4:pos2])
        else:
            # Replace characters that could beseparatorss in directory name by char @
            salb = replaceSpecialChars(self.dirName)
            salb.strip()
            if salb[len(salb) - 1] == "@": salb = salb[:len(salb) - 1]
            if salb[0] == "@": salb = salb[1:]

            # Split datas separated by @
            datas = salb.split("@")
            datas = [str.strip(data) for data in datas]

            # if len(datas)>3:
            #    print("extractDataFromDirName: more than 3 datas = "+str(datas))

            if len(datas) >= 3:
                '''With 3 or more datas in the directory name,
                we suppose that the first one is the artist name,
                If the second is a year, the third is the title'''
                self.title = ""
                self.artistName = datas[0]

                for i in range(1, len(datas)):

                    if (datas[i].isdigit()):
                        if isYear(datas[i]):
                            self.year = year(datas[i])
                    else:
                        if self.title != "": self.title += " - "
                        self.title += datas[i]


            elif len(datas) == 2:
                '''With 2 datas in the directory name,
                we suppose that the first one is the artist name,
                the second is the title'''
                self.title = datas[1]
                self.year = 0
                self.artistName = datas[0]

            else:
                # No syntax does match with this dirname
                logger.debug("No matching: " + salb + " for currentDir: " + self.dirPath)
                self.toVerify = True
        # if self.year in [0, 9999]:
        #     self.year = self.get_year_from_tags()
        if isYear(self.artistName):
            self.toVerify = True
        self.title = self.title.strip()
        self.artistName = self.artistName.strip().upper()
        self.title = self.formatTitle(self.title)

    def get_year_from_tags(self):
        track = self.getTracks(firstFileOnly=True)
        if track:
            return track.get_year_from_tags()
        return 0

    def get_pic_from_tags(self):
        track = self.getTracks(firstFileOnly=True)
        if track:
            return track.get_pic_from_tags()
        return ""

    def getTagsFromFirstFile(self):
        track = self.getTracks(firstFileOnly=True)
        if track:
            if track.artist and self.isValidArtistName(track.artist):
                self.artistName = track.artist
            else:
                return
            if track.album and self.isValidAlbumName(track.album):
                self.title = track.album
            if track.year: self.year = track.year
            print("getTagsFromFirstFile=" + self.artistName + " - " + self.title + " - " + str(self.year))

    def get_year_from_first_file(self):
        track = self.getTracks(firstFileOnly=True)
        if track:
            if track.year:
                self.year = track.year
            return track.year

    def isValidAlbumName(self, name):
        name = name.lower()
        if name:
            if name not in [x.lower() for x in unvalidAlbumName()]:
                if name != 'none':
                    for invalid in unvalidAlbumName():
                        if invalid in name:
                            return False
                    return True

    def isValidArtistName(self, name):
        name = name.lower()
        if name:
            if name not in [x.lower() for x in unvalidArtistName()]:
                if name != 'none':
                    for invalid in unvalidArtistName():
                        if invalid in name:
                            return False
                    return True

    def getTracks(self, subdir="", firstFileOnly=False):
        if subdir == "": self.tracks = []
        self.doStop = False
        if (not self.checkDir()): return False
        res = False
        if (subdir == ""):
            self.tracks = []
            currentDir = self.getAlbumDir()
        else:
            currentDir = os.path.join(self.getAlbumDir(), subdir)

        logger.debug("getTracks path %s", currentDir)
        files = os.listdir(currentDir)
        files.sort()

        nTrack = Track("", "")

        for file in files:
            if self.doStop: break
            if os.path.isdir(os.path.join(currentDir, str(file))):
                # file is a directory
                logger.debug("getTracks sub dir: %s ; %s", subdir, str(file))
                res = self.getTracks(os.path.join(subdir, str(file)), firstFileOnly=firstFileOnly)
            else:

                for ext in musicFilesExtension:
                    if fnmatch.fnmatch(file.lower(), '*.' + ext):

                        sfile = str(file)

                        if ("." in sfile):
                            filename, file_extension = os.path.splitext(sfile)
                            itrack = Track(filename, file_extension, subdir)
                            itrack.path = currentDir
                            itrack.parentAlbum = self

                            if firstFileOnly:
                                itrack.getMutagenTags(self.getAlbumDir())
                                self.tracks.append(itrack)
                                return itrack
                            else:
                                itrack.getMutagenTags(self.getAlbumDir())
                                self.tracks.append(itrack)
                            break
        return res

    def getImages(self, subdir=""):
        self.doStop = False
        if (not self.checkDir()): return False

        if (subdir == ""):
            self.images = []
            currentDir = self.getAlbumDir()
        else:
            currentDir = os.path.join(self.getAlbumDir(), subdir)

        files = os.listdir(currentDir)

        files.sort()

        for file in files:
            if self.doStop: break
            if os.path.isdir(os.path.join(currentDir, str(file))):
                # file is a directory
                self.getImages(os.path.join(subdir, file))
            else:
                if file == "cover":
                    os.rename(os.path.join(currentDir, file), os.path.join(currentDir, "cover.jpg"))

                for ext in imageFilesExtension:
                    if fnmatch.fnmatch(file.lower(), '*.' + ext):
                        sfile = os.path.join(currentDir, file)
                        self.images.append(sfile)
                        break

    def getCover(self):

        if (len(self.images) > 0):
            keywords = ["cover", "front", "artwork", "capa", "caratula", "recto", "frente editada", "frente", "folder",
                        "f"]

            for keyword in keywords:
                coverFound = next((x for x in self.images if keyword == getFileName(x.lower())), "")
                if (coverFound != ""):
                    # print("Image found equal="+keyword)
                    self.cover = coverFound
                    break

            if (coverFound == ""):
                for keyword in keywords:
                    coverFound = next((x for x in self.images if
                                       (keyword in getFileName(x.lower()) and "back" not in getFileName(x.lower()))),
                                      "")
                    if (coverFound != ""):
                        self.cover = coverFound
                        break
            # print("getCover cover="+self.cover)

            if self.cover == "":
                # print("getCover GetDefault="+self.images[0])
                self.cover = self.images[0]

        logger.debug("getCover %s", self.cover)
        if self.cover == "":
            self.cover = self.get_pic_from_tags()
            logger.debug("getCover %s", self.cover)


    def getCoverPath(self):
        return os.path.join(self.getAlbumDir(), self.cover)

    def checkDir(self):
        if self.musicDirectory:
            albDir = self.getAlbumDir()
            if albDir:
                return os.path.exists(albDir)
        else:
            return False

    def setDoStop(self):
        self.doStop = True

    def getAlbumDir(self):
        if self.musicDirectory:
            albumDir = os.path.join(self.musicDirectory.getDirPath(), self.dirPath)
            return albumDir
        else:
            return self.dirPath

    def getTracksFilePath(self):
        files = []
        for track in self.tracks:
            files.append(track.getFilePath())
        return files

    def addStyle(self, idSet):
        self.styleIDSet = self.styleIDSet.union(idSet)

    def updateTitle(self):
        db = database()
        db.updateValue("albums", "title", self.title, "albumID", self.albumID)

    def updateYear(self):
        db = database()
        db.updateValue("albums", "year", self.year, "albumID", self.albumID)

    def updateSize(self):
        db = database()
        db.updateValue("albums", "size", self.size, "albumID", self.albumID)

    def updateLength(self):
        db = database()
        db.updateValue("albums", "length", self.length, "albumID", self.albumID)

    def update(self):
        self.updateTitle()
        self.updateYear()

    def cutCoverFromPath(self, path):
        destFile = os.path.join(self.getAlbumDir(), "cover.jpg")
        if os.path.isfile(destFile):
            os.replace(path, destFile)
        else:
            shutil.move(path, destFile)
        self.cover = "cover.jpg"

    def getAlbumSize(self):
        size = getFolderSize(self.getAlbumDir())
        print(self.title + " size=" + convert_size(self.size))
        if size > 0 and size != self.size:
            self.size = size
            print(self.title + " size=" + convert_size(self.size))
            self.updateSize()

    def getLength(self):

        if len(self.tracks) == 0: self.getTracks()
        alb_length = 0
        for trk in self.tracks:
            alb_length += trk.duration

        print("album length=" + str(alb_length))
        if alb_length > 0 and (alb_length != self.length or self.length is None):
            self.length = int(alb_length)
            self.updateLength()

    def get_formatted_dir_name(self):
        return "{artist} - [{year}] - {title}".format(artist=self.artistName, year=self.year or '9999', title=self.title)



if __name__ == '__main__':
    alb = album("ACDC - [1975] - TNT")
    print(alb.title)
    alb = album("ACDC - [1983] - a tribute to")
    print(alb.title)
    alb = album("ACDC - a tribute to")
    print(alb.get_formatted_dir_name())
