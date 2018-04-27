#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os


from album import *
from database import *


class historyManager():
    '''
    Read and write playing history

    '''

    def __init__(self):

        self.db = database()



     def insertAlbumHistory(self,albumID):

        try:
            c = self.db.connection.cursor()
            sqlInsertAlbum = """    INSERT INTO playHistoryAlbum (albumID, PlayDate)
                                VALUES (?,datetime());
                          """
            c.execute(sqlInsertAlbum,albumID)
            self.db.connection.commit()

        except sqlite3.Error as e:
            print(e)

