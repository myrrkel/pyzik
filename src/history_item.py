#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class HistoryItem:
    """
    Defines different types of history items
    """

    def __init__(self, play_date):
        self.play_date = play_date
        self.history_type = 0  # 2=Album, 1=Track, 3=Radio
        self.data = None

    def init_histo_album(self, album_id):
        self.history_type = 1
        self.data = DataHistoryAlbum(album_id)

    def init_histo_track(self, album_id, file_name):
        self.history_type = 2
        self.data = DataHistoryTrack(album_id, file_name)

    def init_histo_radio(self, radio_name, title):
        self.history_type = 3
        self.data = DataHistoryRadio(radio_name, title)

    def print_data(self):
        print(str(self.play_date) + " " + self.data.get_info())

    def get_column_text(self, col_id):
        if col_id == 0:
            return str(self.play_date)
        else:
            return self.data.get_column_text(col_id)


class DataHistoryAlbum:
    def __init__(self, album_id):
        self.album_id = album_id
        self.album = None

    def get_album(self, music_base):
        self.album = music_base.albumCol.get_album(self.album_id)

    def get_info(self):
        return "Artist: " + self.album.artist_name + " Album: " + self.album.title

    def get_column_text(self, col_id):
        if col_id == 1:
            return ""
        if col_id == 2:
            return self.album.artist_name
        elif col_id == 3:
            return self.album.title
        else:
            return ""


class DataHistoryTrack(DataHistoryAlbum):
    def __init__(self, album_id, file_name):
        self.album_id = album_id
        self.fileName = file_name

    def get_info(self):
        return (
            "Artist: "
            + self.album.artist_name
            + " Album: "
            + self.album.title
            + " File: "
            + self.fileName
        )

    def get_column_text(self, col_id):
        if col_id == 1:
            return self.fileName
        elif col_id == 2:
            return self.album.artist_name
        elif col_id == 3:
            return self.album.title
        else:
            return ""


class DataHistoryRadio:
    def __init__(self, radio_name, title):
        self.radioName = radio_name
        self.title = title

    def get_info(self):
        return "Radio: " + self.radioName + " Title: " + self.title

    def get_column_text(self, col_id):
        if col_id == 1:
            return self.title
        elif col_id == 2:
            return self.radioName
        elif col_id == 3:
            return self.radioName
        else:
            return ""
