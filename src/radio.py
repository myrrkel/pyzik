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

    def init_with_tunein_radio(self, tunein_radio):
        self.name = tunein_radio.Title
        self.country = tunein_radio.Subtitle
        self.search_id = tunein_radio.GuideId

    def get_fip_live_id(self):

        if self.is_fip(strict=True):
            return 'fip'
        name = self.name.lower()
        if "fip " in name:
            if "pop" in name:
                return 'fip_pop'
            if "electro" in name:
                return 'fip_electro'
            if "metal" in name:
                return 'fip_metal'
            if "hiphop" in name or "hip-hop" in name or "hip hop" in name:
                return 'fip_hiphop'
            if "nouveau" in name:
                return 'fip_nouveautes'
            if "reggae" in name:
                return 'fip_reggae'
            if "rock" in name:
                return 'fip_rock'
            if "world" in name or "monde" in name:
                return 'fip_world'
            if "groove" in name:
                return 'fip_groove'
            if "jazz" in name:
                return 'fip_jazz'
        return 'fip'

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

    def is_mouv(self):
        if self.name.lower() == 'mouv':
            return True
        if self.name.lower() == 'mouv':
            return True
        if self.name.lower().startswith('le mouv'):
            return True

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
            live_url = f"https://www.radiofrance.fr/api/v2.1/stations/fip/webradios/{self.get_fip_live_id()}"
            title = self.get_current_track_radio_france(live_url)

        elif self.is_france_musique():
            live_url = "https://www.radiofrance.fr/api/v2.1/stations/francemusique/live"
            title = self.get_current_track_radio_france(live_url)

        elif self.is_france_inter():
            live_url = "https://www.radiofrance.fr/api/v2.1/stations/franceinter/live"
            title = self.get_current_track_radio_france(live_url)

        elif self.is_france_culture():
            live_url = "https://www.radiofrance.fr/api/v2.1/stations/franceculture/live"
            title = self.get_current_track_radio_france(live_url)

        elif self.is_france_info():
            live_url = "https://www.radiofrance.fr/api/v2.1/stations/franceinfo/live"
            title = self.get_current_track_radio_france(live_url)

        elif self.is_mouv():
            live_url = "https://www.radiofrance.fr/api/v2.1/stations/mouv/live"
            title = self.get_current_track_radio_france(live_url)

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

    def get_radio_france_streams(self):
        url = 'https://www.radiofrance.fr/api/v2.1/stations/streams'

    def get_current_track_tsf_jazz(self):
        if not self.is_timeout():
            return self.live_track_title

        url = "https://api.tsfjazz.com/api/tracklists/current/TSF?radio=TSF"
        r = requests.get(url)
        datas = json2obj(r.text)
        self.live_cover_url = datas.thumbnail_medium
        current_track = datas.artist + ' - ' + datas.title
        return current_track

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

    def get_current_track_radio_france(self, live_url):
        """
        Get live title from Radio France
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
            now = datas.now
            if hasattr(datas, 'media'):
                self.live_track_start = datas.media.startTime
                self.live_track_end = datas.media.endTime
                date_end = datetime.fromtimestamp(self.live_track_end)
                print("date_end=" + str(date_end))

            if hasattr(now, 'cover'):
                self.live_cover_url = now.cover.src
            else:
                self.live_cover_url = ""
            if hasattr(now.firstLine, 'title') and isinstance(now.firstLine.title, str):
                current_track = now.firstLine.title + " - " + now.secondLine.title
            else:
                current_track = now.firstLine + " - " + now.secondLine

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
