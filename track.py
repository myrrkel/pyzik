#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import sys
from mutagen.id3 import ID3
from mutagen.id3 import ID3NoHeaderError

class track:
    """
    Track's class, each track is music a file such mp3, ogg, wma (sic), mpc, flac...
    """

    def __init__(self,fileName,extension):
        self.trackID = 0
        self.title = ""
        self.album = ""
        self.artist = ""
        self.year = 0
        self.trackNumber = 0
        self.position = 0
        self.fileName = fileName
        self.extension = extension
        self.musicDirectoryID = ""
        
        #if fileName != "":
        #    self.extractDataFromTags()


    def printInfos(self):
        print("TrackTitle: "+self.title)

    def getFileName(self):
        return self.fileName+self.extension



    def extractDataFromTagsWithVLC(self,player,dir):
        parsedMedia = player.getParsedMedia(os.path.join(dir,self.getFileName()))
        #parsedMedia.parse()
        self.title = parsedMedia.get_meta(0)
        self.album = parsedMedia.get_meta(4)
        self.artist = parsedMedia.get_meta(1)
        #print(parsedMedia.get_parsed_status())
        self.trackNumber = parsedMedia.get_meta(5)
        self.year = parsedMedia.get_meta(8)
        print("title="+self.title+" album="+str(self.album)+" artist="+str(self.artist)+" N°"+str(self.trackNumber))



    def getMutagenTags(self,dir):
        """"""
        try:
            audio = ID3(os.path.join(dir,self.getFileName()))

            self.artist = str(audio.get('TPE1'))
            self.album = str(audio.get('TALB'))
            self.title = str(audio.get("TIT2"))
            self.year = str(audio.get("TDRC"))
            self.trackNumber = str(audio.get("TRCK"))

            if self.title in("","None"): self.title = self. fileName

        except ID3NoHeaderError:
        	print("No tags")

        	

        except:
            print("exception mutagen: "+str(sys.exc_info()[0]))

        if self.title in("","None"): self.title = self. fileName