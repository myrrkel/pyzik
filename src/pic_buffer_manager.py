#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pic_downloader import PicDownloader
from PyQt5.QtGui import QPixmap


class PicBufferItem:
    users = []

    def __init__(self, path, user):
        self.path = path
        self.pix = QPixmap(path)
        self.users.append(user)

    def add_user(self, user):
        self.users.append(user)

    def remove_user(self, user):
        if user in self.users:
            i = self.users.index(user)
            self.users.remove(i)

        return len(self.users)


class PicBufferManager:
    """
    This pic buffer avoid to load several time a same pic file from hard disc,
    keep it in memory as long needed, remove it when the pic is not used anymore or
    to many others pics are loaded.

    """

    items = []

    def get_pic(self, path, user):
        item = self.find_item(path)
        if item is not None:
            pix = item.pix
            item.add_user(user)
        else:
            item = PicBufferItem(path, user)
            pix = item.pix
            item.add_user(user)
            self.items.append(item)
            self.check_buffer_size()

        return pix

    def find_item(self, path):
        items = []
        items += [el for el in self.items if el.path == path]
        if len(items) > 0:
            return items[0]
        else:
            return None

    def check_buffer_size(self):
        """Remove oldest pixmap from the buffer if 5 are in ram"""
        if len(self.items) >= 5:
            self.items.remove(self.items[0])


if __name__ == "__main__":
    pDL = PicDownloader()
    url = "http://jamesostafford.files.wordpress.com/2012/03/41-edgar-broughton-band-inside-out.jpg"

    pDL.get_pic(url)
