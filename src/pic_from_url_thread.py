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
    last_temp_file = ""
    last_url = ""
    url = ""

    def run(self):
        if self.url == "":
            self.last_url = self.url
            self.download_completed.emit("")
            return

        if self.last_url != self.url:
            self.last_url = self.url
            self.last_temp_file = ""
            self.remove_last_temp_file()

            self.last_temp_file = self.downloader.get_pic(self.url)
            if self.last_temp_file:
                self.download_completed.emit(str(self.last_temp_file))
            else:
                logger.error("ERROR NO FILE")
        else:
            if self.last_temp_file != "":
                self.download_completed.emit(self.last_temp_file)

    def reset_last_url(self):
        self.last_url = ""

    def set_url(self, url):

        self.url = url

    def remove_last_temp_file(self):
        if self.last_temp_file != "":
            os.remove(self.last_temp_file)
            self.last_temp_file = ""
