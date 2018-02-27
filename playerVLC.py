#!/usr/bin/env python3
# -*- coding: utf-8 -*-



##############################################
#           Play mp3 with VLC                #
##############################################

import sys
import time
import vlc

class playerVLC:

    def __init__(self):

        # creating a basic vlc instance
        self.instance = vlc.Instance()
        # creating an empty vlc media player
        self.mediaPlayer = self.instance.media_player_new()
        self.mediaListPlayer = self.instance.media_list_player_new()
        self.mediaList = self.instance.media_list_new()
        self.mpEnventManager = self.mediaPlayer.event_manager()
        self.mediaPlayer.audio_set_volume(100)

        self.initMediaList()
           
    def release(self):
        self.mediaPlayer.release()
        self.mediaListPlayer.release()
        self.instance.release()


    def playFile(self,sfile):
        #create the media
        print(sys.version)
        if(sys.version < '3'):
            sfile = unicode(sfile)

        media = self.instance.media_new(sfile)
        # put the media in the media player
        self.mediaPlayer.set_media(media)

        # parse the metadata of the file
        media.parse()
        self.mediaPlayer.play() 

    def addFile(self,sfile):
        media = self.instance.media_new(sfile)
        media.parse()
        self.mediaList.add_media(media)

    def addFileList(self,fileList):
        for sfile in fileList:
            self.mediaList.add_media(self.instance.media_new(sfile))


    def playMediaList(self):
        self.mediaListPlayer.play()


    def pauseMediaList(self):
        self.mediaListPlayer.pause()


    def initMediaList(self):
        #self.mediaList.release()
        #self.mediaListPlayer.release()
        if(self.mediaList != None):
            self.mediaList.release()
        self.mediaList = self.instance.media_list_new()
        self.mediaListPlayer.set_media_player(self.mediaPlayer)
        self.mediaListPlayer.set_media_list(self.mediaList) 

    def dropMediaList(self):
        self.mediaListPlayer.stop()
        self.mediaList.unlock()
        print("nb track="+str(self.mediaList.count()))
        for i in reversed(range(0,self.mediaList.count())):
            print("remove="+str(i))
            self.mediaList.remove_index(i)


    def setVolume(self, Volume):
        """Set the volume
        """
        print("Volume:"+str(Volume))
        self.mediaPlayer.audio_set_volume(Volume)

    def getParsedMedia(self,sfile):
        media = self.instance.media_new(sfile)
        media.parse()
        return media

    def playFuzzyGroovy(self):

        m = self.instance.media_new("http://listen.radionomy.com/fuzzy-and-groovy.m3u")

        self.mediaList.add_media(m)
        self.playMediaList()
        

    def getNowPlaying(self):
        m = self.mediaPlayer.get_media()
        now_playing = m.get_meta(12)
        if now_playing is not None:
            print(now_playing)
            return now_playing
        else:
            return ""



if __name__ == '__main__':
    player = playerVLC()
    player.initMediaList()
    player.playFuzzyGroovy()




