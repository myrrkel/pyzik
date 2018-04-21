#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from operator import itemgetter, attrgetter

class artist:
	"""
	Artist's class, the have 
	"""

	def __init__(self,name,id):
		self.artistID = id
		self.name = self.formatName(name)
		self.countryID = 0
		self.categoryID = 0
		self.albums = []
		

	def getName(self):
		return self.name

	def formatName(self,name):
		return name.upper()



	def printInfos(self):
		print(self.name+" id="+str(self.artistID))

	def sortAlbums(self):
		self.albums = sorted(self.albums, key=attrgetter('year','title'))