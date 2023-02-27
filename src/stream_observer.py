import time
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread

from history_manager import HistoryManager


class StreamObserver(QThread):
    """Watch what's playing and send title"""

    titleChanged = pyqtSignal(str, name="titleChanged")
    do_stop = False
    previous_title = ""
    current_volume = 0
    player = None
    history = HistoryManager()
    music_base = None

    def run(self):
        msg = ""
        while True:
            if self.do_stop:
                break

            if not self.player.is_playing():
                self.previous_title = ""
                time.sleep(1)
                continue

            if not self.player.radio_mode:
                self.previous_title = ""
                time.sleep(1)
                continue

            if self.player.radio_mode:
                if self.player.adblock:
                    title = self.player.get_now_playing()
                    # print("streamObserver="+title+" "+self.player.getTitle()+" "+self.player.getArtist())
                    if title != "NO_META":
                        self.player.mute(False)
                        self.player.ad_killed = False
                        if self.previous_title != title:
                            self.previous_title = title
                            self.player.current_radio_title = self.clean_title(title)
                            self.titleChanged.emit(self.clean_title(title))
                    else:
                        if self.previous_title == "Advert Killed!":
                            self.player.stop()
                            time.sleep(2)
                            self.player.play()

                        else:
                            # It's an advert!
                            self.player.ad_killed = True
                            self.player.mute(True)
                            self.player.stop()
                            msg = "Advert Killed!"
                            self.previous_title = msg
                            self.titleChanged.emit(msg)
                            time.sleep(2)
                            self.player.play()

                else:
                    """No meta, no adblock"""
                    self.player.ad_killed = False
                    trk = self.player.get_current_track_playlist()
                    if trk is not None:
                        if trk.radio is not None:
                            rad = trk.radio
                            title = rad.get_current_track()
                            if title == "":
                                title = self.now_playing()

                        else:
                            title = self.now_playing()

                        if self.previous_title != title:
                            self.previous_title = title
                            self.player.current_radio_title = title
                            print("EMIT= " + title)
                            self.titleChanged.emit(title)

            time.sleep(1)

    def stop(self):
        self.do_stop = True

    def reset_previous_title(self, event):
        if self.previous_title != "Advert Killed!":
            self.previous_title = ""

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
        return self.clean_title(self.player.get_now_playing())
