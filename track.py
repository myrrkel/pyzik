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
        self.position = 0
        self.duration = 0 # in ms
        self.fileName = fileName
        self.subPath = subPath
        self.path = ""
        self.extension = extension
        self.musicDirectoryID = ""
        self.mrl = ""
        self.parentAlbum = None
        self.radioName = ""
        self.radioStream = ""



    def printInfos(self):
        print("TrackTitle: "+self.title)

    def getFilePathInAlbumDir(self):
        return os.path.join(self.subPath,self.fileName+self.extension)

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


    def getAlbumTitle(self):
        if self.parentAlbum is not None:
            return self.parentAlbum.title
        else:
            return self.album

    def getTrackTitle(self):
        if self.radioName != "":
            return self.radioName
        else:
            return self.title

    def getDuration(self,player,dir):
        media = player.getParsedMedia(os.path.join(dir,self.getFilePathInAlbumDir()))
        self.duration = media.get_duration()
        print('Duration='+str(self.duration))
        return self.duration

    def getDurationText(self):
        return time.strftime('%H:%M:%S', time.gmtime(self.duration))
        


    def extractDataFromTagsWithVLC(self,player,dir):
        """Extract ID3 metadatas with VLC"""
        parsedMedia = player.getParsedMedia(os.path.join(dir,self.getFilePathInAlbumDir()))
        self.title = parsedMedia.get_meta(0)
        self.album = parsedMedia.get_meta(4)
        self.artist = parsedMedia.get_meta(1)
        self.trackNumber = parsedMedia.get_meta(5)
        self.year = parsedMedia.get_meta(8)
        print("title="+self.title+" album="+str(self.album)+" artist="+str(self.artist)+" N°"+str(self.trackNumber))


    def setMRL(self,mrl):
        self.mrl = mrl
        path = unquote(mrl)
        if platform.system() == "Windows":
            path = path.replace("file:///","")
        else:
            path = path.replace("file://","")
        self.setPath(path)


    def getMutagenTags(self,dir=""):
        """Extract ID3 metadatas with Mutagen"""
        try:
            if dir != "":
                trackPath = os.path.join(dir,self.getFilePathInAlbumDir())
            else:
                trackPath = os.path.join(self.path,self.getFilePathInAlbumDir())
            '''
            audio = ID3(trackPath)
            '''
            #self.artist = str(audio.tags.get('TPE1'))
            #self.album = str(audio.tags.get('TALB'))
            #self.title = str(audio.tags.get("TIT2"))
            #self.year = str(audio.tags.get("TDRC"))
            #self.trackNumber = str(audio.get("TRCK"))
            

            audio = File(trackPath)
            #["title"]
            self.duration = audio.info.length
            self.title = str(audio.tags.get("TIT2"))
            self.duration = audio.info.length

            if self.title in("","None"): self.title = self.fileName

        except ID3NoHeaderError:
            print("No tags")

        except MutagenError:
            print("MutagenError:"+trackPath)

        except:
            print("exception mutagen: "+str(sys.exc_info()[0]))

        if self.title in("","None"): self.title = self.fileName