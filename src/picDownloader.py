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


    def getPic(self,url):
        #url = "https://cdn.radiofrance.fr/s3/cruiser-production/2016/11/d68ecd67-6435-457e-af3c-d514864ae5f5/400x400_rf_omm_0000360132_dnc.0055215305.jpg"
        
        if url == "":
            self.lastUrl = url
            return


        if self.lastUrl != url:
            
            self.cleanLastTempFile()
            self.lastUrl = url
            response = requests.get(url)
            print("GET Status="+str(response.status_code))
            #response.raw.decode_content = True
            #data = response.raw
            data = response.content
            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(data)
            print("TempPic="+str(temp.name))
            self.lastTempFile = temp.name
            temp.close()

        return self.lastTempFile

    def cleanLastTempFile(self):
        if self.lastTempFile != "":
            print("CleanTempFile:"+self.lastTempFile)
            os.remove(self.lastTempFile)
            self.lastTempFile = ""



