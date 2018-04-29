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
    currentVolume = 0
    player = None   


    def run(self):

        msg = ""
        while True:

            if self.doStop: break

            if self.player.isPlaying() == True:
                if self.player.radioMode == True:
                    title = self.player.getNowPlaying()

                    if title != "NO_META":
                        if (self.previousTitle != title):
                            #if self.previousTitle == "Advert Killed!":
                            #    self.player.setVolume(self.currentVolume)
                            print(title)
                            msg = title
                            self.previousTitle = title
                            self.titleChanged.emit(msg)
                    else:
                        #if self.previousTitle == "Advert Killed!":
                        #    self.currentVolume = self.player.getVolume()
                        #    self.player.setVolume(0)


                        if self.previousTitle != "":
                            
                            self.previousTitle = ""
                            self.player.stop()
                            msg = "Advert Killed!"
                            self.titleChanged.emit(msg)
                            time.sleep(2)
                            self.player.playMediaList()
                else:

                    title = self.player.getTitle()
                    if title != "NO_TITLE":
                        msg = title + " - " + self.player.getArtist()
                        self.previousTitle = title
                        self.titleChanged.emit(msg)

            time.sleep(1)


    def stop(self):
        self.doStop = True
