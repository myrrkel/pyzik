#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import requests

# from google_images_download import google_images_download as gid  # importing the library
from google_images_download import googleimagesdownload as gid  # importing the library
from google_images_download import user_input as gid_user_input  # importing the library
import logging

logger = logging.getLogger(__name__)


class CoverArtFinder:
    """Find URL of cover art jpg"""

    items = []

    def search(self, search_keyword):
        params = [(4, "large"), (8, "medium")]

        for param in params:
            items = self.searchWithParam(search_keyword, param[0], param[1])
            if items:
                self.items = self.items + items
        logger.debug("CoverArtFinder items %s", self.items)

    def searchWithParam(self, search_keyword, limit=4, size="medium"):
        response = gid()  # class instantiation

        records = gid_user_input()

        main_directory = ""
        dir_name = ""

        arguments = records[0]
        arguments["keywords"] = search_keyword
        arguments["no_download"] = True
        arguments["limit"] = limit
        arguments["size"] = size
        arguments["print_urls"] = False
        arguments["thumbnail"] = True
        arguments["aspect_ratio"] = "square"

        params = response.build_url_parameters(arguments)  # building URL with params

        url = response.build_search_url(
            search_keyword,
            params,
            arguments["url"],
            arguments["specific_site"],
            arguments["safe_search"],
        )  # building main search url

        try:
            raw_html = response.download_page(url)  # download page
        except Exception as e:
            print(e)
            return False

        items, errorCount, abs_path = response._get_all_items(
            raw_html, main_directory, dir_name, limit, arguments
        )  # get all image items and download images

        return items


if __name__ == "__main__":
    import sys
    import pyzik
    from PyQt5 import QtCore, QtGui, QtWidgets
    from coverArtFinderDialog import *

    app = QApplication(sys.argv)

    keyword = "jerusalem album 1972"
    keyword = "IN FLAMES Clayman"

    caf_diag = CoverArtFinderDialog()
    caf_diag.keyword = keyword

    caf_diag.show()

    sys.exit(app.exec_())
