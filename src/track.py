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


class track:
    """
    Track's class, each track is music a file such mp3, ogg, wma (sic), mpc, flac...
    """

    def __init__(self,fileName="",extension="",subPath=""):
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
        self.duration = 0 # in ms
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
        #self.coverDownloaded = pyqtSignal(str, name='coverDownloaded')



    def printInfos(self):
        txt = "TrackTitle="+self.title+" No="+str(self.trackNumber)+" DiscNo="+str(self.discNumber)
        txt += " TrackCount="+str(self.trackCount)+" DiscCount="+str(self.discCount)
        print(txt)

    def getName(self):
        return self.fileName+self.extension

    def getFilePathInAlbumDir(self):
        return os.path.join(self.subPath,self.getName())

    def getFilePath(self):
        return os.path.join(self.path,self.getFilePathInAlbumDir())

    def getFullFilePath(self):
        return os.path.join(self.path,self.getName())

    def setPath(self,path):
        self.subPath = ""
        self.path = os.path.dirname(path)
        basename = os.path.basename(path)
        self.fileName, self.extension = os.path.splitext(basename)

    def getArtistName(self):
        if self.parentAlbum is not None:
            return self.parentAlbum.artistName
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
            if self.artist != "" : title = title + " - " + self.artist

        return title

    def getTrackTitle(self):
        if self.radioName != "":
            if self.title != "":
                return self.title
            return self.radioName
        else:
            return self.title

    def getDuration(self,player,dir):
        media = player.getParsedMedia(os.path.join(dir,self.getFilePathInAlbumDir()))
        self.duration = media.get_duration()
        print("Duration=",self.duration)
        return self.duration

    def getDurationText(self):
        return time.strftime('%H:%M:%S', time.gmtime(self.duration))
        

    def isRadio(self):
        return self.radioName != ""

    def extractDataFromTagsWithVLC(self,player,dir):
        """
        Extract ID3 metadatas with VLC
        Using Mutagen is faster
        """
        parsedMedia = player.getParsedMedia(os.path.join(dir,self.getFilePathInAlbumDir()))
        self.title = parsedMedia.get_meta(0)
        self.album = parsedMedia.get_meta(4)
        self.artist = parsedMedia.get_meta(1)
        self.trackNumber = parsedMedia.get_meta(5)
        self.year = parsedMedia.get_meta(8)
        

    def setMRL(self,mrl):
        self.mrl = mrl
        path = unquote(mrl)
        if platform.system() == "Windows":
            path = path.replace("file:///","")
        else:
            path = path.replace("file://","")
        self.setPath(path)


    def getValidTrackNumberFromTAG(self,sTrackNo):
        if sTrackNo in ["","None"]: return
        if "/" in sTrackNo:
            pos = sTrackNo.index("/")
            self.trackNumber = int(sTrackNo[:pos])
            self.trackCount = int(sTrackNo[pos+1:])
        else:
            self.trackNumber = int(sTrackNo)

    def getValidDiscNumberFromTAG(self,sDiscNo):
        if sDiscNo in ["","None"]: return
        if "/" in sDiscNo:
            pos = sDiscNo.index("/")
            self.discNumber = int(sDiscNo[:pos])
            self.discCount = int(sDiscNo[pos+1:])
        else:
            self.discNumber = int(sDiscNo)
            

    def getMutagenTags(self,dir=""):
        """Extract ID3 metadatas, bitrate and duration with Mutagen"""
        try:
            if dir != "":
                trackPath = os.path.join(dir,self.getFilePathInAlbumDir())
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
                y = audio.tags.get("TYER")
                if y: self.year = int(y)
                y = audio.tags.get("TDRC")
                if y: self.year = int(str(y))
                self.getValidTrackNumberFromTAG(str(audio.tags.get("TRCK")))
                self.getValidDiscNumberFromTAG(str(audio.tags.get("TPOS")))


        except ID3NoHeaderError:
            print("No tags")

        except MutagenError:
            print("MutagenError:"+trackPath)

        except:
            print("exception mutagen: ",sys.exc_info()[1])
            

        if self.title in("","None"): self.title = self.fileName
        self.printInfos()


    def getMutagenFastTags(self,dir=""):
        """Extract ID3 metadatas with Mutagen"""
        try:
            if dir != "":
                trackPath = os.path.join(dir,self.getFilePathInAlbumDir())
            else:
                trackPath = self.getFilePath()
            
            audio = ID3(trackPath)
            if audio.tags:
                self.artist = str(audio.tags.get('TPE1'))
                self.album = str(audio.tags.get('TALB'))
                self.title = str(audio.tags.get("TIT2"))
                y = audio.tags.get("TYER")
                if y: self.year = int(y)
                y = audio.tags.get("TDRC")
                if y: self.year = int(str(y))
                self.trackNumber = str(audio.get("TRCK"))

        except ID3NoHeaderError:
            print("No tags")

        except MutagenError:
            print("MutagenError:"+trackPath)

        except:
            print("exception mutagen: ",sys.exc_info()[0])

        if self.title in("","None"): self.title = self.fileName



    def onCoverDownloaded(self,cover):
        self.setCover(cover)
        self.coverDownloaded.emit(cover)
