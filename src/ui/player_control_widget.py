#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QCoreApplication, pyqtSignal, QSize

from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QSizePolicy,
    QFrame,
    QLabel,
)

from src.pic_from_url_thread import PicFromUrlThread
import src.svg_icon as svg
from .wait_overlay_widget import WaitOverlay

import threading
import logging

white = QtGui.QColor(255, 255, 255)
logger = logging.getLogger(__name__)
_translate = QCoreApplication.translate


class PlayerControlsWidget(QWidget):
    player = None
    defaultPixmap = None

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.parent = parent

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self.frameBt = QFrame(self)
        layBt = QHBoxLayout(self.frameBt)
        layBt.setContentsMargins(0, 0, 0, 0)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        self.frameBt.setSizePolicy(sizePolicy)

        self.currentTrack = None

        self.pauseButton = QPushButton()
        self.pauseButton.setToolTip(_translate("playlist", "Pause"))
        self.pauseButton.setIcon(svg.get_svg_icon("pause.svg"))

        layBt.addWidget(self.pauseButton)

        self.previousButton = QPushButton()
        self.previousButton.setToolTip(_translate("playlist", "Previous"))
        self.previousButton.setIcon(svg.get_svg_icon("step-backward.svg"))
        layBt.addWidget(self.previousButton)

        self.nextButton = QPushButton()
        self.nextButton.setToolTip(_translate("playlist", "Next"))
        self.nextButton.setIcon(svg.get_svg_icon("step-forward.svg"))
        layBt.addWidget(self.nextButton)

        self.fullscreenButton = QPushButton()
        self.fullscreenButton.setToolTip(_translate("playlist", "Full screen"))
        self.fullscreenButton.setIcon(svg.get_svg_icon("fullscreen.svg"))
        layBt.addWidget(self.fullscreenButton)

        self.playlistButton = QPushButton()
        self.playlistButton.setToolTip(_translate("playlist", "Playlist"))
        self.playlistButton.setIcon(svg.get_svg_icon("playlist.svg"))
        layBt.addWidget(self.playlistButton)

        self.frameBt.setMaximumSize(QSize(300, 40))
        lay.addWidget(self.frameBt)

        self.volumeSlider = QSlider()
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.volumeSlider.sizePolicy().hasHeightForWidth())
        self.volumeSlider.setSizePolicy(sizePolicy)
        self.volumeSlider.setMinimumSize(QSize(80, 0))
        self.volumeSlider.setMaximumSize(QSize(200, 40))
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setOrientation(Qt.Horizontal)
        self.volumeSlider.setObjectName("volumeSlider")
        lay.addWidget(self.volumeSlider)

        self.frameEmpty = QFrame(self)
        lay.addWidget(self.frameEmpty)


class PlayerControlWidget(QWidget):
    media_list = None
    player = None
    pic_from_url_thread = None
    nextPosition = 0
    is_time_slider_down = False
    current_track = None
    current_cover_path = ""
    track_changed = pyqtSignal(int, name="trackChanged")
    cover_changed = pyqtSignal(int, name="coverChanged")

    def __init__(self, player, parent):
        QWidget.__init__(self)
        self.parent = parent
        self.pic_buffer_manager = parent.pic_buffer_manager

        self.setWindowFlags(QtCore.Qt.Window)
        self.player = player
        self.media_list = self.player.media_list

        self.isWaitingCover = False

        self.defaultRadioPix = svg.get_svg_with_color_param("radio.svg", "", "#000000")

        self.initUI()

        self.parent.isPlayingSignal.connect(self.is_playing)
        self.parent.currentTrackChanged.connect(self.on_current_track_changed)
        self.parent.currentRadioChanged.connect(self.on_current_radio_changed)

    def is_playing(self, event):
        print("PlayerControlWidget isPlaying")
        self.refresh_wait_overlay()

    def on_current_track_changed(self, event):
        print("PlayerControlWidget Currenttrack changed!")
        self.set_current_track(event)

    def refresh_wait_overlay(self):
        if self.player.radio_mode:
            if self.isWaitingCover == False and self.player.is_playing_radio() == True:
                print("PlayerControlWidget refreshWaitOverlay hide")
                self.hide_wait_overlay()
            else:
                self.show_waiting_overlay()

        else:
            print("PlayerControlWidget refresh show wait")
            self.hide_wait_overlay()

    def on_current_radio_changed(self, event):
        print("PlayerControlWidget CurrentRadio changed!")

        self.set_radio_label_text()
        self.current_cover_path = ""
        self.refresh_wait_overlay()

    def cover_mouse_double_click_event(self, event):
        self.showFullScreen()

    def resizeEvent(self, event):
        if self.waitOverlay is not None:
            self.waitOverlay.resize(self.cover.size())

        event.accept()

    def initUI(self):
        self.hMainLayout = QHBoxLayout()
        self.hMainLayout.setContentsMargins(0, 4, 0, 0)
        self.hMainLayout.setSpacing(0)

        self.vLayout = QVBoxLayout()
        self.vLayout.setContentsMargins(4, 0, 0, 0)
        self.vLayout.setSpacing(4)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)
        # self.resize(550,400)

        self.playerControls = PlayerControlsWidget()
        self.playerControls.pauseButton.clicked.connect(self.on_pause)
        self.playerControls.previousButton.clicked.connect(self.player.previous)
        self.playerControls.nextButton.clicked.connect(self.player.next)
        self.playerControls.playlistButton.clicked.connect(self.parent.show_playlist)
        # self.playerControls.deleteButton.clicked.connect(self.onClearPlaylist)
        self.playerControls.fullscreenButton.clicked.connect(self.showFullScreen)

        self.playerControls.volumeSlider.setValue(self.player.get_volume())
        self.playerControls.volumeSlider.sliderMoved.connect(self.set_volume_slider)

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

        self.timeSlider.sliderPressed.connect(self.set_is_time_slider_down)
        self.timeSlider.sliderReleased.connect(self.on_time_slider_is_released)
        self.timeSlider.sliderMoved.connect(self.set_player_position)

        self.hMainFrame = QWidget()
        self.hMainFrame.setLayout(self.hMainLayout)

        self.mainFrame = QWidget()
        self.hLayout = QHBoxLayout()
        self.hLayout.setContentsMargins(0, 0, 0, 0)
        self.hLayout.setSpacing(6)

        self.coverPixmap = QtGui.QPixmap()

        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        self.cover = QLabel()
        self.cover.setSizePolicy(sizePolicy)
        self.cover.setMinimumSize(QSize(100, 100))
        self.cover.setMaximumSize(QSize(100, 100))
        self.cover.setAlignment(Qt.AlignCenter)
        self.cover.setPixmap(self.coverPixmap)
        self.cover.show()
        self.cover.mouseDoubleClickEvent = self.cover_mouse_double_click_event
        self.waitOverlay = WaitOverlay(self.cover, 12, 25, svg.ORANGE, 0)
        # self.hideWaitOverlay()

        self.labelTitle = QLabel()
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        self.labelTitle.setSizePolicy(sizePolicy)
        self.labelTitle.setTextFormat(Qt.RichText)
        self.labelTitle.setScaledContents(True)
        self.labelTitle.setWordWrap(True)

        self.hMainLayout.addWidget(self.cover)

        self.setLayout(self.hMainLayout)

        # self.vLayout.addWidget(self.mainFrame)

        self.vLayout.addWidget(self.labelTitle)
        self.vLayout.addWidget(self.playerControls)
        self.vLayout.addWidget(self.timeSlider)
        self.mainFrame.setLayout(self.vLayout)
        self.hMainLayout.addWidget(self.mainFrame)

        if self.pic_from_url_thread is None:
            self.pic_from_url_thread = PicFromUrlThread()

        self.retranslateUi()

    def connect_pic_downloader(self, picDl):
        self.pic_from_url_thread = picDl
        self.pic_from_url_thread.download_completed.connect(self.on_pic_downloaded)

    def on_pause(self, event):
        self.player.pause()

    def show_default_pixmap(self):
        if self.player.radio_mode:
            self.coverPixmap = self.defaultRadioPix
        else:
            self.coverPixmap = self.defaultPixmap

        self.show_sized_cover()

    def on_pic_downloaded(self, path):
        # self.isWaitingCover = False
        if path == "":
            self.show_default_pixmap()
            self.isWaitingCover = False
            # self.hideWaitOverlay()
        else:
            self.coverPixmap = self.pic_buffer_manager.get_pic(path)
            self.isWaitingCover = False
            self.show_scaled_cover()

        self.refresh_wait_overlay()

    def hide_wait_overlay(self):
        self.waitOverlay.hide()
        self.show_scaled_cover()

    def show_waiting_overlay(self):
        pix = QPixmap(100, 100)
        pix.fill(QtGui.QColor("transparent"))
        self.cover.setPixmap(pix)

        self.waitOverlay.show_overlay()
        self.waitOverlay.resize(self.cover.size())

    def show_scaled_cover(self):
        if not self.coverPixmap.isNull():
            scaledCover = self.coverPixmap.scaled(
                self.cover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.cover.setPixmap(scaledCover)

        else:
            self.cover.clear()

    def show_sized_cover(self, width=50, height=50):
        if not self.coverPixmap.isNull():
            scaledCover = self.coverPixmap.scaled(
                width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.cover.setPixmap(scaledCover)

        else:
            self.cover.clear()

    def setVolume(self, volume):
        self.player.set_volume(volume)

    def set_is_time_slider_down(self, event=None):
        print("setIsTimeSliderDown")
        self.is_time_slider_down = True
        if event is not None:
            return event.accept()

    def set_is_time_slider_released(self, event=None):
        print("setIsTimeSliderReleased")
        self.is_time_slider_down = False
        if event is not None:
            return event.accept()

    def showFullScreen(self):
        if self.parent.fullScreenWidget:
            self.parent.fullScreenWidget.show()
            self.parent.fullScreenWidget.activateWindow()

    def on_clear_playlist(self, event):
        # Remove all medias from the playlist except the current track
        self.player.remove_all_tracks()
        self.showMediaList()

    def retranslateUi(self):
        self.playerControls.pauseButton.setToolTip(_translate("playlist", "Pause"))
        self.playerControls.previousButton.setToolTip(
            _translate("playlist", "Previous")
        )
        self.playerControls.nextButton.setToolTip(_translate("playlist", "Next"))
        self.playerControls.playlistButton.setToolTip(
            _translate("playlist", "Playlist")
        )
        self.playerControls.fullscreenButton.setToolTip(
            _translate("playlist", "Full screen")
        )

    def set_current_track_in_thread(self, title):
        process_thread = threading.Thread(target=self.set_current_track, args=[title])
        process_thread.start()

    def set_current_track(self, title=""):
        if self.player is None:
            return

        index = self.player.get_current_index_playlist()
        print("PlayerControl setCurrentTrack:", index)

        trk = self.player.get_current_track_playlist()
        if trk is None and title:
            self.set_title_label(title)
            self.show_cover()
            return

        self.current_track = trk

        self.set_title_label()

        self.show_cover(trk)

    def show_cover(self, trk=None):
        if self.player.radio_mode:
            cover_url = self.player.get_live_cover_url()
            if cover_url == "":
                rad = self.player.get_current_radio()
                if rad is not None:
                    cover_url = rad.get_radio_pic()

            if cover_url is None:
                cover_url = ""
            logger.debug("showCover: %s", cover_url)
            if self.current_cover_path == cover_url:
                self.isWaitingCover = False
                self.refresh_wait_overlay()
                return

            if cover_url != "":
                self.coverPixmap = QPixmap()
                self.cover.setPixmap(self.coverPixmap)
                self.current_cover_path = cover_url
                self.pic_from_url_thread.url = cover_url
                self.isWaitingCover = True
                self.pic_from_url_thread.start()
            else:
                self.show_default_pixmap()
                self.refresh_wait_overlay()

        else:
            self.isWaitingCover = False
            if trk is not None and trk.parentAlbum is not None:
                if trk.parentAlbum.cover == "" or trk.parentAlbum.cover is None:
                    self.current_cover_path = ""
                    self.coverPixmap = self.defaultPixmap
                else:
                    self.current_cover_path = trk.parentAlbum.get_cover_path()
                    self.coverPixmap = self.pic_buffer_manager.get_pic(self.current_cover_path)

                self.show_scaled_cover()

            self.refresh_wait_overlay()

    def set_title_label(self, title=""):
        logger.debug("setTitleLabel %s", title)
        if title != "":
            self.set_radio_label_text(title)
            return

        if self.current_track:
            if self.current_track.is_radio():
                self.set_radio_label_text()
                self.timeSlider.setVisible(False)
            else:
                self.set_track_label_text()
                self.timeSlider.setVisible(True)

    def set_track_label_text(self):
        if self.current_track is None:
            return

        art_name = self.current_track.get_artist_name()
        alb_title = self.current_track.get_album_title()
        trk_title = self.current_track.get_track_title()
        year = self.current_track.get_album_year()

        if alb_title != "":
            alb_title = " - " + alb_title
        s_year = str(year)
        if not s_year in ["0", ""]:
            alb_title += " (" + s_year + ")"
        title_html = """<html><head/><body>
        <p><span style=\" font-size:15pt; text-shadow:white 0px 0px 4px; font-weight:600;\">{art_name}</span>
        <span style=\" font-size:12pt; font-style:italic;\">{trk_title}</span></p>
        <span style=\" font-size:12pt; font-style:bold;\">{album}</span></p>
        </body></html>"""
        title_html = title_html.format(
            art_name=art_name, trk_title=trk_title, album=alb_title
        )

        self.labelTitle.setText(title_html)

    def set_radio_label_text(self, title=""):
        trk_title = ""
        radio_name = ""
        now_playing = ""
        if title == "":
            if self.current_track is None:
                return
            if self.current_track.radio:
                radio_name = self.current_track.radio.name
                trk_title = self.current_track.radio.live_track_title
            if trk_title == "":
                now_playing = self.player.get_now_playing()
            if now_playing:
                if trk_title == "NO_META":
                    trk_title = ""
        else:
            radio_name = title
            trk_title = ""

        title_html = """<html><head/><body>
        <p><span style=\" font-size:15pt; text-shadow:white 0px 0px 4px; font-weight:600;\">{radio_name}</span>
        <span style=\" font-size:12pt; font-style:italic;\">{trk_title}</span></p>
        </body></html>"""
        title_html = title_html.format(radio_name=radio_name, trk_title=trk_title)

        self.labelTitle.setText(title_html)

    def on_time_slider_is_released(self, event=None):
        print("onTimeSliderIsReleased")

        self.player.set_position(self.nextPosition)
        self.is_time_slider_down = False
        # self.player.setPosition(self.nextPosition)

    def set_player_position(self, pos):
        print(str(pos))
        self.nextPosition = pos / 1000
        # self.player.setPosition(self.nextPosition)

    def get_volume_slider(self):
        return self.playerControls.volumeSlider.value()

    def set_volume_slider(self, vol):
        self.playerControls.volumeSlider.setValue(vol)

    def on_player_position_changed(self, event=None):
        if not self.is_time_slider_down:
            pos = self.player.get_position()
            self.timeSlider.setValue(pos * 1000)
