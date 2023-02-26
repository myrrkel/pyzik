#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
)
from track import *

from pic_from_url_thread import PicFromUrlThread
from table_widget_drag_rows import TableWidgetDragRows
from wait_overlay_widget import WaitOverlay
from PyQt5.QtGui import QPixmap
import threading

from svg_icon import *
import logging

logger = logging.getLogger(__name__)

white = QtGui.QColor(255, 255, 255)

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
        self.pauseButton.setIcon(getSvgIcon("pause.svg"))

        layBt.addWidget(self.pauseButton)

        self.previousButton = QPushButton()
        self.previousButton.setToolTip(_translate("playlist", "Previous"))
        self.previousButton.setIcon(getSvgIcon("step-backward.svg"))
        layBt.addWidget(self.previousButton)

        self.nextButton = QPushButton()
        self.nextButton.setToolTip(_translate("playlist", "Next"))
        self.nextButton.setIcon(getSvgIcon("step-forward.svg"))
        layBt.addWidget(self.nextButton)

        self.fullscreenButton = QPushButton()
        self.fullscreenButton.setToolTip(_translate("playlist", "Full screen"))
        self.fullscreenButton.setIcon(getSvgIcon("fullscreen.svg"))
        layBt.addWidget(self.fullscreenButton)

        self.playlistButton = QPushButton()
        self.playlistButton.setToolTip(_translate("playlist", "Playlist"))
        self.playlistButton.setIcon(getSvgIcon("playlist.svg"))
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
    mediaList = None
    player = None
    picFromUrlThread = None
    nextPosition = 0
    isTimeSliderDown = False
    currentTrack = None
    currentCoverPath = ""
    trackChanged = pyqtSignal(int, name="trackChanged")
    coverChanged = pyqtSignal(int, name="coverChanged")

    def __init__(self, player, parent):
        QDialog.__init__(self)
        self.parent = parent
        self.picBufferManager = parent.picBufferManager

        self.setWindowFlags(Qt.Window)
        self.player = player
        self.mediaList = self.player.mediaList

        self.isWaitingCover = False

        self.defaultRadioPix = getSvgWithColorParam("radio.svg", "", "#000000")

        self.initUI()

        self.parent.isPlayingSignal.connect(self.isPlaying)
        self.parent.currentTrackChanged.connect(self.onCurrentTrackChanged)
        self.parent.currentRadioChanged.connect(self.onCurrentRadioChanged)

    def isPlaying(self, event):
        print("PlayerControlWidget isPlaying")
        self.refreshWaitOverlay()

    def onCurrentTrackChanged(self, event):
        print("PlayerControlWidget Currenttrack changed!")
        self.setCurrentTrack(event)

    def refreshWaitOverlay(self):
        if self.player.radioMode:
            if self.isWaitingCover == False and self.player.isPlayingRadio() == True:
                print("PlayerControlWidget refreshWaitOverlay hide")
                self.hideWaitOverlay()
            else:
                self.showWaitingOverlay()

        else:
            print("PlayerControlWidget refresh show wait")
            self.hideWaitOverlay()

    def onCurrentRadioChanged(self, event):
        print("PlayerControlWidget CurrentRadio changed!")

        self.setRadioLabeLText()
        self.currentCoverPath = ""
        self.refreshWaitOverlay()

    def coverMouseDoubleClickEvent(self, event):
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
        self.playerControls.pauseButton.clicked.connect(self.onPause)
        self.playerControls.previousButton.clicked.connect(self.player.previous)
        self.playerControls.nextButton.clicked.connect(self.player.next)
        self.playerControls.playlistButton.clicked.connect(self.parent.showPlaylist)
        # self.playerControls.deleteButton.clicked.connect(self.onClearPlaylist)
        self.playerControls.fullscreenButton.clicked.connect(self.showFullScreen)

        self.playerControls.volumeSlider.setValue(self.player.getVolume())
        self.playerControls.volumeSlider.sliderMoved.connect(self.setVolume)

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

        self.timeSlider.sliderPressed.connect(self.setIsTimeSliderDown)
        self.timeSlider.sliderReleased.connect(self.onTimeSliderIsReleased)
        self.timeSlider.sliderMoved.connect(self.setPlayerPosition)

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
        self.cover.mouseDoubleClickEvent = self.coverMouseDoubleClickEvent
        self.waitOverlay = WaitOverlay(self.cover, 12, 25, orange, 0)
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

        if self.picFromUrlThread is None:
            self.picFromUrlThread = PicFromUrlThread()

        self.retranslateUi()

    def connectPicDownloader(self, picDl):
        self.picFromUrlThread = picDl
        self.picFromUrlThread.downloadCompleted.connect(self.onPicDownloaded)

    def onPause(self, event):
        self.player.pause()

    def showDefaultPixmap(self):
        if self.player.radioMode:
            self.coverPixmap = self.defaultRadioPix
        else:
            self.coverPixmap = self.defaultPixmap

        self.showSizedCover()

    def onPicDownloaded(self, path):
        # self.isWaitingCover = False
        if path == "":
            self.showDefaultPixmap()
            self.isWaitingCover = False
            # self.hideWaitOverlay()
        else:
            self.coverPixmap = self.picBufferManager.getPic(path, "playerControl")
            self.isWaitingCover = False
            self.showScaledCover()

        self.refreshWaitOverlay()

    def hideWaitOverlay(self):
        self.waitOverlay.hide()
        self.showScaledCover()

    def showWaitingOverlay(self):
        # print("showWaitingOverlay")

        pix = QPixmap(100, 100)
        pix.fill(QtGui.QColor("transparent"))
        self.cover.setPixmap(pix)

        self.waitOverlay.showOverlay()
        self.waitOverlay.resize(self.cover.size())
        # self.show()

    def showScaledCover(self):
        if not self.coverPixmap.isNull():
            scaledCover = self.coverPixmap.scaled(
                self.cover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.cover.setPixmap(scaledCover)

        else:
            self.cover.clear()

    def showSizedCover(self, width=50, height=50):
        if not self.coverPixmap.isNull():
            scaledCover = self.coverPixmap.scaled(
                width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.cover.setPixmap(scaledCover)

        else:
            self.cover.clear()

    def setVolume(self, volume):
        self.player.setVolume(volume)

    def setIsTimeSliderDown(self, event=None):
        print("setIsTimeSliderDown")
        self.isTimeSliderDown = True
        if event is not None:
            return event.accept()

    def setIsTimeSliderReleased(self, event=None):
        print("setIsTimeSliderReleased")
        self.isTimeSliderDown = False
        if event is not None:
            return event.accept()

    def showFullScreen(self):
        if self.parent.fullScreenWidget:
            self.parent.fullScreenWidget.show()
            self.parent.fullScreenWidget.activateWindow()

    def onClearPlaylist(self, event):
        # Remove all medias from the playlist except the current track
        self.player.removeAllTracks()
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

    def setCurrentTrackInThread(self, title):
        processThread = threading.Thread(target=self.setCurrentTrack, args=[title])
        processThread.start()

    def setCurrentTrack(self, title=""):
        if self.player is None:
            return

        index = self.player.get_current_index_playlist()
        print("PlayerControl setCurrentTrack:", index)

        trk = self.player.getCurrentTrackPlaylist()
        if trk is None and title:
            self.setTitleLabel(title)
            self.showCover()
            return

        self.currentTrack = trk

        self.setTitleLabel()

        self.showCover(trk)

    def showCover(self, trk=None):
        if self.player.radioMode:
            coverUrl = self.player.getLiveCoverUrl()
            if coverUrl == "":
                rad = self.player.getCurrentRadio()
                if rad is not None:
                    coverUrl = rad.get_radio_pic()

            if coverUrl is None:
                coverUrl = ""
            logger.debug("showCover: %s", coverUrl)
            if self.currentCoverPath == coverUrl:
                self.isWaitingCover = False
                self.refreshWaitOverlay()
                return

            if coverUrl != "":
                self.coverPixmap = QPixmap()
                self.cover.setPixmap(self.coverPixmap)
                self.currentCoverPath = coverUrl
                self.picFromUrlThread.url = coverUrl
                self.isWaitingCover = True
                self.picFromUrlThread.start()
            else:
                self.showDefaultPixmap()
                self.refreshWaitOverlay()

        else:
            self.isWaitingCover = False
            if trk is not None and trk.parentAlbum is not None:
                if trk.parentAlbum.cover == "" or trk.parentAlbum.cover is None:
                    self.currentCoverPath = ""
                    self.coverPixmap = self.defaultPixmap
                else:
                    self.currentCoverPath = trk.parentAlbum.get_cover_path()
                    self.coverPixmap = self.picBufferManager.getPic(
                        self.currentCoverPath, "playerControl"
                    )

                self.showScaledCover()

            self.refreshWaitOverlay()

    def setTitleLabel(self, title=""):
        logger.debug("setTitleLabel %s", title)
        if title != "":
            self.setRadioLabeLText(title)
            return

        if self.currentTrack:
            if self.currentTrack.is_radio():
                self.setRadioLabeLText()
                self.timeSlider.setVisible(False)
            else:
                self.setTrackLabelText()
                self.timeSlider.setVisible(True)

    def setTrackLabelText(self):
        if self.currentTrack is None:
            return

        art_name = self.currentTrack.get_artist_name()
        alb_title = self.currentTrack.get_album_title()
        trk_title = self.currentTrack.get_track_title()
        year = self.currentTrack.get_album_year()

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

    def setRadioLabeLText(self, title=""):
        trk_title = ""
        radioName = ""
        if title == "":
            if self.currentTrack is None:
                return
            if self.currentTrack.radio:
                radioName = self.currentTrack.radio.name
                trk_title = self.currentTrack.radio.liveTrackTitle
            if trk_title == "":
                now_playing = self.player.getNowPlaying()
            if now_playing:
                if trk_title == "NO_META":
                    trk_title = ""
        else:
            radioName = title
            trk_title = ""

        title_html = """<html><head/><body>
        <p><span style=\" font-size:15pt; text-shadow:white 0px 0px 4px; font-weight:600;\">{radioName}</span>
        <span style=\" font-size:12pt; font-style:italic;\">{trk_title}</span></p>
        </body></html>"""
        title_html = title_html.format(radioName=radioName, trk_title=trk_title)

        self.labelTitle.setText(title_html)

    def onTimeSliderIsReleased(self, event=None):
        print("onTimeSliderIsReleased")

        self.player.setPosition(self.nextPosition)
        self.isTimeSliderDown = False
        # self.player.setPosition(self.nextPosition)

    def setPlayerPosition(self, pos):
        print(str(pos))
        self.nextPosition = pos / 1000
        # self.player.setPosition(self.nextPosition)

    def getVolume(self):
        return self.playerControls.volumeSlider.value()

    def setVolume(self, vol):
        self.playerControls.volumeSlider.setValue(vol)

    def onPlayerPositionChanged(self, event=None):
        if not self.isTimeSliderDown:
            pos = self.player.getPosition()
            # print('onPlayerPositionChanged='+str(pos))
            self.timeSlider.setValue(pos * 1000)
