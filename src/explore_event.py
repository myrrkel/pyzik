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
            {"code": "ALBUM_TO_VERIFY", "label": _translate("event", "Album to check")},
            {
                "code": "ALBUM_TO_VERIFY_NO_TAG",
                "label": _translate("event", "Album to check without tags"),
            },
            {"code": "ALBUM_ADDED", "label": _translate("event", "Album added")},
        ]


class ExploreEvent:
    def __init__(self, code, dir_path, album_id=0, artist_id=0, album=None):
        self.event_code = code
        self.dir_path = dir_path
        self.artist_id = artist_id
        self.album_id = album_id
        self.album = album

    def get_text(self):
        if self.event_code == "ALBUM_DUPLICATE":
            return "Album in " + self.dir_path + " already exists for this artist."
        if self.event_code == "ALBUM_TO_VERIFY":
            return "Album in " + self.dir_path + " must be verified"
        if self.event_code == "ALBUM_TO_VERIFY_NO_TAG":
            return "Album in " + self.dir_path + " must be verified. No tag found."
        if self.event_code == "ALBUM_ADDED":
            return "Album in " + self.dir_path + " added."
        return ""
