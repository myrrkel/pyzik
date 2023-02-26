#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import urllib.parse
import json
import xml.etree.ElementTree as ET
from collections import namedtuple

from radio import Radio
from global_constants import *

import logging

logger = logging.getLogger(__name__)


def _json_object_hook(d):
    return namedtuple("X", d.keys())(*d.values())


def json_to_obj(data):
    return json.loads(data, object_hook=_json_object_hook)


def filter_by_radio_id(seq, RadID):
    for el in seq:
        if int(el.radioID) == int(RadID):
            yield el
            break


class RadioManager:
    """radioManager search and save web radio streams"""

    def __init__(self, music_base=None):
        self.music_base = music_base
        self.machines = ["RadioBrowser", "Dirble", "Dar", "Tunein"]
        self.favRadios = []

    def get_fav_radio(self, radioID):
        resRad = None
        for rad in filter_by_radio_id(self.favRadios, radioID):
            resRad = rad
        return resRad

    def get_redirection(self, url):
        redirection = ""
        try:
            r = requests.get(url, allow_redirects=False)
            redirection = r.headers["Location"]

        except requests.exceptions.HTTPError as err:
            print(err)

        return redirection

    def search_dar_radios(self, search):
        darRadios = []

        idList = self.search_dar_radios_id(search)

        for id in idList:
            print("IDDar=" + str(id))
            darStation = Radio()
            darStation.stream, darStation.name = self.get_dar_station(id)
            darStation.stream = self.get_redirection(darStation.stream)
            # print(darStation.stream)
            darRadios.append(darStation)

        return darRadios

    def search_dar_radios_id(self, search):
        rad_id_list = []
        search = urllib.parse.quote_plus("*" + search + "*")
        try:
            url = "http://api.dar.fm/playlist.php?q=@callsign " + search
            r = requests.get(url)
            tree = ET.fromstring(r.text)

        except requests.exceptions.HTTPError as err:
            print(err)

        for child in tree:
            if child.tag == "station":
                id = child.find("station_id")
                rad_id_list.append(int(id.text))

        return rad_id_list

    def get_dar_station(self, id):
        radio_url = ""
        name = ""

        try:
            url = (
                "http://www.dar.fm/uberstationurlxml.php?station_id="
                + str(id)
                + "&partner_token="
                + dar_api_key
            )
            print(url)
            r = requests.get(url)
            rtxt = r.text.encode("utf-8")
            tree = ET.fromstring(rtxt)

        except requests.exceptions.HTTPError as err:
            print(err)

        if tree.find("url") is not None:
            radioUrl = tree.find("url").text.strip()
            name = tree.find("callsign").text.strip()

        return (radioUrl, name)

    def search_dirble_radios(self, search):
        dirbleRadios = []
        search = urllib.parse.quote_plus(search)
        try:
            r = requests.post(
                "http://api.dirble.com/v2/search?token=" + dirble_api_key,
                data={"query": search},
                timeout=2,
            )
            dradios = json_to_obj(r.text)
            print("Dirble results=" + str(dradios))
            print("Status code=" + str(r.status_code))
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            return []
        except requests.exceptions.ReadTimeout as err:
            print("searchDirbleRadios Timeout")
            return []

        if dradios:
            for dr in dradios:
                if dr.streams is None:
                    return []
                for strm in dr.streams:
                    rad = Radio()
                    rad.init_with_dirble_radio(dr, strm.stream)
                    dirbleRadios.append(rad)

        return dirbleRadios

    def search_radio_brower(self, search):
        """
        Search radios with Radio Browser API
        """
        rb_radios, tradios = [], []
        headers = {
            "User-Agent": "pyzik 0.3",
        }
        search = urllib.parse.quote_plus(search.replace(" ", "_"))

        r = requests.post(
            "http://all.api.radio-browser.info/json/servers", headers=headers
        )
        servers = json_to_obj(r.text)
        logger.debug("Servers %s", servers)
        for server in servers:
            search_url = "http://%s/json/stations/search?name=%s" % (
                server.name,
                search,
            )
            try:
                r = requests.post(search_url, headers=headers, data={"name": search})
                tradios = json_to_obj(r.text)
                break
            except requests.exceptions.HTTPError as err:
                logger.error(err)

        if tradios:
            for tr in tradios:
                rad = Radio()
                rad.name = tr.name
                rad.stream = tr.url
                rad.country = tr.country
                rad.image = tr.favicon
                rad.add_categorie(tr.tags)
                rb_radios.append(rad)

        return rb_radios

    def search_tunein_radios(self, search):
        tuneinRadios = []
        search = urllib.parse.quote_plus(search)

        try:
            r = requests.post(
                "https://api.radiotime.com/profiles?query="
                + search
                + "&filter=s!&fullTextSearch=true&limit=20&formats=mp3,aac,ogg"
            )
            tradios = json_to_obj(r.text)
        except requests.exceptions.HTTPError as err:
            print(err)

        if tradios:
            for tr in tradios.Items:
                rad = Radio()
                rad.init_with_tunein_radio(tr)
                rad.stream = self.get_tunein_stream(rad.searchID)
                tuneinRadios.append(rad)

        return tuneinRadios

    def get_tunein_stream(self, id):
        try:
            url = "https://opml.radiotime.com/Tune.ashx?id=" + id + "&render=json"
            print(url)
            r = requests.get(url)
            # print(r.text)
            station = json_to_obj(r.text)

        except requests.exceptions.HTTPError as err:
            print(err)

        if hasattr(station, "body"):
            if len(station.body) > 0:
                radioUrl = station.body[0].url

        return radioUrl

    def get_fuzzy_groovy(self):
        fg = Radio()
        fg.name = "Fuzzy & Groovy Rock Radio"
        fg.stream = "http://listen.radionomy.com/fuzzy-and-groovy.m3u"
        fg.image = "https://i3.radionomy.com/radios/400/ce7c17ce-4b4b-4698-8ed0-c2881eaf6e6b.png"
        fg.adblock = True
        return fg

    def search(self, search, machine=""):
        resRadios = []
        if machine == "" or machine == "Dar":
            resRadios.extend(self.search_dar_radios(search))
        if machine == "" or machine == "Dirble":
            resRadios.extend(self.search_dirble_radios(search))
        if machine == "" or machine == "Tunein":
            resRadios.extend(self.search_tunein_radios(search))
        if machine == "" or machine == "RadioBrowser":
            resRadios.extend(self.search_radio_brower(search))

        return resRadios

    def load_fav_radios(self):
        self.favRadios = []
        for row in self.music_base.db.get_select(
            """
            SELECT radioID, name, stream, image, thumb, categoryID, sortID
            FROM radios ORDER BY sortID"""
        ):
            rad = Radio()
            rad.load(row)
            # rad.printData()
            self.favRadios.append(rad)


if __name__ == "__main__":
    rm = RadioManager()

    rm.search_dirble_radios("fip")

    # radios = rm.searchRadioBrower("fip")
    # for rad in radios:
    #    rad.printData()
