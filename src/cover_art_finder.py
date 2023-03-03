#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ast import literal_eval
import urllib.request
from urllib.parse import quote

import logging

logger = logging.getLogger(__name__)


class CoverArtFinder:
    """Find URL of cover art jpg"""

    items = []

    def search(self, search_keyword):
        self.items = []
        params = [(20, "large"), (20, "medium")]

        for param in params:
            items = self.search_with_param(search_keyword, param[0], param[1])
            if items:
                self.items = self.items + items
        logger.debug("CoverArtFinder items %s", self.items)

    def search_with_param(self, search_keyword, limit=0, size="medium"):
        arguments = {'language': False, 'format': 'jpg', "keywords": search_keyword,
                     "limit": limit, "size": size, "aspect_ratio": "square"}
        url = self.search_url(search_keyword, arguments)
        return self.get_google_result(url, limit=limit)

    def get_google_result(self, url, limit=0):
        try:
            headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}
            req = urllib.request.Request(url, headers=headers)
            res = urllib.request.urlopen(req)
            result = str(res.read().decode('utf-8'))
            return self.get_images_from_result(result, limit)
        except Exception as err:
            logger.error(err)
            pass

    def get_images_from_result(self, result, limit=0):
        data_start = 'AF_initDataCallback('
        start_line = result.find(data_start)
        end_object = result.find(');</script>', start_line + 1)
        start_line = result.find(data_start, end_object)
        end_object = result.find(');</script>', start_line + 1)
        object_raw = str(result[start_line + len(data_start):end_object])
        str_data = object_raw.replace('key:', "'key':").replace('data:', "'data':").replace('hash:', "'hash':").replace('null', 'None')
        str_data = str_data.replace('true', 'True').replace('false', 'False').replace('sideChannel', '"sideChannel"')
        datas = literal_eval(str_data)
        dict_list = self.get_dict_in_list(datas.get('data', []))
        image_list = self.images_from_datas(dict_list)
        if limit:
            image_list = image_list[:limit]

        return image_list

    def get_dict_in_list(self, data_list):
        dict_list = []
        for data in data_list:
            if isinstance(data, list):
                dict_list.extend(self.get_dict_in_list(data))
            if isinstance(data, dict):
                dict_list.append(data)
        return dict_list

    def images_from_datas(self, datas):
        images = []
        if isinstance(datas, list):
            data_image = {}
            for data in datas:
                if isinstance(data, dict):
                    if len(data.keys()) == 1:
                        data_list = data[list(data.keys())[0]]
                        images.extend(self.images_from_datas(data_list))

                if isinstance(data, list):
                    if len(data) == 3 and isinstance(data[0], str):
                        if not data_image:
                            data_image['thumbnail'] = data
                            data_image["image_thumbnail_url"] = data[0]
                        else:
                            data_image['image'] = data
                            data_image["image_link"] = data[0]
                            data_image["image_height"] = data[1]
                            data_image["image_width"] = data[2]
                    else:
                        if data:
                            images.extend(self.images_from_datas(data))
            if data_image:
                images.append(data_image)
        return images

    def get_url_parameters(self, arguments):
        param_url = ''

        params = {'size': [arguments['size'],
                           {'large': 'isz:l', 'medium': 'isz:m', 'icon': 'isz:i'}],
                  'aspect_ratio': [arguments['aspect_ratio'],
                                   {'tall': 'iar:t', 'square': 'iar:s', 'wide': 'iar:w', 'panoramic': 'iar:xw'}],
                  'format': [arguments['format'],
                             {'jpg': 'ift:jpg', 'gif': 'ift:gif', 'png': 'ift:png', 'bmp': 'ift:bmp', 'svg': 'ift:svg',
                              'webp': 'webp', 'ico': 'ift:ico', 'raw': 'ift:craw'}]}

        for key, value in params.items():
            if value[0]:
                ext_param = value[1][value[0]]
                if param_url:
                    param_url = param_url + ',' + ext_param
                else:
                    param_url = param_url + ext_param
        return "&tbs=" + param_url

    def search_url(self, search_term, arguments):
        params = self.get_url_parameters(arguments)
        url = 'https://www.google.com/search?q=' + quote(
            search_term.encode(
                'utf-8')) + '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch' + params + '&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg'

        return url


if __name__ == "__main__":
    import sys

    from PyQt5 import QtWidgets
    from cover_art_finder_dialog import CoverArtFinderDialog

    app = QtWidgets.QApplication(sys.argv)

    keyword = "jerusalem album 1972"

    caf_diag = CoverArtFinderDialog()
    caf_diag.keyword = keyword

    caf_diag.show()

    sys.exit(app.exec_())
