#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import database
import os

from album import *
from database import *


def filterByTitle_ID(seq, title, art_id):
	for el in seq:
		if el.artistID==art_id:
			if el.title==el.formatTitle(title): yield el
			elif el.title.replace("AND","&") ==el.formatTitle(title): yield el
			elif el.title ==el.formatTitle(title).replace("AND","&"): yield el

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
		sqlInsertAlbum = """	INSERT INTO albums (title, artistID)
								VALUES ('{title}','{artistID}');
						  """.format(title=album.title,artistID=album.artistID)

		album.albumID = self.db.insertLine(sqlInsertAlbum)

		return album.albumID


	def loadAlbums(self):
		for row_alb in self.db.getSelect("SELECT albumID, title, artistID FROM albums"):
			alb = album("")
			alb.load(row_alb)
			self.addAlbum(alb)


	def findAlbums(self,stitle,id):
		albumList = []
		for alb in filterByTitle_ID(self.albums,stitle,id):
			print("Found Album "+stitle+" id="+str(alb.albumID))
			albumList.append(alb)
		return albumList


	