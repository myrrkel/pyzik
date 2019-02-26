#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

from PyQt5.QtCore import pyqtSignal, QThread
import requests
import tempfile

import time


class picFromUrlThread(QThread):


    """Get a pic from an url"""

    downloadCompleted = pyqtSignal(str, name='downloadCompleted')
    lastTempFile = ""
    lastUrl = ""



    def run(self,url):
        #url = "https://cdn.radiofrance.fr/s3/cruiser-production/2016/11/d68ecd67-6435-457e-af3c-d514864ae5f5/400x400_rf_omm_0000360132_dnc.0055215305.jpg"
        
        if url == "":
            self.lastUrl = url
            self.downloadCompleted.emit("")
            return


        if self.lastUrl != url:
            self.lastUrl = url
            self.removeLastTempFile()
            response = requests.get(url)
            print("GET Status="+str(response.status_code))
            #response.raw.decode_content = True
            #data = response.raw
            data = response.content
            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(data)
            print("TempPic="+str(temp.name))
            temp.close()
            if  os.path.isfile(temp.name):
                self.lastTempFile = str(temp.name)
                self.downloadCompleted.emit(str(temp.name))
            else:
                print(print("ERROR NO FILE TempPic="+str(temp.name)))
        else:
            self.downloadCompleted.emit(str(self.lastTempFile))
  
    def resetLastURL(self):
        self.lastUrl = ""

    def removeLastTempFile(self):
        if self.lastTempFile != "":
            print("removeLastTempFile:"+self.lastTempFile)
            os.remove(self.lastTempFile)
            self.lastTempFile = ""



