#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PyQt5 import QtWidgets, QtGui, QtCore
import dialogMusicDirectories
from musicBase import MusicBase
from musicDirectory import MusicDirectory
from database import Database
from musicGenres import MusicGenres
from svgIcon import *
import logging

logger = logging.getLogger(__name__)


class DialogMusicDirectoriesLoader(QtWidgets.QDialog):
    def __init__(self, music_base, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.music_base = music_base
        self.currentDir = None
        self.ui = dialogMusicDirectories.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window)
        # self.setWindowTitle("PyZik")
        self.ui.wRight.setEnabled(False)

        self.ui.AddButton.clicked.connect(self.onAddDir)
        self.ui.DeleteButton.clicked.connect(self.onDeleteDir)
        self.ui.DirButton.clicked.connect(self.onChangeDir)
        self.ui.Name.textChanged.connect(self.onNameChanged)
        self.ui.comboStyle.currentIndexChanged.connect(self.onChangeGenre)
        self.ui.comboDirType.currentIndexChanged.connect(self.onChangeDirType)

        self.ui.AddButton.setIcon(getSvgIcon("folder_add.svg"))
        self.ui.DeleteButton.setIcon(getSvgIcon("folder_delete.svg"))

        self.loadDirList()
        self.showGenres()

    def onNameChanged(self, item):
        self.currentDir.dirName = self.ui.Name.text()

    def onDirChanged(self, item):
        if self.currentDir is not None:
            self.currentDir.music_base = self.music_base
            self.currentDir.updateMusicDirectoryDB()
        sel = self.ui.DirListView.selectionModel().selectedIndexes()

        nrow = item.row()
        model = self.ui.DirListView.model()

        modelitem = model.item(nrow)
        if not modelitem:
            return
        md = modelitem.musicDir
        self.currentDir = md
        self.ui.wRight.setEnabled(True)
        self.ui.Name.setText(md.dirName)
        self.ui.DirEdit.setText(md.dirPath)
        print("Current Style ID=", md.styleID)
        print("Current MD ", md.dirName, md.musicDirectoryID)
        if md.styleID >= 0:
            i = self.ui.comboStyle.findData(md.styleID)
            self.ui.comboStyle.setCurrentIndex(i)
        else:
            self.ui.comboStyle.setCurrentIndex(-1)

        self.ui.comboDirType.setCurrentIndex(md.dirType)

        self.ui.wRight.setEnabled(True)

    def onAddDir(self):
        success = False
        sDir = self.selectDir()
        if sDir != "":
            md = MusicDirectory(self.music_base, sDir)
            dirName = os.path.basename(sDir)
            print("Add directory " + dirName)
            md.dirName, ok = QtWidgets.QInputDialog.getText(
                self, "Give a name to your directory", "Directory name:", False, dirName
            )
            if (md.dirName != "") & ok:
                self.music_base.musicDirectoryCol.addMusicDirectory(md)

                print("Directory=" + sDir + " DirName=" + md.dirName)

                model = self.ui.DirListView.model()
                itemDir = QtGui.QStandardItem(md.dirName)
                itemDir.musicDir = md
                model.appendRow(itemDir)
                index = model.createIndex(model.rowCount() - 1, 0)
                selmodel = self.ui.DirListView.selectionModel()
                selmodel.clear()
                selmodel.select(index, QtCore.QItemSelectionModel.Select)
                self.onDirChanged(index)

    def onDeleteDir(self):
        indexes = self.ui.DirListView.selectionModel().selectedIndexes()
        model = self.ui.DirListView.model()
        i = indexes[0].row()

        self.music_base.deleteMusicDirectory(self.currentDir)
        model.removeRow(i)

        if i >= model.rowCount() - 1:
            index = model.createIndex(model.rowCount() - 1, 0)
        else:
            index = model.createIndex(i, 0)
        self.ui.DirListView.setModel(model)
        self.ui.DirListView.selectionModel().select(
            index, QtCore.QItemSelectionModel.Select
        )
        self.onDirChanged(index)

    def onChangeDir(self):
        sDir = self.selectDir()
        self.ui.DirEdit.text = sDir
        self.currentDir.dirPath = sDir

    def onChangeGenre(self):
        if self.currentDir is not None:
            currentData = self.ui.comboStyle.currentData()
            if currentData:
                self.currentDir.styleID = currentData
                print("New Genre ID=", self.currentDir.styleID)

    def onChangeDirType(self):
        if self.currentDir is not None:
            self.currentDir.dirType = self.ui.comboDirType.currentIndex()
            print("New Dir Type ID=", self.currentDir.dirType)

    def selectDir(self):
        sDir = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        return sDir

    def closeEvent(self, event):
        if self.currentDir is not None:
            self.currentDir.music_base = self.music_base
            self.currentDir.updateMusicDirectoryDB()

    def loadDirList(self):
        model = QtGui.QStandardItemModel(self.ui.DirListView)
        for musicDir in self.music_base.musicDirectoryCol.musicDirectories:
            itemDir = QtGui.QStandardItem(musicDir.dirName)
            itemDir.musicDir = musicDir
            model.appendRow(itemDir)
        self.ui.DirListView.setModel(model)
        self.ui.DirListView.selectionModel().currentChanged.connect(self.onDirChanged)

    def showGenres(self):
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
    app.setStyleSheet(darkStyle.darkStyle.load_stylesheet_pyqt5())

    mb = MusicBase()

    mb.musicDirectoryCol.loadMusicDirectories()

    window = DialogMusicDirectoriesLoader(mb)

    window.show()

    sys.exit(app.exec_())
