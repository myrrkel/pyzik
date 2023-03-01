#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import urllib3
from PyQt5.QtCore import pyqtSignal, QThread
from pic_downloader import PicDownloader
import logging

logger = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PicFromUrlThread(QThread):
    """Get a pic from url"""
    downloader = PicDownloader()
    download_completed = pyqtSignal(str, name="downloadCompleted")
    lastTempFile = ""
    lastUrl = ""
    url = ""

    def run(self):
        if self.url == "":
            self.lastUrl = self.url
            self.download_completed.emit("")
            return

        if self.lastUrl != self.url:
            self.lastUrl = self.url
            self.lastTempFile = ""
            self.remove_last_temp_file()

            self.lastTempFile = self.downloader.get_pic(self.url)
            if self.lastTempFile:
                self.download_completed.emit(str(self.lastTempFile))
            else:
                logger.error("ERROR NO FILE")
        else:
            if self.lastTempFile != "":
                self.download_completed.emit(self.lastTempFile)

    def reset_last_url(self):
        self.lastUrl = ""

    def set_url(self, url):

        self.url = url

    def remove_last_temp_file(self):
        if self.lastTempFile != "":
            os.remove(self.lastTempFile)
            self.lastTempFile = ""
