#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os


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
		#	self.extractDataFromTags()


	def printInfos(self):
		print("TrackTitle: "+self.title)

	def getFileName(self):
		return self.fileName+self.extension



	def extractDataFromTags(self,player,dir):
		parsedMedia = player.getParsedMedia(os.path.join(dir,self.getFileName()))
		#parsedMedia.parse()
		self.title = parsedMedia.get_meta(0)
		self.album = parsedMedia.get_meta(4)
		self.artist = parsedMedia.get_meta(1)
		#print(parsedMedia.get_parsed_status())
		self.trackNumber = parsedMedia.get_meta(5)
		self.year = parsedMedia.get_meta(8)
		print("title="+self.title+" album="+str(self.album)+" artist="+str(self.artist)+" N°"+str(self.trackNumber))


			