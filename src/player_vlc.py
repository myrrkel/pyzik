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

        # creating an empty vlc media player
        self.media_player = self.instance.media_player_new()
        self.mediaListPlayer = self.instance.media_list_player_new()
        self.media_list = self.instance.media_list_new()
        self.player_event_manager = self.media_player.event_manager()

        self.radio_mode = False
        self.current_radio_title = ""
        self.current_radio_name = ""
        self.current_radio = False
        self.adblock = False
        self.ad_killed = False
        self.loading_radio = False
        self.playlist_changed_event = pyqtSignal(int, name="playlistChanged")
        self.current_radio_changed_event = pyqtSignal(int, name="currentRadioChanged")
        self.title_changed_event = pyqtSignal(str, name="titleChanged")

        self.now_playing = ""

        self.init_media_list()

        print("VLC version = " + str(vlc.libvlc_get_version()))

    def release(self):
        self.media_player.release()
        self.mediaListPlayer.release()
        self.instance.release()

    def get_album_from_mrl(self, mrl):
        track_data = [item for item in self.tracksDatas if item[0] == mrl]

        if track_data is not None:
            if len(track_data) > 0:
                return track_data[0][1]
            else:
                return None
        else:
            return None

    def get_track_from_mrl(self, mrl):
        track_data = [item for item in self.tracksDatas if item[0] == mrl]

        if track_data is not None:
            if len(track_data) > 0:
                return track_data[0][2]
            else:
                track_data = [item for item in self.tracksDatas if item[1] == mrl]
                if len(track_data) > 0:
                    return track_data[0][2]
                else:
                    return None
        else:
            return None

    def is_playing(self):
        return self.media_player.is_playing()

    def is_playing_radio(self):
        return not self.ad_killed and self.is_playing() and not self.loading_radio

    def get_current_index_playlist(self):
        m = self.media_player.get_media()
        index = self.media_list.index_of_item(m)
        if index == -1:
            if self.media_list.count() > 0:
                index = self.find_item_index_in_playlist(m.get_mrl())

        return index

    def get_current_mrl_playlist(self):
        m = self.media_player.get_media()
        if m is not None:
            return m.get_mrl()
        else:
            return None

    def get_item_at_index(self, index):
        return self.media_list.item_at_index(index)

    def get_track_at_index(self, index):
        item = self.get_item_at_index(index)
        print(str("getTrackAtIndex " + str(item)))
        return self.get_track_from_mrl(item.get_mrl())

    def find_item_index_in_playlist(self, mrl):
        res = 0
        for i in range(self.media_list.count()):
            item = self.get_item_at_index(i)
            if item.get_mrl() == mrl:
                return i

        return res

    def get_current_track_playlist(self):
        mrl = self.get_current_mrl_playlist()
        if mrl is not None:
            return self.get_track_from_mrl(mrl)
        else:
            return None

    def play_album(self, album, autoplay=True):
        self.radio_mode = False
        i = 0
        for trk in album.tracks:
            path = trk.get_full_file_path()
            media = self.instance.media_new(path)

            self.media_list.add_media(media)
            self.tracksDatas.append((media.get_mrl(), "", trk))

            if i == 0 and autoplay:
                index = self.media_list.count() - 1
                self.mediaListPlayer.play_item_at_index(index)
            i += 1
        self.playlist_changed_event.emit(1)

    def add_album(self, album):
        for trk in album.tracks:
            path = trk.get_full_file_path()
            media = self.instance.media_new(path)
            trk.radioName = ""

            self.media_list.add_media(media)
            self.tracksDatas.append((media.get_mrl(), "", trk))
        self.playlist_changed_event.emit(1)

    def play_file(self, file):
        # create the media
        media = self.instance.media_new(file)
        # put the media in the media player
        self.media_player.set_media(media)

        # parse the metadata of the file
        media.parse()
        self.media_player.play()

    def add_file(self, file):
        media = self.instance.media_new(file)
        media.parse()
        self.media_list.add_media(media)
        self.playlist_changed_event.emit(1)

    def add_file_list(self, file_list):
        for file in file_list:
            self.media_list.add_media(self.instance.media_new(file))

    def play_media_list(self):
        self.mediaListPlayer.play()

    def stop(self):
        self.media_player.stop()

    def play(self):
        self.media_player.play()

    def pause(self):
        self.media_player.pause()

    def next(self):
        self.mediaListPlayer.next()

    def previous(self):
        self.mediaListPlayer.previous()

    def reset_current_item_index(self, index):
        self.mediaListPlayer.reset_current_item_index(index)

    def mute(self, value):
        self.media_player.audio_set_mute(value)

    def pause_media_list(self):
        self.mediaListPlayer.pause()

    def init_media_list(self):
        # self.mediaList.release()
        # self.mediaListPlayer.release()
        if self.media_list is not None:
            self.media_list.release()

        self.media_list = self.instance.media_list_new()
        self.mediaListPlayer.set_media_player(self.media_player)
        self.mediaListPlayer.set_media_list(self.media_list)

    def refresh_media_list_player(self):
        self.mediaListPlayer.set_media_list(self.media_list)

    def drop_media_list(self):
        self.mediaListPlayer.stop()
        self.media_list.unlock()
        for i in reversed(range(0, self.media_list.count())):
            self.media_list.remove_index(i)
        self.playlist_changed_event.emit(1)

    def remove_all_tracks(self):
        # Remove all medias from the playlist except the current track
        current_index = self.get_current_index_playlist()
        for i in reversed(range(0, self.media_list.count())):
            if i != current_index:
                self.media_list.remove_index(i)
        self.playlist_changed_event.emit(1)

    def get_volume(self):
        """Get the volume from the player"""
        volume = int(self.media_player.audio_get_volume())
        return volume

    def set_volume(self, Volume):
        """Set the volume"""
        self.media_player.audio_set_volume(Volume)

    def get_position(self):
        """Get the position in media"""
        return self.media_player.get_position()

    def set_position(self, pos):
        """Set the position in media"""
        return self.media_player.set_position(pos)

    def get_parsed_media(self, file):
        media = self.get_media(file)
        media.parse()
        return media

    def get_media(self, file):
        media = self.instance.media_new(file)
        return media

    def play_radio_in_thread(self, radio):
        process_thread = threading.Thread(target=self.play_radio, args=[radio])
        process_thread.start()

    def play_radio(self, radio):
        self.radio_mode = True
        self.current_radio = radio
        self.loading_radio = True
        self.adblock = radio.adblock
        self.drop_media_list()
        media = self.instance.media_new(radio.stream)

        self.media_list.add_media(media)
        self.playlist_changed_event.emit(1)
        self.current_radio_name = radio.name
        self.current_radio_title = "..."
        logger.info("playRadio %s", radio.name)
        self.title_changed_event.emit(radio.name)
        self.play_media_list()
        trk = Track()
        trk.radioID = radio.radio_id
        trk.radioName = radio.name
        trk.radioStream = radio.stream
        trk.radio = radio

        # Wait until playing start.
        start_since = 0
        while self.is_playing() == 0:
            time.sleep(0.05)
            start_since = start_since + 0.05
            # Get current state.
            state = self.get_state()
            if state == "State.Ended":
                self.stop()
                self.radio_mode = False
                return

            if state != "State.Opening":
                logger.debug("VLC state=" + state)

            if start_since > 5:
                # Find out if stream is working.
                if state == "vlc.State.Error" or state == "State.Error":
                    print("Stream is dead. Current state = {}".format(state))
                    self.stop()
                    self.radio_mode = False
                    return
                elif state == "State.Ended":
                    self.stop()
                    self.radio_mode = False
                    return
                else:
                    print("VLC state=" + state)

        self.loading_radio = False
        mrl = self.get_current_mrl_playlist()
        print(radio.name + " mrl=" + mrl)
        self.tracksDatas.append((mrl, radio.stream, trk))
        self.current_radio_changed_event.emit(1)

    def get_state(self):
        return str(self.media_player.get_state())

    def get_now_playing(self):
        if not self.radio_mode:
            return self.current_radio_title
        m = self.media_player.get_media()
        if m is not None:
            now_playing = m.get_meta(12)
            if now_playing is not None:
                if self.now_playing != now_playing:
                    self.now_playing = now_playing
                    print("PlayerVLC NowPlaying = " + now_playing)
                return cleanTitle(now_playing)
            else:
                if self.adblock:
                    print("PlayerVLC NowPlaying = NO_META")
                    return "NO_META"
                else:
                    print("PlayerVLC NowPlaying = " + self.current_radio_title)
                    return self.current_radio_title
        else:
            print("PlayerVLC NowPlaying = NO_STREAM_MEDIA")
            return "NO_STREAM_MEDIA"

    def get_live_cover_url(self):
        url = ""
        rad = self.get_current_radio()
        if rad is not None:
            url = rad.live_cover_url
        return url

    def get_current_radio(self):
        rad = None
        trk = self.get_current_track_playlist()
        if trk is not None and trk.radio is not None:
            rad = trk.radio
        return rad

    def get_current_title(self):
        title = ""
        trk = self.get_current_track_playlist()
        if trk is not None:
            if trk.radioName == "":
                title = trk.getFullTitle()
            else:
                title = self.get_now_playing()
                if title == "NO_META":
                    title = trk.radioName
        return title

    def get_title(self):
        title = ""
        m = self.media_player.get_media()
        if m is not None:
            title = m.get_meta(0)
        else:
            title = "NO_TITLE"
        return title

    def get_artist(self):
        artist = ""
        m = self.media_player.get_media()
        if m:
            artist = m.get_meta(1)
        return artist or "NO_ARTIST"

    def get_album(self):
        album = ""
        m = self.media_player.get_media()
        if m:
            album = m.get_meta(4)
        return album or "NO_ALBUM"

    def get_track_number(self):
        number = 0
        m = self.media_player.get_media()
        if m:
            number = int(m.get_meta(5))
        return number or 0

    def get_date(self):
        year = ""
        m = self.media_player.get_media()
        if m:
            year = m.get_meta(8)
        return year

    def set_playlist_track(self, index):
        print("setPlaylistTrack=" + str(index))
        trk = self.get_track_at_index(index)
        self.radio_mode = trk.radio_name != ""
        print("radioMode=" + str(self.radio_mode))

        self.mediaListPlayer.play_item_at_index(index)


if __name__ == "__main__":
    player = PlayerVLC()
    # player.initMediaList()
    player.play_file(
        "C://Users//mp05.octave//Music//FREEDOM//FREEDOM - [1970] - Freedom At Last//Freedom - 01 - Enchanted Wood - 3.03.mp3"
    )
