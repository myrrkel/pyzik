#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from src.radio_manager import RadioManager
from src.search_radio_thread import SearchRadioThread
import src.svg_icon as svg
from .progress_widget import ProgressWidget
from .wait_overlay_widget import WaitOverlay


class SearchControlsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        _translate = QtCore.QCoreApplication.translate

        self.searchEdit = QtWidgets.QLineEdit()
        self.searchEdit.setText("")

        self.searchButton = QtWidgets.QPushButton("Search")
        self.searchButton.setIcon(svg.get_svg_icon("radio-tower.svg"))
        lay.addWidget(self.searchEdit)
        lay.addWidget(self.searchButton)


class MachineSelectorControlsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, machines=[]):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.checks = []
        self.lay = QtWidgets.QHBoxLayout(self)
        self.lay.setContentsMargins(0, 0, 0, 9)

        for i, machine in enumerate(machines):
            check = QtWidgets.QCheckBox(machine)
            if i == 0:
                check.setChecked(True)
            self.checks.append(check)
            self.lay.addWidget(check)

    def get_selected_machines(self):
        machines = []
        for check in self.checks:
            if check.isChecked():
                print("Checked=" + check.text())
                machines.append(check.text())

        return machines


class PlayControlsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        _translate = QtCore.QCoreApplication.translate

        self.playButton = QtWidgets.QPushButton("Play")
        self.playButton.setIcon(svg.get_svg_icon("play.svg"))
        lay.addWidget(self.playButton)

        self.addButton = QtWidgets.QPushButton("Add")
        self.addButton.setIcon(svg.get_svg_icon("plus.svg"))
        lay.addWidget(self.addButton)


class SearchRadioWidget(QtWidgets.QDialog):
    radioAdded = pyqtSignal(int, name="radioAdded")

    def __init__(self, music_base, player, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowFlags(QtCore.Qt.Window)

        self.radios = []
        self.radio_manager = RadioManager(music_base)
        self.player = player
        self.search_radio_thread = SearchRadioThread()

        self.init_ui()

        self.init_column_headers()

        self.searchControls.searchEdit.setFocus()
        self.setTabOrder(
            self.searchControls.searchEdit, self.searchControls.searchButton
        )

    def init_ui(self):
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        self.setSizePolicy(sizePolicy)
        self.resize(600, 400)
        self.init_table_widget_items()

        self.searchControls = SearchControlsWidget()
        self.searchControls.searchButton.clicked.connect(self.on_search)

        self.playControls = PlayControlsWidget()
        self.playControls.playButton.clicked.connect(self.on_click_play_radio)
        self.playControls.addButton.clicked.connect(self.on_add_padio)

        self.machineSelectorControls = MachineSelectorControlsWidget(
            None, self.radio_manager.machines
        )

        self.mainLayout.addWidget(self.searchControls)
        self.mainLayout.addWidget(self.machineSelectorControls)
        self.mainLayout.addWidget(self.tableWidgetItems)
        self.mainLayout.addWidget(self.playControls)

        self.overlay = WaitOverlay(self)
        self.overlay.hide()

        self.retranslateUi()

    def resizeEvent(self, event):
        self.overlay.resize(event.size())

    def on_search(self, event):
        self.overlay.show_overlay()
        search = self.searchControls.searchEdit.text()

        self.wProgress = ProgressWidget(self)
        self.search_radio_thread.search_progress.connect(self.wProgress.set_value)
        self.search_radio_thread.search_current_machine.connect(
            self.wProgress.set_directory_text
        )
        self.search_radio_thread.search_completed.connect(self.on_search_complete)
        self.wProgress.progressClosed.connect(self.search_radio_thread.stop)
        self.search_radio_thread.search = search
        self.search_radio_thread.machines = (
            self.machineSelectorControls.get_selected_machines()
        )
        self.search_radio_thread.start()

    def on_play_padio(self, item):
        self.player.play_radio_in_thread(self.radios[item])

    def on_click_play_radio(self, event):
        i = self.tableWidgetItems.currentRow()
        if i > -1:
            self.player.play_radio_in_thread(self.radios[i])

    def on_add_padio(self, item):
        i = self.tableWidgetItems.currentRow()
        if i > -1:
            radio = self.radios[i]
            radio.save_radio(self.radio_manager.music_base.db)
            self.radioAdded.emit(1)

    def on_search_complete(self, event):
        self.radios = self.search_radio_thread.res_radios
        self.show_items(self.radios)
        self.init_column_headers()
        self.wProgress.close()
        self.overlay.hide()

    def init_table_widget_items(self):
        self.tableWidgetItems = QtWidgets.QTableWidget(self)

        self.tableWidgetItems.setGeometry(0, 0, 600, 300)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)

        self.tableWidgetItems.setSizePolicy(sizePolicy)
        self.tableWidgetItems.setMinimumSize(QtCore.QSize(50, 0))
        self.tableWidgetItems.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tableWidgetItems.setObjectName("tableWidgetItems")
        self.tableWidgetItems.setColumnCount(5)
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

        self.tableWidgetItems.cellDoubleClicked.connect(self.on_play_padio)

        self.init_column_headers()

    def init_column_headers(self):
        hHeader = self.tableWidgetItems.horizontalHeader()
        vHeader = self.tableWidgetItems.verticalHeader()
        vHeader.hide()

        hHeader.resizeSections(QtWidgets.QHeaderView.ResizeToContents)
        hHeader.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        item = self.tableWidgetItems.horizontalHeaderItem(0)
        item.setText(_translate("searchRadio", "Name"))
        item = self.tableWidgetItems.horizontalHeaderItem(1)
        item.setText(_translate("searchRadio", "Country"))
        item = self.tableWidgetItems.horizontalHeaderItem(2)
        item.setText(_translate("searchRadio", "Genre"))
        item = self.tableWidgetItems.horizontalHeaderItem(3)
        item.setText(_translate("searchRadio", "Stream"))

        self.setWindowTitle(_translate("searchRadio", "Search radio"))
        self.searchControls.searchButton.setText(_translate("searchRadio", "Search"))
        self.playControls.playButton.setText(_translate("searchRadio", "Play"))
        self.playControls.addButton.setText(_translate("searchRadio", "Add"))

    def show_items(self, items):
        self.tableWidgetItems.setStyleSheet(
            "selection-background-color: black;selection-color: white;"
        )
        self.tableWidgetItems.setColumnCount(4)
        self.tableWidgetItems.setRowCount(0)
        i = 0
        for item in items:
            self.tableWidgetItems.insertRow(i)
            title_item = QtWidgets.QTableWidgetItem(item.name)
            title_item.setFlags(title_item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetItems.setItem(i, 0, title_item)

            artist_item = QtWidgets.QTableWidgetItem(item.country)
            artist_item.setFlags(artist_item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetItems.setItem(i, 1, artist_item)

            album_item = QtWidgets.QTableWidgetItem(item.get_categories_text())
            album_item.setFlags(album_item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetItems.setItem(i, 2, album_item)

            duration_item = QtWidgets.QTableWidgetItem(item.stream)
            duration_item.setFlags(duration_item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetItems.setItem(i, 3, duration_item)

            i += 1


if __name__ == "__main__":
    import sys
    from src.music_base import MusicBase
    from src.player_vlc import PlayerVLC

    app = QtWidgets.QApplication(sys.argv)
    mb = MusicBase()
    mb.load_music_base(False)

    player = PlayerVLC()

    searchWidget = SearchRadioWidget(mb, player)

    searchWidget.show()
    sys.exit(app.exec_())
