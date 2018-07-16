import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
import requests
import tempfile

import time


class picFromUrlThread(QThread):


    """Get a pic from an url"""

    downloadCompleted = pyqtSignal(str, name='downloadCompleted')


    def run(self,url):
 

        #url = 'https://cdn.radiofrance.fr/s3/cruiser-production/2017/02/a0baccc1-38c0-47c8-82e0-07b80968e592/400x400_rf_omm_0000378730_dnc.0038979639.jpg'
        #data = urllib.request.urlopen(url).read()
        response = requests.get(url)
        data = response.content
        temp = tempfile.NamedTemporaryFile()
        temp.write(data)
        print("TempPic="+str(temp.name))
        self.downloadCompleted.emit(str(temp.name))
  



