#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import urllib.parse
import json
from collections import namedtuple

from radio import Radio

import logging

logger = logging.getLogger(__name__)


def _json_object_hook(d):
    return namedtuple("X", d.keys())(*d.values())


def json_to_obj(data):
    return json.loads(data, object_hook=_json_object_hook)


def filter_by_radio_id(seq, rad_id):
    for el in seq:
        if int(el.radio_id) == int(rad_id):
            yield el
            break


class RadioManager:
    """radioManager search and save web radio streams"""

    def __init__(self, music_base=None):
        self.music_base = music_base
        self.machines = ["RadioBrowser", "Tunein"]
        self.fav_radios = []

    def get_fav_radio(self, radio_id):
        radio = None
        for rad in filter_by_radio_id(self.fav_radios, radio_id):
            radio = rad
        return radio

    def search_radio_brower(self, search):
        """
        Search radios with Radio Browser API
        """
        radios, radio_results = [], []
        headers = {"User-Agent": "pyzik 0.3"}
        search = urllib.parse.quote_plus(search.replace(" ", "_"))
        url = "http://all.api.radio-browser.info/json/servers"
        r = requests.post(url, headers=headers)
        servers = json_to_obj(r.text)
        for server in servers:
            search_url = f"http://{server.name}/json/stations/search?name={search}"
            try:
                r = requests.post(search_url, headers=headers, data={"name": search})
                radio_results = json_to_obj(r.text)
                break
            except requests.exceptions.HTTPError as err:
                logger.error(err)

        if radio_results:
            for radio_result in radio_results:
                radio = Radio()
                radio.name = radio_result.name
                radio.stream = radio_result.url
                radio.country = radio_result.country
                radio.image = radio_result.favicon
                radio.add_category(radio_result.tags)
                radios.append(radio)

        return radios

    def search_tunein_radios(self, search):
        tunein_radios = []
        search = urllib.parse.quote_plus(search)
        try:
            url = f"https://api.radiotime.com/profiles?query={search}"
            url += "&filter=s!&fullTextSearch=true&limit=20&formats=mp3,aac,ogg"
            r = requests.post(url)
            stations = json_to_obj(r.text)
        except requests.exceptions.HTTPError as err:
            logger.error(err)
            return

        if stations:
            for station in stations.Items:
                radio = Radio()
                radio.init_with_tunein_radio(station)
                radio.stream = self.get_tunein_stream(radio.search_id)
                tunein_radios.append(radio)

        return tunein_radios

    def get_tunein_stream(self, tunein_id):
        try:
            url = "https://opml.radiotime.com/Tune.ashx?id=" + tunein_id + "&render=json"
            print(url)
            r = requests.get(url)
            station = json_to_obj(r.text)

        except requests.exceptions.HTTPError as err:
            logger.error(err)
            return 

        if hasattr(station, "body"):
            if len(station.body) > 0:
                return station.body[0].url

    def get_fuzzy_groovy(self):
        fg = Radio()
        fg.name = "Fuzzy & Groovy Rock Radio"
        fg.stream = "https://open.spotify.com/playlist/4kZWpuho3TE3wlBIZz3LHL?si=0d36d0e19fb94e49"
        fg.image = "https://i.scdn.co/image/ab67706c0000da848b6ee2995e737eb987d45ad3"
        fg.adblock = True
        return fg

    def search(self, search, machine=""):
        res_radios = []
        if machine == "" or machine == "Tunein":
            res_radios.extend(self.search_tunein_radios(search))
        if machine == "" or machine == "RadioBrowser":
            res_radios.extend(self.search_radio_brower(search))
        return res_radios

    def load_fav_radios(self):
        self.fav_radios = []
        for row in self.music_base.db.get_select(
            """
            SELECT radioID, name, stream, image, thumb, categoryID, sortID
            FROM radios ORDER BY sortID"""
        ):
            rad = Radio()
            rad.load(row)
            self.fav_radios.append(rad)


if __name__ == "__main__":
    rm = RadioManager()
    rm.search_radio_brower("fip")

