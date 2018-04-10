import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread

import time


class streamObserver(QThread):


    """Watch what's playing and send title"""

    titleChanged = pyqtSignal(str, name='titleChanged')

    #self.window = window
    
    doStop = False
    previousTitle = ""
    player = None   


    def run(self):

        msg = ""
        while True:

            if self.doStop: break

            if self.player.isPlaying() == True:
                title = self.player.getNowPlaying()

                if title != "NO_META":
                    if (self.previousTitle != title):
                        print(title)
                        msg = title
                        self.previousTitle = title
                else:
                    
                    title = self.player.getTitle()
                    if title != "NO_TITLE":
                        msg = title + " - " + self.player.getArtist()

                    else:
                        if self.previousTitle != "":
                            self.previousTitle = ""
                            self.player.stop()
                            msg = "Advert Killed!"

                            time.sleep(2)
                            self.player.playMediaList()

                self.titleChanged.emit(msg)

            time.sleep(1)


    def stop(self):
        self.doStop = True
