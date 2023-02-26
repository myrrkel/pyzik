#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
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
        self.albums = []  # Album Collection
        self.music_base = main_music_base

    def add_album(self, album):
        if album.album_id == 0:
            album.album_id = self.music_base.db.insertAlbum(album)

        album.music_directory = self.music_base.musicDirectoryCol.get_music_directory(
            album.music_directory_id
        )
        self.albums.append(album)
        return album.album_id

    def print_albums(self):
        for alb in self.albums:
            alb.printInfos()

    def load_albums(self):
        for rowAlb in self.music_base.db.getSelect(
            "SELECT albumID, title, year, dirPath, artistID, musicDirectoryID, size, length FROM albums"
        ):
            alb = Album("")
            alb.load(rowAlb)
            self.add_album(alb)

    def find_albums(self, stitle, artID):
        albumList = []
        for alb in filter_by_title_artist_id(self.albums, stitle, artID):
            albumList.append(alb)
        return albumList

    def get_album(self, albID):
        return find_by_album_id(self.albums, albID) or Album("")

    def get_random_album(self, styleID=-2):
        if styleID > -2:
            albList = [alb for alb in self.albums if styleID in alb.style_ids]
        else:
            albList = self.albums

        nbAlbum = len(albList)
        if nbAlbum > 0:
            irandom = random.randint(0, nbAlbum - 1)
            resAlb = albList[irandom]
            return resAlb

    def get_albums_size(self):
        for alb in self.albums:
            alb.getAlbumSize()


if __name__ == "__main__":
    from musicBase import MusicBase

    ac = AlbumCollection()
    ac.music_base = MusicBase()
    ac.music_base.load_music_base()
    ac.load_albums()
    ac.print_albums()
