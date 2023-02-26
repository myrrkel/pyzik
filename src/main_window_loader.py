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

from main_window import Ui_MainWindow

from darkStyle import darkStyle
from player_vlc import vlc

from music_base import MusicBase
from music_directory import MusicDirectory
from database import Database

from dialog_music_directories_loader import DialogMusicDirectoriesLoader
from stream_observer import StreamObserver
from artist import Artist
from album import Album
from album_thread import LoadAlbumFilesThread
from music_base_thread import ExploreAlbumsDirectoriesThread
from playlist_widget import PlaylistWidget
from history_widget import HistoryWidget
from search_radio_widget import SearchRadioWidget
from full_screen_widget import FullScreenWidget
from full_screen_cover_widget import FullScreenCoverWidget
from player_control_widget import PlayerControlWidget
from progress_widget import ProgressWidget
from album_widget import AlbumWidget
from import_albums_widget import ImportAlbumsWidget
from explore_events_widget import ExploreEventList, ExploreEventsWidget
from cover_art_finder_dialog import CoverArtFinderDialog
from svg_icon import *
from pic_from_url_thread import PicFromUrlThread
from pic_buffer_manager import PicBufferManager
import logging

logger = logging.getLogger(__name__)
# orange = QtGui.QColor(216, 119, 0)
_translate = QCoreApplication.translate


def open_file(filename):
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
            self.defaultPixmap = get_svg_with_color_param("vinyl-record2.svg")

        self.fullScreenWidget = FullScreenWidget(self.player)
        self.fullScreenWidget.connect_pic_downloader(self.picFromUrlThread)
        self.fullScreenWidget.defaultPixmap = self.defaultPixmap
        self.fullScreenWidget.picBufferManager = self.picBufferManager
        self.fullScreenCoverWidget = FullScreenCoverWidget()
        self.fullScreenCoverWidget.defaultPixmap = self.defaultPixmap
        self.fullScreenCoverWidget.picBufferManager = self.picBufferManager
        self.currentArtist = Artist("", 0)
        self.current_album = Album("")

        self.setWindowIcon(QtGui.QIcon(self.defaultPixmap))

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.playerControl = PlayerControlWidget(self.player, self)
        self.playerControl.connect_pic_downloader(self.picFromUrlThread)
        self.playerControl.defaultPixmap = self.defaultPixmap
        self.ui.verticalMainLayout.addWidget(self.playerControl)
        self.playerControl.hide()

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        self.playerControl.setSizePolicy(sizePolicy)

        self.init_player_buttons()

        self.set_title_label("")
        self.setWindowTitle("Pyzik")

        self.init_album_table_widget()
        self.init_track_table_widget()

        self.show_genres()
        self.show_artists()
        self.load_settings()

        self.init_radio_fav_menu()
        self.init_extra_menu()

        # Connect UI triggers
        self.ui.listViewArtists.selectionModel().currentChanged.connect(
            self.on_artist_change
        )
        self.ui.actionMusic_directories.triggered.connect(self.on_menu_music_directories)
        self.ui.actionExplore_music_directories.triggered.connect(self.on_menu_explore)
        self.ui.actionRandom_album.triggered.connect(self.ramdom_album)
        self.ui.actionDelete_database.triggered.connect(self.on_menu_delete_database)
        self.ui.actionFuzzyGroovy.triggered.connect(self.on_play_fuzzy_groovy)
        self.ui.actionSearchRadio.triggered.connect(self.on_play_search_radio)
        self.ui.actionPlaylist.triggered.connect(self.show_playlist)
        self.ui.actionHistory.triggered.connect(self.show_history)
        self.ui.actionLanguageSpanish.triggered.connect(
            functools.partial(self.change_language, "es")
        )
        self.ui.actionLanguageFrench.triggered.connect(
            functools.partial(self.change_language, "fr")
        )
        self.ui.actionLanguageEnglish.triggered.connect(
            functools.partial(self.change_language, "en")
        )
        self.ui.playButton.clicked.connect(self.on_play_album)
        self.ui.addAlbumButton.clicked.connect(self.on_add_album)
        self.ui.searchCoverButton.clicked.connect(self.on_search_cover_album)
        # self.ui.nextButton.clicked.connect(self.player.mediaListPlayer.next)
        self.ui.openDirButton.clicked.connect(self.on_open_dir)
        # self.ui.previousButton.clicked.connect(self.player.mediaListPlayer.previous)
        self.ui.searchEdit.textChanged.connect(self.filter_artists)
        self.ui.searchEdit.returnPressed.connect(self.on_search_enter)
        self.ui.tableWidgetAlbums.selectionModel().currentRowChanged.connect(
            self.on_album_change
        )
        self.ui.tableWidgetAlbums.customContextMenuRequested.connect(
            self.handle_header_albums_menu
        )

        self.ui.comboBoxStyle.currentIndexChanged.connect(self.filter_artists)

        self.shortcutRandomAlbum = QShortcut(QtGui.QKeySequence("Ctrl+R"), self)
        self.shortcutRandomAlbum.activated.connect(self.ramdom_album)
        self.shortcutPlaylist = QShortcut(QtGui.QKeySequence("Ctrl+P"), self)
        self.shortcutPlaylist.activated.connect(self.show_playlist)
        self.shortcutPause = QShortcut(QtGui.QKeySequence("Space"), self)
        self.shortcutPause.activated.connect(self.player.pause)
        self.shortcutFullScreen = QShortcut(QtGui.QKeySequence("Ctrl+F"), self)
        self.shortcutFullScreen.activated.connect(self.showFullScreen)

        # Connect VLC triggers
        self.player.mpEnventManager.event_attach(
            vlc.EventType.MediaPlayerMediaChanged, self.on_player_media_changed_vlc
        )
        self.player.mpEnventManager.event_attach(
            vlc.EventType.MediaPlayerPaused, self.paused
        )
        self.player.mpEnventManager.event_attach(
            vlc.EventType.MediaPlayerPlaying, self.is_playing
        )
        self.player.mpEnventManager.event_attach(
            vlc.EventType.MediaPlayerPositionChanged, self.on_player_position_changed
        )
        # self.player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerAudioVolume , self.setVolumeSliderFromPlayer)

        self.ui.volumeSlider.setVisible(False)

        self.playerControl.playerControls.volumeSlider.setMaximum(100)
        self.playerControl.playerControls.volumeSlider.setValue(self.volume)
        self.player.set_volume(self.volume)
        self.playerControl.playerControls.volumeSlider.valueChanged.connect(
            self.set_volume
        )

        # Write message in status bar
        # self.ui.statusBar.showMessage("Pyzik")

        self.threadStreamObserver = StreamObserver()
        self.threadStreamObserver.player = self.player
        self.threadStreamObserver.music_base = self.music_base
        self.threadStreamObserver.titleChanged.connect(
            self.on_player_media_changed_stream_observer
        )
        self.player.mpEnventManager.event_attach(
            vlc.EventType.MediaPlayerStopped,
            self.threadStreamObserver.reset_previous_title,
        )
        self.threadStreamObserver.start()

        self.loadAlbumFilesThread = LoadAlbumFilesThread()
        self.loadAlbumFilesThread.setTerminationEnabled(True)
        self.loadAlbumFilesThread.imagesLoaded.connect(self.show_album_cover)
        self.loadAlbumFilesThread.tracksLoaded.connect(self.show_album_tracks)

        self.exploreAlbumsDirectoriesThread = ExploreAlbumsDirectoriesThread()

        self.ui.coverWidget.resizeEvent = self.resizeEvent
        self.ui.coverWidget.mouseDoubleClickEvent = self.cover_mouse_double_click_event

        self.currentTrackChanged.connect(self.on_current_track_changed)
        self.showPlayerControlEmited.connect(self.show_player_control)

        self.ui.searchEdit.setFocus()

    def cover_mouse_double_click_event(self, event):
        self.show_full_screen_cover()

    def show_full_screen_cover(self):
        self.fullScreenCoverWidget.set_pixmap_from_uri(self.current_album.get_cover_path())
        self.fullScreenCoverWidget.show()

    def showEvent(self, event):
        # This function is called when the mainWindow is shown
        if self.firstShow == True:
            self.player.playlistChangedEvent = self.playlistChanged
            self.player.currentRadioChangedEvent = self.currentRadioChanged
            self.player.titleChangedEvent = self.currentTrackChanged
            self.ramdom_album()
            self.firstShow = False

    def on_explore_completed(self, event):
        logger.debug("onExploreCompleted")
        events = self.music_base.musicDirectoryCol.get_explore_events()
        # logger.debug("EXPLORE EVENTS=" + str([e.get_text() for e in events]))
        if events:
            self.open_explore_events_widget(events)
        self.music_base.db = Database()
        self.show_artists()
        self.show_genres()

    def open_explore_events_widget(self, events):
        if not hasattr(self, "explore_events_widget"):
            self.explore_events_widget = ExploreEventsWidget(
                self, self.music_base, events
            )
        else:
            self.explore_events_widget.items = events
        self.explore_events_widget.show()

    def on_play_search_radio(self):
        if self.searchRadio is None:
            self.searchRadio = SearchRadioWidget(self.music_base, self.player, self)
            self.searchRadio.radioAdded.connect(self.on_add_fav_radio)

        self.searchRadio.show()
        self.searchRadio.activateWindow()

    def on_add_fav_radio(self):
        # self.music_base.db.initDataBase()
        self.music_base.radioMan.load_fav_radios()
        self.init_radio_fav_menu()

    def ramdom_album(self):
        styleID = self.ui.comboBoxStyle.currentData()
        alb = self.music_base.albumCol.get_random_album(styleID)
        self.current_album = alb
        if alb is not None:
            print("RamdomAlb=" + alb.title)
            art = self.music_base.artistCol.get_artist_by_id(alb.artist_id)
            self.currentArtist = art
            self.select_artist_list_view(art)
            self.show_artist(art)
            # self.showAlbum(alb)

    def open_import_album_widget(self):
        if not self.import_album_widget:
            self.import_album_widget = ImportAlbumsWidget(self, self.music_base)
        self.import_album_widget.show()

    def play_random_playlist(self):
        print("playRandomPlaylist")
        index = self.player.mediaList.count()
        styleID = self.ui.comboBoxStyle.currentData()
        albs = self.music_base.generate_random_album_list(10, styleID)
        i = 0
        for alb in albs:
            print("playRandomPlaylist=" + alb.title)
            alb.get_images()
            alb.get_cover()
            alb.get_tracks()
            self.add_album(alb)

        self.player.radioMode = False
        self.player.mediaListPlayer.play_item_at_index(index)

    def set_volume(self, volume):
        self.player.set_volume(volume)

    def get_volume_from_slider(self):
        return self.playerControl.get_volume_slider()

    def set_volume_slider_from_player(self, event):
        volume = self.player.get_volume()
        self.playerControl.set_volume(volume)

    def on_player_position_changed(self, event=None):
        self.playerControl.on_player_position_changed(event)
        if self.playList is not None:
            self.playList.on_player_position_changed(event)

    def paused(self, event):
        print("Paused!")

    def show_player_control(self, event):
        self.playerControl.show()

    def is_playing(self, event):
        print("isPlaying!")
        self.isPlayingSignal.emit(self.player.is_playing())
        self.showPlayerControlEmited.emit("")

    """
    Init widgets
    """

    def init_album_table_widget(self):
        self.ui.tableWidgetAlbums.setRowCount(0)
        hHeader = self.ui.tableWidgetAlbums.horizontalHeader()
        vHeader = self.ui.tableWidgetAlbums.verticalHeader()
        vHeader.hide()
        hHeader.setSectionResizeMode(0, QHeaderView.Stretch)
        hHeader.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hHeader.hideSection(2)

    def init_track_table_widget(self):
        self.ui.tableWidgetTracks.setRowCount(0)
        hHeader = self.ui.tableWidgetTracks.horizontalHeader()
        vHeader = self.ui.tableWidgetTracks.verticalHeader()
        vHeader.hide()
        hHeader.setSectionResizeMode(0, QHeaderView.Stretch)
        hHeader.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hHeader.hideSection(2)

    def init_extra_menu(self):
        if not hasattr(self.ui, "actionRandomPlaylist"):
            self.ui.actionRandomPlaylist = QAction(self.ui.menuAlbums)
            self.ui.actionRandomPlaylist.triggered.connect(self.play_random_playlist)
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

    def init_radio_fav_menu(self):
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
                functools.partial(self.on_play_fav_radio, rad.radioID)
            )

        self.ui.menuRadios.addAction(self.ui.menuFavRadios.menuAction())
        self.ui.menuFavRadios.setTitle(_translate("radio", "Favorite radios"))

    """
    Menu Actions
    """

    def on_menu_music_directories(self):
        self.music_base.db = Database()
        dirDiag = DialogMusicDirectoriesLoader(self.music_base, self)
        dirDiag.show()
        dirDiag.exec_()

    def on_play_fuzzy_groovy(self):
        fg = self.music_base.radioMan.get_fuzzy_groovy()
        self.play_radio(fg)

    def on_play_fav_radio(self, radioID):
        rad = self.music_base.radioMan.get_fav_radio(radioID)
        self.play_radio(rad)

    def play_radio(self, radio):
        self.playerControl.set_title_label(radio.name)
        self.playerControl.show_waiting_overlay()
        self.player.play_radio_in_thread(radio)

    def on_menu_explore(self):
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
            self.on_explore_completed
        )
        self.wProgress.progressClosed.connect(self.exploreAlbumsDirectoriesThread.stop)
        self.exploreAlbumsDirectoriesThread.start()

    def on_menu_delete_database(self):
        self.music_base.db.create_connection()
        self.music_base.db.drop_all_tables()
        self.music_base.empty_datas()
        self.music_base.db.init_data_base()
        self.show_artists()
        self.init_album_table_widget()
        self.init_album_view()

    def handle_header_albums_menu(self, pos):
        # print('column(%d)' % self.ui.tableWidgetAlbums.horizontalHeader().logicalIndexAt(pos))
        menu = QMenu()
        actionEditAlbum = QAction(menu)
        actionEditAlbum.setObjectName("actionEditAlbum")
        actionEditAlbum.setText(_translate("album", "Edit"))
        menu.addAction(actionEditAlbum)
        # actionEditAlbum.triggered.connect(functools.partial(self.onPlayFavRadio, rad.radioID))
        actionEditAlbum.triggered.connect(self.on_edit_album)

        menu.exec(QtGui.QCursor.pos())

    def on_edit_album(self):
        sel_rows = self.ui.tableWidgetAlbums.selectionModel().selectedRows()
        if len(sel_rows) >= 0:
            album_id_sel = self.ui.tableWidgetAlbums.item(sel_rows[0].row(), 2).text()
            alb = self.music_base.albumCol.get_album(album_id_sel)
            if alb.album_id != 0:
                self.editAlbumWidget = AlbumWidget(alb, self)
                self.editAlbumWidget.show()
            else:
                print("No album to edit")

    """
    Genre comboBox functions
    """

    def show_genres(self):
        self.ui.comboBoxStyle.clear()
        self.ui.comboBoxStyle.addItem(_translate("playlist", "All styles"), -2)

        id_set = self.music_base.musicDirectoryCol.get_style_id_set()
        for genre in self.music_base.genres.get_available_genres_form_id_set(id_set):
            self.ui.comboBoxStyle.addItem(genre[0], genre[1])

    def on_change_genre(self):
        genre_id = self.ui.comboBoxStyle.currentData()

        if genre_id < 0:
            self.set_hidden_all_artist_item(False)
        else:
            self.set_hidden_all_artist_item(True)

            model = self.ui.listViewArtists.model()
            for i in range(model.rowCount()):
                itemArt = model.item(i)
                if genre_id in itemArt.artist.style_ids:
                    i = itemArt.row()
                    self.ui.listViewArtists.setRowHidden(i, False)

    """
    Artist listView functions
    """

    def show_artists(self):
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
            self.on_artist_change
        )

    def set_hidden_all_artist_item(self, hide):
        # Hide all artists
        model = self.ui.listViewArtists.model()
        for i in range(model.rowCount()):
            self.ui.listViewArtists.setRowHidden(i, hide)

    def get_first_visible_artist_item(self):
        model = self.ui.listViewArtists.model()
        for i in range(model.rowCount()):
            if not self.ui.listViewArtists.isRowHidden(i):
                return model.item(i)

    def on_artist_change(self, item):
        # When call from listView, item is a QModelIndex
        nrow = item.row()

        model = self.ui.listViewArtists.model()
        if self.currentArtist.artist_id != model.item(nrow).artist.artist_id:
            self.show_artist(model.item(nrow).artist)

    def select_artist_list_view(self, artist):
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

    def on_search_enter(self):
        # After typing, the user hit enter
        # to select the first artist found
        item = self.get_first_visible_artist_item()
        if item is not None:
            selModel = self.ui.listViewArtists.selectionModel()
            selModel.reset()
            selModel.select(item.index(), QItemSelectionModel.Select)
            self.show_artist(item.artist)

    def on_search_change(self, event):
        # When user write a search, shows only matching artists
        search = self.ui.searchEdit.text()

        if len(search) == 0:
            self.set_hidden_all_artist_item(False)
        else:
            self.set_hidden_all_artist_item(True)
            items = self.ui.listViewArtists.model().findItems(search, Qt.MatchContains)
            for item in items:
                i = item.row()
                self.ui.listViewArtists.setRowHidden(i, False)

    def filter_artists(self):
        genreID = self.ui.comboBoxStyle.currentData()
        search = self.ui.searchEdit.text()

        if (genreID is None or genreID == -2) and search == "":
            self.set_hidden_all_artist_item(False)
        else:
            # self.setHiddenAllArtistItem(True)

            model = self.ui.listViewArtists.model()
            for i in range(model.rowCount()):
                itemArt = model.item(i)
                i = itemArt.row()
                if (genreID == -2 or genreID in itemArt.artist.style_ids) and (
                    search.upper() in itemArt.artist.name.upper() or search == ""
                ):
                    self.ui.listViewArtists.setRowHidden(i, False)
                else:
                    self.ui.listViewArtists.setRowHidden(i, True)

    """
    Album tableWidget functions
    """

    def get_album_from_table(self):
        # Return the selected album
        selAlbItems = self.ui.tableWidgetAlbums.selectedItems()
        for item in selAlbItems:
            r = item.row()
            albumIDSel = self.ui.tableWidgetAlbums.item(r, 2).text()

            alb = self.music_base.albumCol.get_album(albumIDSel)
            if alb.album_id == 0:
                print("Album is Empty. Item:" + str(item))
            return alb

    def on_album_change(self, item):
        if item.row() >= 0:
            albumIDSel = self.ui.tableWidgetAlbums.item(item.row(), 2).text()
            alb = self.music_base.albumCol.get_album(albumIDSel)
            if alb.album_id != 0:
                self.show_album(alb)
            else:
                print("No album to show")

    def show_artist(self, artist):
        self.currentArtist = artist
        self.show_albums(self.currentArtist)

    def show_albums(self, artist):
        # Add albums in the QTableView
        if artist == None:
            return
        print("Show albums Art=" + artist.name)
        self.ui.tableWidgetAlbums.setRowCount(0)
        if len(artist.albums) == 0:
            return

        if self.current_album is None:
            self.current_album = artist.get_random_album()

        if self.current_album.artist_id != artist.artist_id:
            self.current_album = artist.get_random_album()

        index_to_sel = 0
        i = 0
        artist.sort_albums()
        for alb in artist.albums:
            self.ui.tableWidgetAlbums.insertRow(i)

            title_item = QTableWidgetItem(alb.title)
            title_item.setFlags(title_item.flags() ^ Qt.ItemIsEditable)
            self.ui.tableWidgetAlbums.setItem(i, 0, title_item)

            year_item = QTableWidgetItem(str(alb.year))
            year_item.setFlags(year_item.flags() ^ Qt.ItemIsEditable)
            self.ui.tableWidgetAlbums.setItem(i, 1, year_item)

            id_item = QTableWidgetItem(str(alb.album_id))
            id_item.setFlags(id_item.flags() ^ Qt.ItemIsEditable)
            self.ui.tableWidgetAlbums.setItem(i, 2, id_item)

            if alb.album_id == self.current_album.album_id:
                index_to_sel = i

            i += 1

        self.ui.tableWidgetAlbums.selectRow(index_to_sel)
        self.ui.tableWidgetAlbums.scrollTo(
            self.ui.tableWidgetAlbums.currentIndex(), QAbstractItemView.PositionAtCenter
        )

    def init_album_view(self):
        self.current_album = None
        self.ui.labelArtist.set_text("")
        self.ui.tableWidgetTracks.setRowCount(0)
        self.show_cover("")

    def show_album(self, album):
        print(
            "showAlbum: "
            + album.title
            + " size="
            + str(album.size)
            + " length="
            + str(album.length)
        )
        self.current_album = album
        self.set_title_label(self.currentArtist.name, album.title, album.year)
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

    def show_album_tracks(self, result):
        # self.ui.tableWidgetTracks.setColumnCount(1)
        self.ui.tableWidgetTracks.setRowCount(0)
        i = 0
        for track in self.current_album.tracks:
            self.ui.tableWidgetTracks.insertRow(i)

            titleItem = QTableWidgetItem(track.title)
            titleItem.setFlags(titleItem.flags() ^ Qt.ItemIsEditable)
            self.ui.tableWidgetTracks.setItem(i, 0, titleItem)

            durationItem = QTableWidgetItem(track.get_duration_text())
            durationItem.setFlags(durationItem.flags() ^ Qt.ItemIsEditable)
            self.ui.tableWidgetTracks.setItem(i, 1, durationItem)

            i += 1

    def show_album_cover(self, result):
        print("showAlbumCover= " + str(result) + " - " + self.current_album.cover)
        album = self.current_album
        if album is None:
            return
        if album.cover != "":
            # coverPixmap = album.getCoverPixmap()
            self.show_cover(album.get_cover_path())
        else:
            self.show_cover("")

    """
    Interactions with vlc module
    """

    def play_album(self, alb):
        """Add tracks in playlist and start playing"""

        self.music_base.history.insert_album_history(alb.album_id)
        self.player.play_album(alb)

        self.set_volume(self.get_volume_from_slider())

    def add_album(self, alb):
        """Add tracks in playlist and start playing"""
        self.player.add_album(alb)
        self.set_volume(self.get_volume_from_slider())

    def show_playlist(self, showOnlyIfNew=False):
        isNew = False
        if self.playList is None:
            isNew = True
            self.playList = PlaylistWidget(self.player, self)
            self.playList.picBufferManager = self.picBufferManager
            self.playList.fullScreenWidget = self.fullScreenWidget
            self.playList.connect_pic_downloader(self.picFromUrlThread)
            self.playList.trackChanged.connect(self.player.set_playlist_track)
            self.playList.currentRadioChanged = self.currentRadioChanged
            self.player.playlistChangedEvent = self.playlistChanged
            self.playList.playlistChanged = self.playlistChanged

        self.playList.show_media_list()

        if isNew or showOnlyIfNew == False:
            self.playList.show()
            self.playList.activateWindow()

    def show_history(self):
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

    def on_current_track_changed(self, event=None):
        logger.debug("onCurrentTrackChanged %s", event)
        if not self.player.radioMode:
            title = None
            trk = self.player.get_current_track_playlist()
            if trk is not None and trk.parentAlbum is not None:
                self.music_base.history.insert_track_history(
                    trk.parentAlbum.album_id, trk.get_file_path_in_album_dir()
                )
        else:
            if not event:
                return
            title = event
            if not title in ["...", "", "-"]:
                self.music_base.history.insert_radio_history(
                    self.player.currentRadioName, title
                )

        if self.playList is not None:
            self.playList.set_current_track(title)
        if self.fullScreenWidget is not None:
            self.fullScreenWidget.set_current_track(title)
        # if self.playerControl is not None:
        #    self.playerControl.setCurrentTrackInThread(title)

    def on_player_media_changed_vlc(self, event):
        print("onPlayerMediaChangedVLC")
        self.currentTrackChanged.emit("")

    def on_player_media_changed_stream_observer(self, title):
        print("onPlayerMediaChangedStreamObserver=" + title)
        self.currentTrackChanged.emit(title)

    def on_play_album(self, item):
        if self.current_album:
            print("onPlayAlbum " + self.current_album.get_album_dir())
            self.play_album(self.current_album)

    def on_add_album(self, item):
        if self.current_album:
            print("onAddAlbum " + self.current_album.get_album_dir())
            self.add_album(self.current_album)

    def on_search_cover_album(self):
        self.coverFinder = CoverArtFinderDialog(self.current_album, self)
        self.coverFinder.signalCoverSaved.connect(self.show_album_cover)
        self.coverFinder.show()

    def on_open_dir(self):
        if self.current_album:
            open_file(self.current_album.get_album_dir())

    """
    Miscellaneous UI functions 
    """

    def set_title_label(self, artist_name="", album_title="", year=""):
        if self.currentArtist and not artist_name:
            artist_name = self.currentArtist.name
        if self.current_album and not album_title:
            album_title = self.current_album.title
            year = self.current_album.year

        album_description = album_title
        year = str(year)
        if not year in ["0", ""]:
            album_description += " (" + year + ")"
        sTitle = """<html><head/><body>
        <p><span style=\" font-size:14pt; font-weight:600;\">{Artist}</span></p>
        <p><span style=\" font-style:italic;\">{Album}</span></p>
        </body></html>"""
        sTitle = sTitle.format(Artist=artist_name, Album=album_description)

        self.ui.labelArtist.setText(sTitle)

    def show_cover(self, path, p_cover_pixmap=None):
        if path == "":
            self.coverPixmap = self.defaultPixmap
        else:
            print("MyCover=" + path)
            self.coverPixmap = self.picBufferManager.get_pic(path, "main.albCover")

        scaled_cover = self.coverPixmap.scaled(
            self.ui.cover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.ui.cover.setPixmap(scaled_cover)
        self.ui.cover.show()

    def resizeEvent(self, event):
        self.resize_cover()

    def resize_cover(self):
        if not self.coverPixmap.isNull():
            scaled_cover = self.coverPixmap.scaled(
                self.ui.cover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.ui.cover.setPixmap(scaled_cover)

    def init_player_buttons(self):
        self.ui.searchCoverButton.setText(_translate("coverArtFinder", "Cover finder"))
        self.ui.playButton.setToolTip(self.ui.playButton.text())
        self.ui.openDirButton.setToolTip(self.ui.openDirButton.text())
        self.ui.addAlbumButton.setToolTip(self.ui.addAlbumButton.text())
        self.ui.searchCoverButton.setToolTip(self.ui.searchCoverButton.text())

        self.ui.playButton.setText("")
        self.ui.openDirButton.setText("")
        self.ui.addAlbumButton.setText("")
        self.ui.searchCoverButton.setText("")

        self.ui.playButton.setIcon(get_svg_icon("play-circle.svg"))
        self.ui.addAlbumButton.setIcon(get_svg_icon("add_music.svg"))
        self.ui.openDirButton.setIcon(get_svg_icon("folder-open.svg"))
        self.ui.searchCoverButton.setIcon(get_svg_icon("picture.svg"))

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
        self.save_settings()

    def save_settings(self):
        if self.player is not None:
            curVolume = self.player.get_volume()
        else:
            curVolume = self.volume

        if curVolume is not None and curVolume > 0:
            self.settings.setValue("volume", curVolume)

    def load_settings(self):
        if self.settings.contains("volume"):
            self.volume = self.settings.value("volume", type=int)
        else:
            self.volume = 100

    def change_language(self, locale):
        # translator for built-in qt strings
        self.translator.unInstallTranslators()
        self.translator.installTranslators(locale)
        self.retranslateUi()
        self.init_player_buttons()
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
        self.set_title_label()

    def retranslateUi(self):
        self.ui.menuFavRadios.setTitle(_translate("radio", "Favorite radios"))
        self.init_extra_menu()
        self.ui.searchCoverButton.set_text(_translate("coverArtFinder", "Cover finder"))
        self.ui.retranslateUi(self)


if __name__ == "__main__":
    from pyzik import *

    main()
