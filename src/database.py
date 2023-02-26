#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, os
from PyQt5.QtCore import pyqtSignal
from shutil import copyfile
from io import StringIO

from progress_widget import *
from global_constants import *
import logging

logger = logging.getLogger(__name__)


class Database:
    """
    Do the SQL things

    """

    def __init__(self, isHistory=False, db_path=""):
        self.isHistory = isHistory

        if self.isHistory:
            self.databaseName = "history.db"
        else:
            self.databaseName = "pyzik.db"

        if db_path:
            self.dataPath = db_path
        else:
            self.dataPath = dataDir + "/data/" + self.databaseName
        self.dataPathMain = dataDir + "/data/pyzik.db"
        self.connection = ""
        self.memoryConnection = ""

        self.createConnection()

    def initDataBase(self):
        print("Database in " + self.dataPath)
        if self.isHistory:
            self.createTablePlayHistoryAlbum()
            self.createTablePlayHistoryTrack()
            self.createTablePlayHistoryRadio()
            self.checkHistoryInMainDB()

        else:
            self.createTableArtists()
            self.createTableAlbums()
            self.createTableMusicDirectories()
            self.createTableRadios()

    def initMemoryDB(self):
        # Read database to tempfile

        tempfile = StringIO()

        for line in self.connection.iterdump():
            tempfile.write("%s\n" % line)

        self.connection.close()
        tempfile.seek(0)

        # Create a database in memory and import from tempfile
        self.memoryConnection = sqlite3.connect(":memory:")
        self.memoryConnection.cursor().executescript(tempfile.read())
        self.memoryConnection.commit()
        self.memoryConnection.row_factory = sqlite3.Row

        self.connection = self.memoryConnection

    def saveMemoryToDisc(self):
        copyfile(self.dataPath, self.dataPath + "k")

        self.createConnection()
        self.dropAll()
        with self.connection:
            for line in self.memoryConnection.iterdump():
                if line not in (
                    "BEGIN;",
                    "COMMIT;",
                ):  # let python handle the transactions
                    self.connection.execute(line)

        self.connection.commit()

    def createConnection(self):
        """create a database connection to the SQLite database
        specified by self.dataPath
        :return: Connection object or None
        """
        dirPath, db_file = os.path.split(self.dataPath)
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)

        try:
            self.connection = sqlite3.connect(self.dataPath)
            return self.connection
        except sqlite3.Error as e:
            print(e)
            return None

    def vacuum(self):
        try:
            c = self.connection.cursor()
            c.execute("VACUUM")

        except sqlite3.Error as e:
            print(e)

    def execSQLWithoutResult(self, sql, attachMain=False):
        try:
            c = self.connection.cursor()
            if attachMain:
                c.execute("ATTACH DATABASE '" + self.dataPathMain + "' as 'maindb';")
            c.execute("BEGIN;")
            c.execute(sql)
            c.execute("COMMIT;")
            if attachMain:
                c.execute("DETACH DATABASE 'maindb';")
            return True
        except sqlite3.Error as e:
            print(e)
            return False

    def dropTable(self, tableName, attachMain=False):
        """drop the table called tableName"""
        print("dropTable " + tableName)
        self.execSQLWithoutResult("DROP TABLE IF EXISTS " + tableName, attachMain)

    def checkHistoryInMainDB(self):
        if self.isHistory:
            if self.tableExistsInMainDB("playHistoryRadio") > 0:
                if self.getCountTableInMainDB("playHistoryRadio") > 0:
                    query = """INSERT INTO playHistoryRadio (radioName, title, playDate) 
                           SELECT radioName, title, playDate FROM maindb.playHistoryRadio as phr;"""
                    if self.execSQLWithoutResult(query, True):
                        self.dropTable("maindb.playHistoryRadio", True)

            if self.tableExistsInMainDB("playHistoryAlbum") > 0:
                if self.getCountTableInMainDB("playHistoryAlbum") > 0:
                    query = """INSERT INTO playHistoryAlbum (albumID, playDate) 
                           SELECT albumID, playDate FROM maindb.playHistoryAlbum as pha;"""
                    if self.execSQLWithoutResult(query, True):
                        self.dropTable("maindb.playHistoryAlbum", True)

            if self.tableExistsInMainDB("playHistoryTrack") > 0:
                if self.getCountTableInMainDB("playHistoryTrack") > 0:
                    query = """INSERT INTO playHistoryTrack (albumID, fileName, playDate) 
                           SELECT albumID, fileName, playDate FROM maindb.playHistoryTrack as pht;"""
                    if self.execSQLWithoutResult(query, True):
                        self.dropTable("maindb.playHistoryTrack", True)

    def dropAll(self):
        if self.isHistory:
            self.dropHistoryTables()
        else:
            self.dropAllTables()
            self.dropTable("musicDirectories")

        self.vacuum()

    def dropAllTables(self):
        self.dropTable("artists")
        self.dropTable("albums")
        self.dropTable("radios")
        # self.dropTable("musicDirectories")

    def dropHistoryTables(self):
        self.dropTable("playHistoryAlbum")
        self.dropTable("playHistoryTrack")
        self.dropTable("playHistoryRadio")

    def insertLine(self, insertSQL):
        """insert a line from the insertSQL statement"""
        try:
            c = self.connection.cursor()
            c.execute(insertSQL)
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

    def createTableRadios(self):
        sqlCreateTableRadio = """  CREATE TABLE IF NOT EXISTS radios (
                                    radioID integer PRIMARY KEY,
                                    name text NOT NULL,
                                    stream text NOT NULL,
                                    image text,
                                    thumb text,
                                    categoryID integer,
                                    sortID integer
                                ); """
        self.execSQLWithoutResult(sqlCreateTableRadio)

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

        if not self.columnExistsInTable("albums", "creationDate"):
            print("add column creationdate")
            sqlAddcolumnDirType = """ ALTER TABLE albums ADD COLUMN creationDate date"""
            self.execSQLWithoutResult(sqlAddcolumnDirType)

        if not self.columnExistsInTable("albums", "length"):
            print("add column length")
            sqlAddcolumnDirType = """ ALTER TABLE albums ADD COLUMN length int"""
            self.execSQLWithoutResult(sqlAddcolumnDirType)

        if not self.columnExistsInTable("albums", "size"):
            print("add column size")
            sqlAddcolumnDirType = """ ALTER TABLE albums ADD COLUMN size int"""
            self.execSQLWithoutResult(sqlAddcolumnDirType)

    def createTableMusicDirectories(self):
        sqlCreateTableMusicDirectories = """ CREATE TABLE IF NOT EXISTS musicDirectories (
                                        musicDirectoryID integer PRIMARY KEY,
                                        dirPath text NOT NULL,
                                        dirName text,
                                        styleID integer
                                    ); """
        self.execSQLWithoutResult(sqlCreateTableMusicDirectories)

        if not self.columnExistsInTable("musicDirectories", "dirType"):
            sqlAddcolumnDirType = """ ALTER TABLE musicDirectories ADD COLUMN dirType integer default 0 """
            self.execSQLWithoutResult(sqlAddcolumnDirType)

    def createTablePlayHistoryAlbum(self):
        sqlCreateTablePlayHistoryAlbum = """ CREATE TABLE IF NOT EXISTS playHistoryAlbum (
                                        historyAlbumID integer PRIMARY KEY,
                                        albumID integer,
                                        playDate datetime,
                                        FOREIGN KEY (albumID) REFERENCES albums(albumID)
                                    ); """
        self.execSQLWithoutResult(sqlCreateTablePlayHistoryAlbum)

    def createTablePlayHistoryTrack(self):
        sqlCreateTablePlayHistoryTrack = """ CREATE TABLE IF NOT EXISTS playHistoryTrack (
                                        historyTrackID integer PRIMARY KEY,
                                        albumID integer,
                                        fileName text NOT NULL,
                                        playDate datetime,
                                        FOREIGN KEY (albumID) REFERENCES albums(albumID)
                                    ); """
        self.execSQLWithoutResult(sqlCreateTablePlayHistoryTrack)

    def createTablePlayHistoryRadio(self):
        sqlCreateTablePlayHistoryRadio = """ CREATE TABLE IF NOT EXISTS playHistoryRadio (
                                        historyRadioID integer PRIMARY KEY,
                                        radioName text NOT NULL,
                                        title text,
                                        playDate datetime
                                    ); """
        self.execSQLWithoutResult(sqlCreateTablePlayHistoryRadio)

        if not self.columnExistsInTable("playHistoryRadio", "radioID"):
            sqlAddcolumnDirType = """ ALTER TABLE playHistoryRadio ADD COLUMN radioID integer default 0 """
            self.execSQLWithoutResult(sqlAddcolumnDirType)

    def getSelect(self, select_sql, attachMain=False, params=None):
        # print('getSelect: '+select_sql)
        c = self.connection.cursor()
        if params is None:
            if attachMain:
                c.execute("ATTACH DATABASE '" + self.dataPathMain + "' as 'maindb';")
            c.execute(select_sql)
            rows = c.fetchall()
            if attachMain:
                c.execute("DETACH DATABASE 'maindb';")
        else:
            c.execute(select_sql, params)
            rows = c.fetchall()
        return rows

    def getCountTable(self, table):
        result = self.getSelect("SELECT COUNT(*) FROM " + table + ";")
        print("count=" + str(result))
        return result[0][0]

    def getCountTableInMainDB(self, table):
        result = self.getSelect(
            "SELECT COUNT(*) FROM maindb." + table + ";", attachMain=True
        )
        print("count=" + str(result))
        return result[0][0]

    def tableExists(self, table):
        query = (
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='"
            + table
            + "'"
        )
        result = self.getSelect(query)
        print("table " + table + " exists=" + str(result))
        return result[0][0]

    def tableExistsInMainDB(self, table):
        query = (
            "SELECT COUNT(*) FROM maindb.sqlite_master WHERE type='table' AND name='"
            + table
            + "'"
        )
        result = self.getSelect(query, True)
        # print("table "+table+" exists="+str(result))
        return result[0][0]

    def columnExistsInTable(self, table, column):
        # print('columnExistsInTable: '+table+"."+column)
        sqlExists = "PRAGMA table_info('" + table + "');"
        columns = []
        columns = self.getSelect(sqlExists)
        for col in columns:
            if column == col[1]:
                return True

        return False

    def insert(self, sql):
        """Execute an insert query"""
        try:
            c = self.connection.cursor()
            c.execute(sql)
            self.connection.commit()
            return c.lastrowid
        except sqlite3.Error as e:
            print(e)
            return 0

    def deleteWithID(self, table, idName, idValue):
        """Delete a row from table where the id called idName == idValue"""
        rowcount = 0
        try:
            c = self.connection.cursor()
            c.execute("DELETE FROM " + table + " WHERE " + idName + "=" + str(idValue))
            self.connection.commit()
            return c.rowcount
        except sqlite3.Error as e:
            print(e)
            return 0

    def insertAlbum(self, album):
        try:
            c = self.connection.cursor()
            sqlInsertAlbum = """    INSERT INTO albums (title, artistID,dirPath,year,musicDirectoryID,creationDate)
                                VALUES (?,?,?,?,?,date('now'));
                          """
            c.execute(
                sqlInsertAlbum,
                (
                    album.title,
                    album.artist_id,
                    album.dir_path,
                    album.year,
                    album.music_directory_id,
                ),
            )
            self.connection.commit()
            album.album_id = c.lastrowid
        except sqlite3.Error as e:
            logger.error(e)

        return album.album_id

    def insertArtist(self, artist):
        try:
            c = self.connection.cursor()
            sqlInsertArtist = """    INSERT INTO artists (name)
                                VALUES (?);
                          """
            c.execute(sqlInsertArtist, (artist.name,))
            self.connection.commit()
            artist.artist_id = c.lastrowid
        except sqlite3.Error as e:
            print("InsertArtist error=" + str(e))

        return artist.artist_id

    def insertTrackHistory(self, albumID, fileName):
        """Insert track in history"""

        try:
            c = self.connection.cursor()
            sqlInsertTrackHistory = """    INSERT INTO playHistoryTrack (albumID, fileName, playDate)
                        VALUES (?,?,datetime('now','localtime'));"""

            c.execute(sqlInsertTrackHistory, (albumID, fileName))
            self.connection.commit()
        except sqlite3.Error as e:
            print("insertTrackHistory error=" + str(e))
            return -1

    def insertRadioHistory(self, radioName, title):
        """Insert radio title in history"""
        try:
            c = self.connection.cursor()
            sqlInsertRadioHistory = """    INSERT INTO playHistoryRadio (radioName, title, playDate)
                        VALUES (?,?,datetime('now','localtime'));"""

            c.execute(sqlInsertRadioHistory, (radioName, title))
            self.connection.commit()
        except sqlite3.Error as e:
            print("insertRadioHistory error=" + str(e))
            return -1

    def insertAlbumHistory(self, albumID):
        """Insert album in history"""
        try:
            c = self.connection.cursor()
            sqlInsertAlbumHistory = """    INSERT INTO playHistoryAlbum (albumID, playDate)
                        VALUES (?,datetime('now','localtime'));"""

            c.execute(sqlInsertAlbumHistory, (albumID,))
            self.connection.commit()
        except sqlite3.Error as e:
            print("insertAlbumHistory error=" + str(e))
            return -1

        # sql = """    INSERT INTO playHistoryAlbum ({columns})
        #                 VALUES ('{albumID}',datetime('now','localtime'));
        #           """.format(columns="albumID, playDate",albumID=albumID)
        # return self.database.insert(sql)

    def updateValue(self, table, column, value, columnID, rowID):
        try:
            c = self.connection.cursor()
            sqlUpdate = (
                "UPDATE "
                + table
                + " SET "
                + column
                + "=? WHERE "
                + columnID
                + "="
                + str(rowID)
                + ";"
            )

            c.execute(sqlUpdate, (value,))

            self.connection.commit()

        except sqlite3.Error as e:
            print(e)


if __name__ == "__main__":
    db = Database()
    # db.dropHistoryTables()
