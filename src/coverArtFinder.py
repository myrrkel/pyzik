#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import requests

from google_images_download import google_images_download as gid   #importing the library




class CoverArtFinder:
    """Find URL of cover art jpg"""

    items = []


    def search(self,keyword):
        params = [(4,"large"), (8,"medium")]

        for param in params:
            items = self.searchWithParam(keyword,param[0],param[1])
            if items:
                self.items |= items


    def searchWithParam(self,keyword,limit=4,size="medium"):

        response = gid.googleimagesdownload()   #class instantiation

        records = gid.user_input()

        main_directory = ""
        dir_name = ""

        arguments = records[0]
        arguments["keywords"]       = keyword
        arguments["no_download"]    = True
        arguments["limit"]          = limit
        arguments["size"]           = size
        arguments["print_urls"]     = False
        arguments["thumbnail"]      = True
        arguments["aspect_ratio"]   = "square"

        params = response.build_url_parameters(arguments)     #building URL with params

        url = response.build_search_url(keyword, params, arguments['url'], arguments['similar_images'], arguments['specific_site'], arguments['safe_search'])      #building main search url

        try:
            raw_html = response.download_page(url)  # download page
        except Exception as e:
            print(e)
            return False


        items, errorCount, abs_path = response._get_all_items(raw_html, main_directory, dir_name, limit, arguments)    #get all image items and download images

        return items

        

        #paths = response.download(arguments)   #passing the arguments to the function
        #print(paths)   #printing absolute paths of the downloaded images
    


if __name__ == '__main__':

    import sys
    from coverArtFinderDialog import *

    app = QApplication(sys.argv)

    keyword = "jerusalem 1972"
    caf = CoverArtFinder()
    caf.search(keyword)

    caf_diag = coverArtFinderDialog()
    caf_diag.keyword = keyword

    caf_diag.show()


    sys.exit(app.exec_())