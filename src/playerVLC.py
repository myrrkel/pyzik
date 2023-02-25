#!/usr/bin/env python3
# -*- coding: utf-8 -*-


##############################################
#           Play mp3 with VLC                #
##############################################
import sys
import time
import vlc
import os
import threading
from track import Track
from PyQt5.QtCore import pyqtSignal
import ctypes as c
import logging

logger = logging.getLogger(__name__)

c_int_p = c.POINTER(c.c_int)
c_uint8_p = c.POINTER(c.c_uint8)
c_int_pp = c.POINTER(c_int_p)
c_int8_p = c.POINTER(c.c_int8)
c_int8_pp = c.POINTER(c_int8_p)
c_uint8_pp = c.POINTER(c_uint8_p)
c_ubyte_p = c.POINTER(c.c_ubyte)
c_float_p = c.POINTER(c.c_float)
c_double_p = c.POINTER(c.c_double)
c_void_p_p = c.POINTER(c.c_void_p)
c_short_p = c.POINTER(c.c_short)

dirtySymbols = ["@", "+", "*", "#"]


def cleanTitle(title):
    s = title
    if s[0] in dirtySymbols:
        s = s[1:]
    if s[-1] in dirtySymbols:
        s = s[:-2]
    return s.strip()


def print(txt):
    logger.info(txt)


class PlayerVLC:
    tracksDatas = []

    def __init__(self):
        # creating a basic vlc instance
        self.instance = vlc.Instance("--quiet")

        cmp_audioPostrender = c.addressof(self.audioPostrender)
        cmp_audioPrerender = c.addressof(self.audioPrerender)
        # print("cmp_audioPrerender="+str(cmp_audioPrerender)+" cmp_audioPostrender="+str(cmp_audioPostrender))

        # self.instance = vlc.Instance("--sout=#transcode{acodec=s16l}:smem{audio-postrender-callback="+str(cmp_audioPostrender)+",audio-prerender-callback="+str(cmp_audioPrerender)+"}")

        # creating an empty vlc media player
        self.mediaPlayer = self.instance.media_player_new()
        self.mediaListPlayer = self.instance.media_list_player_new()
        self.mediaList = self.instance.media_list_new()
        self.mpEnventManager = self.mediaPlayer.event_manager()

        self.radioMode = False
        self.currentRadioTitle = ""
        self.currentRadioName = ""
        self.currentRadio = False
        self.adblock = False
        self.adKilled = False
        self.loadingRadio = False
        self.playlistChangedEvent = pyqtSignal(int, name="playlistChanged")
        self.currentRadioChangedEvent = pyqtSignal(int, name="currentRadioChanged")
        self.titleChangedEvent = pyqtSignal(str, name="titleChanged")

        self.nowPlaying = ""

        self.initMediaList()

        print("VLC version = " + str(vlc.libvlc_get_version()))

        # void prepareRender(void* p_audio_data, uint8_t** pp_pcm_buffer , size_t size); // Audio prerender callback
        # void handleStream(void* p_audio_data, uint8_t* p_pcm_buffer, unsigned int channels, unsigned int rate, unsigned int nb_samples, unsigned int bits_per_sample, size_t size, int64_t pts); // Audio postrender callback

    @c.CFUNCTYPE(
        c.c_void_p,
        c_uint8_p,
        c.c_uint,
        c.c_uint,
        c.c_uint,
        c.c_uint,
        c.c_size_t,
        c.c_int64,
    )
    def audioPostrender(
        self,
        p_audio_data,
        p_pcm_buffer,
        channels,
        rate,
        nb_samples,
        bits_per_sample,
        size,
        pts,
    ):  # Audio postrender callback
        print("HandleStream")

    @c.CFUNCTYPE(c.c_void_p, c_uint8_pp, c.c_size_t)
    def audioPrerender(
        self, p_audio_data, pp_pcm_buffer, size
    ):  # Audio prerender callback
        print("prepareRender")

    def release(self):
        self.mediaPlayer.release()
        self.mediaListPlayer.release()
        self.instance.release()

    def getAlbumFromMrl(self, mrl):
        trackData = [item for item in self.tracksDatas if item[0] == mrl]

        if trackData is not None:
            if len(trackData) > 0:
                return trackData[0][1]
            else:
                return None
        else:
            return None

    def getTrackFromMrl(self, mrl):
        trackData = [item for item in self.tracksDatas if item[0] == mrl]

        if trackData is not None:
            if len(trackData) > 0:
                return trackData[0][2]
            else:
                trackData = [item for item in self.tracksDatas if item[1] == mrl]
                if len(trackData) > 0:
                    return trackData[0][2]
                else:
                    return None
        else:
            return None

    def isPlaying(self):
        return self.mediaPlayer.is_playing()

    def isPlayingRadio(self):
        return (
            self.adKilled == False and self.isPlaying() and self.loadingRadio == False
        )

    def get_current_index_playlist(self):
        m = self.mediaPlayer.get_media()
        index = self.mediaList.index_of_item(m)
        if index == -1:
            if self.mediaList.count() > 0:
                index = self.findItemIndexInPlaylist(m.get_mrl())

        return index

    def getCurrentMrlPlaylist(self):
        m = self.mediaPlayer.get_media()
        if m is not None:
            return m.get_mrl()
        else:
            return None

    def getItemAtIndex(self, index):
        return self.mediaList.item_at_index(index)

    def getTrackAtIndex(self, index):
        item = self.getItemAtIndex(index)
        print(str("getTrackAtIndex " + str(item)))
        return self.getTrackFromMrl(item.get_mrl())

    def findItemIndexInPlaylist(self, mrl):
        res = 0
        for i in range(self.mediaList.count()):
            item = self.getItemAtIndex(i)
            if item.get_mrl() == mrl:
                return i

        return res

    def getCurrentTrackPlaylist(self):
        mrl = self.getCurrentMrlPlaylist()
        if mrl is not None:
            return self.getTrackFromMrl(mrl)
        else:
            return None

    def playAlbum(self, album, autoplay=True):
        self.radioMode = False
        i = 0
        for trk in album.tracks:
            path = trk.getFullFilePath()
            media = self.instance.media_new(path)

            self.mediaList.add_media(media)
            self.tracksDatas.append((media.get_mrl(), "", trk))

            if i == 0 and autoplay:
                index = self.mediaList.count() - 1
                self.mediaListPlayer.play_item_at_index(index)
            i += 1
        self.playlistChangedEvent.emit(1)

    def addAlbum(self, album):
        for trk in album.tracks:
            path = trk.getFullFilePath()
            media = self.instance.media_new(path)
            trk.radioName = ""

            self.mediaList.add_media(media)
            self.tracksDatas.append((media.get_mrl(), "", trk))
        self.playlistChangedEvent.emit(1)

    def playFile(self, sfile):
        # create the media
        print(sys.version)
        if sys.version < "3":
            sfile = unicode(sfile)

        media = self.instance.media_new(sfile)
        # put the media in the media player
        self.mediaPlayer.set_media(media)

        # parse the metadata of the file
        media.parse()
        self.mediaPlayer.play()

    def addFile(self, sfile):
        media = self.instance.media_new(sfile)
        media.parse()
        self.mediaList.add_media(media)
        self.playlistChangedEvent.emit(1)

    def addFileList(self, fileList):
        for sfile in fileList:
            self.mediaList.add_media(self.instance.media_new(sfile))

    def playMediaList(self):
        self.mediaListPlayer.play()

    def stop(self):
        self.mediaPlayer.stop()

    def play(self):
        self.mediaPlayer.play()

    def pause(self):
        self.mediaPlayer.pause()

    def next(self):
        self.mediaListPlayer.next()

    def previous(self):
        self.mediaListPlayer.previous()

    def resetCurrentItemIndex(self, index):
        self.mediaListPlayer.reset_current_item_index(index)

    def mute(self, value):
        self.mediaPlayer.audio_set_mute(value)

    def pauseMediaList(self):
        self.mediaListPlayer.pause()

    def initMediaList(self):
        # self.mediaList.release()
        # self.mediaListPlayer.release()
        if self.mediaList is not None:
            self.mediaList.release()

        self.mediaList = self.instance.media_list_new()
        self.mediaListPlayer.set_media_player(self.mediaPlayer)
        self.mediaListPlayer.set_media_list(self.mediaList)

    def refreshMediaListPlayer(self):
        self.mediaListPlayer.set_media_list(self.mediaList)

    def dropMediaList(self):
        self.mediaListPlayer.stop()
        self.mediaList.unlock()
        for i in reversed(range(0, self.mediaList.count())):
            self.mediaList.remove_index(i)
        self.playlistChangedEvent.emit(1)

    def removeAllTracks(self):
        # Remove all medias from the playlist except the current track
        currentIndex = self.get_current_index_playlist()
        for i in reversed(range(0, self.mediaList.count())):
            if i != currentIndex:
                self.mediaList.remove_index(i)
        self.playlistChangedEvent.emit(1)

    def getVolume(self):
        """Get the volume from the player"""
        volume = int(self.mediaPlayer.audio_get_volume())
        return volume

    def setVolume(self, Volume):
        """Set the volume"""
        self.mediaPlayer.audio_set_volume(Volume)

    def getPosition(self):
        """Get the position in media"""
        return self.mediaPlayer.get_position()

    def setPosition(self, pos):
        """Set the position in media"""
        return self.mediaPlayer.set_position(pos)

    def getParsedMedia(self, sfile):
        media = self.getMedia(sfile)
        media.parse()
        return media

    def getMedia(self, sfile):
        media = self.instance.media_new(sfile)
        return media

    def playRadioInThread(self, radio):
        processThread = threading.Thread(target=self.playRadio, args=[radio])
        processThread.start()

    def playRadio(self, radio):
        self.radioMode = True
        self.currentRadio = radio
        self.loadingRadio = True
        self.adblock = radio.adblock
        self.dropMediaList()
        media = self.instance.media_new(radio.stream)

        self.mediaList.add_media(media)
        self.playlistChangedEvent.emit(1)
        self.currentRadioName = radio.name
        self.currentRadioTitle = "..."
        logger.info("playRadio %s", radio.name)
        self.titleChangedEvent.emit(radio.name)
        self.playMediaList()
        trk = Track()
        trk.radioID = radio.radioID
        trk.radioName = radio.name
        trk.radioStream = radio.stream
        trk.radio = radio

        # Wait until playing start.
        startSince = 0
        while self.isPlaying() == 0:
            time.sleep(0.05)
            startSince = startSince + 0.05
            # Get current state.
            state = self.getState()
            if state == "State.Ended":
                self.stop()
                self.radioMode = False
                return

            if state != "State.Opening":
                logger.debug("VLC state=" + state)

            if startSince > 5:
                # Find out if stream is working.
                if state == "vlc.State.Error" or state == "State.Error":
                    print("Stream is dead. Current state = {}".format(state))
                    self.stop()
                    self.radioMode = False
                    return
                elif state == "State.Ended":
                    self.stop()
                    self.radioMode = False
                    return
                else:
                    print("VLC state=" + state)

        self.loadingRadio = False
        mrl = self.getCurrentMrlPlaylist()
        print(radio.name + " mrl=" + mrl)
        self.tracksDatas.append((mrl, radio.stream, trk))
        self.currentRadioChangedEvent.emit(1)

    def getState(self):
        return str(self.mediaPlayer.get_state())

    def getNowPlaying(self):
        if not self.radioMode:
            return self.currentRadioTitle
        m = self.mediaPlayer.get_media()
        if m is not None:
            nowPlaying = m.get_meta(12)
            if nowPlaying is not None:
                if self.nowPlaying != nowPlaying:
                    self.nowPlaying = nowPlaying
                    print("PlayerVLC NowPlaying = " + nowPlaying)
                return cleanTitle(nowPlaying)
            else:
                if self.adblock:
                    print("PlayerVLC NowPlaying = NO_META")
                    return "NO_META"
                else:
                    print("PlayerVLC NowPlaying = " + self.currentRadioTitle)
                    return self.currentRadioTitle
        else:
            print("PlayerVLC NowPlaying = NO_STREAM_MEDIA")
            return "NO_STREAM_MEDIA"

    def getLiveCoverUrl(self):
        url = ""
        rad = self.getCurrentRadio()
        if rad is not None:
            url = rad.liveCoverUrl
        return url

    def getCurrentRadio(self):
        rad = None
        trk = self.getCurrentTrackPlaylist()
        if trk is not None and trk.radio is not None:
            rad = trk.radio
        return rad

    def getCurrentTitle(self):
        title = ""
        trk = self.getCurrentTrackPlaylist()
        if trk is not None:
            if trk.radioName == "":
                title = trk.getFullTitle()
            else:
                title = self.getNowPlaying()
                if title == "NO_META":
                    title = trk.radioName
        return title

    def getTitle(self):
        title = ""
        m = self.mediaPlayer.get_media()
        if m is not None:
            title = m.get_meta(0)
        else:
            title = "NO_TITLE"
        return title

    def getArtist(self):
        artist = ""
        m = self.mediaPlayer.get_media()
        if m is not None:
            artist = m.get_meta(1)
            if artist == None:
                artist = "NO_ARTIST"
        else:
            artist = "NO_ARTIST"
        return artist

    def getAlbum(self):
        album = ""
        m = self.mediaPlayer.get_media()
        if m is not None:
            album = m.get_meta(4)
        else:
            album = "NO_ALBUM"
        return album

    def getTrackNumber(self):
        number = 0
        m = self.mediaPlayer.get_media()
        if m is not None:
            number = int(m.get_meta(5))
        else:
            number = 0
        return number

    def getDate(self):
        year = ""
        m = self.mediaPlayer.get_media()
        if m is not None:
            year = m.get_meta(8)
        return year

    def setPlaylistTrack(self, index):
        print("setPlaylistTrack=" + str(index))
        trk = self.getTrackAtIndex(index)
        self.radioMode = trk.radioName != ""
        print("radioMode=" + str(self.radioMode))

        self.mediaListPlayer.play_item_at_index(index)


if __name__ == "__main__":
    player = PlayerVLC()
    # player.initMediaList()
    player.playFile(
        "C://Users//mp05.octave//Music//FREEDOM//FREEDOM - [1970] - Freedom At Last//Freedom - 01 - Enchanted Wood - 3.03.mp3"
    )
