#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import tempfile
import logging

logger = logging.getLogger(__name__)


class PicDownloader:
    """Get a pic from an url"""

    last_temp_file = ""
    last_url = ""

    def get_pic(self, pic_url):
        if pic_url == "":
            self.last_url = pic_url
            return

        if self.last_url != pic_url:
            self.clean_last_temp_file()
            self.last_url = pic_url
            response = requests.get(pic_url)
            if response.status_code == 404:
                self.last_temp_file = ""
                return ""

            data = response.content
            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(data)
            self.last_temp_file = temp.name
            temp.close()

        return self.last_temp_file

    def clean_last_temp_file(self):
        if self.last_temp_file != "":
            try:
                os.remove(self.last_temp_file)
            except Exception as err:
                logger.info(err)
            self.last_temp_file = ""


if __name__ == "__main__":
    downloader = PicDownloader()
    url = "https://jamesostafford.files.wordpress.com/2012/03/41-edgar-broughton-band-inside-out.jpg"
    downloader.get_pic(url)
