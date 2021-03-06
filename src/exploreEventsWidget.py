#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSignal
from directoryWidget import *
from musicDirectory import *
from svgIcon import *
import logging

logger = logging.getLogger(__name__)
_translate = QtCore.QCoreApplication.translate


class ExploreEventsWidget(QtWidgets.QDialog):

    items = ExploreEventList()

    def __init__(self, parent, musicbase=None, items=[]):
        QtWidgets.QDialog.__init__(self)
        self.parent = parent
        self.musicbase = musicbase
        self.items = items
        self.musicbase.db = database()
        self.setWindowFlags(QtCore.Qt.Window)

        self.initUI()


    def initUI(self):
        self.setWindowTitle(_translate("menu", "Explore Events"))
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        self.setSizePolicy(sizePolicy)
        self.resize(550, 400)

        self.header_label = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header_label.sizePolicy().hasHeightForWidth())
        self.main_layout.addWidget(self.header_label)

        # self.from_directory = directoryWidget(self)
        # self.main_layout.addWidget(self.from_directory)

        # self.explore_button = QtWidgets.QPushButton(_translate("explore event", "Explore directory"))
        # self.explore_button.clicked.connect(self.explore_directory)
        # self.explore_button.setIcon(getSvgIcon("folder_search.svg"))
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        # self.explore_button.setSizePolicy(sizePolicy)
        # self.main_layout.addWidget(self.explore_button)
        # self.main_layout.setAlignment(self.explore_button, Qt.AlignHCenter)

        # self.defaut_music_directory = QtWidgets.QComboBox()
        # self.defaut_music_directory.currentIndexChanged.connect(self.on_change_to_directory)
        # self.load_dir_list(self.defaut_music_directory)
        # combo_with_label = QtWidgets.QWidget()
        # combo_layout = QtWidgets.QHBoxLayout(combo_with_label)
        # combo_layout.setContentsMargins(0, 0, 0, 0)
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # sizePolicy.setHorizontalStretch(100)
        # sizePolicy.setVerticalStretch(0)
        # self.defaut_music_directory.setSizePolicy(sizePolicy)
        # self.defaut_music_directory_label = QtWidgets.QLabel(self)
        # combo_layout.addWidget(self.defaut_music_directory_label)
        # combo_layout.addWidget(self.defaut_music_directory)
        # self.main_layout.addWidget(combo_with_label)

        self.initTableWidgetItems()
        self.main_layout.addWidget(self.tableWidgetItems)


        # self.import_button = QtWidgets.QPushButton(_translate("explore event", "Import selected albums in music directories"))
        # self.import_button.clicked.connect(self.import_albums)
        # self.import_button.setIcon(getSvgIcon("folder_import.svg"))
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        # self.import_button.setSizePolicy(sizePolicy)
        # self.main_layout.addWidget(self.import_button)
        # self.main_layout.setAlignment(self.import_button, Qt.AlignHCenter)


        self.retranslateUi()

        self.initColumnHeaders()

        self.showTableItems(self.items)

        self.show_header()

    # def import_albums(self):
    #     alb_dict_list = self.get_albums_dict_list()
    #
    #     self.wProgress = progressWidget(self, can_be_closed=False, with_file_progress=True)
    #     self.wProgress.setProgressLabel(_translate("explore event", "Copying:"))
    #     self.wProgress.show()
    #     self.import_alb_thread = ImportAlbumsThread()
    #     self.import_alb_thread.alb_dict_list = alb_dict_list
    #     self.import_alb_thread.musicbase = self.musicbase
    #     self.import_alb_thread.album_import_progress.connect(self.wProgress.setValue)
    #     self.import_alb_thread.album_import_started_signal.connect(self.wProgress.setDirectoryText)
    #     self.import_alb_thread.file_copy_started_signal.connect(self.wProgress.setFileText)
    #     self.import_alb_thread.import_completed_signal.connect(self.explore_completed)
    #     self.import_alb_thread.start()

    # def explore_completed(self):
    #     self.wProgress.close()
    #     self.explore_directory()

    # def get_albums_dict_list(self):
    #     alb_dict_list = []
    #     for row in range(self.tableWidgetItems.rowCount()):
    #         item = self.tableWidgetItems.item(row, 0)
    #         if item.checkState():
    #             alb_dict = item.alb_item
    #             cell_dir = self.tableWidgetItems.cellWidget(row, 1)
    #             alb_dict['to_dir'] = cell_dir.model().item(cell_dir.currentIndex()).music_dir
    #             alb_dict_list.append(alb_dict)
    #     return alb_dict_list

    # def on_change_to_directory(self, event):
    #     if hasattr(self, 'tableWidgetItems'):
    #         for row in range(self.tableWidgetItems.rowCount()):
    #             cell_dir = self.tableWidgetItems.cellWidget(row, 1)
    #             cell_dir.setCurrentIndex(self.defaut_music_directory.currentIndex())

    def show_header(self):
        self.header_label.setText("Album added: %s" % self.items.count_album_added())

    def toggle_selected_row(self):
        for row in range(self.tableWidgetItems.rowCount()):
            item = self.tableWidgetItems.item(row, 0)
            if item.checkState() == Qt.Unchecked:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    # def explore_directory(self, event):
    #     dir_path = self.from_directory.getText()
    #     if not os.path.isdir(dir_path):
    #         QtWidgets.QMessageBox.warning(self, _translate("directory", "You must select a directory."),
    #                                       _translate("directory", "You must select a directory."),
    #                                       QtWidgets.QMessageBox.Ok)
    #     else:
    #         music_dir = musicDirectory(self.musicbase, dir_path)
    #         res = music_dir.explore_albums_to_import()
    #         for alb in res:
    #             logger.debug(alb)
    #         self.showTableItems(res)

    def load_dir_list(self, combo):
        model = QtGui.QStandardItemModel(combo)
        for music_dir in self.musicbase.musicDirectoryCol.musicDirectories:
            itemDir = QtGui.QStandardItem(music_dir.dirName)
            itemDir.music_dir = music_dir
            model.appendRow(itemDir)
        combo.setModel(model)


    def initTableWidgetItems(self):
        self.tableWidgetItems = QtWidgets.QTableWidget(self)

        self.tableWidgetItems.setGeometry(0, 0, 550, 300)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)

        self.tableWidgetItems.setSizePolicy(sizePolicy)
        self.tableWidgetItems.setMinimumSize(QtCore.QSize(50, 0))
        self.tableWidgetItems.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tableWidgetItems.setObjectName("tableWidgetItems")
        self.tableWidgetItems.setColumnCount(8)
        self.tableWidgetItems.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetItems.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetItems.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetItems.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetItems.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetItems.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetItems.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetItems.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetItems.setHorizontalHeaderItem(7, item)

    def initColumnHeaders(self):
        hHeader = self.tableWidgetItems.horizontalHeader()
        vHeader = self.tableWidgetItems.verticalHeader()
        vHeader.hide()

        # hHeader.resizeSections(QtWidgets.QHeaderView.ResizeToContents)
        # hHeader.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)

        hHeader.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        hHeader.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        hHeader.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
        # self.tableWidgetItems.setColumnHidden(5, True)
        hHeader.sectionClicked.connect(self.toggle_selected_row, Qt.UniqueConnection)

    def retranslateUi(self):
        self.setWindowTitle(_translate("menu", "Explore Events"))
        # self.from_directory.setLabel(_translate("explore event", "From directory"))
        # self.explore_button.setText(_translate("explore event", "Explore directory"))
        # self.import_button.setText(_translate("explore event", "Import selected albums in music directories"))
        # self.to_directory.setLabel(_translate("explore event", "To directory"))
        # self.defaut_music_directory_label.setText(_translate("explore event", "To directory"))

        item = self.tableWidgetItems.horizontalHeaderItem(0)
        item.setText("")
        item = self.tableWidgetItems.horizontalHeaderItem(1)
        item.setText(_translate("explore event", "To directory"))
        item = self.tableWidgetItems.horizontalHeaderItem(2)
        item.setText(_translate("pyzik", "Artist"))
        item = self.tableWidgetItems.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Album"))
        item = self.tableWidgetItems.horizontalHeaderItem(4)
        item.setText(_translate("album", "Year"))
        item = self.tableWidgetItems.horizontalHeaderItem(5)
        item.setText(_translate("directory", "Directory"))
        item = self.tableWidgetItems.horizontalHeaderItem(6)
        item.setText(_translate("explore event", "Exists"))
        item = self.tableWidgetItems.horizontalHeaderItem(7)
        item.setText(_translate("explore event", "Read Tags"))

    def add_item_to_line(self, line, col, item):
        self.tableWidgetItems.setItem(line, col, item)
        return col + 1

    def showTableItems(self, items):
        items = items.filter_exclude_code("ALBUM_ADDED")
        self.tableWidgetItems.setStyleSheet("selection-background-color: black;selection-color: white;")
        # self.tableWidgetItems.setColumnCount(4)
        self.tableWidgetItems.setRowCount(0)

        for i, item in enumerate(items):
            self.tableWidgetItems.insertRow(i)
            i_col = 0

            item_sel = QtWidgets.QTableWidgetItem()
            item_sel.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
            item_sel.setCheckState(QtCore.Qt.Checked)
            item_sel.alb_item = item
            i_col = self.add_item_to_line(i, i_col, item_sel)
            # self.tableWidgetItems.setItem(i, 0, item_sel)

            item_code = QtWidgets.QTableWidgetItem(item.event_code)
            item_code.setFlags(item_code.flags() ^ QtCore.Qt.ItemIsEditable)
            # self.tableWidgetItems.setItem(i, 0, item_code)
            i_col = self.add_item_to_line(i, i_col, item_code)

            item_path = QtWidgets.QTableWidgetItem(item.dirPath)
            item_path.setFlags(item_path.flags() ^ QtCore.Qt.ItemIsEditable)
            # self.tableWidgetItems.setItem(i, 1, item_path)
            i_col = self.add_item_to_line(i, i_col, item_path)

            if item.album:
                item_artist = QtWidgets.QTableWidgetItem(item.album.artist_name)
                item_artist.setFlags(item_artist.flags() ^ QtCore.Qt.ItemIsEditable)
                # self.tableWidgetItems.setItem(i, 2, item_artist)
                i_col = self.add_item_to_line(i, i_col, item_artist)

                item_title = QtWidgets.QTableWidgetItem(item.album.title)
                item_title.setFlags(item_title.flags() ^ QtCore.Qt.ItemIsEditable)
                # self.tableWidgetItems.setItem(i, 3, item_title)
                i_col = self.add_item_to_line(i, i_col, item_title)

                item_year = QtWidgets.QTableWidgetItem(str(item.album.year))
                item_year.setFlags(item_year.flags() ^ QtCore.Qt.ItemIsEditable)
                # self.tableWidgetItems.setItem(i, 4, item_year)
                i_col = self.add_item_to_line(i, i_col, item_year)

            # selItem = QtWidgets.QTableWidgetItem()
            # selItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
            # selItem.setCheckState(QtCore.Qt.Checked)
            # selItem.alb_item = item
            # self.tableWidgetItems.setItem(i, 0, selItem)
            #
            # combo_music_directory = QtWidgets.QComboBox()
            # combo_music_directory.wheelEvent = lambda event: None
            # self.load_dir_list(combo_music_directory)
            # combo_music_directory.setCurrentIndex(self.defaut_music_directory.currentIndex())
            # self.tableWidgetItems.setCellWidget(i, 1, combo_music_directory)
            #
            # artistItem = QtWidgets.QTableWidgetItem(item['alb'].artist_name)
            # artistItem.setFlags(artistItem.flags() ^ QtCore.Qt.ItemIsEditable)
            # self.tableWidgetItems.setItem(i, 2, artistItem)
            #
            # albumItem = QtWidgets.QTableWidgetItem(item['alb'].title)
            # albumItem.setFlags(albumItem.flags() ^ QtCore.Qt.ItemIsEditable)
            # self.tableWidgetItems.setItem(i, 3, albumItem)
            #
            #
            # yearItem = QtWidgets.QTableWidgetItem(str(item['alb'].year))
            # yearItem.setFlags(yearItem.flags() ^ QtCore.Qt.ItemIsEditable)
            # self.tableWidgetItems.setItem(i, 4, yearItem)
            #
            # dirItem = QtWidgets.QTableWidgetItem(item['album_dir'])
            # dirItem.setFlags(dirItem.flags() ^ QtCore.Qt.ItemIsEditable)
            # self.tableWidgetItems.setItem(i, 5, dirItem)
            #
            #
            # albumExistItem = QtWidgets.QCheckBox()
            # albumExistItem.setTristate(False)
            # set_check_state(albumExistItem, item['album_exists'])
            #
            # albumExistItem.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            # albumExistItem.sizePolicy().setHorizontalStretch(100)
            # albumExistItem.setMaximumSize(100, 200)
            # albumExistItem.mouseReleaseEvent = lambda event: None
            # albumExistItem.setStyleSheet("background-color: rgba(0, 0, 0, 0.0);")
            # self.tableWidgetItems.setCellWidget(i, 6, albumExistItem)
            #
            # check_tags_button = QtWidgets.QPushButton()
            # check_tags_button.alb_item = item
            # check_tags_button.clicked.connect(self.check_tags)
            # check_tags_button.setIcon(getSvgIcon("lightning2.svg"))
            # self.tableWidgetItems.setCellWidget(i, 7, check_tags_button)

        hHeader = self.tableWidgetItems.horizontalHeader()
        hHeader.resizeSections(QtWidgets.QHeaderView.ResizeToContents)
        hHeader.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)


    def check_tags(self, event):
        check_tags_button = self.tableWidgetItems.focusWidget()
        index = self.tableWidgetItems.indexAt(check_tags_button.pos())
        row = index.row()
        logger.info(row)
        alb = check_tags_button.alb_item['alb']
        alb.getTagsFromFirstFile()
        curArt = self.musicbase.artistCol.findArtists(alb.artist_name)
        # GetArtist return a new artist if it doesn't exists in artistsCol
        if len(curArt) == 1:
            curArt = curArt[0]
            alb.artistID = curArt.artistID
            alb.artist_name = curArt.name.upper()
            albums = curArt.findAlbums(alb.title)
            album_exists = len(albums) > 0
            albumExistItem = self.tableWidgetItems.cellWidget(row, 6)
            set_check_state(albumExistItem, album_exists)

        artistItem = self.tableWidgetItems.item(row, 2)
        albumItem = self.tableWidgetItems.item(row, 3)
        yearItem = self.tableWidgetItems.item(row, 4)
        artistItem.setText(alb.artist_name)
        albumItem.setText(alb.title)
        yearItem.setText(str(alb.year))
        logger.info("%s - %s", alb.artist_name, alb.title)


if __name__ == "__main__":
    import sys
    from pyzik import *
    from musicBase import *

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(darkStyle.darkStyle.load_stylesheet_pyqt5())
    mb = musicBase()
    mb.loadMusicBase()

    importWidget = ExploreEventsWidget(app, mb)
    # importWidget.from_directory.setText('/home/mperrocheau/Documents/TEST')

    importWidget.show()
    sys.exit(app.exec_())
