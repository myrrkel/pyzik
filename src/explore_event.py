#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from PyQt5 import QtCore

logger = logging.getLogger(__name__)
_translate = QtCore.QCoreApplication.translate


class ExploreEventList(list):
    def filter_by_code(self, event_code):
        return [el for el in self if el.event_code == event_code]

    def filter_exclude_code(self, event_code):
        return [el for el in self if el.event_code != event_code]

    def count_album_added(self):
        return len(self.filter_by_code("ALBUM_ADDED"))

    def get_event_types(self):
        return [
            {
                "code": "ALBUM_DUPLICATE",
                "label": _translate("events", "Album duplicate"),
            },
            {"code": "ALBUM_TO_VERIFY", "label": _translate("Album to check")},
            {
                "code": "ALBUM_TO_VERIFY_NO_TAG",
                "label": _translate("Album to check without tags"),
            },
            {"code": "ALBUM_ADDED", "label": _translate("Album added")},
        ]


class ExploreEvent:
    def __init__(self, code, dirpath, albumID=0, artistID=0, album=None):
        self.event_code = code
        self.dirPath = dirpath
        self.artistID = artistID
        self.albumID = albumID
        self.album = album

    def get_text(self):
        if self.event_code == "ALBUM_DUPLICATE":
            return "Album in " + self.dirPath + " already exists for this artist."
        if self.event_code == "ALBUM_TO_VERIFY":
            return "Album in " + self.dirPath + " must be verified"
        if self.event_code == "ALBUM_TO_VERIFY_NO_TAG":
            return "Album in " + self.dirPath + " must be verified. No tag found."
        if self.event_code == "ALBUM_ADDED":
            return "Album in " + self.dirPath + " added."
        return ""
