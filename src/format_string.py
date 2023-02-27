#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import unicodedata

"""
Useful functions to format titles, dir name...
"""


def delete_accent(value):
    return str(unicodedata.normalize("NFD", value).encode("ascii", "ignore"))


def simplified_string(value):
    res = value.replace("THE ", "")
    res = res.replace("&", "AND")

    return res


def delete_ponctuation(value):
    return re.sub("\W+", "", value)


def get_search_key(value):
    res = value.strip().upper()
    res = simplified_string(res)
    res = delete_accent(res)
    res = delete_ponctuation(res)
    res = res.replace(" ", "")
    return res
