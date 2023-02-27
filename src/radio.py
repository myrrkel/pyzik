#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import requests
import urllib.parse
import json
from bs4 import BeautifulSoup
from collections import namedtuple
from datetime import datetime, timedelta
import time
import pytz
import email.utils as eut
from pic_from_url_thread import PicFromUrlThread
from PyQt5.QtGui import QPixmap
from pic_downloader import PicDownloader


def _json_object_hook(d):
    for k in d.keys():
        k = k.replace("-", "_")
    for v in d.values():
        if isinstance(v, str):
            v = v.replace("-", "_")
    return namedtuple("X", d.keys(), rename=True)(*d.values())


def json2obj(data):
    return json.loads(data, object_hook=_json_object_hook)


class Radio:
    """
    Radio Stream
    """

    def __init__(self):
        self.radio_id = 0
        self.name = ""
        self.country = ""
        self.image = ""
        self.thumb = ""
        self.categories = []
        self.stream = ""
        self.stream_link = ""
        self.search_id = ""
        self.sort_id = 0
        self.adblock = False

        self.live_id = -1
        self.live_track_start = None
        self.live_track_end = None
        self.live_track_title = ""
        self.live_cover_url = ""
        self.cover = None
        self.cover_pixmap = QPixmap()

    def load(self, row):
        self.radio_id = row[0]
        self.name = row[1]
        self.stream = row[2]
        self.image = row[3]
        self.thumb = row[4]
        self.category_id = row[5]
        self.sort_id = row[6]

    def add_category(self, cat):
        self.categories.append(cat)

    def add_stream(self, stream):
        self.streams.append(stream)

    def get_category_id(self):
        return 0

    def insert_radio(self, db):
        db.create_connection()

        try:
            c = db.connection.cursor()
            req = """    INSERT INTO radios (name, stream)
                                      VALUES (?,?);
                          """
            c.execute(req, (self.name, self.stream))
            db.connection.commit()
            self.radio_id = c.lastrowid

        except sqlite3.Error as e:
            print(e)

    def save_radio(self, db):
        if self.radio_id == 0:
            self.insert_radio(db)

        db.create_connection()

        try:
            c = db.connection.cursor()
            req = """    UPDATE radios SET name=?, stream=?,image=?,thumb=?,categoryID=?,sortID=?
                                      WHERE radioID = ?;
                          """
            c.execute(
                req,
                (
                    self.name,
                    self.stream,
                    self.image,
                    self.thumb,
                    self.get_category_id(),
                    self.sort_id,
                    self.radio_id,
                ),
            )
            db.connection.commit()

        except sqlite3.Error as e:
            print(e)

    def init_with_dirble_radio(self, dRadio, stream):
        self.name = dRadio.name
        self.country = dRadio.country

        if hasattr(dRadio, "image"):
            if len(dRadio.image) > 0:
                self.image = dRadio.image[0]
                if hasattr(dRadio.image, "thumb"):
                    self.thumb = dRadio.image.thumb[0]

        self.stream = stream
        for cat in dRadio.categories:
            self.add_category(cat.title)

    def init_with_tunein_radio(self, tRadio):
        self.name = tRadio.Title
        self.country = tRadio.Subtitle
        self.search_id = tRadio.GuideId

    def get_fip_live_id(self):
        fip_id = -1
        if self.is_fip(strict=True):
            fip_id = 7
        elif "FIP " in self.name.upper():
            key = "webradio"
            iwr = str(self.stream.find(key) + len(key))
            if iwr.isdigit():
                nwr = int(self.stream[int(iwr)])
                if nwr == 4:
                    fip_id = 69
                elif nwr == 5:
                    fip_id = 70
                elif nwr == 6:
                    fip_id = 71
                elif nwr == 8:
                    fip_id = 74
                else:
                    fip_id = 63 + nwr

        return fip_id

    def is_fip(self, strict=False):
        rad_name = "FIP"
        if strict:
            return self.name.upper() == rad_name
        else:
            return self.name.upper() == rad_name or rad_name + " " in self.name.upper()

    def is_france_musique(self, strict=False):
        radio_name = "FRANCE MUSIQUE"
        if strict:
            return self.name.upper() == radio_name
        else:
            return self.name.upper() == radio_name or radio_name + " " in self.name.upper()

    def is_france_inter(self, strict=False):
        radio_name = "FRANCE INTER"
        return self.name.upper() == radio_name

    def is_france_culture(self):
        radio_name = "FRANCE CULTURE"
        return self.name.upper() == radio_name

    def is_france_info(self):
        radio_name = "FRANCE INFO"
        return self.name.upper() == radio_name

    def is_tsf_jazz(self):
        radio_name = "TSF JAZZ"
        return self.name.upper() == radio_name

    def is_kexp(self):
        radio_name = "KEXP"
        return self.name.upper() == radio_name or radio_name + " " in self.name.upper()

    def get_france_musique_live_id(self, rurl):
        if self.is_france_musique(strict=True):
            return 4

        try:
            url = "http://www.francemusique.fr"
            r = requests.get(url)
            html = r.text

        except requests.exceptions.HTTPError as err:
            print(err)
            return -1

        soup = BeautifulSoup(html, "html.parser")

        for radio_list in soup.findAll("ul", {"class": "web-radio-header-wrapper-list"}):
            for rad in radio_list.findAll("li"):
                url = rad.get("data-live-url")
                print(url)
                live_id = rad.get("data-station-id")

                pos1 = rurl.rfind("/")
                pos2 = rurl.rfind("-")
                station = rurl[pos1 + 1 : pos2]
                print(station + " LiveID=" + str(live_id))
                if station in url:
                    return live_id

                if rurl.replace("http://", "").replace("https://", "") in url:
                    return live_id

        return -1

    def get_current_track(self):
        title = ""
        if self.is_fip():
            live_url = "https://www.fip.fr/livemeta/" + str(self.get_fip_live_id())
            title = self.get_current_track_rf(live_url)

        elif self.is_france_musique():
            if self.live_id < 0:
                self.live_id = int(self.get_france_musique_live_id(self.stream))
            if self.live_id < 0:
                return ""
            live_url = "https://www.francemusique.fr/livemeta/pull/" + str(self.live_id)
            title = self.get_current_track_rf(live_url)

        elif self.is_france_inter():
            live_url = "https://www.francemusique.fr/livemeta/pull/1"
            title = self.get_current_track_rf(live_url)

        elif self.is_france_culture():
            live_url = "https://www.francemusique.fr/livemeta/pull/5"
            title = self.get_current_track_rf(live_url)

        elif self.is_france_info():
            live_url = "https://www.francemusique.fr/livemeta/pull/2"
            title = self.get_current_track_rf(live_url)

        elif self.is_tsf_jazz():
            title = self.get_current_track_tsf_jazz()

        elif self.is_kexp():
            title = self.get_current_track_kexp()

        else:
            title = ""

        title = self.clean_title(title)
        self.live_track_title = title

        return title

    def clean_title(self, title):
        clean = title.strip()
        if clean == "|":
            clean = ""
        if clean == "-":
            clean = ""
        if "targetspot" in clean.lower():
            clean = ""
        return clean

    def is_timeout(self, nb_sec=10):
        res = True
        tsNow = time.time()
        if self.live_track_end is not None:
            if self.live_track_end > tsNow:
                res = False
            else:
                res = True
                self.live_track_end = tsNow + 10
        else:
            self.live_track_end = tsNow

        return res

    def get_current_track_tsf_jazz(self):
        if not self.is_timeout():
            return self.live_track_title

        url = "http://www.tsfjazz.com/getSongInformations.php"
        r = requests.get(url)
        track = r.text.replace("|", " - ")
        return track

    def get_current_track_kexp(self):
        if not self.is_timeout():
            return self.live_track_title

        current_track = ""
        try:
            live_url = "https://legacy-api.kexp.org/play/?format=json&limit=1"
            print("LiveUrl=" + live_url)
            r = requests.get(live_url)
            if r.text == "":
                return ""
            if len(r.text) > 0 and r.text[0] != "{":
                return ""
            date_request = r.headers.__getitem__("Date")
            date_srv = datetime(*eut.parsedate(date_request)[:6])
            print("dateSrv= " + str(date_srv))
            datas = json2obj(r.text)
        except requests.exceptions.HTTPError as err:
            print(err)

        if datas:
            if datas.results[0].playtype.playtypeid == 1:
                current_track = (
                    str(datas.results[0].artist.name)
                    + " - "
                    + str(datas.results[0].track.name)
                )
            else:
                current_track = self.get_current_show_kexp()

        return current_track

    def get_current_show_kexp(self):
        current_show = ""

        try:
            live_url = "https://legacy-api.kexp.org/show/?format=json&limit=1"
            print("LiveShowUrl=" + live_url)
            r = requests.get(live_url)
            if r.text == "":
                return ""
            if len(r.text) > 0 and r.text[0] != "{":
                return ""
            datas = json2obj(r.text)
        except requests.exceptions.HTTPError as err:
            print(err)

        if datas:
            current_show = (
                str(datas.results[0].program.name)
                + " - "
                + str(datas.results[0].hosts[0].name)
            )

        return current_show

    def get_current_track_rf(self, live_url):
        """
        Get live title from RF
        """

        if self.live_track_end is not None:
            now = time.time()
            if self.live_track_end > now:
                return self.live_track_title

        try:
            r = requests.get(live_url)
            if r.text == "":
                return ""
            if len(r.text) > 0 and r.text[0] != "{":
                return ""
            date_request = r.headers.__getitem__("Date")
            date_srv = datetime(*eut.parsedate(date_request)[:6])
            print("dateSrv= " + str(date_srv))
            datas = json2obj(r.text)
        except requests.exceptions.HTTPError as err:
            print(err)

        if datas:
            if self.is_france_info():
                level = 1
            else:
                level = 0
            pos = datas.levels[level].position
            step_id = datas.levels[level].items[pos]
            for stp in datas.steps:
                if stp.stepId == step_id:
                    self.live_track_start = stp.start
                    self.live_track_end = stp.end

                    date_end = datetime.fromtimestamp(self.live_track_end)
                    print("date_end=" + str(date_end))
                    current_track = ""
                    if self.is_fip() or self.is_france_musique():
                        if hasattr(stp, "visual") and stp.visual[:4].lower() == "http":
                            self.live_cover_url = stp.visual
                            print("visual=" + self.live_cover_url)

                        if hasattr(stp, "authors") and isinstance(stp.authors, str):
                            if stp.authors != "":
                                current_track = stp.authors

                        if hasattr(stp, "composers") and isinstance(stp.composers, str):
                            if stp.composers != "":
                                current_track = stp.composers

                        if current_track != "":
                            current_track = current_track + " - " + stp.title
                        else:
                            current_track = stp.title

                    if (
                        self.is_france_inter()
                        or self.is_france_info()
                        or self.is_france_culture()
                    ):
                        if hasattr(stp, "visual") and stp.visual[:3].lower() == "http":
                            self.live_cover_url = stp.visual
                            print("visual=" + self.live_cover_url)

                        if hasattr(stp, "titleConcept") and isinstance(
                            stp.titleConcept, str
                        ):
                            current_track = stp.titleConcept
                            if stp.titleConcept != "":
                                current_track = current_track + " - " + stp.title
                        else:
                            current_track = stp.title

        print("trackTitle=" + str(current_track))
        return current_track

    def print_data(self):
        print(
            self.name
            + " # "
            + self.stream
            + " # "
            + str(self.image)
            + " # "
            + str(self.thumb)
        )

    def get_radio_pic(self):
        url = self.image
        if url == "":
            url = self.thumb
        return url

    def get_categories_text(self):
        s = "; "
        return s.join(self.categories)

    def get_cover_url(self):
        url = self.live_cover_url
        if url == "":
            url = self.get_radio_pic()
        return url

    def get_cover(self):
        return self.cover

    def set_cover(self, cover):
        self.cover = cover


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    url = "https://direct.francemusique.fr/live/francemusiqueeasyclassique-hifi.aac"

    pos1 = url.rfind("/")
    pos2 = url.rfind("-")
    print(str(pos1) + " - " + str(pos2))
    station = url[pos1:pos2]
    print(station)

    utc = datetime.utcnow()
    print(str(utc))
    dnow = datetime.now()
    print(str(dnow))
    print(time.mktime(dnow.timetuple()))

    local = pytz.timezone("Europe/Paris")
    print(str(local))

    # datetime.fromtimestamp

    local_dt = local.localize(utc, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    print("local_dt=" + str(local_dt) + " utc_dt=" + str(utc_dt))

    rad = Radio()
    rad.stream = "https://direct.francemusique.fr/live/francemusiquelajazz-hifi.mp3"
    rad.name = "France Musique La Jazz"
    print("Rad=" + rad.get_current_track())

    sys.exit(app.exec_())
