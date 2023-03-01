#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import tempfile
import logging

logger = logging.getLogger(__name__)


class PicDownloader:
    """Get a pic from an url"""

    lastTempFile = ""
    lastUrl = ""

    def get_pic(self, pic_url):
        if pic_url == "":
            self.lastUrl = pic_url
            return

        if self.lastUrl != pic_url:
            self.clean_last_temp_file()
            self.lastUrl = pic_url
            response = requests.get(pic_url)
            if response.status_code == 404:
                self.lastTempFile = ""
                return ""

            data = response.content
            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(data)
            self.lastTempFile = temp.name
            temp.close()

        return self.lastTempFile

    def clean_last_temp_file(self):
        if self.lastTempFile != "":
            try:
                os.remove(self.lastTempFile)
            except Exception as err:
                logger.info(err)
            self.lastTempFile = ""


if __name__ == "__main__":
    downloader = PicDownloader()
    url = "https://jamesostafford.files.wordpress.com/2012/03/41-edgar-broughton-band-inside-out.jpg"
    downloader.get_pic(url)
