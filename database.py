#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

class database():
	'''
	Do the SQL things

	'''

	def __init__(self):
		self.connection = ""
		self.createConnection("./data/pyzik.db")
		self.createTableArtists()
		self.createTableAlbums()
		self.createTableMusicDirectories()


	def createConnection(self,db_file):
		""" create a database connection to the SQLite database
		specified by db_file
		:param db_file: database file
		:return: Connection object or None
		"""
		
		try:
			self.connection = sqlite3.connect(db_file)
			return self.connection
		except sqlite3.Error as e:
			print(e)
			return None

	def createTable(self, create_table_sql):
		""" create a table from the create_table_sql statement
		:param conn: Connection object
		:param create_table_sql: a CREATE TABLE statement
		:return:
		"""
		try:
			c = self.connection.cursor()
			c.execute(create_table_sql)
		except sqlite3.Error as e:
				print(e)

	def dropTable(self, table_name):
		""" drop the table called table_name
		"""
		try:
			c = self.connection.cursor()
			c.execute("drop table "+table_name)
		except sqlite3.Error as e:
				print(e)

	def dropAllTables(self):
		self.dropTable("artists")
		self.dropTable("albums")
		self.dropTable("musicDirectories")

	def insertLine(self, insert_sql):
		""" create a table from the create_table_sql statement
		:param conn: Connection object
		:param create_table_sql: a CREATE TABLE statement
		:return:
		"""
		try:
			c = self.connection.cursor()
			c.execute(insert_sql)
			self.connection.commit()
			return c.lastrowid
		except sqlite3.Error as e:
			print(e)


	def createTableArtists(self):
		sqlCreateTableArtist = """  CREATE TABLE IF NOT EXISTS artists (
									artistID integer PRIMARY KEY,
									name text NOT NULL,
									countryID integer,
									categoryID integer
								); """
		self.createTable(sqlCreateTableArtist)


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
		self.createTable(sqlCreateTableAlbum)

	def createTableMusicDirectories(self):
		sqlCreateTableMusicDirectories = """ CREATE TABLE IF NOT EXISTS musicDirectories (
										musicDirectoryID integer PRIMARY KEY,
										dirPath text NOT NULL,
										dirName text,
										styleID integer
									); """
		self.createTable(sqlCreateTableMusicDirectories)

	def dropAllTables(self):
		self.dropTable("albums")
		self.dropTable("artists")
		self.dropTable("musicDirectories")


	def getSelect(self,select_sql):
		c = self.connection.cursor()
		c.execute(select_sql)
		rows = c.fetchall()
		return rows





