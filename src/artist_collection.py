#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Iterable
from artist import Artist
import format_string
from operator import itemgetter, attrgetter
from sortedcontainers import SortedKeyList


def filter_by_name(seq, value):
    value = format_string.get_search_key(value)
    return list(el for el in seq if el.get_search_key() == value)


def find_by_id(seq, value):
    return next(el for el in seq if el.artist_id == value)


class ArtistCollection:
    """
    Artist's class, each album is in a directory.
    """

    def __init__(self, main_music_base):
        self.artists: Iterable[Artist] = SortedKeyList(key=attrgetter("name"))  # [] #Artist Collection
        self.music_base = main_music_base

    def add_artist(self, artist):
        # Add an artist in artists list,
        if artist.artist_id == 0:
            artist.artist_id = self.music_base.db.insert_artist(artist)

        self.artists.add(artist)

        return artist

    def get_artist(self, artist_name):
        artist = Artist(artist_name, 0)
        artist_list = self.find_artists(artist.name)

        if len(artist_list) == 0:
            # If the artist is not found in artistCol, we add it and return the
            return self.add_artist(artist)
        elif len(artist_list) == 1:
            # If artists is found
            return artist_list[0]
        else:
            # If there is more than 1 artist, ask for the good one to user
            # For the moment, just return the first one
            return artist_list[0]

    def find_artists(self, name):
        return filter_by_name(self.artists, name)

    def get_artist_by_id(self, artist_id):
        return find_by_id(self.artists, artist_id)

    def print_artists(self):
        for art in self.artists:
            art.print_infos()

    def load_artists(self):
        for rowArt in self.music_base.db.get_select(
            "SELECT artistID, name FROM artists ORDER BY name"
        ):
            art = Artist(rowArt[1], rowArt[0])
            self.add_artist(art)

    def sort_artists(self):
        self.artists = sorted(self.artists, key=attrgetter("name"))
