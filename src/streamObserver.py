import sys
import time
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread

from historyManager import HistoryManager
from radioManager import RadioManager


class StreamObserver(QThread):
    """Watch what's playing and send title"""

    titleChanged = pyqtSignal(str, name="titleChanged")

    # self.window = window

    doStop = False
    previousTitle = ""
    currentVolume = 0
    player = None
    history = HistoryManager()
    music_base = None

    def run(self):
        msg = ""
        while True:
            if self.doStop:
                break

            if self.player.isPlaying() == False:
                self.previousTitle = ""
                time.sleep(1)
                continue

            if self.player.radioMode == False:
                self.previousTitle = ""
                time.sleep(1)
                continue

            if self.player.radioMode == True:
                if self.player.adblock == True:
                    title = self.player.getNowPlaying()
                    # print("streamObserver="+title+" "+self.player.getTitle()+" "+self.player.getArtist())
                    if title != "NO_META":
                        self.player.mute(False)
                        self.player.adKilled = False
                        if self.previousTitle != title:
                            self.previousTitle = title
                            self.player.currentRadioTitle = self.clean_title(title)
                            self.titleChanged.emit(self.clean_title(title))
                    else:
                        if self.previousTitle == "Advert Killed!":
                            self.player.stop()
                            time.sleep(2)
                            self.player.play()

                        else:
                            # It's an advert!
                            self.player.adKilled = True
                            self.player.mute(True)
                            self.player.stop()
                            msg = "Advert Killed!"
                            self.previousTitle = msg
                            self.titleChanged.emit(msg)
                            time.sleep(2)
                            self.player.play()

                else:
                    """No meta, no adblock"""
                    # print("NOADBLOCK")
                    self.player.adKilled = False
                    trk = self.player.getCurrentTrackPlaylist()
                    if trk is not None:
                        # print("rad:"+trk.radioName+" id:"+str(trk.radioID))
                        if trk.radio is not None:
                            rad = trk.radio
                            title = rad.get_current_track()
                            if title == "":
                                title = self.now_playing()

                        else:
                            title = self.now_playing()

                        if self.previousTitle != title:
                            self.previousTitle = title
                            self.player.currentRadioTitle = title
                            print("EMIT= " + title)
                            self.titleChanged.emit(title)

            time.sleep(1)

    def stop(self):
        self.doStop = True

    def reset_previous_title(self, event):
        if self.previousTitle != "Advert Killed!":
            self.previousTitle = ""

    def clean_title(self, title):
        clean = title.strip()
        if clean == "|":
            clean = ""
        if clean == "-":
            clean = ""
        if "targetspot" in clean.lower():
            clean = ""
        return clean

    def now_playing(self):
        return self.clean_title(self.player.getNowPlaying())
