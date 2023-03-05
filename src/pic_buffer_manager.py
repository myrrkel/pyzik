#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pic_downloader import PicDownloader
from PyQt5.QtGui import QPixmap


class PicBufferItem:
    users = []

    def __init__(self, path):
        self.path = path
        self.pix = QPixmap(path)


class PicBufferManager:
    """
    This pic buffer avoid to load several time a same pic file from hard disc,
    keep it in memory as long needed, remove it when the pic is not used anymore or
    to many others pics are loaded.

    """

    items = []

    def get_pic(self, path):
        item = self.find_item(path)
        if not item:
            item = PicBufferItem(path)
            self.items.append(item)
            self.check_buffer_size()
        pix = item.pix
        return pix

    def find_item(self, path):
        items = []
        items += [el for el in self.items if el.path == path]
        if len(items) > 0:
            return items[0]

    def check_buffer_size(self):
        """Remove oldest pixmap from the buffer if 5 are in ram"""
        if len(self.items) >= 5:
            self.items.remove(self.items[0])


if __name__ == "__main__":
    pDL = PicDownloader()
    url = "https://jamesostafford.files.wordpress.com/2012/03/41-edgar-broughton-band-inside-out.jpg"

    pDL.get_pic(url)
