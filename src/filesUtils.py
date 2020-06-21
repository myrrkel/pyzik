#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shutil
import glob
import os
import logging
import time

logger = logging.getLogger(__name__)


def move_directory_file_by_file(from_path, to_path, file_copy_started_signal=None, test_mode=False):

    if not test_mode:
        os.makedirs(to_path)
    files = glob.glob(glob.escape(from_path + os.sep) + "**" + os.sep + "*.*", recursive=True)
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
