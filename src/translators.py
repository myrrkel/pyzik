#!/usr/bin/env python3translation
# -*- coding: utf-8 -*-


from PyQt5 import QtCore
from src import APP_DIR


class Translators:
    def __init__(self, app):
        self.app = app
        self.installed_translators = []

    def install_translator(self, filename, locale):
        translator = QtCore.QTranslator(self.app)
        translator.load(APP_DIR + "/translation/{0}_{1}.qm".format(filename, locale))
        self.installed_translators.append(translator)
        self.app.installTranslator(translator)

    def un_install_translators(self):
        for translator in self.installed_translators:
            self.app.removeTranslator(translator)
        self.installed_translators = []

    def install_translators(self, locale):
        self.install_translator("pyzik", locale)
        self.install_translator("playlistWidget", locale)
        self.install_translator("historyWidget", locale)
        self.install_translator("customWidget", locale)
        self.install_translator("widgets", locale)
