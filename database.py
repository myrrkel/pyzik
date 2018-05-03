#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, os

class database():
	'''
	Do the SQL things

	'''

	def __init__(self):
		self.dataDir = "./data"
		self.connection = ""
		self.createConnection(self.dataDir+"/pyzik.db")
		self.createTableArtists()
		self.createTableAlbums()
		self.createTableMusicDirectories()
		self.createTablePlayHistoryAlbum()


	def createConnection(self,db_file):
		""" create a database connection to the SQLite database
		specified by db_file
		:param db_file: database file
		:return: Connection object or None
		"""

		if not os.path.exists(self.dataDir):
			os.makedirs(self.dataDir)
		
		try:
			self.connection = sqlite3.connect(db_file)
			return self.connection
		except sqlite3.Error as e:
			print(e)
			return None

	def execSQLWithoutResult(self, sql):
		try:
			c = self.connection.cursor()
			c.execute(sql)
		except sqlite3.Error as e:
				print(e)

	def dropTable(self, table_name):
		""" drop the table called table_name
		"""
		self.execSQLWithoutResult("DROP TABLE "+table_name)


	def dropAllTables(self):
		self.dropTable("artists")
		self.dropTable("albums")
		#self.dropTable("musicDirectories")

	def insertLine(self, insert_sql):
		""" insert a line from the insert_sql statement """
		try:
			c = self.connection.cursor()
			c.execute(insert_sql)
			self.connection.commit()
			return c.lastrowid
		except sqlite3.Error as e:
			print(e)
			return -1


	def createTableArtists(self):
		sqlCreateTableArtist = """  CREATE TABLE IF NOT EXISTS artists (
									artistID integer PRIMARY KEY,
									name text NOT NULL,
									countryID integer,
									categoryID integer
								); """
		self.execSQLWithoutResult(sqlCreateTableArtist)


	def createTableAlbums(self):
		sqlCreateTableAlbum = """ CREATE TABLE IF NOT EXISTS albums (
										albumID integer PRIMARY KEY,
										title text NOT NULL,
										dirName text,
										dirPath text,
										musicDirectoryID integer,
										artistID integer,
										year integer,
										cover text,
										FOREIGN KEY (artistID) REFERENCES artists(artistID),
										FOREIGN KEY (musicDirectoryID) REFERENCES musicDirectories(musicDirectoryID)
									); """
		self.execSQLWithoutResult(sqlCreateTableAlbum)

	def createTableMusicDirectories(self):
		sqlCreateTableMusicDirectories = """ CREATE TABLE IF NOT EXISTS musicDirectories (
										musicDirectoryID integer PRIMARY KEY,
										dirPath text NOT NULL,
										dirName text,
										styleID integer
									); """
		self.execSQLWithoutResult(sqlCreateTableMusicDirectories)

		if not self.columnExistsInTable("musicDirectories","dirType"):
			sqlAddcolumnDirType = """ ALTER TABLE musicDirectories ADD COLUMN dirType integer default 0 """
			self.execSQLWithoutResult(sqlAddcolumnDirType)




	def createTablePlayHistoryAlbum(self):
		sqlCreateTablePlayHistoryAlbum = """ CREATE TABLE IF NOT EXISTS playHistoryAlbum (
										HistoryAlbumID integer PRIMARY KEY,
										albumID integer,
										PlayDate datetime,
										FOREIGN KEY (albumID) REFERENCES albums(albumID)
									); """
		self.execSQLWithoutResult(sqlCreateTablePlayHistoryAlbum)



	def getSelect(self,select_sql,params=None):
		c = self.connection.cursor()
		if params == None:
			c.execute(select_sql)
		else:
			c.execute(select_sql,params)
		rows = c.fetchall()
		return rows


	def columnExistsInTable(self,table,column):
		sqlExists = "PRAGMA table_info("+table+");"
		columns = self.getSelect(sqlExists)
		for col in columns:
			if column == col[1] : return True

		return False




