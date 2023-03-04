#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shutil
import glob
import os
import subprocess
import sys
import logging
import time
import math

logger = logging.getLogger(__name__)


def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])


def move_directory_file_by_file(
    from_path, to_path, file_copy_started_signal=None, test_mode=False
):
    if not test_mode:
        os.makedirs(to_path)
    files = glob.glob(
        glob.escape(from_path + os.sep) + "**" + os.sep + "*.*", recursive=True
    )
    files = sorted(files)
    logger.info("FILES %s in %s", files, from_path)
    for file in files:
        if file_copy_started_signal:
            file_copy_started_signal.emit(os.path.basename(file))
        if test_mode:
            time.sleep(1)
        else:
            shutil.move(file, to_path)
    if not test_mode:
        os.rmdir(from_path)


def get_folder_size(folder):
    if not os.path.isdir(folder):
        return 0
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        item_path = os.path.join(folder, item)
        if os.path.isfile(item_path):
            total_size += os.path.getsize(item_path)
        elif os.path.isdir(item_path):
            total_size += get_folder_size(item_path)
    return total_size


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def get_file_name(path):
    filename = os.path.basename(path)
    filename, file_extension = os.path.splitext(filename)
    return filename
