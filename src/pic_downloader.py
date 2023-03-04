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
            # self.clean_last_temp_file()
            self.last_url = pic_url
            try:
                headers = {
                    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}
                response = requests.get(pic_url, headers=headers)
                if response.status_code != 200:
                    logger.error(response.content)
                    self.last_temp_file = ""
                    return ""
            except Exception as err:
                logger.error(err)
                return
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
                logger.error(err)
                pass
            self.last_temp_file = ""


if __name__ == "__main__":
    downloader = PicDownloader()
    # url = "https://jamesostafford.files.wordpress.com/2012/03/41-edgar-broughton-band-inside-out.jpg"
    url = "https://i.discogs.com/HiAz203qbRHstUt2itZvExE0" \
          "7nabIlYYsHgfdykAcKY/rs:fit/g:sm/q:90/h:600/w:600/czM6" \
          "Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTIxODQz/MjItMT" \
          "Q4Nzc4NTg1/Ni02NzM4LmpwZWc.jpeg"
    downloader.get_pic(url)
