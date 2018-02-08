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
		self.position = 0
		self.fileName = fileName
		self.extension = extension
		self.musicDirectoryID = ""
		
		if fileName != "":
			self.extractDataFromTags()


	def printInfos(self):
		print("TrackTitle: "+self.title)

	def getFileName(self):
		return self.fileName+"."+self.extension



	def extractDataFromTags(self):
		self.title = self.fileName.replace("_"," ")


			