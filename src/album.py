#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os

import shutil
import fnmatch
import track
import database
from files_utils import *
from utils import *
from global_constants import *
import format_string as FS
import logging

logger = logging.getLogger(__name__)


def get_common_formats(with_year=True, generic=False):
    def get_separator(sep, side, var_name):
        return {"separator": sep, "side": side, "var": var_name}

    common_name_formats = []

    if generic:
        if with_year:
            # 'DEEP PURPLE @ 1972 @ Machine Head'
            separators = [get_separator("@", "left", "artist_name"),
                          get_separator("@", "left", "year"),
                          get_separator("", "right", "title")]
            common_name_formats.append(separators)

            # 'DEEP PURPLE @ Machine Head @ 1972 @'
            separators = [get_separator("@", "left", "artist_name"),
                          get_separator("@", "left", "title"),
                          get_separator("@", "left", "year")]
            common_name_formats.append(separators)

            # 'DEEP PURPLE @ Machine Head @ 1972'
            separators = [get_separator("@", "left", "artist_name"),
                          get_separator("@", "left", "title"),
                          get_separator("", "right", "year")]
            common_name_formats.append(separators)

        else:
            # 'DEEP PURPLE @ Machine Head'
            separators = [get_separator("@", "left", "artist_name"),
                          get_separator("", "right", "title")]
            common_name_formats.append(separators)

            # 'DEEP PURPLE @ Machine Head @'
            separators = [get_separator("@", "left", "artist_name"),
                          get_separator("@", "left", "title")]
            common_name_formats.append(separators)
    else:
        if with_year:
            # 'DEEP PURPLE - [1972] - Machine Head'
            separators = [get_separator(" - [", "left", "artist_name"),
                          get_separator("] - ", "left", "year"),
                          get_separator("", "right", "title"),
                          ]
            common_name_formats.append(separators)

            # 'DEEP PURPLE - (1972) - Machine Head'
            separators = [get_separator(" - (", "left", "artist_name"),
                          get_separator(") - ", "left", "year"),
                          get_separator("", "right", "title")]
            common_name_formats.append(separators)

            # 'DEEP PURPLE (1972) Machine Head'
            separators = [get_separator("(", "left", "artist_name"),
                          get_separator(")", "left", "year"),
                          get_separator("", "right", "title")]
            common_name_formats.append(separators)

            # 'DEEP PURPLE - 1972 - Machine Head'
            separators = [get_separator(" - ", "left", "artist_name"),
                          get_separator(" - ", "left", "year"),
                          get_separator("", "right", "title")]
            common_name_formats.append(separators)

            # 'DEEP PURPLE - Machine Head (1972)'
            separators = [
                get_separator(" - ", "left", "artist_name"),
                get_separator("(", "left", "title"),
                get_separator(")", "left", "year")]
            common_name_formats.append(separators)

            # 'DEEP PURPLE - Machine Head [1972]'
            separators = [get_separator(" - ", "left", "artist_name"),
                          get_separator("[", "left", "title"),
                          get_separator("]", "left", "year")]
            common_name_formats.append(separators)

        else:
            # 'DEEP PURPLE - Machine Head'
            separators = [get_separator(" - ", "left", "artist_name"),
                          get_separator("", "right", "title")]
            common_name_formats.append(separators)

    return common_name_formats


name_formats_with_year = get_common_formats(with_year=True, generic=False)

name_formats_generic_with_year = get_common_formats(with_year=True, generic=True)

name_formats_without_year = get_common_formats(with_year=False, generic=False)

name_formats_generic_without_year = get_common_formats(with_year=False, generic=True)


def invalid_album_name():
    return [
        "Unknown album",
        "Album inconnu",
    ]


def invalid_artist_name():
    return [
        "Unknown artist",
        "Artiste inconnu",
    ]


def title_except(title):
    exceptions = ["a", "an", "of", "the", "is", "in", "to"]
    word_list = re.split(" ", title)

    final = [capitaliseWord(word_list[0])]
    for word in word_list[1:]:
        if str.lower(word) in exceptions:
            final.append(word.lower())
        else:
            final.append(capitaliseWord(word))
    return " ".join(final)


def replace_special_chars(text):
    # Replace strings in given text according to the dictionary 'rep'

    rep = {
        "_": " ",
        "  ": " ",
        "#": "@",
        "-(": "@",
        ")-": "@",
        "- (": "@",
        ") -": "@",
        "-[": "@",
        "]-": "@",
        "- [": "@",
        "] -": "@",
        "(": "@",
        ")": "@",
        "[": "@",
        "]": "@",
        " - ": "@",
        "@ @": "@",
        "@@": "@",
    }

    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    return pattern.sub(lambda match: rep[re.escape(match.group(0))], text)


class Album:
    """
    Album's class, each album is in a directory name.
    """

    def __init__(self, dirname="", music_directory=None):
        self.album_id = 0
        self.title = ""
        self.dir_name = dirname
        self.dir_path = dirname
        self.artist_id = ""
        self.artist_name = ""
        self.year = 0
        self.cover = ""
        self.size = 0
        self.length = 0
        self.to_verify = False
        self.tracks = []
        self.images = []
        self.style_ids = set()
        self.doStop = False
        self.music_directory = music_directory
        self.coverPixmap = None  # QPixmap()
        if music_directory:
            self.music_directory_id = music_directory.music_directory_id
        else:
            self.music_directory_id = 0
        self.searchKey = ""

        if dirname != "":
            self.extract_data_from_dir_name()

    def load(self, row):
        self.album_id = row[0]
        self.title = row[1]
        self.year = row[2]
        self.dir_path = row[3]
        self.artist_id = row[4]
        self.music_directory_id = row[5]
        self.size = row[6]
        self.length = row[7]

    def format_title(self, title):
        return title_except(title)

    def get_cover_search_text(self):
        txt = self.artist_name
        if int(self.year) > 0 and int(self.year) != 9999:
            txt = txt + " " + str(self.year)
        txt = txt + " " + self.title
        return txt

    def get_search_key(self):
        if self.searchKey == "":
            self.searchKey = FS.get_search_key(self.title.upper())
        return self.searchKey

    def print_infos(self):
        print(
            "Title: "
            + self.title
            + "  # Artist: "
            + self.artist_name
            + "  # ArtistID: "
            + str(self.artist_id)
            + "  # Year: "
            + str(self.year)
            + "  # music_directory_id: "
            + str(self.music_directory_id)
            + "  # dir_path: "
            + str(self.dir_path)
        )

    def split_with_separator(self, string_separator, string_to_split):
        res_val = res_left = False
        if string_separator["side"] == "left":
            res_split = string_to_split.split(string_separator["separator"], maxsplit=1)
            if len(res_split) == 2:
                res_val, res_left = res_split[0], res_split[1]
        elif string_separator["side"] == "right":
            if string_separator["separator"] == "":
                res_val, res_left = string_to_split, ""

        if res_val and string_separator["var"] == "year":
            if not (res_val.isdigit() and isYear(res_val)):
                return False
            else:
                res_val = year(res_val)

        if res_val:
            return res_val, res_left
        return False

    def eval_name_formats(self, album_name, name_formats):
        for name_format in name_formats:
            logger.debug(
                "eval_name_formats name_format=%s album_name=%s",
                name_format,
                album_name,
            )
            valid = True
            txt = album_name
            for i, separator in enumerate(name_format):
                res = self.split_with_separator(separator, txt)
                if res:
                    val, txt = res
                    name_format[i]["val"] = val
                    logger.debug(
                        "split_with_separator sep=%s val=%s txt=%s", separator, val, txt
                    )
                else:
                    valid = False
                    break
            if valid:
                return name_format

        return False

    def extract_data_from_dir_name(self):
        self.to_verify = False
        txt = self.dir_name
        logger.info(
            "extractDataFromDirName name_formats_with_year %s", name_formats_with_year
        )
        format_found = self.eval_name_formats(txt, name_formats_with_year)

        if not format_found:
            txt = replace_special_chars(self.dir_name).strip()
            logger.info(
                "extractDataFromDirName name_formats_generic_with_year %s",
                name_formats_generic_with_year,
            )
            format_found = self.eval_name_formats(txt, name_formats_generic_with_year)

        if not format_found:
            txt = self.dir_name
            logger.info(
                "extractDataFromDirName name_formats_without_year %s",
                name_formats_without_year,
            )
            format_found = self.eval_name_formats(txt, name_formats_without_year)

        if not format_found:
            txt = replace_special_chars(self.dir_name).strip()
            logger.info(
                "extractDataFromDirName name_formats_generic_without_year %s",
                name_formats_generic_without_year,
            )
            format_found = self.eval_name_formats(
                txt, name_formats_generic_without_year
            )

        if format_found:
            for separator in format_found:
                setattr(self, separator["var"], separator["val"])

        self.title = self.title.strip()
        self.artist_name = self.artist_name.strip().upper()
        self.title = self.format_title(self.title)

        if isYear(self.artist_name) or not self.title or not self.artist_name:
            self.to_verify = True

    def get_year_from_tags(self):
        track = self.get_tracks(first_file_only=True)
        if track:
            return track.get_year_from_tags()
        return 0

    def get_pic_from_tags(self):
        track = self.get_tracks(first_file_only=True)
        if track:
            return track.get_pic_from_tags()
        return ""

    def get_tags_from_first_file(self):
        track = self.get_tracks(first_file_only=True)
        if track:
            if track.artist and self.is_valid_artist_name(track.artist):
                self.artist_name = track.artist
            else:
                return
            if track.album and self.is_valid_album_name(track.album):
                self.title = track.album
            if track.year:
                self.year = track.year
            print(
                "getTagsFromFirstFile="
                + self.artist_name
                + " - "
                + self.title
                + " - "
                + str(self.year)
            )

    def get_year_from_first_file(self):
        track = self.get_tracks(first_file_only=True)
        if track:
            if track.year:
                self.year = track.year
            return track.year

    def is_valid_album_name(self, name):
        name = name.lower()
        if name:
            if name not in [x.lower() for x in invalid_album_name()]:
                if name != "none":
                    for invalid in invalid_album_name():
                        if invalid in name:
                            return False
                    return True

    def is_valid_artist_name(self, name):
        name = name.lower()
        if name:
            if name not in [x.lower() for x in invalid_artist_name()]:
                if name != "none":
                    for invalid in invalid_artist_name():
                        if invalid in name:
                            return False
                    return True

    def get_tracks(self, subdir="", first_file_only=False):
        if subdir == "":
            self.tracks = []
        self.doStop = False
        if not self.check_dir():
            return False
        res = False
        if subdir == "":
            self.tracks = []
            current_dir = self.get_album_dir()
        else:
            current_dir = os.path.join(self.get_album_dir(), subdir)

        logger.debug("get_tracks() path %s", current_dir)
        files = os.listdir(current_dir)
        files.sort()

        nTrack = track.Track("", "")

        for file in files:
            if self.doStop:
                break
            if os.path.isdir(os.path.join(current_dir, str(file))):
                # file is a directory
                logger.debug("get_tracks() sub dir: %s ; %s", subdir, str(file))
                res = self.get_tracks(
                    os.path.join(subdir, str(file)), first_file_only=first_file_only
                )
            else:
                for ext in musicFilesExtension:
                    if fnmatch.fnmatch(file.lower(), "*." + ext):
                        sfile = str(file)

                        if "." in sfile:
                            filename, file_extension = os.path.splitext(sfile)
                            itrack = track.Track(filename, file_extension, subdir)
                            itrack.path = current_dir
                            itrack.parentAlbum = self

                            if first_file_only:
                                itrack.get_mutagen_tags(self.get_album_dir())
                                self.tracks.append(itrack)
                                return itrack
                            else:
                                itrack.get_mutagen_tags(self.get_album_dir())
                                self.tracks.append(itrack)
                            break
        return res

    def get_images(self, subdir=""):
        self.doStop = False
        if not self.check_dir():
            return False

        if subdir == "":
            self.images = []
            current_dir = self.get_album_dir()
        else:
            current_dir = os.path.join(self.get_album_dir(), subdir)

        files = os.listdir(current_dir)

        files.sort()

        for file in files:
            if self.doStop:
                break
            if os.path.isdir(os.path.join(current_dir, str(file))):
                # file is a directory
                self.get_images(os.path.join(subdir, file))
            else:
                if file == "cover":
                    os.rename(
                        os.path.join(current_dir, file),
                        os.path.join(current_dir, "cover.jpg"),
                    )

                for ext in imageFilesExtension:
                    if fnmatch.fnmatch(file.lower(), "*." + ext):
                        sfile = os.path.join(current_dir, file)
                        self.images.append(sfile)
                        break

    def get_cover(self):
        if len(self.images) > 0:
            keywords = [
                "cover",
                "front",
                "artwork",
                "capa",
                "caratula",
                "recto",
                "portada",
                "frente editada",
                "frente",
                "folder",
                "f",
            ]

            cover_found = ""
            for keyword in keywords:
                cover_found = next(
                    (x for x in self.images if keyword == getFileName(x.lower())), ""
                )
                if cover_found != "":
                    self.cover = cover_found
                    break

            if cover_found == "":
                for keyword in keywords:
                    cover_found = next(
                        (
                            x
                            for x in self.images
                            if keyword in getFileName(x.lower())
                            and "back" not in getFileName(x.lower())
                        ),
                        "",
                    )
                    if cover_found:
                        self.cover = cover_found
                        break
            # print("getCover cover="+self.cover)

            if self.cover == "":
                # print("getCover GetDefault="+self.images[0])
                self.cover = self.images[0]

        logger.debug("getCover %s", self.cover)
        if self.cover == "":
            self.cover = self.get_pic_from_tags()
            logger.debug("getCover %s", self.cover)

    def get_cover_path(self):
        return os.path.join(self.get_album_dir(), self.cover)

    def check_dir(self):
        if self.music_directory:
            albDir = self.get_album_dir()
            if albDir:
                return os.path.exists(albDir)
        else:
            return False

    def set_do_stop(self):
        self.doStop = True

    def get_album_dir(self):
        if self.music_directory:
            album_dir = os.path.join(self.music_directory.get_dir_path(), self.dir_path)
            return album_dir
        else:
            return self.dir_path

    def get_tracks_file_path(self):
        files = []
        for track in self.tracks:
            files.append(track.getFilePath())
        return files

    def add_style(self, idSet):
        self.style_ids = self.style_ids.union(idSet)

    def update_title(self):
        db = database.Database()
        db.updateValue("albums", "title", self.title, "album_id", self.album_id)

    def update_year(self):
        db = database.Database()
        db.updateValue("albums", "year", self.year, "album_id", self.album_id)

    def update_size(self):
        db = database.Database()
        db.updateValue("albums", "size", self.size, "album_id", self.album_id)

    def update_length(self):
        db = database.Database()
        db.updateValue("albums", "length", self.length, "album_id", self.album_id)

    def update(self):
        self.update_title()
        self.update_year()

    def cut_cover_from_path(self, path):
        dest_file = os.path.join(self.get_album_dir(), "cover.jpg")
        if os.path.isfile(dest_file):
            os.replace(path, dest_file)
        else:
            shutil.move(path, dest_file)
        self.cover = "cover.jpg"

    def get_album_size(self):
        size = getFolderSize(self.get_album_dir())
        print(self.title + " size=" + convert_size(self.size))
        if size > 0 and size != self.size:
            self.size = size
            print(self.title + " size=" + convert_size(self.size))
            self.update_size()

    def get_length(self):
        if len(self.tracks) == 0:
            self.get_tracks()
        alb_length = 0
        for trk in self.tracks:
            alb_length += trk.duration

        print("album length=" + str(alb_length))
        if alb_length > 0 and (alb_length != self.length or self.length is None):
            self.length = int(alb_length)
            self.update_length()

    def get_formatted_dir_name(self):
        return "{artist} - [{year}] - {title}".format(
            artist=self.artist_name, year=self.year or "9999", title=self.title
        )


if __name__ == "__main__":
    alb = Album("ACDC - [1975] - TNT")
    print(alb.title)
    alb = Album("ACDC - [1983] - a tribute to")
    print(alb.title)
    alb = Album("ACDC - a tribute to")
    print(alb.get_formatted_dir_name())
