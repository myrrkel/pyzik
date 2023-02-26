#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
import random

from album import Album

import logging

logger = logging.getLogger(__name__)


def filter_by_title_artist_id(seq, title, art_id):
    """not used any more, use artist.findAlbum()"""
    for el in seq:
        if el.artist_id == art_id:
            if el.title == el.formatTitle(title):
                yield el
                break
            elif el.title.replace("And", "&") == el.formatTitle(title).replace(
                "And", "&"
            ):
                yield el
                break


def find_by_album_id2(seq, alb_id):
    return next(el for el in seq if int(el.album_id) == int(alb_id))


def find_by_album_id(seq, alb_id):
    return next((el for el in seq if int(el.album_id) == int(alb_id)), None)


class AlbumCollection:
    """
    AlbumCollection class
    """

    music_base = None

    def __init__(self, main_music_base):
        self.albums: List[Album] = list()
        self.music_base = main_music_base

    def add_album(self, album):
        if album.album_id == 0:
            album.album_id = self.music_base.db.insert_album(album)

        album.music_directory = self.music_base.musicDirectoryCol.get_music_directory(
            album.music_directory_id
        )
        self.albums.append(album)
        return album.album_id

    def print_albums(self):
        for alb in self.albums:
            alb.print_infos()

    def load_albums(self):
        for rowAlb in self.music_base.db.get_select(
            "SELECT albumID, title, year, dirPath, artistID, musicDirectoryID, size, length FROM albums"
        ):
            alb = Album("")
            alb.load(rowAlb)
            self.add_album(alb)

    def find_albums(self, title, art_id):
        album_list = []
        for alb in filter_by_title_artist_id(self.albums, title, art_id):
            album_list.append(alb)
        return album_list

    def get_album(self, alb_id):
        return find_by_album_id(self.albums, alb_id) or Album("")

    def get_random_album(self, style_id=-2):
        if style_id > -2:
            alb_list = [alb for alb in self.albums if style_id in alb.style_ids]
        else:
            alb_list = self.albums

        nb_album = len(alb_list)
        if nb_album > 0:
            num_random = random.randint(0, nb_album - 1)
            return alb_list[num_random]

    def get_albums_size(self):
        for alb in self.albums:
            alb.get_album_size()


if __name__ == "__main__":
    from music_base import MusicBase
    ac = AlbumCollection(MusicBase())
    ac.music_base.load_music_base()
    ac.load_albums()
    ac.print_albums()
