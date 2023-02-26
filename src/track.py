#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import platform
from mutagen.id3 import ID3
from mutagen.id3 import ID3NoHeaderError
from mutagen import MutagenError
from mutagen import File
from urllib.parse import unquote
import logging
from utils import *

logger = logging.getLogger(__name__)


class Track:
    """
    Track's class, each track is music a file such mp3, ogg, wma (sic), mpc, flac...
    """

    def __init__(self, file_name="", extension="", sub_path=""):
        self.track_id = 0
        self.title = ""
        self.album = ""
        self.artist = ""
        self.year = 0
        self.track_number = 0
        self.track_count = 0
        self.disc_number = 0
        self.disc_count = 0
        self.position = 0
        self.duration = 0  # in ms
        self.bitrate = 0
        self.file_name = file_name
        self.sub_path = sub_path
        self.path = ""
        self.extension = extension
        self.music_directory_id = ""
        self.mrl = ""
        self.parent_album = None
        self.radio_name = ""
        self.radioStream = ""
        self.radioID = 0
        self.radio = None
        # self.coverDownloaded = pyqtSignal(str, name='coverDownloaded')

    def printInfos(self):
        txt = (
            "TrackTitle="
            + self.title
            + " No="
            + str(self.track_number)
            + " DiscNo="
            + str(self.disc_number)
        )
        txt += (
            " TrackCount=" + str(self.track_count) + " DiscCount=" + str(self.disc_count)
        )
        logger.debug(txt)

    def get_name(self):
        return self.file_name + self.extension

    def get_file_path_in_album_dir(self):
        return os.path.join(self.sub_path, self.get_name())

    def get_file_path(self):
        # return os.path.join(self.path, self.get_file_path_in_album_dir())
        return os.path.join(self.path, self.get_name())

    def get_full_file_path(self):
        return os.path.join(self.path, self.get_name())

    def set_path(self, path):
        self.sub_path = ""
        self.path = os.path.dirname(path)
        basename = os.path.basename(path)
        self.file_name, self.extension = os.path.splitext(basename)

    def get_artist_name(self):
        if self.parent_album is not None:
            return self.parent_album.artist_name
        else:
            return self.artist

    def get_album_year(self):
        if self.parent_album is not None and self.year == 0:
            return self.parent_album.year
        else:
            return self.year

    def get_album_title(self):
        if self.parent_album is not None:
            return self.parent_album.title
        else:
            return self.album

    def get_full_title(self):
        title = self.get_track_title()
        if not self.is_radio():
            if self.artist != "":
                title = title + " - " + self.artist

        return title

    def get_track_title(self):
        if self.radio_name != "":
            if self.title != "":
                return self.title
            return self.radio_name
        else:
            return self.title

    def get_duration(self, player, dir):
        media = player.getParsedMedia(os.path.join(dir, self.get_file_path_in_album_dir()))
        self.duration = media.get_duration()
        return self.duration

    def get_duration_text(self):
        return time.strftime("%H:%M:%S", time.gmtime(self.duration))

    def is_radio(self):
        return self.radio_name != "" or self.radio

    def extract_data_from_tags_with_vlc(self, player, dir):
        """
        Extract ID3 metadatas with VLC
        Using Mutagen is faster
        """
        parsed_media = player.getParsedMedia(
            os.path.join(dir, self.get_file_path_in_album_dir())
        )
        self.title = parsed_media.get_meta(0)
        self.album = parsed_media.get_meta(4)
        self.artist = parsed_media.get_meta(1)
        self.track_number = parsed_media.get_meta(5)
        self.year = parsed_media.get_meta(8)

    def set_mrl(self, mrl):
        self.mrl = mrl
        path = unquote(mrl)
        if platform.system() == "Windows":
            path = path.replace("file:///", "")
        else:
            path = path.replace("file://", "")
        self.set_path(path)

    def get_valid_track_number_from_tag(self, track_num):
        if track_num in ["", "None"]:
            return
        if "/" in track_num:
            pos = track_num.index("/")
            self.track_number = int(track_num[:pos])
            self.track_count = int(track_num[pos + 1:])
        else:
            self.track_number = int(track_num)

    def get_valid_disc_number_from_tag(self, disc_num):
        if disc_num in ["", "None"]:
            return
        if "/" in disc_num:
            pos = disc_num.index("/")
            self.disc_number = int(disc_num[:pos])
            self.disc_count = int(disc_num[pos + 1:])
        else:
            self.disc_number = int(disc_num)

    def get_mutagen_tags(self, dir=""):
        """Extract ID3 metadatas, bitrate and duration with Mutagen"""
        if dir != "":
            track_path = os.path.join(dir, self.get_file_path_in_album_dir())
        else:
            track_path = self.get_file_path()
        try:
            audio = File(track_path)

            if audio.info:
                self.duration = audio.info.length
                self.bitrate = audio.info.bitrate

            if audio.tags:
                self.title = str(audio.tags.get("TIT2"))
                self.artist = str(audio.tags.get("TPE1"))
                self.album = str(audio.tags.get("TALB"))
                self.year = self.get_year_from_tag_dict(audio.tags)
                self.get_valid_track_number_from_tag(str(audio.tags.get("TRCK")))
                self.get_valid_disc_number_from_tag(str(audio.tags.get("TPOS")))

        except ID3NoHeaderError:
            logger.info("No tags")

        except MutagenError:
            logger.error("MutagenError:" + track_path)

        except Exception as e:
            logger.error("get_mutagen_tags Exception mutagen: %s", e)

        if self.title in ("", "None"):
            self.title = self.file_name
        self.printInfos()

    def get_year_from_tags(self, dir=""):
        """Extract year with Mutagen"""
        try:
            if dir != "":
                track_path = os.path.join(dir, self.get_file_path_in_album_dir())
            else:
                track_path = self.get_file_path()
            logger.debug("get_year_from_tags track path %s", track_path)
            audio = File(track_path)

            if audio.tags:
                self.year = self.get_year_from_tag_dict(audio.tags)
                return self.year
        except Exception as e:
            logger.error("get_year_from_tags exception mutagen: %s", e)
            return 0

    def get_year_from_tag_dict(self, tag_dict):
        if tag_dict:
            y = tag_dict.get("TYER")
            if y:
                return year(y)
            else:
                y = tag_dict.get("TDRC")
                if y:
                    str_y = str(y)
                    if len(str_y) > 4:
                        logger.debug("datas: %s", str_y)
                        str_y = str_y[:4]
                    return year(str_y)

        return 0

    def get_pic_from_tags(self, dir=""):
        """Extract cover pic with Mutagen"""
        try:
            if dir != "":
                track_path = os.path.join(dir, self.get_file_path_in_album_dir())
            else:
                track_path = self.get_file_path()
            logger.debug("get_pic_from_tags track path %s", track_path)
            audio = File(track_path)
            logger.debug("get_pic_from_tags track tags %s", audio.tags)
            if audio.tags:
                pic = audio.tags.get("APIC:")
                if pic:
                    alb_dir = os.path.dirname(track_path)
                    img_path = os.path.join(alb_dir, "cover.jpg")
                    img_short_path = os.path.join(dir, "cover.jpg")
                    logger.debug("get_pic_from_tags track img %s", img_path)
                    f = open(img_path, "w+b")
                    data = pic.data
                    f.write(data)
                    f.close()
                    return img_path
            return ""
        except Exception as e:
            logger.error("get_pic_from_tags exception mutagen: %s", e)
            return ""

    def get_mutagen_fast_tags(self, dir=""):
        """Extract ID3 metadatas with Mutagen"""
        try:
            if dir != "":
                track_path = os.path.join(dir, self.get_file_path_in_album_dir())
            else:
                track_path = self.get_file_path()

            audio = ID3(track_path)
            if audio.tags:
                self.artist = str(audio.tags.get("TPE1"))
                self.album = str(audio.tags.get("TALB"))
                self.title = str(audio.tags.get("TIT2"))
                self.year = self.get_year_from_tag_dict(audio.tags)

                self.track_number = str(audio.get("TRCK"))

        except ID3NoHeaderError:
            logger.debug("No tags")

        except MutagenError:
            logger.error("MutagenError:" + track_path)

        except Exception as e:
            logger.error("getMutagenFastTags exception mutagen: %s", e)

        if self.title in ("", "None"):
            self.title = self.file_name

    def on_cover_downloaded(self, cover):
        self.set_cover(cover)
        self.cover_downloaded.emit(cover)


if __name__ == "__main__":
    import sys
    from pyzik import *
    from musicBase import MusicBase

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(darkStyle.darkStyle.load_stylesheet_pyqt5())
    mb = MusicBase()
    mb.load_music_base()
    trk = Track("09. Not Suitable For Life", ".mp3", "/home/Documents/TEST/")
    trk.path = "/home/Documents/TEST/"
    logger.debug(trk)
    trk.get_pic_from_tags()
