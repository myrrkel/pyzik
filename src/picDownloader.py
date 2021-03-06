#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

import requests
import tempfile

import time


class picDownloader:
    """Get a pic from an url"""

    lastTempFile = ""
    lastUrl = ""

    def getPic(self, url):

        if url == "":
            self.lastUrl = url
            return

        if self.lastUrl != url:

            self.cleanLastTempFile()
            self.lastUrl = url
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201'})
            print("GET Status=" + str(response.status_code))
            if response.status_code == 404:
                self.lastTempFile = ""
                return ""
            # response.raw.decode_content = True
            # data = response.raw
            data = response.content
            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(data)
            print("TempPic=" + str(temp.name))
            self.lastTempFile = temp.name
            temp.close()

        return self.lastTempFile

    def cleanLastTempFile(self):
        if self.lastTempFile != "":
            print("CleanTempFile:" + self.lastTempFile)
            os.remove(self.lastTempFile)
            self.lastTempFile = ""


if __name__ == "__main__":
    pDL = picDownloader()
    url = "http://jamesostafford.files.wordpress.com/2012/03/41-edgar-broughton-band-inside-out.jpg"

    pDL.getPic(url)
