#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from artist import Artist
import formatString as FS
from operator import itemgetter, attrgetter
from sortedcontainers import SortedKeyList


def filterByName(seq, value):
    value = FS.getSearchKey(value)
    return list(el for el in seq if el.getSearchKey() == value)


def findByID(seq, value):
    return next(el for el in seq if el.artistID == value)


class ArtistCollection:
    """
    Artist's class, each album is in a directory.
    """

    def __init__(self, mainMusicBase):
        self.artists = SortedKeyList(key=attrgetter("name"))  # [] #Artist Collection
        self.music_base = mainMusicBase

    def add_artist(self, artist):
        # Add an artist in artists list,

        if artist.artistID == 0:
            artist.artistID = self.music_base.db.insertArtist(artist)

        self.artists.add(artist)

        return artist

    def get_artist(self, artistName):
        newArt = Artist(artistName, 0)

        artistList = self.find_artists(newArt.name)

        if len(artistList) == 0:
            # If the artist is not found in artistCol, we add it and return the
            curArt = self.add_artist(newArt)
        elif len(artistList) == 1:
            # If artists is found
            curArt = artistList[0]
        else:
            # If there is more than 1 artist, ask for the good one to user
            # For the moment, just return the first one
            curArt = artistList[0]

        return curArt

    def find_artists(self, sname):
        return filterByName(self.artists, sname)

    def get_artist_by_id(self, id):
        return findByID(self.artists, id)

    def print_artists(self):
        for art in self.artists:
            art.printInfos()

    def load_artists(self):
        for rowArt in self.music_base.db.getSelect(
            "SELECT artistID, name FROM artists ORDER BY name"
        ):
            art = Artist(rowArt[1], rowArt[0])
            self.add_artist(art)

    def artist_compare(art1, art2):
        return art1.name > art2.name

    def sort_artists(self):
        self.artists = sorted(self.artists, key=attrgetter("name"))
