#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import unicodedata

"""
Usefull functions to format titles, dir name...
"""


def deleteAccent(value):
    return str(unicodedata.normalize('NFD', value).encode('ascii', 'ignore'))


def simplifiedString(value):
    res = value.replace("THE ", "")
    res = res.replace("&", "AND")

    return res


def deletePonctuation(value):
    return re.sub('\W+', '', value)


def getSearchKey(value):
    res = value
    res = simplifiedString(res)
    res = deleteAccent(res)
    res = deletePonctuation(res)
    res = res.replace(" ", "")
    return res
