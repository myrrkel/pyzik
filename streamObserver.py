import sys

from threading import Thread

import time


class streamObserver(Thread):


    """Thread chargé simplement d'afficher une lettre dans la console."""


    def __init__(self,window,player):

        Thread.__init__(self)

        self.window = window
        self.player = player
        self.doStop = False
        self.previousTitle = ""


    def run(self):

        """Code à exécuter pendant l'exécution du thread."""

        while True:

            if self.doStop: break

            title = self.player.getNowPlaying()

            if title != "NO_META":
                if (self.previousTitle != title):
                    print(title)
                    self.previousTitle = title
            else:
                if self.previousTitle != "":
                    self.previousTitle = ""
                    self.player.stop()
                    print("Advert Killed!")
                    time.sleep(2)
                    self.player.playMediaList()



            time.sleep(1)


    def stop(self):
        self.doStop = True
