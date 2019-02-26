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


        response = gid.googleimagesdownload()   #class instantiation

        records = gid.user_input()

        limit = 4
        main_directory = ""
        dir_name = ""

        arguments = records[0]
        arguments["keywords"]       = keyword
        arguments["no_download"]    = True
        arguments["limit"]          = limit
        arguments["size"]           = "large"
        arguments["print_urls"]     = True
        arguments["thumbnail"]      = True
        arguments["aspect_ratio"]   = "square"

        print(records[0])



        #arguments = {"keywords":keyword,"no_download":True,"limit":4,"size":"large","print_urls":True,"thumbnail":True,"aspect_ratio":"square"}   #creating list of arguments
        

        params = response.build_url_parameters(arguments)     #building URL with params

        url = response.build_search_url(keyword,params,arguments['url'],arguments['similar_images'],arguments['specific_site'],arguments['safe_search'])      #building main search url

        raw_html = response.download_page(url)  # download page

        items,errorCount,abs_path = response._get_all_items(raw_html,main_directory,dir_name,limit,arguments)    #get all image items and download images
        
        self.items = items

        print(items)

        #paths = response.download(arguments)   #passing the arguments to the function
        #print(paths)   #printing absolute paths of the downloaded images
    


if __name__ == '__main__':

    import sys
    from thumbnailViewerWidget import *

    app = QApplication(sys.argv)
    caf = CoverArtFinder()
    caf.search("jerusalem 1972 she came like a bat from hell")

    thumbViewer = thumbnailViewerWidget(caf.items)
    thumbViewer.show()


    sys.exit(app.exec_())