#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
from shutil import copyfile
from io import StringIO
from utils import year_to_num
import os
from src import DATA_DIR
import logging

logger = logging.getLogger(__name__)


class Database:
    """
    Do the SQL things
    """

    def __init__(self, is_history=False, db_path=""):
        self.isHistory = is_history

        if self.isHistory:
            self.databaseName = "history.db"
        else:
            self.databaseName = "pyzik.db"

        if db_path:
            self.dataPath = db_path
        else:
            self.dataPath = DATA_DIR + "/data/" + self.databaseName
        self.dataPathMain = DATA_DIR + "/data/pyzik.db"
        self.connection = ""
        self.memoryConnection = ""

        self.create_connection()

    def init_data_base(self):
        print("Database in " + self.dataPath)
        if self.isHistory:
            self.create_table_play_history_album()
            self.create_table_play_history_track()
            self.create_table_play_history_radio()
            self.check_history_in_main_db()

        else:
            self.create_table_artists()
            self.create_table_albums()
            self.create_table_music_directories()
            self.create_table_radios()

    def init_memory_db(self):
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

    def save_memory_to_disc(self):
        copyfile(self.dataPath, self.dataPath + "k")

        self.create_connection()
        self.drop_all()
        with self.connection:
            for line in self.memoryConnection.iterdump():
                if line not in (
                    "BEGIN;",
                    "COMMIT;",
                ):  # let python handle the transactions
                    self.connection.execute(line)

        self.connection.commit()

    def create_connection(self):
        """create a database connection to the SQLite database
        specified by self.dataPath
        :return: Connection object or None
        """
        dir_path, db_file = os.path.split(self.dataPath)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

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

    def exec_sql_without_result(self, sql, attach_main=False):
        try:
            c = self.connection.cursor()
            if attach_main:
                c.execute("ATTACH DATABASE '" + self.dataPathMain + "' as 'maindb';")
            c.execute("BEGIN;")
            c.execute(sql)
            c.execute("COMMIT;")
            if attach_main:
                c.execute("DETACH DATABASE 'maindb';")
            return True
        except sqlite3.Error as e:
            print(e)
            return False

    def drop_table(self, table_name, attach_main=False):
        """drop the table called tableName"""
        print("dropTable " + table_name)
        self.exec_sql_without_result("DROP TABLE IF EXISTS " + table_name, attach_main)

    def check_history_in_main_db(self):
        if self.isHistory:
            if self.table_exists_in_main_db("playHistoryRadio") > 0:
                if self.get_count_table_in_main_db("playHistoryRadio") > 0:
                    query = """INSERT INTO playHistoryRadio (radioName, title, playDate) 
                           SELECT radioName, title, playDate FROM maindb.playHistoryRadio as phr;"""
                    if self.exec_sql_without_result(query, True):
                        self.drop_table("maindb.playHistoryRadio", True)

            if self.table_exists_in_main_db("playHistoryAlbum") > 0:
                if self.get_count_table_in_main_db("playHistoryAlbum") > 0:
                    query = """INSERT INTO playHistoryAlbum (albumID, playDate) 
                           SELECT albumID, playDate FROM maindb.playHistoryAlbum as pha;"""
                    if self.exec_sql_without_result(query, True):
                        self.drop_table("maindb.playHistoryAlbum", True)

            if self.table_exists_in_main_db("playHistoryTrack") > 0:
                if self.get_count_table_in_main_db("playHistoryTrack") > 0:
                    query = """INSERT INTO playHistoryTrack (albumID, fileName, playDate) 
                           SELECT albumID, fileName, playDate FROM maindb.playHistoryTrack as pht;"""
                    if self.exec_sql_without_result(query, True):
                        self.drop_table("maindb.playHistoryTrack", True)

    def drop_all(self):
        if self.isHistory:
            self.drop_history_tables()
        else:
            self.drop_all_tables()
            self.drop_table("musicDirectories")

        self.vacuum()

    def drop_all_tables(self):
        self.drop_table("artists")
        self.drop_table("albums")
        self.drop_table("radios")
        # self.dropTable("musicDirectories")

    def drop_history_tables(self):
        self.drop_table("playHistoryAlbum")
        self.drop_table("playHistoryTrack")
        self.drop_table("playHistoryRadio")

    def insert_line(self, insert_sql):
        """insert a line from the insertSQL statement"""
        try:
            c = self.connection.cursor()
            c.execute(insert_sql)
            self.connection.commit()
            return c.lastrowid
        except sqlite3.Error as e:
            print(e)
            return -1

    def create_table_artists(self):
        req = """  CREATE TABLE IF NOT EXISTS artists (
                                    artistID integer PRIMARY KEY,
                                    name text NOT NULL,
                                    countryID integer,
                                    categoryID integer
                                ); """
        self.exec_sql_without_result(req)

    def create_table_radios(self):
        req = """  CREATE TABLE IF NOT EXISTS radios (
                                    radioID integer PRIMARY KEY,
                                    name text NOT NULL,
                                    stream text NOT NULL,
                                    image text,
                                    thumb text,
                                    categoryID integer,
                                    sortID integer
                                ); """
        self.exec_sql_without_result(req)

    def create_table_albums(self):
        req = """ CREATE TABLE IF NOT EXISTS albums (
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
        self.exec_sql_without_result(req)

        if not self.column_exists_in_table("albums", "creationDate"):
            sql_add_column_dir_type = """ ALTER TABLE albums ADD COLUMN creationDate date"""
            self.exec_sql_without_result(sql_add_column_dir_type)

        if not self.column_exists_in_table("albums", "length"):
            sql_add_column_dir_type = """ ALTER TABLE albums ADD COLUMN length int"""
            self.exec_sql_without_result(sql_add_column_dir_type)

        if not self.column_exists_in_table("albums", "size"):
            sql_add_column_dir_type = """ ALTER TABLE albums ADD COLUMN size int"""
            self.exec_sql_without_result(sql_add_column_dir_type)

    def create_table_music_directories(self):
        req = """ CREATE TABLE IF NOT EXISTS musicDirectories (
                                        musicDirectoryID integer PRIMARY KEY,
                                        dirPath text NOT NULL,
                                        dirName text,
                                        styleID integer
                                    ); """
        self.exec_sql_without_result(req)

        if not self.column_exists_in_table("musicDirectories", "dirType"):
            sql_add_column_dir_type = """ ALTER TABLE musicDirectories ADD COLUMN dirType integer default 0 """
            self.exec_sql_without_result(sql_add_column_dir_type)

    def create_table_play_history_album(self):
        req = """ CREATE TABLE IF NOT EXISTS playHistoryAlbum (
                                        historyAlbumID integer PRIMARY KEY,
                                        albumID integer,
                                        playDate datetime,
                                        FOREIGN KEY (albumID) REFERENCES albums(albumID)
                                    ); """
        self.exec_sql_without_result(req)

    def create_table_play_history_track(self):
        req = """ CREATE TABLE IF NOT EXISTS playHistoryTrack (
                                        historyTrackID integer PRIMARY KEY,
                                        albumID integer,
                                        fileName text NOT NULL,
                                        playDate datetime,
                                        FOREIGN KEY (albumID) REFERENCES albums(albumID)
                                    ); """
        self.exec_sql_without_result(req)

    def create_table_play_history_radio(self):
        req = """ CREATE TABLE IF NOT EXISTS playHistoryRadio (
                                        historyRadioID integer PRIMARY KEY,
                                        radioName text NOT NULL,
                                        title text,
                                        playDate datetime
                                    ); """
        self.exec_sql_without_result(req)

        if not self.column_exists_in_table("playHistoryRadio", "radioID"):
            sql_add_column_dir_type = """ ALTER TABLE playHistoryRadio ADD COLUMN radioID integer default 0 """
            self.exec_sql_without_result(sql_add_column_dir_type)

    def get_select(self, select_sql, attach_main=False, params=None):
        c = self.connection.cursor()
        if params is None:
            if attach_main:
                c.execute("ATTACH DATABASE '" + self.dataPathMain + "' as 'maindb';")
            c.execute(select_sql)
            rows = c.fetchall()
            if attach_main:
                c.execute("DETACH DATABASE 'maindb';")
        else:
            c.execute(select_sql, params)
            rows = c.fetchall()
        return rows

    def get_count_table(self, table):
        result = self.get_select("SELECT COUNT(*) FROM " + table + ";")
        print("count=" + str(result))
        return result[0][0]

    def get_count_table_in_main_db(self, table):
        try:
            result = self.get_select(
                "SELECT COUNT(*) FROM maindb." + table + ";", attach_main=True
            )
            print("count=" + str(result))
            return result[0][0]
        except Exception as err:
            print(err)
            pass
        return 0

    def table_exists(self, table):
        query = f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table}'"
        result = self.get_select(query)
        print("table " + table + " exists=" + str(result))
        return result[0][0]

    def table_exists_in_main_db(self, table):
        try:
            query = f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table}'"
            result = self.get_select(query, True)
            return result[0][0]
        except Exception as err:
            print(err)
            pass
        return False

    def column_exists_in_table(self, table, column):
        req = "PRAGMA table_info('" + table + "');"
        columns = self.get_select(req)
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

    def delete_with_id(self, table, id_name, id_value):
        """Delete a row from table where the id called idName == idValue"""
        try:
            c = self.connection.cursor()
            c.execute("DELETE FROM " + table + " WHERE " + id_name + "=" + str(id_value))
            self.connection.commit()
            return c.rowcount
        except sqlite3.Error as e:
            print(e)
            return 0

    def insert_album(self, album):
        try:
            c = self.connection.cursor()
            req = """    INSERT INTO albums (title, artistID,dirPath,year,musicDirectoryID,creationDate)
                                VALUES (?,?,?,?,?,date('now'));
                          """
            c.execute(
                req,
                (
                    album.title,
                    album.artist_id,
                    album.dir_path,
                    year_to_num(album.year),
                    album.music_directory_id,
                ),
            )
            self.connection.commit()
            album.album_id = c.lastrowid
        except sqlite3.Error as e:
            logger.error(e)

        return album.album_id

    def insert_artist(self, artist):
        try:
            c = self.connection.cursor()
            req = """    INSERT INTO artists (name)
                                VALUES (?);
                          """
            c.execute(req, (artist.name,))
            self.connection.commit()
            artist.artist_id = c.lastrowid
        except sqlite3.Error as e:
            print("InsertArtist error=" + str(e))

        return artist.artist_id

    def insert_track_history(self, album_id, file_name):
        """Insert track in history"""

        try:
            c = self.connection.cursor()
            req = """    INSERT INTO playHistoryTrack (albumID, fileName, playDate)
                        VALUES (?,?,datetime('now','localtime'));"""

            c.execute(req, (album_id, file_name))
            self.connection.commit()
        except sqlite3.Error as e:
            print("insertTrackHistory error=" + str(e))
            return -1

    def insert_radio_history(self, radio_name, title):
        """Insert radio title in history"""
        try:
            c = self.connection.cursor()
            req = """    INSERT INTO playHistoryRadio (radioName, title, playDate)
                        VALUES (?,?,datetime('now','localtime'));"""

            c.execute(req, (radio_name, title))
            self.connection.commit()
        except sqlite3.Error as e:
            print("insertRadioHistory error=" + str(e))
            return -1

    def insert_album_history(self, album_id):
        """Insert album in history"""
        try:
            c = self.connection.cursor()
            req = """    INSERT INTO playHistoryAlbum (albumID, playDate)
                        VALUES (?,datetime('now','localtime'));"""

            c.execute(req, (album_id,))
            self.connection.commit()
        except sqlite3.Error as e:
            print("insertAlbumHistory error=" + str(e))
            return -1

    def update_value(self, table, column, value, column_id, row_id):
        try:
            c = self.connection.cursor()
            req = (
                "UPDATE "
                + table
                + " SET "
                + column
                + "=? WHERE "
                + column_id
                + "="
                + str(row_id)
                + ";"
            )

            c.execute(req, (value,))

            self.connection.commit()

        except sqlite3.Error as e:
            print(e)


if __name__ == "__main__":
    db = Database()
    # db.dropHistoryTables()
