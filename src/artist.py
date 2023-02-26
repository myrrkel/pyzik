#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
from operator import itemgetter, attrgetter
import random
from album import Album
import format_string
import logging

logger = logging.getLogger(__name__)


def get_simplest_title(title, char):
    simple = title.replace(".", char)
    simple = simple.replace(",", char)
    simple = simple.replace("'", char)
    simple = simple.replace("!", char)
    simple = simple.replace(":", char)
    simple = simple.replace("?", char)
    simple = simple.replace("  ", " ")
    simple = simple.strip()
    return simple


def get_alternative_title(title):
    alter = title
    if " & " in alter:
        alter = alter.replace(" & ", " And ")
    else:
        alter = alter.replace(" And ", " & ")
    return alter


def filter_albums_by_title(seq, title):
    title = format_string.get_search_key(title.upper())

    for el in seq:
        if el.get_search_key() == title:
            yield el
            break


class Artist:
    """
    Artist's class, the have
    """

    def __init__(self, name, artist_id):
        self.artist_id = artist_id
        self.name = self.format_name(name)
        self.countryID = 0
        self.categoryID = 0
        self.style_ids = set()
        self.albums: List[Album] = list()
        self.itemListViewArtist = None
        self.searchKey = ""

    def get_name(self):
        return self.name

    def format_name(self, name):
        return name.upper()

    def get_search_key(self):
        if self.searchKey == "":
            self.searchKey = format_string.get_search_key(self.name)
        return self.searchKey

    def print_infos(self):
        print(self.name + " id=" + str(self.artist_id))

    def sort_albums(self):
        self.albums = sorted(self.albums, key=attrgetter("year", "title"))

    def get_random_album(self):
        nbAlbum = len(self.albums)
        if nbAlbum > 0:
            irandom = random.randint(0, nbAlbum - 1)
            resAlb = self.albums[irandom]
            return resAlb

    def add_album(self, alb):
        self.albums.append(alb)

    def add_style(self, idSet):
        self.style_ids = self.style_ids.union(idSet)

    def find_albums(self, stitle):
        albumList = []
        for alb in filter_albums_by_title(self.albums, stitle):
            albumList.append(alb)
        return albumList
