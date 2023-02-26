#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PyQt5 import QtWidgets, QtGui, QtCore
import dialog_music_directories
from music_base import MusicBase
from music_directory import MusicDirectory
from database import Database
from music_genres import MusicGenres
from svg_icon import *
import logging

logger = logging.getLogger(__name__)


class DialogMusicDirectoriesLoader(QtWidgets.QDialog):
    def __init__(self, music_base, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.music_base = music_base
        self.currentDir = None
        self.ui = dialog_music_directories.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window)
        # self.setWindowTitle("PyZik")
        self.ui.wRight.setEnabled(False)

        self.ui.AddButton.clicked.connect(self.on_add_dir)
        self.ui.DeleteButton.clicked.connect(self.on_delete_dir)
        self.ui.DirButton.clicked.connect(self.on_change_dir)
        self.ui.Name.textChanged.connect(self.on_name_changed)
        self.ui.comboStyle.currentIndexChanged.connect(self.on_change_genre)
        self.ui.comboDirType.currentIndexChanged.connect(self.on_change_dir_type)

        self.ui.AddButton.setIcon(get_svg_icon("folder_add.svg"))
        self.ui.DeleteButton.setIcon(get_svg_icon("folder_delete.svg"))

        self.load_dir_list()
        self.show_genres()

    def on_name_changed(self, item):
        self.currentDir.dirName = self.ui.Name.text()

    def on_dir_changed(self, item):
        if self.currentDir is not None:
            self.currentDir.music_base = self.music_base
            self.currentDir.update_music_directory_db()
        sel = self.ui.DirListView.selectionModel().selectedIndexes()

        nrow = item.row()
        model = self.ui.DirListView.model()

        modelitem = model.item(nrow)
        if not modelitem:
            return
        md = modelitem.musicDir
        self.currentDir = md
        self.ui.wRight.setEnabled(True)
        self.ui.Name.set_text(md.dirName)
        self.ui.DirEdit.set_text(md.dir_path)
        print("Current Style ID=", md.styleID)
        print("Current MD ", md.dirName, md.music_directory_id)
        if md.styleID >= 0:
            i = self.ui.comboStyle.findData(md.styleID)
            self.ui.comboStyle.setCurrentIndex(i)
        else:
            self.ui.comboStyle.setCurrentIndex(-1)

        self.ui.comboDirType.setCurrentIndex(md.dirType)

        self.ui.wRight.setEnabled(True)

    def on_add_dir(self):
        success = False
        sDir = self.select_dir()
        if sDir != "":
            md = MusicDirectory(self.music_base, sDir)
            dirName = os.path.basename(sDir)
            print("Add directory " + dirName)
            md.dirName, ok = QtWidgets.QInputDialog.getText(
                self, "Give a name to your directory", "Directory name:", QtWidgets.QLineEdit.EchoMode(), dirName
            )
            if (md.dirName != "") & ok:
                self.music_base.musicDirectoryCol.add_music_directory(md)

                print("Directory=" + sDir + " DirName=" + md.dirName)

                model = self.ui.DirListView.model()
                itemDir = QtGui.QStandardItem(md.dirName)
                itemDir.musicDir = md
                model.appendRow(itemDir)
                index = model.createIndex(model.rowCount() - 1, 0)
                selmodel = self.ui.DirListView.selectionModel()
                selmodel.clear()
                selmodel.select(index, QtCore.QItemSelectionModel.Select)
                self.on_dir_changed(index)

    def on_delete_dir(self):
        indexes = self.ui.DirListView.selectionModel().selectedIndexes()
        model = self.ui.DirListView.model()
        i = indexes[0].row()

        self.music_base.delete_music_directory(self.currentDir)
        model.removeRow(i)

        if i >= model.rowCount() - 1:
            index = model.createIndex(model.rowCount() - 1, 0)
        else:
            index = model.createIndex(i, 0)
        self.ui.DirListView.setModel(model)
        self.ui.DirListView.selectionModel().select(
            index, QtCore.QItemSelectionModel.Select
        )
        self.on_dir_changed(index)

    def on_change_dir(self):
        sDir = self.select_dir()
        self.ui.DirEdit.text = sDir
        self.currentDir.dir_path = sDir

    def on_change_genre(self):
        if self.currentDir is not None:
            currentData = self.ui.comboStyle.currentData()
            if currentData:
                self.currentDir.styleID = currentData
                print("New Genre ID=", self.currentDir.styleID)

    def on_change_dir_type(self):
        if self.currentDir is not None:
            self.currentDir.dirType = self.ui.comboDirType.currentIndex()
            print("New Dir Type ID=", self.currentDir.dirType)

    def select_dir(self):
        return str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))

    def closeEvent(self, event):
        if self.currentDir is not None:
            self.currentDir.music_base = self.music_base
            self.currentDir.update_music_directory_db()

    def load_dir_list(self):
        model = QtGui.QStandardItemModel(self.ui.DirListView)
        for musicDir in self.music_base.musicDirectoryCol.music_directories:
            itemDir = QtGui.QStandardItem(musicDir.dirName)
            itemDir.musicDir = musicDir
            model.appendRow(itemDir)
        self.ui.DirListView.setModel(model)
        self.ui.DirListView.selectionModel().currentChanged.connect(self.on_dir_changed)

    def show_genres(self):
        self.ui.comboStyle.clear()
        for genre in self.music_base.genres.genresTabSorted:
            self.ui.comboStyle.addItem(genre[0], genre[1])


if __name__ == "__main__":
    import sys
    from darkStyle import darkStyle

    app = QtWidgets.QApplication(sys.argv)

    translator = QtCore.QTranslator(app)
    locale = QtCore.QLocale.system().name()

    translator.load("pyzik_%s.qm" % locale)

    app.installTranslator(translator)

    # Load & Set the DarkStyleSheet
    dark = darkStyle.darkStyle()
    app.setStyleSheet(dark.load_stylesheet_pyqt5())

    mb = MusicBase()

    mb.musicDirectoryCol.load_music_directories()

    window = DialogMusicDirectoriesLoader(mb)

    window.show()

    sys.exit(app.exec_())
