#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from typing import List
import fnmatch
from track import Track
import database
from files_utils import *
from src import utils, IMAGE_FILE_EXTENSIONS, MUSIC_FILE_EXTENSIONS

import format_string
import logging

logger = logging.getLogger(__name__)


def keyword_not_back(image, keyword):
    name = get_file_name(image.lower())
    return keyword in name and 'back' not in name


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

    final = [utils.capitalise_word(word_list[0])]
    for word in word_list[1:]:
        if str.lower(word) in exceptions:
            final.append(word.lower())
        else:
            final.append(utils.capitalise_word(word))
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

    def __init__(self, dir_name="", music_directory=None):
        self.album_id = 0
        self.title = ""
        self.dir_name = dir_name
        self.dir_path = dir_name
        self.artist_id = ""
        self.artist_name = ""
        self.year = 0
        self.cover = ""
        self.size = 0
        self.length = 0
        self.to_verify = False
        self.tracks: List[Track] = list()
        self.images = []
        self.style_ids = set()
        self.do_stop = False
        self.music_directory = music_directory
        self.cover_pixmap = None  # QPixmap()
        self.cover_saved = False
        if music_directory:
            self.music_directory_id = music_directory.music_directory_id
        else:
            self.music_directory_id = 0
        self.searchKey = ""

        if dir_name != "":
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
            self.searchKey = format_string.get_search_key(self.title.upper())
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
            if not (res_val.isdigit() and utils.is_year(res_val)):
                return False
            else:
                res_val = utils.year_to_num(res_val)

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

        if utils.is_year(self.artist_name) or not self.title or not self.artist_name:
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
        self.do_stop = False
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

        for file in files:
            if self.do_stop:
                break
            file = str(file)
            if os.path.isdir(os.path.join(current_dir, file)):
                # file is a directory
                logger.debug("get_tracks() sub dir: %s ; %s", subdir, file)
                res = self.get_tracks(os.path.join(subdir, file),
                                      first_file_only=first_file_only)
            else:
                for ext in MUSIC_FILE_EXTENSIONS:
                    if fnmatch.fnmatch(file.lower(), "*." + ext):
                        if "." in file:
                            filename, file_extension = os.path.splitext(file)
                            track = Track(filename, file_extension, subdir)
                            track.path = current_dir
                            track.parentAlbum = self

                            if first_file_only:
                                track.get_mutagen_tags(self.get_album_dir())
                                self.tracks.append(track)
                                return track
                            else:
                                track.get_mutagen_tags(self.get_album_dir())
                                self.tracks.append(track)
                            break
        return res

    def get_images(self, subdir=""):
        images = []
        subdir_images = []
        self.do_stop = False
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
            if self.do_stop:
                break
            if os.path.isdir(os.path.join(current_dir, str(file))):
                # file is a directory
                subdir_images.extend(self.get_images(os.path.join(subdir, file)))
            else:
                if file == "cover":
                    os.rename(
                        os.path.join(current_dir, file),
                        os.path.join(current_dir, "cover.jpg"),
                    )

                for ext in IMAGE_FILE_EXTENSIONS:
                    if fnmatch.fnmatch(file.lower(), "*." + ext):
                        file_name = os.path.join(current_dir, file)
                        images.append(file_name)
                        break
        images.extend(subdir_images)
        self.images = images
        return images

    def get_cover(self):
        if not self.images:
            self.cover = self.get_pic_from_tags()
            return

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

        for keyword in keywords:
            for image in self.images:
                if keyword == get_file_name(image.lower()):
                    self.cover = image
                    return

        for keyword in keywords:
            for image in self.images:
                if keyword_not_back(image, keyword):
                    self.cover = image
                    return

        if not self.cover:
            self.cover = self.images[0]

    def get_cover_path(self):
        return os.path.join(self.get_album_dir(), self.cover)

    def check_dir(self):
        if self.music_directory:
            alb_dir = self.get_album_dir()
            if alb_dir:
                return os.path.exists(alb_dir)
        else:
            return False

    def set_do_stop(self):
        self.do_stop = True

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

    def add_style(self, id_set):
        self.style_ids = self.style_ids.union(id_set)

    def update_title(self):
        db = database.Database()
        db.update_value("albums", "title", self.title, "albumID", self.album_id)

    def update_year(self):
        db = database.Database()
        db.update_value("albums", "year", self.year, "albumID", self.album_id)

    def update_size(self):
        db = database.Database()
        db.update_value("albums", "size", self.size, "albumID", self.album_id)

    def update_length(self):
        db = database.Database()
        db.update_value("albums", "length", self.length, "albumID", self.album_id)

    def update(self):
        self.update_title()
        self.update_year()

    def cut_cover_from_path(self, path):
        dest_file = os.path.join(self.get_album_dir(), "cover.jpg")
        if os.path.isfile(dest_file):
            os.remove(dest_file)
        shutil.move(path, dest_file)
        self.cover = "cover.jpg"

    def get_album_size(self):
        size = get_folder_size(self.get_album_dir())
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
