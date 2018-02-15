#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from musicDirectory import *
from database import *


def filterByTitle_ID(seq, title, art_id):
	for el in seq:
		if el.musicDirectoryID==art_id:
			if el.title==el.formatTitle(title): yield el
			elif el.title.replace("AND","&") ==el.formatTitle(title): yield el
			elif el.title ==el.formatTitle(title).replace("AND","&"): yield el


class musicDirectoryCollection:
	"""
	MusicDirectoryCollection class
	"""

	def __init__(self):
		self.musicDirectories = [] #MusicDirectory Collection
		self.db = database()
		

	def addMusicDirectory(self,musicDirectory):
		if musicDirectory.musicDirectoryID == 0:
			musicDirectory.musicDirectoryID = self.insertMusicDirectoryDB(musicDirectory)

		self.musicDirectories.append(musicDirectory)
		return musicDirectory.musicDirectoryID

	def printMusicDirectories(self):
		for dir in self.musicDirectories:
			dir.printInfos()



	def insertMusicDirectoryDB(self,musicDirectory):
		'''
		sqlInsertMusicDirectory = """	INSERT INTO musicDirectories (dirPath, dirName)
								VALUES ('{dirPath}','{dirName}');
						  """.format(dirPath=musicDirectory.dirPath,dirName=musicDirectory.dirName)
		'''

		try:
			c = self.db.connection.cursor()
			sqlInsertMusicDirectory = """	INSERT INTO musicDirectories (dirPath, dirName)
								VALUES (?,?);
						  """
			c.execute(sqlInsertMusicDirectory,(musicDirectory.dirPath,musicDirectory.dirName))
			self.db.connection.commit()
			musicDirectory.musicDirectoryID = c.lastrowid
		except sqlite3.Error as e:
			print(e)
		
		#musicDirectory.musicDirectoryID = self.db.insertLine(sqlInsertMusicDirectory)

		return musicDirectory.musicDirectoryID


	def loadMusicDirectories(self):
		req = "SELECT musicDirectoryID, dirPath, dirName, styleID FROM musicDirectories"
		for row_dir in self.db.getSelect(req):
			print('{0} : {1}'.format(row_dir[0], row_dir[1]))
			dir = musicDirectory("")
			dir.load(row_dir)
			self.addMusicDirectory(dir)


	def findMusicDirectories(self,stitle,id):
		musicDirectoryList = []
		for dir in filterByTitle_ID(self.musicDirectories,stitle,id):
			print("Found MusicDirectory "+stitle+" id="+str(dir.musicDirectoryID))
			musicDirectoryList.append(dir)
		return musicDirectoryList


	