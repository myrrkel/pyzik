#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from explore_event import ExploreEventList
from import_albums_widget import set_check_state
from database import Database
import logging

logger = logging.getLogger(__name__)
_translate = QtCore.QCoreApplication.translate


class ExploreEventsWidget(QtWidgets.QDialog):
    items = ExploreEventList()

    def __init__(self, parent, music_base=None, items=[]):
        QtWidgets.QDialog.__init__(self)
        self.parent = parent
        self.music_base = music_base
        self.items = items
        self.music_base.db = Database()
        self.setWindowFlags(QtCore.Qt.Window)

        self.initUI()

    def initUI(self):
        self.setWindowTitle(_translate("menu", "Explore Events"))
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        self.setSizePolicy(sizePolicy)
        self.resize(550, 400)

        self.header_label = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header_label.sizePolicy().hasHeightForWidth())
        self.main_layout.addWidget(self.header_label)

        self.init_table_widget_items()
        self.main_layout.addWidget(self.tableWidgetItems)

        self.retranslateUi()

        self.init_column_headers()
        if self.items:
            self.show_table_items(self.items)
            self.show_header()

    def show_header(self):
        self.header_label.setText("Album added: %s" % self.items.count_album_added())

    def toggle_selected_row(self):
        for row in range(self.tableWidgetItems.rowCount()):
            item = self.tableWidgetItems.item(row, 0)
            if item.checkState() == Qt.Unchecked:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def load_dir_list(self, combo):
        model = QtGui.QStandardItemModel(combo)
        for music_dir in self.music_base.music_directory_col.music_directories:
            item_dir = QtGui.QStandardItem(music_dir.directory_name)
            item_dir.music_dir = music_dir
            model.appendRow(item_dir)
        combo.setModel(model)

    def init_table_widget_items(self):
        self.tableWidgetItems = QtWidgets.QTableWidget(self)

        self.tableWidgetItems.setGeometry(0, 0, 550, 300)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
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

    def init_column_headers(self):
        horizontal_header = self.tableWidgetItems.horizontalHeader()
        vertical_header = self.tableWidgetItems.verticalHeader()
        vertical_header.hide()

        # horizontal_header.resizeSections(QtWidgets.QHeaderView.ResizeToContents)
        # horizontal_header.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)

        horizontal_header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        horizontal_header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        horizontal_header.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
        # self.tableWidgetItems.setColumnHidden(5, True)
        horizontal_header.sectionClicked.connect(self.toggle_selected_row, QtCore.Qt.UniqueConnection)

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

    def show_table_items(self, items):
        items = items.filter_exclude_code("ALBUM_ADDED")
        self.tableWidgetItems.setStyleSheet(
            "selection-background-color: black;selection-color: white;"
        )
        # self.tableWidgetItems.setColumnCount(4)
        self.tableWidgetItems.setRowCount(0)

        for i, item in enumerate(items):
            self.tableWidgetItems.insertRow(i)
            i_col = 0

            item_sel = QtWidgets.QTableWidgetItem()
            item_sel.setFlags(
                QtCore.Qt.ItemIsUserCheckable
                | QtCore.Qt.ItemIsEditable
                | QtCore.Qt.ItemIsEnabled
            )
            item_sel.setCheckState(QtCore.Qt.Checked)
            item_sel.alb_item = item
            i_col = self.add_item_to_line(i, i_col, item_sel)
            # self.tableWidgetItems.setItem(i, 0, item_sel)

            item_code = QtWidgets.QTableWidgetItem(item.event_code)
            item_code.setFlags(item_code.flags() ^ QtCore.Qt.ItemIsEditable)
            # self.tableWidgetItems.setItem(i, 0, item_code)
            i_col = self.add_item_to_line(i, i_col, item_code)

            item_path = QtWidgets.QTableWidgetItem(item.dir_path)
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

        hHeader = self.tableWidgetItems.horizontalHeader()
        hHeader.resizeSections(QtWidgets.QHeaderView.ResizeToContents)
        hHeader.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)

    def check_tags(self, event):
        check_tags_button = self.tableWidgetItems.focusWidget()
        index = self.tableWidgetItems.indexAt(check_tags_button.pos())
        row = index.row()
        logger.info(row)
        alb = check_tags_button.alb_item["alb"]
        alb.getTagsFromFirstFile()
        artist = self.music_base.artist_col.findArtists(alb.artist_name)
        # GetArtist return a new artist if it doesn't exists in artistsCol
        if len(artist) == 1:
            artist = artist[0]
            alb.artist_id = artist.artist_id
            alb.artist_name = artist.name.upper()
            albums = artist.find_albums(alb.title)
            album_exists = len(albums) > 0
            album_exist_item = self.tableWidgetItems.cellWidget(row, 6)
            set_check_state(album_exist_item, album_exists)

        artist_item = self.tableWidgetItems.item(row, 2)
        album_item = self.tableWidgetItems.item(row, 3)
        year_item = self.tableWidgetItems.item(row, 4)
        artist_item.setText(alb.artist_name)
        album_item.setText(alb.title)
        year_item.setText(str(alb.year_to_num))
        logger.info("%s - %s", alb.artist_name, alb.title)


if __name__ == "__main__":
    import sys
    from pyzik import *
    from music_base import MusicBase

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    mb = MusicBase()
    mb.load_music_base()

    importWidget = ExploreEventsWidget(app, mb)
    # importWidget.from_directory.setText('/home/mperrocheau/Documents/TEST')

    importWidget.show()
    sys.exit(app.exec_())
