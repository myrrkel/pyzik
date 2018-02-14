#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import database
import os
import random

from album import *
from database import *


def filterByTitle_ArtistID(seq, title, art_id):
	for el in seq:
		if el.artistID == art_id:
			if el.title == el.formatTitle(title):
				yield el
				break
			elif el.title.replace("And","&") == el.formatTitle(title):
				yield el
				break
			elif el.title == el.formatTitle(title).replace("And","&"):
				yield el
				break

def filterByAlbumID(seq, alb_id):
	for el in seq:
		if int(el.albumID) == int(alb_id):
			yield el
			break
			

class albumCollection:
	"""
	AlbumCollection class
	"""

	def __init__(self):
		self.albums = [] #Album Collection
		self.db = database()
		

	def addAlbum(self,album):
		if album.albumID == 0:
			album.albumID = self.insertAlbumDB(album)

		self.albums.append(album)
		return album.albumID

	def printAlbums(self):
		for alb in self.albums:
			alb.printInfos()



	def insertAlbumDB(self,album):
		sqlInsertAlbum = """	INSERT INTO albums (title, artistID,dirPath,year,musicDirectoryID)
								VALUES ('{title}','{artistID}','{dirPath}','{year}','{musicDirectoryID}');
						  """.format(title=album.title,artistID=album.artistID,dirPath=album.dirPath,\
						  		year=album.year,musicDirectoryID=album.musicDirectoryID)

		album.albumID = self.db.insertLine(sqlInsertAlbum)

		return album.albumID


	def loadAlbums(self):
		for row_alb in self.db.getSelect("SELECT albumID, title, year, dirPath, artistID FROM albums"):
			alb = album("")
			alb.load(row_alb)
			self.addAlbum(alb)


	def findAlbums(self,stitle,artID):
		albumList = []
		for alb in filterByTitle_ArtistID(self.albums,stitle,artID):
			print("Found Album "+stitle+" artID="+str(alb.albumID))
			albumList.append(alb)
		return albumList


	def getAlbum(self,albID):
		resAlb = album("")
		for alb in filterByAlbumID(self.albums,albID):
			resAlb = alb
		return resAlb


	def getRandomAlbum(self):
		irandom  = random.randint(0, len(self.albums)-1)
		resAlb = self.albums[irandom]
		return resAlb


	