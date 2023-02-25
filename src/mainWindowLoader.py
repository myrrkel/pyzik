#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import functools

from PyQt5.QtCore import (
    Qt,
    QSettings,
    QCoreApplication,
    QItemSelectionModel,
    pyqtSignal,
    QSize,
)
from PyQt5.QtWidgets import (
    QTableWidgetItem,
    QShortcut,
    QHeaderView,
    QMenu,
    QAction,
    QAbstractItemView,
    QMainWindow,
    QSizePolicy,
)
from PyQt5.QtGui import (
    QPixmap,
    QIcon,
    QKeySequence,
    QCursor,
    QStandardItemModel,
    QStandardItem,
    QColor,
)

import mainWindow  # import of mainWindow.py made with pyuic5

from darkStyle import darkStyle
from playerVLC import vlc

from musicBase import MusicBase
from musicDirectory import MusicDirectory
from database import Database

from dialogMusicDirectoriesLoader import DialogMusicDirectoriesLoader
from streamObserver import StreamObserver
from artist import Artist
from album import Album
from albumThread import LoadAlbumFilesThread
from musicBaseThread import ExploreAlbumsDirectoriesThread
from playlistWidget import PlaylistWidget
from historyWidget import HistoryWidget
from searchRadioWidget import SearchRadioWidget
from fullScreenWidget import FullScreenWidget
from fullScreenCoverWidget import FullScreenCoverWidget
from playerControlWidget import PlayerControlWidget
from progressWidget import ProgressWidget
from albumWidget import AlbumWidget
from importAlbumsWidget import ImportAlbumsWidget
from exploreEventsWidget import ExploreEventList
from coverArtFinderDialog import CoverArtFinderDialog
from svgIcon import *
from picFromUrlThread import PicFromUrlThread
from picBufferManager import PicBufferManager
import logging

logger = logging.getLogger(__name__)
# orange = QtGui.QColor(216, 119, 0)
_translate = QCoreApplication.translate


def openFile(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])


class MainWindowLoader(QMainWindow):
    currentTrackChanged = pyqtSignal(str, name="currentTrackChanged")
    currentRadioChanged = pyqtSignal(int, name="currentRadioChanged")
    playlistChanged = pyqtSignal(int, name="playlistChanged")

    showPlayerControlEmited = pyqtSignal(str, name="showPlayerControlEmited")
    isPlayingSignal = pyqtSignal(int, name="isPlayingSignal")
    defaultPixmap = None

    def __init__(
        self, parent=None, app=None, music_base=None, player=None, translator=None
    ):
        QMainWindow.__init__(self, parent)

        self.app = app
        self.translator = translator
        self.music_base = music_base
        self.player = player

        self.picFromUrlThread = PicFromUrlThread()
        self.picBufferManager = PicBufferManager()

        self.settings = QSettings("pyzik", "pyzik")
        self.firstShow = True
        self.playList = None
        self.searchRadio = None
        self.histoWidget = None
        self.coverFinder = None
        self.import_album_widget = None

        self.coverPixmap = QtGui.QPixmap()
        if not self.defaultPixmap:
            self.defaultPixmap = getSvgWithColorParam("vinyl-record2.svg")

        self.fullScreenWidget = FullScreenWidget(self.player)
        self.fullScreenWidget.connectPicDownloader(self.picFromUrlThread)
        self.fullScreenWidget.defaultPixmap = self.defaultPixmap
        self.fullScreenWidget.picBufferManager = self.picBufferManager
        self.fullScreenCoverWidget = FullScreenCoverWidget()
        self.fullScreenCoverWidget.defaultPixmap = self.defaultPixmap
        self.fullScreenCoverWidget.picBufferManager = self.picBufferManager
        self.currentArtist = Artist("", 0)
        self.current_album = Album("")

        self.setWindowIcon(QtGui.QIcon(self.defaultPixmap))

        self.ui = mainWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.playerControl = PlayerControlWidget(self.player, self)
        self.playerControl.connectPicDownloader(self.picFromUrlThread)
        self.playerControl.defaultPixmap = self.defaultPixmap
        self.ui.verticalMainLayout.addWidget(self.playerControl)
        self.playerControl.hide()

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        self.playerControl.setSizePolicy(sizePolicy)

        self.initPlayerButtons()

        self.setTitleLabel("")
        self.setWindowTitle("Pyzik")

        self.initAlbumTableWidget()
        self.initTrackTableWidget()

        self.showGenres()
        self.showArtists()
        self.loadSettings()

        self.initRadioFavMenu()
        self.initExtraMenu()

        # Connect UI triggers
        self.ui.listViewArtists.selectionModel().currentChanged.connect(
            self.onArtistChange
        )
        self.ui.actionMusic_directories.triggered.connect(self.onMenuMusicDirectories)
        self.ui.actionExplore_music_directories.triggered.connect(self.onMenuExplore)
        self.ui.actionRandom_album.triggered.connect(self.ramdomAlbum)
        self.ui.actionDelete_database.triggered.connect(self.onMenuDeleteDatabase)
        self.ui.actionFuzzyGroovy.triggered.connect(self.onPlayFuzzyGroovy)
        self.ui.actionSearchRadio.triggered.connect(self.onPlaySearchRadio)
        self.ui.actionPlaylist.triggered.connect(self.showPlaylist)
        self.ui.actionHistory.triggered.connect(self.showHistory)
        self.ui.actionLanguageSpanish.triggered.connect(
            functools.partial(self.changeLanguage, "es")
        )
        self.ui.actionLanguageFrench.triggered.connect(
            functools.partial(self.changeLanguage, "fr")
        )
        self.ui.actionLanguageEnglish.triggered.connect(
            functools.partial(self.changeLanguage, "en")
        )
        self.ui.playButton.clicked.connect(self.onPlayAlbum)
        self.ui.addAlbumButton.clicked.connect(self.onAddAlbum)
        self.ui.searchCoverButton.clicked.connect(self.onSearchCoverAlbum)
        # self.ui.nextButton.clicked.connect(self.player.mediaListPlayer.next)
        self.ui.openDirButton.clicked.connect(self.onOpenDir)
        # self.ui.previousButton.clicked.connect(self.player.mediaListPlayer.previous)
        self.ui.searchEdit.textChanged.connect(self.filterArtists)
        self.ui.searchEdit.returnPressed.connect(self.onSearchEnter)
        self.ui.tableWidgetAlbums.selectionModel().currentRowChanged.connect(
            self.onAlbumChange
        )
        self.ui.tableWidgetAlbums.customContextMenuRequested.connect(
            self.handleHeaderAlbumsMenu
        )

        self.ui.comboBoxStyle.currentIndexChanged.connect(self.filterArtists)

        self.shortcutRandomAlbum = QShortcut(QtGui.QKeySequence("Ctrl+R"), self)
        self.shortcutRandomAlbum.activated.connect(self.ramdomAlbum)
        self.shortcutPlaylist = QShortcut(QtGui.QKeySequence("Ctrl+P"), self)
        self.shortcutPlaylist.activated.connect(self.showPlaylist)
        self.shortcutPause = QShortcut(QtGui.QKeySequence("Space"), self)
        self.shortcutPause.activated.connect(self.player.pause)
        self.shortcutFullScreen = QShortcut(QtGui.QKeySequence("Ctrl+F"), self)
        self.shortcutFullScreen.activated.connect(self.showFullScreen)

        # Connect VLC triggers
        self.player.mpEnventManager.event_attach(
            vlc.EventType.MediaPlayerMediaChanged, self.onPlayerMediaChangedVLC
        )
        self.player.mpEnventManager.event_attach(
            vlc.EventType.MediaPlayerPaused, self.paused
        )
        self.player.mpEnventManager.event_attach(
            vlc.EventType.MediaPlayerPlaying, self.isPlaying
        )
        self.player.mpEnventManager.event_attach(
            vlc.EventType.MediaPlayerPositionChanged, self.onPlayerPositionChanged
        )
        # self.player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerAudioVolume , self.setVolumeSliderFromPlayer)

        self.ui.volumeSlider.setVisible(False)

        self.playerControl.playerControls.volumeSlider.setMaximum(100)
        self.playerControl.playerControls.volumeSlider.setValue(self.volume)
        self.player.setVolume(self.volume)
        self.playerControl.playerControls.volumeSlider.valueChanged.connect(
            self.setVolume
        )

        # Write message in status bar
        # self.ui.statusBar.showMessage("Pyzik")

        self.threadStreamObserver = StreamObserver()
        self.threadStreamObserver.player = self.player
        self.threadStreamObserver.music_base = self.music_base
        self.threadStreamObserver.titleChanged.connect(
            self.onPlayerMediaChangedStreamObserver
        )
        self.player.mpEnventManager.event_attach(
            vlc.EventType.MediaPlayerStopped,
            self.threadStreamObserver.resetPreviousTitle,
        )
        self.threadStreamObserver.start()

        self.loadAlbumFilesThread = LoadAlbumFilesThread()
        self.loadAlbumFilesThread.setTerminationEnabled(True)
        self.loadAlbumFilesThread.imagesLoaded.connect(self.showAlbumCover)
        self.loadAlbumFilesThread.tracksLoaded.connect(self.showAlbumTracks)

        self.exploreAlbumsDirectoriesThread = ExploreAlbumsDirectoriesThread()

        self.ui.coverWidget.resizeEvent = self.resizeEvent
        self.ui.coverWidget.mouseDoubleClickEvent = self.coverMouseDoubleClickEvent

        self.currentTrackChanged.connect(self.onCurrentTrackChanged)
        self.showPlayerControlEmited.connect(self.showPlayerControl)

        self.ui.searchEdit.setFocus()

    def coverMouseDoubleClickEvent(self, event):
        self.showFullScreenCover()

    def showFullScreenCover(self):
        self.fullScreenCoverWidget.setPixmapFromUri(self.current_album.getCoverPath())
        self.fullScreenCoverWidget.show()

    def showEvent(self, event):
        # This function is called when the mainWindow is shown
        if self.firstShow == True:
            self.player.playlistChangedEvent = self.playlistChanged
            self.player.currentRadioChangedEvent = self.currentRadioChanged
            self.player.titleChangedEvent = self.currentTrackChanged
            self.ramdomAlbum()
            self.firstShow = False

    def onExploreCompleted(self, event):
        logger.debug("onExploreCompleted")
        events = self.music_base.musicDirectoryCol.getExploreEvents()
        # logger.debug("EXPLORE EVENTS=" + str([e.get_text() for e in events]))
        if events:
            self.open_explore_events_widget(events)
        self.music_base.db = Database()
        self.showArtists()
        self.showGenres()

    def open_explore_events_widget(self, events):
        if not hasattr(self, "explore_events_widget"):
            self.explore_events_widget = ExploreEventsWidget(
                self, self.music_base, events
            )
        else:
            self.explore_events_widget.items = events
        self.explore_events_widget.show()

    def onPlaySearchRadio(self):
        if self.searchRadio is None:
            self.searchRadio = SearchRadioWidget(self.music_base, self.player, self)
            self.searchRadio.radioAdded.connect(self.onAddFavRadio)

        self.searchRadio.show()
        self.searchRadio.activateWindow()

    def onAddFavRadio(self):
        # self.music_base.db.initDataBase()
        self.music_base.radioMan.loadFavRadios()
        self.initRadioFavMenu()

    def ramdomAlbum(self):
        styleID = self.ui.comboBoxStyle.currentData()
        alb = self.music_base.albumCol.get_random_album(styleID)
        self.current_album = alb
        if alb is not None:
            print("RamdomAlb=" + alb.title)
            art = self.music_base.artistCol.get_artist_by_id(alb.artistID)
            self.currentArtist = art
            self.selectArtistListView(art)
            self.showArtist(art)
            # self.showAlbum(alb)

    def open_import_album_widget(self):
        if not self.import_album_widget:
            self.import_album_widget = ImportAlbumsWidget(self, self.music_base)
        self.import_album_widget.show()

    def playRandomPlaylist(self):
        print("playRandomPlaylist")
        index = self.player.mediaList.count()
        styleID = self.ui.comboBoxStyle.currentData()
        albs = self.music_base.generateRandomAlbumList(10, styleID)
        i = 0
        for alb in albs:
            print("playRandomPlaylist=" + alb.title)
            alb.getImages()
            alb.getCover()
            alb.getTracks()
            self.addAlbum(alb)

        self.player.radioMode = False
        self.player.mediaListPlayer.play_item_at_index(index)

    def setVolume(self, volume):
        self.player.setVolume(volume)

    def getVolumeFromSlider(self):
        return self.playerControl.getVolume()

    def setVolumeSliderFromPlayer(self, event):
        volume = self.player.getVolume()
        self.playerControl.setVolume(volume)

    def onPlayerPositionChanged(self, event=None):
        self.playerControl.onPlayerPositionChanged(event)
        if self.playList is not None:
            self.playList.onPlayerPositionChanged(event)

    def paused(self, event):
        print("Paused!")

    def showPlayerControl(self, event):
        self.playerControl.show()

    def isPlaying(self, event):
        print("isPlaying!")
        self.isPlayingSignal.emit(self.player.isPlaying())
        self.showPlayerControlEmited.emit("")

    """
    Init widgets
    """

    def initAlbumTableWidget(self):
        self.ui.tableWidgetAlbums.setRowCount(0)
        hHeader = self.ui.tableWidgetAlbums.horizontalHeader()
        vHeader = self.ui.tableWidgetAlbums.verticalHeader()
        vHeader.hide()
        hHeader.setSectionResizeMode(0, QHeaderView.Stretch)
        hHeader.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hHeader.hideSection(2)

    def initTrackTableWidget(self):
        self.ui.tableWidgetTracks.setRowCount(0)
        hHeader = self.ui.tableWidgetTracks.horizontalHeader()
        vHeader = self.ui.tableWidgetTracks.verticalHeader()
        vHeader.hide()
        hHeader.setSectionResizeMode(0, QHeaderView.Stretch)
        hHeader.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hHeader.hideSection(2)

    def initExtraMenu(self):
        if not hasattr(self.ui, "actionRandomPlaylist"):
            self.ui.actionRandomPlaylist = QAction(self.ui.menuAlbums)
            self.ui.actionRandomPlaylist.triggered.connect(self.playRandomPlaylist)
            self.ui.menuAlbums.addAction(self.ui.actionRandomPlaylist)
        self.ui.actionRandomPlaylist.setText(_translate("menu", "Random playlist"))

        if not hasattr(self.ui, "action_open_import_album_widget"):
            self.ui.action_open_import_album_widget = QAction(self.ui.menuAlbums)
            self.ui.action_open_import_album_widget.triggered.connect(
                self.open_import_album_widget
            )
            self.ui.menuAlbums.addAction(self.ui.action_open_import_album_widget)
        self.ui.action_open_import_album_widget.setText(
            _translate("menu", "Import albums")
        )

    def initRadioFavMenu(self):
        if not hasattr(self.ui, "menuFavRadios"):
            self.ui.menuFavRadios = QMenu(self.ui.menuRadios)
        else:
            for action in self.ui.menuFavRadios.actions():
                self.ui.menuFavRadios.removeAction(action)

        for rad in self.music_base.radioMan.favRadios:
            self.ui.actionFavRadio = QAction(self.ui.menuFavRadios)
            self.ui.actionFavRadio.setObjectName("actionFavRadio_" + rad.name)
            self.ui.actionFavRadio.setText(rad.name)
            self.ui.menuFavRadios.addAction(self.ui.actionFavRadio)
            self.ui.actionFavRadio.triggered.connect(
                functools.partial(self.onPlayFavRadio, rad.radioID)
            )

        self.ui.menuRadios.addAction(self.ui.menuFavRadios.menuAction())
        self.ui.menuFavRadios.setTitle(_translate("radio", "Favorite radios"))

    """
    Menu Actions
    """

    def onMenuMusicDirectories(self):
        self.music_base.db = Database()
        dirDiag = DialogMusicDirectoriesLoader(self.music_base, self)
        dirDiag.show()
        dirDiag.exec_()

    def onPlayFuzzyGroovy(self):
        fg = self.music_base.radioMan.getFuzzyGroovy()
        self.playRadio(fg)

    def onPlayFavRadio(self, radioID):
        rad = self.music_base.radioMan.getFavRadio(radioID)
        self.playRadio(rad)

    def playRadio(self, radio):
        self.playerControl.setTitleLabel(radio.name)
        self.playerControl.showWaitingOverlay()
        self.player.playRadioInThread(radio)

    def onMenuExplore(self):
        self.exploreAlbumsDirectoriesThread.music_base = self.music_base
        self.wProgress = ProgressWidget(self)
        self.exploreAlbumsDirectoriesThread.progressChanged.connect(
            self.wProgress.setValue
        )
        self.exploreAlbumsDirectoriesThread.directoryChanged.connect(
            self.wProgress.setDirectoryText
        )
        self.exploreAlbumsDirectoriesThread.exploreCompleted.connect(
            self.wProgress.close
        )
        self.exploreAlbumsDirectoriesThread.exploreCompleted.connect(
            self.onExploreCompleted
        )
        self.wProgress.progressClosed.connect(self.exploreAlbumsDirectoriesThread.stop)
        self.exploreAlbumsDirectoriesThread.start()

    def onMenuDeleteDatabase(self):
        self.music_base.db.createConnection()
        self.music_base.db.dropAllTables()
        self.music_base.emptyDatas()
        self.music_base.db.initDataBase()
        self.showArtists()
        self.initAlbumTableWidget()
        self.initAlbumView()

    def handleHeaderAlbumsMenu(self, pos):
        # print('column(%d)' % self.ui.tableWidgetAlbums.horizontalHeader().logicalIndexAt(pos))
        menu = QMenu()
        actionEditAlbum = QAction(menu)
        actionEditAlbum.setObjectName("actionEditAlbum")
        actionEditAlbum.setText(_translate("album", "Edit"))
        menu.addAction(actionEditAlbum)
        # actionEditAlbum.triggered.connect(functools.partial(self.onPlayFavRadio, rad.radioID))
        actionEditAlbum.triggered.connect(self.onEditAlbum)

        menu.exec(QtGui.QCursor.pos())

    def onEditAlbum(self):
        selRows = self.ui.tableWidgetAlbums.selectionModel().selectedRows()
        if len(selRows) >= 0:
            albumIDSel = self.ui.tableWidgetAlbums.item(selRows[0].row(), 2).text()
            alb = self.music_base.albumCol.getAlbum(albumIDSel)
            if alb.albumID != 0:
                self.editAlbumWidget = albumWidget(alb, self)
                self.editAlbumWidget.show()
            else:
                print("No album to edit")

    """
    Genre comboBox functions
    """

    def showGenres(self):
        self.ui.comboBoxStyle.clear()
        self.ui.comboBoxStyle.addItem(_translate("playlist", "All styles"), -2)

        idSet = self.music_base.musicDirectoryCol.getStyleIDSet()
        for genre in self.music_base.genres.getAvailableGenresFormIDSet(idSet):
            self.ui.comboBoxStyle.addItem(genre[0], genre[1])

    def onChangeGenre(self):
        genreID = self.ui.comboBoxStyle.currentData()

        if genreID < 0:
            self.setHiddenAllArtistItem(False)
        else:
            self.setHiddenAllArtistItem(True)

            model = self.ui.listViewArtists.model()
            for i in range(model.rowCount()):
                itemArt = model.item(i)
                if genreID in itemArt.artist.styleIDSet:
                    i = itemArt.row()
                    self.ui.listViewArtists.setRowHidden(i, False)

    """
    Artist listView functions
    """

    def showArtists(self):
        # Add artists in the QListView
        model = QtGui.QStandardItemModel(self.ui.listViewArtists)
        for art in self.music_base.artistCol.artists:
            itemArt = QtGui.QStandardItem(art.name)
            itemArt.artist = art
            art.itemListViewArtist = itemArt
            model.appendRow(itemArt)

        self.ui.listViewArtists.setModel(model)
        self.ui.listViewArtists.show()
        self.ui.listViewArtists.selectionModel().currentChanged.connect(
            self.onArtistChange
        )

    def setHiddenAllArtistItem(self, hide):
        # Hide all artists
        model = self.ui.listViewArtists.model()
        for i in range(model.rowCount()):
            self.ui.listViewArtists.setRowHidden(i, hide)

    def getFirstVisibleArtistItem(self):
        model = self.ui.listViewArtists.model()
        for i in range(model.rowCount()):
            if not self.ui.listViewArtists.isRowHidden(i):
                return model.item(i)

    def onArtistChange(self, item):
        # When call from listView, item is a QModelIndex
        nrow = item.row()

        model = self.ui.listViewArtists.model()
        if self.currentArtist.artistID != model.item(nrow).artist.artistID:
            self.showArtist(model.item(nrow).artist)

    def selectArtistListView(self, artist):
        item = artist.itemListViewArtist

        selModel = self.ui.listViewArtists.selectionModel()
        selModel.reset()
        selModel.select(item.index(), QItemSelectionModel.SelectCurrent)

        self.ui.listViewArtists.scrollTo(
            item.index(), QAbstractItemView.PositionAtCenter
        )

    """
    Search artist functions
    """

    def onSearchEnter(self):
        # After typing, the user hit enter
        # to select the first artist found
        item = self.getFirstVisibleArtistItem()
        if item is not None:
            selModel = self.ui.listViewArtists.selectionModel()
            selModel.reset()
            selModel.select(item.index(), QItemSelectionModel.Select)
            self.showArtist(item.artist)

    def onSearchChange(self, event):
        # When user write a search, shows only matching artists
        search = self.ui.searchEdit.text()

        if len(search) == 0:
            self.setHiddenAllArtistItem(False)
        else:
            self.setHiddenAllArtistItem(True)
            items = self.ui.listViewArtists.model().findItems(search, Qt.MatchContains)
            for item in items:
                i = item.row()
                self.ui.listViewArtists.setRowHidden(i, False)

    def filterArtists(self):
        genreID = self.ui.comboBoxStyle.currentData()
        search = self.ui.searchEdit.text()

        if (genreID is None or genreID == -2) and search == "":
            self.setHiddenAllArtistItem(False)
        else:
            # self.setHiddenAllArtistItem(True)

            model = self.ui.listViewArtists.model()
            for i in range(model.rowCount()):
                itemArt = model.item(i)
                i = itemArt.row()
                if (genreID == -2 or genreID in itemArt.artist.styleIDSet) and (
                    search.upper() in itemArt.artist.name.upper() or search == ""
                ):
                    self.ui.listViewArtists.setRowHidden(i, False)
                else:
                    self.ui.listViewArtists.setRowHidden(i, True)

    """
    Album tableWidget functions
    """

    def getAlbumFromTable(self):
        # Return the selected album
        selAlbItems = self.ui.tableWidgetAlbums.selectedItems()
        for item in selAlbItems:
            r = item.row()
            albumIDSel = self.ui.tableWidgetAlbums.item(r, 2).text()

            alb = self.music_base.albumCol.getAlbum(albumIDSel)
            if alb.albumID == 0:
                print("Album is Empty. Item:" + str(item))
            return alb

    def onAlbumChange(self, item):
        if item.row() >= 0:
            albumIDSel = self.ui.tableWidgetAlbums.item(item.row(), 2).text()
            alb = self.music_base.albumCol.getAlbum(albumIDSel)
            if alb.albumID != 0:
                self.showAlbum(alb)
            else:
                print("No album to show")

    def showArtist(self, artist):
        self.currentArtist = artist
        self.showAlbums(self.currentArtist)

    def showAlbums(self, artist):
        # Add albums in the QTableView
        if artist == None:
            return
        print("Show albums Art=" + artist.name)
        self.ui.tableWidgetAlbums.setRowCount(0)
        if len(artist.albums) == 0:
            return

        if self.current_album is None:
            self.current_album = artist.getRandomAlbum()

        if self.current_album.artistID != artist.artistID:
            self.current_album = artist.getRandomAlbum()

        indexToSel = 0
        i = 0
        artist.sortAlbums()
        for alb in artist.albums:
            self.ui.tableWidgetAlbums.insertRow(i)

            titleItem = QTableWidgetItem(alb.title)
            titleItem.setFlags(titleItem.flags() ^ Qt.ItemIsEditable)
            self.ui.tableWidgetAlbums.setItem(i, 0, titleItem)

            yearItem = QTableWidgetItem(str(alb.year))
            yearItem.setFlags(yearItem.flags() ^ Qt.ItemIsEditable)
            self.ui.tableWidgetAlbums.setItem(i, 1, yearItem)

            idItem = QTableWidgetItem(str(alb.albumID))
            idItem.setFlags(idItem.flags() ^ Qt.ItemIsEditable)
            self.ui.tableWidgetAlbums.setItem(i, 2, idItem)

            if alb.albumID == self.current_album.albumID:
                indexToSel = i

            i += 1

        self.ui.tableWidgetAlbums.selectRow(indexToSel)
        self.ui.tableWidgetAlbums.scrollTo(
            self.ui.tableWidgetAlbums.currentIndex(), QAbstractItemView.PositionAtCenter
        )

    def initAlbumView(self):
        self.current_album = None
        self.ui.labelArtist.setText("")
        self.ui.tableWidgetTracks.setRowCount(0)
        self.showCover("")

    def showAlbum(self, album):
        print(
            "showAlbum: "
            + album.title
            + " size="
            + str(album.size)
            + " length="
            + str(album.length)
        )
        self.current_album = album
        self.setTitleLabel(self.currentArtist.name, album.title, album.year)
        self.ui.tableWidgetTracks.setRowCount(0)

        # Start a thread to load album datas from directory
        # When updated, triggers launch showAlbumCover and showAlbumTracks
        if self.loadAlbumFilesThread.isRunning():
            print("Stop Thread loadAlbum")
            self.loadAlbumFilesThread.stop()
            self.loadAlbumFilesThread.wait()

        self.loadAlbumFilesThread.album = album
        self.loadAlbumFilesThread.player = self.player
        self.loadAlbumFilesThread.start()

    def showAlbumTracks(self, result):
        # self.ui.tableWidgetTracks.setColumnCount(1)
        self.ui.tableWidgetTracks.setRowCount(0)
        i = 0
        for track in self.current_album.tracks:
            self.ui.tableWidgetTracks.insertRow(i)

            titleItem = QTableWidgetItem(track.title)
            titleItem.setFlags(titleItem.flags() ^ Qt.ItemIsEditable)
            self.ui.tableWidgetTracks.setItem(i, 0, titleItem)

            durationItem = QTableWidgetItem(track.getDurationText())
            durationItem.setFlags(durationItem.flags() ^ Qt.ItemIsEditable)
            self.ui.tableWidgetTracks.setItem(i, 1, durationItem)

            i += 1

    def showAlbumCover(self, result):
        print("showAlbumCover= " + str(result) + " - " + self.current_album.cover)
        album = self.current_album
        if album is None:
            return
        if album.cover != "":
            # coverPixmap = album.getCoverPixmap()
            self.showCover(album.getCoverPath())
        else:
            self.showCover("")

    """
    Interactions with vlc module
    """

    def playAlbum(self, alb):
        """Add tracks in playlist and start playing"""

        self.music_base.history.insertAlbumHistory(alb.albumID)
        self.player.playAlbum(alb)

        self.setVolume(self.getVolumeFromSlider())

    def addAlbum(self, alb):
        """Add tracks in playlist and start playing"""
        self.player.addAlbum(alb)
        self.setVolume(self.getVolumeFromSlider())

    def showPlaylist(self, showOnlyIfNew=False):
        isNew = False
        if self.playList is None:
            isNew = True
            self.playList = PlaylistWidget(self.player, self)
            self.playList.picBufferManager = self.picBufferManager
            self.playList.fullScreenWidget = self.fullScreenWidget
            self.playList.connectPicDownloader(self.picFromUrlThread)
            self.playList.trackChanged.connect(self.player.setPlaylistTrack)
            self.playList.currentRadioChanged = self.currentRadioChanged
            self.player.playlistChangedEvent = self.playlistChanged
            self.playList.playlistChanged = self.playlistChanged

        self.playList.showMediaList()

        if isNew or showOnlyIfNew == False:
            self.playList.show()
            self.playList.activateWindow()

    def showHistory(self):
        if self.histoWidget is None:
            self.histoWidget = HistoryWidget(self.music_base, self)

        self.histoWidget.show()
        self.histoWidget.activateWindow()

    def showFullScreen(self):
        print("showFullScreen")
        if self.fullScreenWidget is None:
            self.fullScreenWidget = FullScreenWidget(self.player)

        self.fullScreenWidget.show()
        self.fullScreenWidget.activateWindow()

    def onCurrentTrackChanged(self, event=None):
        logger.debug("onCurrentTrackChanged %s", event)
        if not self.player.radioMode:
            title = None
            trk = self.player.getCurrentTrackPlaylist()
            if trk is not None and trk.parentAlbum is not None:
                self.music_base.history.insertTrackHistory(
                    trk.parentAlbum.albumID, trk.getFilePathInAlbumDir()
                )
        else:
            if not event:
                return
            title = event
            if not title in ["...", "", "-"]:
                self.music_base.history.insertRadioHistory(
                    self.player.currentRadioName, title
                )

        if self.playList is not None:
            self.playList.setCurrentTrack(title)
        if self.fullScreenWidget is not None:
            self.fullScreenWidget.setCurrentTrack(title)
        # if self.playerControl is not None:
        #    self.playerControl.setCurrentTrackInThread(title)

    def onPlayerMediaChangedVLC(self, event):
        print("onPlayerMediaChangedVLC")
        self.currentTrackChanged.emit("")

    def onPlayerMediaChangedStreamObserver(self, title):
        print("onPlayerMediaChangedStreamObserver=" + title)
        self.currentTrackChanged.emit(title)

    def onPlayAlbum(self, item):
        if self.current_album:
            print("onPlayAlbum " + self.current_album.get_album_dir())
            self.playAlbum(self.current_album)

    def onAddAlbum(self, item):
        if self.current_album:
            print("onAddAlbum " + self.current_album.get_album_dir())
            self.addAlbum(self.current_album)

    def onSearchCoverAlbum(self):
        self.coverFinder = CoverArtFinderDialog(self.current_album, self)
        self.coverFinder.signalCoverSaved.connect(self.showAlbumCover)
        self.coverFinder.show()

    def onOpenDir(self):
        if self.current_album:
            openFile(self.current_album.get_album_dir())

    """
    Miscellaneous UI functions 
    """

    def setTitleLabel(self, artName="", albTitle="", year=""):
        if self.currentArtist is not None and artName == "":
            artName = self.currentArtist.name
        if self.current_album is not None and albTitle == "":
            albTitle = self.current_album.title
            year = self.current_album.year

        sAlbum = albTitle
        sYear = str(year)
        if not sYear in ["0", ""]:
            sAlbum += " (" + sYear + ")"
        sTitle = """<html><head/><body>
        <p><span style=\" font-size:14pt; font-weight:600;\">{Artist}</span></p>
        <p><span style=\" font-style:italic;\">{Album}</span></p>
        </body></html>"""
        sTitle = sTitle.format(Artist=artName, Album=sAlbum)

        self.ui.labelArtist.setText(sTitle)

    def showCover(self, path, pCoverPixmap=None):
        if path == "":
            self.coverPixmap = self.defaultPixmap
        else:
            print("MyCover=" + path)
            self.coverPixmap = self.picBufferManager.getPic(path, "main.albCover")

        scaledCover = self.coverPixmap.scaled(
            self.ui.cover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.ui.cover.setPixmap(scaledCover)
        self.ui.cover.show()

    def resizeEvent(self, event):
        self.resizeCover()

    def resizeCover(self):
        if not self.coverPixmap.isNull():
            scaledCover = self.coverPixmap.scaled(
                self.ui.cover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.ui.cover.setPixmap(scaledCover)

    def initPlayerButtons(self):
        self.ui.searchCoverButton.setText(_translate("coverArtFinder", "Cover finder"))
        self.ui.playButton.setToolTip(self.ui.playButton.text())
        self.ui.openDirButton.setToolTip(self.ui.openDirButton.text())
        self.ui.addAlbumButton.setToolTip(self.ui.addAlbumButton.text())
        self.ui.searchCoverButton.setToolTip(self.ui.searchCoverButton.text())

        self.ui.playButton.setText("")
        self.ui.openDirButton.setText("")
        self.ui.addAlbumButton.setText("")
        self.ui.searchCoverButton.setText("")

        self.ui.playButton.setIcon(getSvgIcon("play-circle.svg"))
        self.ui.addAlbumButton.setIcon(getSvgIcon("add_music.svg"))
        self.ui.openDirButton.setIcon(getSvgIcon("folder-open.svg"))
        self.ui.searchCoverButton.setIcon(getSvgIcon("picture.svg"))

        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(True)

        self.ui.playButton.setSizePolicy(sizePolicy)
        self.ui.openDirButton.setSizePolicy(sizePolicy)
        self.ui.addAlbumButton.setSizePolicy(sizePolicy)
        self.ui.searchCoverButton.setSizePolicy(sizePolicy)

        self.ui.playButton.setMaximumSize(QSize(40, 25))
        self.ui.openDirButton.setMaximumSize(QSize(40, 25))
        self.ui.addAlbumButton.setMaximumSize(QSize(40, 25))
        self.ui.searchCoverButton.setMaximumSize(QSize(40, 25))

        self.ui.playButton.setMinimumSize(QSize(27, 27))
        self.ui.openDirButton.setMinimumSize(QSize(27, 27))
        self.ui.addAlbumButton.setMinimumSize(QSize(27, 27))
        self.ui.searchCoverButton.setMinimumSize(QSize(27, 27))

    def closeEvent(self, event):
        if self.playList is not None:
            self.playList.close()
        if self.histoWidget is not None:
            self.histoWidget.close()
        if self.searchRadio is not None:
            self.searchRadio.close()
        if self.coverFinder is not None:
            self.coverFinder.close()
        self.saveSettings()

    def saveSettings(self):
        if self.player is not None:
            curVolume = self.player.getVolume()
        else:
            curVolume = self.volume

        if curVolume is not None and curVolume > 0:
            self.settings.setValue("volume", curVolume)

    def loadSettings(self):
        if self.settings.contains("volume"):
            self.volume = self.settings.value("volume", type=int)
        else:
            self.volume = 100

    def changeLanguage(self, locale):
        # translator for built-in qt strings
        self.translator.unInstallTranslators()
        self.translator.installTranslators(locale)
        self.retranslateUi()
        self.initPlayerButtons()
        if self.playList is not None:
            self.playList.retranslateUi()
        if self.histoWidget is not None:
            self.histoWidget.retranslateUi()
        if self.searchRadio is not None:
            self.searchRadio.retranslateUi()
        if self.playerControl is not None:
            self.playerControl.retranslateUi()
        if self.coverFinder is not None:
            self.coverFinder.retranslateUi()
        if self.import_album_widget is not None:
            self.import_album_widget.retranslateUi()

        self.update()
        self.setWindowTitle("Pyzik")
        self.setTitleLabel()

    def retranslateUi(self):
        self.ui.menuFavRadios.setTitle(_translate("radio", "Favorite radios"))
        self.initExtraMenu()
        self.ui.searchCoverButton.setText(_translate("coverArtFinder", "Cover finder"))
        self.ui.retranslateUi(self)


if __name__ == "__main__":
    from pyzik import *

    main()
