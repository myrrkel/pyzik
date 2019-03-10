#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtGui import QPixmap


class picBufferItem:

    users = []

    def __init__(self,path,user):
        self.path = path
        self.pix =  QPixmap(path)
        self.users.append(user)

    def addUser(self, user):

        self.users.append(user)

    def removeUser(self, user):
        
        if user in self.users:
            i = self.users.index(user)
            self.users.remove(i)

        return len(self.users)

class picBufferManager:


    """
    This pic buffer avoid to load sevral time a same pic file from hard disc,
    keep it in memory as long needed, remove it when the pic is not used anymore or
    to many others pics are loaded.

    """

    items = []


    def getPic(self,url,user):
        
        
        if url in self.items:
            i = self.items.index(url)
            pix = self.items[i].pix
            self.items[i].addUser(user)
        else:
            item = picBufferItem(url,user)
            pix = item.pix
            self.items.append(item)


        return pix


if __name__ == "__main__":

    pDL = picDownloader()
    url = "http://jamesostafford.files.wordpress.com/2012/03/41-edgar-broughton-band-inside-out.jpg"
        
    pDL.getPic(url)