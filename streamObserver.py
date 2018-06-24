import sys
import time
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread

from historyManager import *




class streamObserver(QThread):


    """Watch what's playing and send title"""

    titleChanged = pyqtSignal(str, name='titleChanged')

    #self.window = window
    
    doStop = False
    previousTitle = ""
    currentVolume = 0
    player = None
    history = historyManager()



    def run(self):


        msg = ""
        while True:

            if self.doStop: break

            if self.player.isPlaying() == True:
                if self.player.radioMode == True:
                    title = self.player.getNowPlaying()
                    #print("streamObserver="+title+" "+self.player.getTitle()+" "+self.player.getArtist())
                    if title != "NO_META":
                        self.player.mute(False)
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


                        if self.previousTitle == "Advert Killed!":
                            self.player.stop()
                            time.sleep(2)
                            self.player.play()
                            
                        #elif self.previousTitle != "":
                        else:
                            #It's an advert!
                            
                            self.player.mute(True)
                            self.player.stop()
                            msg = "Advert Killed!"
                            self.previousTitle = msg
                            print(msg)
                            self.titleChanged.emit(msg)
                            time.sleep(2)
                            self.player.play()



            time.sleep(1)


    def stop(self):
        self.doStop = True

    def resetPreviousTitle(self,event):
        if self.previousTitle != "Advert Killed!":
            self.previousTitle = ""

