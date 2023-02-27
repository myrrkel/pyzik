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
        self.country_id = 0
        self.category_id = 0
        self.style_ids = set()
        self.albums: List[Album] = list()
        self.item_list_view_artist = None
        self.search_key = ""

    def get_name(self):
        return self.name

    def format_name(self, name):
        return name.upper()

    def get_search_key(self):
        if self.search_key == "":
            self.search_key = format_string.get_search_key(self.name)
        return self.search_key

    def print_infos(self):
        print(self.name + " id=" + str(self.artist_id))

    def sort_albums(self):
        self.albums = sorted(self.albums, key=attrgetter("year", "title"))

    def get_random_album(self):
        nb_album = len(self.albums)
        if nb_album > 0:
            int_random = random.randint(0, nb_album - 1)
            res_alb = self.albums[int_random]
            return res_alb

    def add_album(self, alb):
        self.albums.append(alb)

    def add_style(self, id_set):
        self.style_ids = self.style_ids.union(id_set)

    def find_albums(self, title):
        album_list = []
        for alb in filter_albums_by_title(self.albums, title):
            album_list.append(alb)
        return album_list
