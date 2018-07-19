import sys
import os

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
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
        if self.lastUrl != url:
            self.lastUrl = url
            self.cleanLastTempFile()
            response = requests.get(url)
            print("GET Status="+str(response.status_code))
            #response.raw.decode_content = True
            #data = response.raw
            data = response.content
            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(data)
            print("TempPic="+str(temp.name))
            temp.close()
            self.lastTempFile = temp.name
            self.downloadCompleted.emit(str(temp.name))
        #else:
        #    self.downloadCompleted.emit(str(self.lastTempFile))
  

    def cleanLastTempFile(self):
        if self.lastTempFile != "":
            print("CleanTempFile:"+self.lastTempFile)
            os.remove(self.lastTempFile)
            self.lastTempFile = ""



