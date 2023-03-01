#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize, QCoreApplication, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QDialog,
    QPushButton,
    QVBoxLayout,
    QHeaderView,
    QHBoxLayout,
    QSlider,
    QSizePolicy,
    QFrame,
    QLabel,
    QShortcut,
    QTableWidgetItem,
)
from PyQt5.QtGui import QPixmap
from track import Track
import requests
from pic_from_url_thread import PicFromUrlThread
from table_widget_drag_rows import TableWidgetDragRows

from vlc import EventType as vlcEventType
from svg_icon import *
import logging

logger = logging.getLogger(__name__)

# orange = QtGui.QColor(216, 119, 0)
white = QtGui.QColor(255, 255, 255)

_translate = QCoreApplication.translate


class PlayerControlsWidget(QWidget):
    player = None

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self.pauseButton = QPushButton()
        self.pauseButton.setToolTip(_translate("playlist", "Pause"))
        self.pauseButton.setIcon(get_svg_icon("pause.svg"))

        lay.addWidget(self.pauseButton)

        self.previousButton = QPushButton()
        self.previousButton.setToolTip(_translate("playlist", "Previous"))
        self.previousButton.setIcon(get_svg_icon("step-backward.svg"))
        lay.addWidget(self.previousButton)

        self.nextButton = QPushButton()
        self.nextButton.setToolTip(_translate("playlist", "Next"))
        self.nextButton.setIcon(get_svg_icon("step-forward.svg"))
        lay.addWidget(self.nextButton)

        self.deleteButton = QPushButton()
        self.deleteButton.setToolTip(_translate("playlist", "Delete all tracks"))
        self.deleteButton.setIcon(get_svg_icon("bin.svg"))
        lay.addWidget(self.deleteButton)

        self.fullscreenButton = QPushButton()
        self.fullscreenButton.setToolTip(_translate("playlist", "Full screen"))
        self.fullscreenButton.setIcon(get_svg_icon("fullscreen.svg"))
        lay.addWidget(self.fullscreenButton)

        self.volumeSlider = QSlider()
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.volumeSlider.sizePolicy().hasHeightForWidth())
        self.volumeSlider.setSizePolicy(sizePolicy)
        self.volumeSlider.setMinimumSize(QSize(80, 0))
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setOrientation(Qt.Horizontal)
        self.volumeSlider.setObjectName("volumeSlider")
        lay.addWidget(self.volumeSlider)


class PlaylistWidget(QDialog):
    picFromUrlThread = None
    currentCoverPath = ""
    picBufferManager = None
    mediaList = None
    player = None
    nextPosition = 0
    isTimeSliderDown = False
    trackChanged = pyqtSignal(int, name="trackChanged")
    currentRadioChanged = pyqtSignal(int, name="currentRadioChanged")

    def __init__(self, player, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowFlags(Qt.Window)
        if parent:
            self.parent = parent
        self.player = player
        self.mediaList = self.player.media_list
        self.fullScreenWidget = None

        if self.picFromUrlThread is None:
            self.picFromUrlThread = PicFromUrlThread()

        self.initUI()
        self.tableWidgetTracks.cellDoubleClicked.connect(self.change_track)
        self.cover.mouseDoubleClickEvent = self.mouseDoubleClickEvent
        self.parent.playlist_changed.connect(self.on_playlist_changed)

    def mouseDoubleClickEvent(self, event):
        self.showFullScreen()

    def initUI(self):
        self.picFromUrlThread.download_completed.connect(self.on_pic_downloaded)

        # self.setWindowIcon(QtGui.QIcon(self.parent.defaultPixmap))

        self.vLayout = QVBoxLayout()
        self.vLayout.setContentsMargins(6, 6, 6, 6)
        self.setLayout(self.vLayout)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        self.setSizePolicy(sizePolicy)
        self.resize(550, 400)
        self.init_table_widget_tracks()

        self.playerControls = PlayerControlsWidget()
        self.playerControls.pauseButton.clicked.connect(self.onPause)
        self.playerControls.previousButton.clicked.connect(self.player.previous)
        self.playerControls.nextButton.clicked.connect(self.player.next)
        self.playerControls.deleteButton.clicked.connect(self.on_clear_playlist)
        self.playerControls.fullscreenButton.clicked.connect(self.showFullScreen)

        self.playerControls.volumeSlider.setValue(self.player.get_volume())
        self.playerControls.volumeSlider.sliderMoved.connect(self.set_volume)

        self.timeSlider = QSlider(self)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timeSlider.sizePolicy().hasHeightForWidth())
        self.timeSlider.setSizePolicy(sizePolicy)
        self.timeSlider.setMinimumSize(QSize(60, 0))
        self.timeSlider.setMinimum(0)
        self.timeSlider.setMaximum(1000)
        self.timeSlider.setOrientation(Qt.Horizontal)
        self.timeSlider.setObjectName("timeSlider")

        # self.timeSlider.mousePressEvent=self.setIsTimeSliderDown
        # self.timeSlider.mouseReleaseEvent=self.onTimeSliderIsReleased

        self.timeSlider.sliderPressed.connect(self.set_is_time_slider_down)
        self.timeSlider.sliderReleased.connect(self.on_time_slider_is_released)
        self.timeSlider.sliderMoved.connect(self.set_player_position)
        # self.player.mpEnventManager.event_attach(vlcEventType.MediaPlayerPositionChanged, self.onPlayerPositionChanged)

        self.shortcutPause = QShortcut(QtGui.QKeySequence("Space"), self)
        self.shortcutPause.activated.connect(self.player.pause)
        self.shortcutFullScreen = QShortcut(QtGui.QKeySequence("Ctrl+F"), self)
        self.shortcutFullScreen.activated.connect(self.showFullScreen)

        self.mainFrame = QFrame()
        self.hLayout = QHBoxLayout()
        self.hLayout.setContentsMargins(0, 0, 0, 0)
        self.hLayout.setSpacing(6)
        self.mainFrame.setLayout(self.hLayout)

        self.coverPixmap = QtGui.QPixmap()
        self.defaultRadioPix = get_svg_with_color_param("radio.svg", "", "#000000")
        self.defaultPixmap = QtGui.QPixmap()

        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        # sizePolicy.setWidthForHeight(True)

        self.cover = QLabel()
        self.cover.setSizePolicy(sizePolicy)
        self.cover.setMinimumSize(QSize(200, 200))
        self.cover.setMaximumSize(QSize(200, 200))
        self.cover.setPixmap(self.coverPixmap)

        self.hLayout.addWidget(self.cover)
        self.hLayout.addWidget(self.tableWidgetTracks)

        self.vLayout.addWidget(self.mainFrame)
        self.vLayout.addWidget(self.timeSlider)
        self.vLayout.addWidget(self.playerControls)

        self.retranslateUi()

        # self.resizeEvent = self.onResize

    def onPause(self, event):
        self.player.pause()

    def connect_pic_downloader(self, picDl):
        self.picFromUrlThread = picDl
        self.picFromUrlThread.download_completed.connect(self.on_pic_downloaded)

    def on_pic_downloaded(self, path):
        print("Playlist onPicDownloaded")
        self.show_cover_pixmap(path)

    def set_volume(self, volume):
        self.player.set_volume(volume)

    def set_is_time_slider_down(self, event=None):
        print("setIsTimeSliderDown")
        self.isTimeSliderDown = True
        if event is not None:
            return event.accept()

    def set_is_time_slider_released(self, event=None):
        print("setIsTimeSliderReleased")
        self.isTimeSliderDown = False
        if event is not None:
            return event.accept()

    def onResize(self, event):
        hHeader = self.tableWidgetTracks.horizontalHeader()
        hHeader.resizeSections(QHeaderView.Stretch)

    def showFullScreen(self):
        if self.fullScreenWidget:
            self.fullScreenWidget.show()
            self.fullScreenWidget.activateWindow()

    def init_table_widget_tracks(self):
        self.tableWidgetTracks = TableWidgetDragRows(self)

        self.tableWidgetTracks.setGeometry(0, 0, 550, 300)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)

        self.tableWidgetTracks.setSizePolicy(sizePolicy)
        self.tableWidgetTracks.setMinimumSize(QSize(50, 0))

        self.tableWidgetTracks.setObjectName("tableWidgetTracks")
        self.tableWidgetTracks.setColumnCount(5)
        self.tableWidgetTracks.setRowCount(0)
        item = QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(1, item)
        item = QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(2, item)
        item = QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(3, item)
        item = QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(4, item)

        self.init_column_headers()

        self.tableWidgetTracks.trackMoved.connect(self.on_track_moved)
        self.tableWidgetTracks.beforeTrackMove.connect(self.on_before_track_move)

    def init_column_headers(self):
        horizontal_header = self.tableWidgetTracks.horizontalHeader()
        vertical_header = self.tableWidgetTracks.verticalHeader()
        vertical_header.hide()

        horizontal_header.resizeSections(QHeaderView.ResizeToContents)
        horizontal_header.setSectionResizeMode(QHeaderView.Interactive)
        horizontal_header.hideSection(4)

        if self.tableWidgetTracks.columnWidth(0) < 100:
            self.tableWidgetTracks.setColumnWidth(0, 100)
        else:
            if self.tableWidgetTracks.columnWidth(0) > 300:
                self.tableWidgetTracks.setColumnWidth(0, 300)

    def on_before_track_move(self, param):
        for i in range(0, self.tableWidgetTracks.rowCount()):
            id_line = self.tableWidgetTracks.item(i, 4).setText(str(i))

    def on_track_moved(self, track_move: (int, int)):
        self.mediaList.lock()
        # Get new order of tracks
        new_order = []
        for i in range(0, self.tableWidgetTracks.rowCount()):
            id_line = self.tableWidgetTracks.item(i, 4).text()
            new_order.append(int(id_line))

        new_current = 0
        current_index = self.player.get_current_index_playlist()

        # Backup current vlc media list
        tmp_media_list = []
        for i in range(0, self.mediaList.count()):
            tmp_media_list.append(self.mediaList.item_at_index(i))

        self.player.remove_all_tracks()

        # Add tracks in new order
        for i, id_line in enumerate(new_order):
            if id_line != current_index:
                self.mediaList.insert_media(tmp_media_list[id_line], i)
            else:
                new_current = i

        self.mediaList.unlock()

        print("new_current=" + str(new_current))

        self.player.refresh_media_list_player()
        self.show_media_list()
        # self.player.resetCurrentItemIndex(new_current)

    def on_clear_playlist(self, event):
        # Remove all medias from the playlist except the current track
        self.player.remove_all_tracks()
        self.show_media_list()

    def retranslateUi(self):
        item = self.tableWidgetTracks.horizontalHeaderItem(0)
        item.setText(_translate("playlist", "Title"))
        item = self.tableWidgetTracks.horizontalHeaderItem(1)
        item.setText(_translate("playlist", "Artist"))
        item = self.tableWidgetTracks.horizontalHeaderItem(2)
        item.setText(_translate("playlist", "Album"))
        item = self.tableWidgetTracks.horizontalHeaderItem(3)
        item.setText(_translate("playlist", "Duration"))
        item = self.tableWidgetTracks.horizontalHeaderItem(4)
        item.setText(_translate("playlist", "ID"))

        self.playerControls.pauseButton.setToolTip(_translate("playlist", "Pause"))
        self.playerControls.previousButton.setToolTip(
            _translate("playlist", "Previous")
        )
        self.playerControls.nextButton.setToolTip(_translate("playlist", "Next"))
        self.playerControls.fullscreenButton.setToolTip(
            _translate("playlist", "Full screen")
        )
        self.playerControls.deleteButton.setToolTip(
            _translate("playlist", "Delete all tracks")
        )

        self.setWindowTitle(_translate("playlist", "Playlist"))

    def show_tracks(self, tracks):
        self.tableWidgetTracks.setStyleSheet(
            "selection-background-color: black;selection-color: white;"
        )
        self.tableWidgetTracks.setColumnCount(5)
        self.tableWidgetTracks.setRowCount(0)
        i = 0
        for track in tracks:
            self.tableWidgetTracks.insertRow(i)
            title_item = QTableWidgetItem(track.get_track_title())
            title_item.setFlags(title_item.flags() ^ Qt.ItemIsEditable)
            self.tableWidgetTracks.setItem(i, 0, title_item)

            if track.radio_name == "":
                artist_item = QTableWidgetItem(track.get_artist_name())
                artist_item.setFlags(artist_item.flags() ^ Qt.ItemIsEditable)
                self.tableWidgetTracks.setItem(i, 1, artist_item)

                album_item = QTableWidgetItem(track.get_album_title())
                album_item.setFlags(album_item.flags() ^ Qt.ItemIsEditable)
                self.tableWidgetTracks.setItem(i, 2, album_item)

                duration_item = QTableWidgetItem(track.get_duration_text())
                duration_item.setFlags(duration_item.flags() ^ Qt.ItemIsEditable)
                self.tableWidgetTracks.setItem(i, 3, duration_item)
            else:
                print("radioName=" + track.radio_name)
                artist_item = QTableWidgetItem(self.player.current_radio_name)
                artist_item.setFlags(artist_item.flags() ^ Qt.ItemIsEditable)
                self.tableWidgetTracks.setItem(i, 1, artist_item)

                album_item = QTableWidgetItem(self.player.current_radio_name)
                album_item.setFlags(album_item.flags() ^ Qt.ItemIsEditable)
                self.tableWidgetTracks.setItem(i, 2, album_item)

                duration_item = QTableWidgetItem(track.get_duration_text())
                duration_item.setFlags(duration_item.flags() ^ Qt.ItemIsEditable)
                self.tableWidgetTracks.setItem(i, 3, duration_item)

            order_item = QTableWidgetItem(str(i))
            order_item.setFlags(order_item.flags() ^ Qt.ItemIsEditable)
            self.tableWidgetTracks.setItem(i, 4, order_item)

            i += 1

    def showEvent(self, event):
        self.show_media_list()

    def show_media_list(self):
        tracks = []

        self.mediaList = self.player.media_list
        for i in range(self.mediaList.count()):
            m = self.mediaList.item_at_index(i)
            if m is None:
                print("BREAK ShowMediaList media=", i)
                break

            mrl = m.get_mrl()
            # print("ShowMediaList mrl="+mrl)
            t = self.player.get_track_from_mrl(mrl)
            if t is None:
                t = Track()
                t.set_mrl(mrl)
                t.title = self.player.get_title()

            # t.albumObj = player.getAlbumFromMrl(mrl)
            # t.setMRL(mrl)
            # t.getMutagenTags()
            tracks.append(t)

        self.show_tracks(tracks)
        self.set_current_track()

    def set_current_track(self, title=""):
        if not self.isVisible():
            return

        trk = self.player.get_current_track_playlist()

        if title in ["", "..."] and trk:
            if trk.is_radio():
                title = self.player.get_now_playing()
                if title == "...":
                    title = trk.radio_name
            else:
                title = trk.get_track_title()

        logger.debug("setCurrentTrack window title %s", title)
        if title != "":
            self.setWindowTitle(title)
        else:
            self.setWindowTitle(_translate("playlist", "Playlist"))

        index = self.player.get_current_index_playlist()

        if self.tableWidgetTracks.rowCount == 0:
            self.show_media_list()

        for i in range(0, self.mediaList.count()):
            item = self.tableWidgetTracks.item(i, 0)
            if item is None:
                print("BREAK setCurrentTrack item=", i)
                break

            if trk is None:
                self.show_default_pixmap()
                if self.player.radio_mode:
                    item.setText(title)
                    item1 = self.tableWidgetTracks.item(i, 1)
                    item1.setText("")
                    item2 = self.tableWidgetTracks.item(i, 2)
                    item2.setText("")
                else:
                    print("trk is None")

            if trk is not None and trk.radio_name != "" and i == index:
                if title != "":
                    if title == "NO_META":
                        title = trk.radio_name
                    item.setText(title)
                else:
                    now_playing = self.player.get_now_playing()
                    if now_playing == "NO_META":
                        now_playing = trk.radio_name
                    item.setText(now_playing)

                item1 = self.tableWidgetTracks.item(i, 1)
                item1.setText(self.player.current_radio_name)
                item2 = self.tableWidgetTracks.item(i, 2)
                item2.setText(self.player.current_radio_name)

            f = item.font()
            if i == index:
                if trk is not None:
                    self.show_cover(trk)
                f.setBold(True)
                f.setItalic(True)
                color = ORANGE
            else:
                f.setBold(False)
                f.setItalic(False)
                color = white

            item.setFont(f)

            for j in range(0, 2):
                self.tableWidgetTracks.item(i, j).setFont(f)

            for j in range(0, 3):
                self.tableWidgetTracks.item(i, j).setForeground(color)

            if i == index:
                self.tableWidgetTracks.setCurrentItem(item)

        self.tableWidgetTracks.scrollTo(self.tableWidgetTracks.currentIndex())

        self.update()

        self.init_column_headers()

    def show_cover(self, trk):
        if self.player.radio_mode:
            self.coverPixmap = QPixmap()
            cover_url = self.player.get_live_cover_url()
            if cover_url == "":
                rad = self.player.get_current_radio()
                if rad is not None:
                    cover_url = rad.get_radio_pic()

            if cover_url is None:
                cover_url = ""

            if self.currentCoverPath == cover_url:
                return

            if cover_url != "":
                self.currentCoverPath = cover_url
                self.picFromUrlThread.url = cover_url
                self.picFromUrlThread.start()
            else:
                self.show_default_pixmap()

        else:
            # self.picFromUrlThread.resetLastURL()
            if trk is not None and trk.parentAlbum is not None:
                print("playlistWidget trk.parentAlbum.cover=" + trk.parentAlbum.cover)
                if trk.parentAlbum.cover == "" or trk.parentAlbum.cover is None:
                    self.coverPixmap = self.defaultPixmap
                else:
                    cover_path = trk.parentAlbum.get_cover_path()

                    self.show_cover_pixmap(cover_path)

    def show_cover_pixmap(self, path):
        if self.picBufferManager is None:
            self.coverPixmap = QtGui.QPixmap(path)
        else:
            self.coverPixmap = self.picBufferManager.get_pic(path, "PlaylistWidget")

        self.show_scaled_cover()

    def show_default_pixmap(self):
        if self.player.radio_mode:
            self.coverPixmap = self.defaultRadioPix
        else:
            self.coverPixmap = self.defaultPixmap

        self.show_scaled_cover()

    def show_scaled_cover(self):
        if not self.coverPixmap.isNull():
            scaled_cover = self.coverPixmap.scaled(
                self.cover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.cover.setPixmap(scaled_cover)

        else:
            self.cover.clear()

    def change_track(self, item):
        i = self.tableWidgetTracks.currentRow()

        self.trackChanged.emit(i)

    def on_time_slider_is_released(self, event=None):
        print("onTimeSliderIsReleased")

        self.player.set_position(self.nextPosition)
        self.isTimeSliderDown = False
        # self.player.setPosition(self.nextPosition)

    def set_player_position(self, pos):
        print(str(pos))
        self.nextPosition = pos / 1000
        # self.player.setPosition(self.nextPosition)

    def on_player_position_changed(self, event=None):
        if not self.isTimeSliderDown:
            pos = self.player.get_position()
            # print('onPlayerPositionChanged='+str(pos))
            self.timeSlider.setValue(pos * 1000)

    def on_playlist_changed(self, event):
        print("PlayerControlWidget playlist changed!")
        self.show_media_list()


if __name__ == "__main__":
    import sys
    from player_vlc import PlayerVLC

    player = PlayerVLC()

    app = QApplication(sys.argv)

    playlist = PlaylistWidget(player)

    playlist.tableWidgetTracks.setColumnCount(4)
    playlist.tableWidgetTracks.setRowCount(5)

    for i in range(5):
        playlist.tableWidgetTracks.setItem(i, 0, QTableWidgetItem("test" + str(i)))
        playlist.tableWidgetTracks.setItem(i, 1, QTableWidgetItem("toto" + str(i)))

    playlist.show()

    url = "/tmp/tmp8mfrufdl"
    playlist.on_pic_downloaded(url)

    sys.exit(app.exec_())
