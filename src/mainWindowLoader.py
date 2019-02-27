#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, subprocess, functools

from PyQt5.QtCore import Qt, QSettings, QCoreApplication, QItemSelectionModel, pyqtSignal
from PyQt5.QtWidgets import QTableWidgetItem, QShortcut, QHeaderView, QMenu, QAction, QAbstractItemView, QMainWindow
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence, QCursor, QStandardItemModel, QStandardItem, QColor

import mainWindow  # import of mainWindow.py made with pyuic5

from darkStyle import darkStyle
from playerVLC import *

from musicBase import *
from musicDirectory import *
from database import *


from dialogMusicDirectoriesLoader import *
from streamObserver import *
from albumThread import *
from musicBaseThread import *
from playlistWidget import *
from historyWidget import *
from searchRadioWidget import *
from fullScreenWidget import *
from fullScreenCoverWidget import *
from playerControlWidget import *
from albumWidget import *
from coverArtFinderDialog import *
from svgIcon import *
from picFromUrlThread import *

orange = QtGui.QColor(216, 119, 0)
_translate = QCoreApplication.translate

def openFile(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener ="open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])



class MainWindowLoader(QMainWindow):

    currentTrackChanged = pyqtSignal(str, name='currentTrackChanged')
    showPlayerControlEmited = pyqtSignal(str, name='showPlayerControlEmited')

    def __init__(self, parent=None,app=None,musicbase=None,player=None,translator=None):
        QMainWindow.__init__(self, parent)

        self.app = app
        self.translator = translator
        self.musicBase = musicbase
        self.player = player

        self.picFromUrlThread = picFromUrlThread()

        self.settings = QSettings('pyzik', 'pyzik')
        self.firstShow = True
        self.playList = None
        self.searchRadio = None
        self.histoWidget = None


        self.coverPixmap = QtGui.QPixmap()
        #self.defaultPixmap = QtGui.QPixmap("img/vinyl-record.svg")
        self.defaultPixmap = getSvgWithColorParam("vinyl-record2.svg")

        self.fullScreenWidget = fullScreenWidget(self.player)
        self.fullScreenWidget.defaultPixmap = self.defaultPixmap
        self.fullScreenCoverWidget = fullScreenCoverWidget()
        self.fullScreenCoverWidget.defaultPixmap = self.defaultPixmap
        self.currentArtist = artist("",0)
        self.currentAlbum = album("")



        #self.setWindowIcon(getLogo())
        self.setWindowIcon(QtGui.QIcon(self.defaultPixmap))

        self.ui = mainWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.playerControl = playerControlWidget(self.player,self)
        self.playerControl.picFromUrlThread = self.picFromUrlThread
        self.playerControl.defaultPixmap = self.defaultPixmap
        #self.playerControl.setMaximumSize(QtCore.QSize(16777215, 140))
        self.ui.verticalMainLayout.addWidget(self.playerControl)
        self.playerControl.hide()
        #self.ui.playerWidget = self.playerControl
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        self.playerControl.setSizePolicy(sizePolicy)
        #self.playerControl.player = self.player
        #self.playerControl.trackChanged.connect(self.player.setPlaylistTrack)
        #self.playerControl.height = 50

        self.initPlayerButtons()

        self.setTitleLabel("")
        self.setWindowTitle("Pyzik")

        self.initAlbumTableWidget()
        self.initTrackTableWidget()

        self.showGenres()
        self.showArtists()
        self.loadSettings()

        self.initRadioFavMenu()

        #Connect UI triggers
        self.ui.listViewArtists.selectionModel().currentChanged.connect(self.onArtistChange)
        self.ui.actionMusic_directories.triggered.connect(self.onMenuMusicDirectories)
        self.ui.actionExplore_music_directories.triggered.connect(self.onMenuExplore)
        self.ui.actionRandom_album.triggered.connect(self.ramdomAlbum)
        self.ui.actionDelete_database.triggered.connect(self.onMenuDeleteDatabase)
        self.ui.actionFuzzyGroovy.triggered.connect(self.onPlayFuzzyGroovy)
        self.ui.actionSearchRadio.triggered.connect(self.onPlaySearchRadio)
        self.ui.actionPlaylist.triggered.connect(self.showPlaylist)
        self.ui.actionHistory.triggered.connect(self.showHistory)
        self.ui.actionLanguageSpanish.triggered.connect(functools.partial(self.changeLanguage, 'es'))
        self.ui.actionLanguageFrench.triggered.connect(functools.partial(self.changeLanguage, 'fr'))
        self.ui.actionLanguageEnglish.triggered.connect(functools.partial(self.changeLanguage, 'en'))
        self.ui.playButton.clicked.connect(self.onPlayAlbum)
        self.ui.addAlbumButton.clicked.connect(self.onAddAlbum)
        self.ui.searchCoverButton.clicked.connect(self.onSearchCoverAlbum)
        #self.ui.nextButton.clicked.connect(self.player.mediaListPlayer.next)
        self.ui.openDirButton.clicked.connect(self.onOpenDir)
        #self.ui.previousButton.clicked.connect(self.player.mediaListPlayer.previous)
        self.ui.searchEdit.textChanged.connect(self.filterArtists)
        self.ui.searchEdit.returnPressed.connect(self.onSearchEnter)
        self.ui.tableWidgetAlbums.selectionModel().currentRowChanged.connect(self.onAlbumChange)
        self.ui.tableWidgetAlbums.customContextMenuRequested.connect(self.handleHeaderAlbumsMenu)

        self.ui.comboBoxStyle.currentIndexChanged.connect(self.filterArtists)
                
        self.shortcutRandomAlbum = QShortcut(QtGui.QKeySequence("Ctrl+R"), self)
        self.shortcutRandomAlbum.activated.connect(self.ramdomAlbum)
        self.shortcutPlaylist = QShortcut(QtGui.QKeySequence("Ctrl+P"), self)
        self.shortcutPlaylist.activated.connect(self.showPlaylist)
        self.shortcutPause = QShortcut(QtGui.QKeySequence("Space"), self)
        self.shortcutPause.activated.connect(self.player.pause)
        self.shortcutFullScreen = QShortcut(QtGui.QKeySequence("Ctrl+F"), self)
        self.shortcutFullScreen.activated.connect(self.showFullScreen)


        #Connect VLC triggers
        self.player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerMediaChanged, self.onPlayerMediaChangedVLC)
        self.player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerPaused, self.paused)
        self.player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerPlaying, self.isPlaying)
        self.player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerPositionChanged, self.onPlayerPositionChanged)
        #self.player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerAudioVolume , self.setVolumeSliderFromPlayer)

        self.ui.volumeSlider.setVisible(False)

        self.playerControl.playerControls.volumeSlider.setMaximum(100)
        self.playerControl.playerControls.volumeSlider.setValue(self.volume)
        self.player.setVolume(self.volume)
        self.playerControl.playerControls.volumeSlider.valueChanged.connect(self.setVolume)
        
        
        #Write message in status bar
        #self.ui.statusBar.showMessage("Pyzik")

        self.threadStreamObserver = streamObserver()
        self.threadStreamObserver.player = self.player
        self.threadStreamObserver.musicBase = self.musicBase
        self.threadStreamObserver.titleChanged.connect(self.onPlayerMediaChangedStreamObserver)
        self.player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerStopped, self.threadStreamObserver.resetPreviousTitle)
        self.threadStreamObserver.start()


        self.loadAlbumFilesThread = loadAlbumFilesThread()
        self.loadAlbumFilesThread.setTerminationEnabled(True)
        self.loadAlbumFilesThread.imagesLoaded.connect(self.showAlbumCover)
        self.loadAlbumFilesThread.tracksLoaded.connect(self.showAlbumTracks)

        self.exploreAlbumsDirectoriesThread = exploreAlbumsDirectoriesThread()
        #self.exploreAlbumsDirectoriesThread.exploreCompleted.connect(self.onExploreCompleted)

        self.ui.coverWidget.resizeEvent = self.resizeEvent
        self.ui.coverWidget.mouseDoubleClickEvent = self.mouseDoubleClickEvent

        self.currentTrackChanged.connect(self.onCurrentTrackChanged)
        self.showPlayerControlEmited.connect(self.showPlayerControl)

        self.ui.searchEdit.setFocus()

    def mouseDoubleClickEvent(self,event):
        self.showFullScreenCover()

    def showFullScreenCover(self):
        self.fullScreenCoverWidget.setPixmapFromUri(self.currentAlbum.getCoverPath())
        self.fullScreenCoverWidget.show()
        
    def showEvent(self,event):
        #This function is called when the mainWindow is shown
        if self.firstShow == True:
            self.ramdomAlbum()
            self.firstShow = False

    def onPlayFuzzyGroovy(self):   
        fg = self.musicBase.radioMan.getFuzzyGroovy()   
        self.player.playRadio(fg)


    def onExploreCompleted(self,event):
        print("onExploreCompleted")
        self.musicBase.db = database()
        #self.musicBase.loadMusicBase()
        self.showArtists()
        self.showGenres()
        

    def onPlaySearchRadio(self):   

        if self.searchRadio is None:
            self.searchRadio = searchRadioWidget(self.musicBase,self.player)
            self.searchRadio.radioAdded.connect(self.onAddFavRadio)
            
        self.searchRadio.show()
        self.searchRadio.activateWindow()


    def onAddFavRadio(self):
        #self.musicBase.db.initDataBase()
        self.musicBase.radioMan.loadFavRadios()
        self.initRadioFavMenu()

        

    def ramdomAlbum(self):
        styleID = self.ui.comboBoxStyle.currentData()
        alb = self.musicBase.albumCol.getRandomAlbum(styleID)
        self.currentAlbum = alb
        if alb is not None:
            print("RamdomAlb="+alb.title)
            art = self.musicBase.artistCol.getArtistByID(alb.artistID)
            self.currentArtist = art
            self.selectArtistListView(art)
            self.showArtist(art)
            #self.showAlbum(alb)



    def setVolume(self, volume):
        self.player.setVolume(volume)

    def getVolumeFromSlider(self):
        return self.playerControl.getVolume()

    def setVolumeSliderFromPlayer(self,event):
        volume = self.player.getVolume()
        self.playerControl.setVolume(volume)

    def onPlayerPositionChanged(self,event=None):
        self.playerControl.onPlayerPositionChanged(event)
        if self.playList is not None:
            self.playList.onPlayerPositionChanged(event)

    #def setStatus(self,msg):
        #self.ui.labelArtist.setText(msg)
        #self.ui.statusBar.showMessage(msg)

    def paused(self,event):
        print("Paused!")

    def showPlayerControl(self,event):
        self.playerControl.show()

    def isPlaying(self,event):
        print("isPlaying!")
        self.showPlayerControlEmited.emit("")
   


    '''
    Init widgets
    '''
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

    def initRadioFavMenu(self):

        if not hasattr(self.ui,"menuFavRadios") :
            self.ui.menuFavRadios = QMenu(self.ui.menuRadios)
        else:
            for action in self.ui.menuFavRadios.actions():
                self.ui.menuFavRadios.removeAction(action)

        for rad in self.musicBase.radioMan.favRadios:

            self.ui.actionFavRadio = QAction(self.ui.menuFavRadios)
            self.ui.actionFavRadio.setObjectName("actionFavRadio_"+rad.name)
            self.ui.actionFavRadio.setText(rad.name)
            self.ui.menuFavRadios.addAction(self.ui.actionFavRadio)
            self.ui.actionFavRadio.triggered.connect(functools.partial(self.onPlayFavRadio, rad.radioID))

        self.ui.menuRadios.addAction(self.ui.menuFavRadios.menuAction())
        self.ui.menuFavRadios.setTitle(_translate("radio","Favorite radios"))
        

    '''
    Menu Actions
    '''
    def onMenuMusicDirectories(self):
        self.musicBase.db = database()
        dirDiag = DialogMusicDirectoriesLoader(self.musicBase)
        dirDiag.show()
        dirDiag.exec_()

    def onPlayFavRadio(self,radioID):
        rad = self.musicBase.radioMan.getFavRadio(radioID)
        self.player.playRadio(rad)
        self.showPlaylist(True)
        
    def onMenuExplore(self):
        self.exploreAlbumsDirectoriesThread.musicBase = self.musicBase 
        self.wProgress = progressWidget()
        self.exploreAlbumsDirectoriesThread.progressChanged.connect(self.wProgress.setValue)
        self.exploreAlbumsDirectoriesThread.directoryChanged.connect(self.wProgress.setDirectoryText)
        self.exploreAlbumsDirectoriesThread.exploreCompleted.connect(self.wProgress.close)
        self.exploreAlbumsDirectoriesThread.exploreCompleted.connect(self.onExploreCompleted)
        self.wProgress.progressClosed.connect(self.exploreAlbumsDirectoriesThread.stop)
        self.exploreAlbumsDirectoriesThread.start()

    
    def onMenuDeleteDatabase(self):
        self.musicBase.db.createConnection()
        self.musicBase.db.dropAllTables()
        self.musicBase.emptyDatas()
        self.showArtists()
        self.initAlbumTableWidget()
        self.initAlbumView()


    def handleHeaderAlbumsMenu(self, pos):
        
        #print('column(%d)' % self.ui.tableWidgetAlbums.horizontalHeader().logicalIndexAt(pos))
        menu = QMenu()
        actionEditAlbum = QAction(menu)
        actionEditAlbum.setObjectName("actionEditAlbum")
        actionEditAlbum.setText(_translate("album","Edit"))
        menu.addAction(actionEditAlbum)
        #actionEditAlbum.triggered.connect(functools.partial(self.onPlayFavRadio, rad.radioID))
        actionEditAlbum.triggered.connect(self.onEditAlbum)

        menu.exec(QtGui.QCursor.pos())


    def onEditAlbum(self):
        selRows = self.ui.tableWidgetAlbums.selectionModel().selectedRows()
        if len(selRows) >= 0:
            albumIDSel = self.ui.tableWidgetAlbums.item(selRows[0].row(),2).text()
            alb = self.musicBase.albumCol.getAlbum(albumIDSel)
            if(alb.albumID != 0):
                self.editAlbumWidget = albumWidget(alb)
                self.editAlbumWidget.show()
            else:
                print("No album to edit")


    '''
    Genre comboBox functions
    '''

    def showGenres(self):

        self.ui.comboBoxStyle.clear()
        self.ui.comboBoxStyle.addItem(_translate("playlist","All styles"),-2)

        idSet = self.musicBase.musicDirectoryCol.getStyleIDSet()
        for genre in self.musicBase.genres.getAvailableGenresFormIDSet(idSet):
            self.ui.comboBoxStyle.addItem(genre[0],genre[1])
        


    def onChangeGenre(self):
        genreID = self.ui.comboBoxStyle.currentData()
            

        if(genreID<0):
            self.setHiddenAllArtistItem(False)
        else:
            self.setHiddenAllArtistItem(True)
            
            model = self.ui.listViewArtists.model()
            for i in range(model.rowCount()):
                itemArt = model.item(i)
                if genreID in itemArt.artist.styleIDSet:
                    i = itemArt.row()
                    self.ui.listViewArtists.setRowHidden(i,False)


            
    '''
    Artist listView functions
    '''

    def showArtists(self):
        # Add artists in the QListView
        model = QtGui.QStandardItemModel(self.ui.listViewArtists)
        for art in self.musicBase.artistCol.artists:
            itemArt = QtGui.QStandardItem(art.name)
            itemArt.artist = art
            art.itemListViewArtist = itemArt
            model.appendRow(itemArt)

        self.ui.listViewArtists.setModel(model)
        self.ui.listViewArtists.show()
        self.ui.listViewArtists.selectionModel().currentChanged.connect(self.onArtistChange)

    def setHiddenAllArtistItem(self,hide):
        #Hide all artists
        model = self.ui.listViewArtists.model()
        for i in range(model.rowCount()):
            self.ui.listViewArtists.setRowHidden(i,hide)

    def getFirstVisibleArtistItem(self):
        model = self.ui.listViewArtists.model()
        for i in range(model.rowCount()):
            if(not self.ui.listViewArtists.isRowHidden(i)):
                return model.item(i)
        
    def onArtistChange(self,item):
        #When call from listView, item is a QModelIndex
        nrow = item.row()
        
        model = self.ui.listViewArtists.model()
        if self.currentArtist.artistID != model.item(nrow).artist.artistID :
            self.showArtist(model.item(nrow).artist)
            
   

    def selectArtistListView(self,artist):

        item = artist.itemListViewArtist

        selModel = self.ui.listViewArtists.selectionModel()
        selModel.reset()
        selModel.select(item.index(), QItemSelectionModel.SelectCurrent)

        self.ui.listViewArtists.scrollTo(item.index(), QAbstractItemView.PositionAtCenter)

    '''
    Search artist functions
    '''
    def onSearchEnter(self):
    #After typing, the user hit enter
    #to select the first artist found
        item = self.getFirstVisibleArtistItem()
        if item is not None:
            selModel = self.ui.listViewArtists.selectionModel()
            selModel.reset()
            selModel.select(item.index(), QItemSelectionModel.Select)
            self.showArtist(item.artist)

    def onSearchChange(self,event):
        #When user write a search, shows only matching artists
        search = self.ui.searchEdit.text()

        if(len(search)==0):
            self.setHiddenAllArtistItem(False)
        else:
            self.setHiddenAllArtistItem(True)
            items = self.ui.listViewArtists.model().findItems(search,Qt.MatchContains)
            for item in items:
                i = item.row()
                self.ui.listViewArtists.setRowHidden(i,False)


    def filterArtists(self):
        genreID = self.ui.comboBoxStyle.currentData()
        search = self.ui.searchEdit.text()    

        if((genreID is None or genreID ==-2) and search==""):
            self.setHiddenAllArtistItem(False)
        else:
            #self.setHiddenAllArtistItem(True)
            
            model = self.ui.listViewArtists.model()
            for i in range(model.rowCount()):
                itemArt = model.item(i)
                i = itemArt.row()
                if (( genreID == -2 or genreID in itemArt.artist.styleIDSet)
                and (search.upper() in itemArt.artist.name.upper() or search=="")): 
                    self.ui.listViewArtists.setRowHidden(i,False)
                else:
                    self.ui.listViewArtists.setRowHidden(i,True)


    '''
    Album tableWidget functions
    '''
    def getAlbumFromTable(self):
        #Return the selected album
        selAlbItems = self.ui.tableWidgetAlbums.selectedItems()
        for item in selAlbItems:
            r = item.row()
            albumIDSel = self.ui.tableWidgetAlbums.item(r,2).text()
            
            alb = self.musicBase.albumCol.getAlbum(albumIDSel)
            if(alb.albumID == 0): 
                print("Album is Empty. Item:"+str(item))
            return alb


    def onAlbumChange(self,item):
        if item.row() >= 0:
            print("OnAlbumChange:",item.row())
            albumIDSel = self.ui.tableWidgetAlbums.item(item.row(),2).text()
            alb = self.musicBase.albumCol.getAlbum(albumIDSel)
            if(alb.albumID != 0):
                self.showAlbum(alb)
            else:
                print("No album to show")

    def showArtist(self,artist):
        self.currentArtist = artist
        self.showAlbums(self.currentArtist)

    def showAlbums(self,artist):
        #Add albums in the QTableView
        if artist == None: 
            return
        print("Show albums Art="+artist.name)

        if self.currentAlbum is None:
            self.currentAlbum = artist.getRandomAlbum()

        if self.currentAlbum.artistID != artist.artistID:
            self.currentAlbum = artist.getRandomAlbum()

        self.ui.tableWidgetAlbums.setRowCount(0)
        indexToSel = 0
        i = 0
        artist.sortAlbums()
        for alb in artist.albums:
            self.ui.tableWidgetAlbums.insertRow(i)

            titleItem = QTableWidgetItem(alb.title)
            titleItem.setFlags(titleItem.flags() ^ Qt.ItemIsEditable)
            self.ui.tableWidgetAlbums.setItem(i,0,titleItem)

            yearItem = QTableWidgetItem(str(alb.year))
            yearItem.setFlags(yearItem.flags() ^ Qt.ItemIsEditable)
            self.ui.tableWidgetAlbums.setItem(i,1,yearItem)
            
            idItem = QTableWidgetItem(str(alb.albumID))
            idItem.setFlags(idItem.flags() ^ Qt.ItemIsEditable)
            self.ui.tableWidgetAlbums.setItem(i,2,idItem)

            if(alb.albumID==self.currentAlbum.albumID):
                indexToSel = i

            i += 1

        self.ui.tableWidgetAlbums.selectRow(indexToSel)
        self.ui.tableWidgetAlbums.scrollTo(self.ui.tableWidgetAlbums.currentIndex(), QAbstractItemView.PositionAtCenter)

    def initAlbumView(self):
        self.currentAlbum = None
        self.ui.labelArtist.setText("")
        self.ui.tableWidgetTracks.setRowCount(0)
        self.showCover("")


    def showAlbum(self,album):
        print("showAlbum: "+album.title)
        self.currentAlbum = album
        self.setTitleLabel(self.currentArtist.name,album.title,album.year)
        
        #Start a thread to load album datas from directory
        #When updated, triggers launch showAlbumCover and showAlbumTracks
        if self.loadAlbumFilesThread.isRunning() :
            print("Stop Thread loadAlbum")
            self.loadAlbumFilesThread.stop()
            self.loadAlbumFilesThread.wait()
        
        self.loadAlbumFilesThread.album = album
        self.loadAlbumFilesThread.player = self.player
        self.loadAlbumFilesThread.start()


    def showAlbumTracks(self,result):        
        #self.ui.tableWidgetTracks.setColumnCount(1)
        self.ui.tableWidgetTracks.setRowCount(0)
        i=0
        for track in self.currentAlbum.tracks:
            self.ui.tableWidgetTracks.insertRow(i)

            titleItem = QTableWidgetItem(track.title)
            titleItem.setFlags(titleItem.flags() ^ Qt.ItemIsEditable)
            self.ui.tableWidgetTracks.setItem(i,0,titleItem)

            durationItem = QTableWidgetItem(track.getDurationText())
            durationItem.setFlags(durationItem.flags() ^ Qt.ItemIsEditable)
            self.ui.tableWidgetTracks.setItem(i,1,durationItem)

            i+=1

    def showAlbumCover(self,result):
        album = self.currentAlbum
        if album.cover != "":
            self.showCover(album.getCoverPath()) 
        else:
            self.showCover("")


    '''
    Interactions with vlc module
    '''
    def playAlbum(self,alb):
        '''Add tracks in playlist and start playing'''
        
        self.musicBase.history.insertAlbumHistory(alb.albumID)
        self.player.playAlbum(alb)
        
        self.setVolume(self.getVolumeFromSlider())


    def addAlbum(self,alb):
        '''Add tracks in playlist and start playing'''
        self.player.addAlbum(alb)
        self.setVolume(self.getVolumeFromSlider())


    def showPlaylist(self,showOnlyIfNew=False):

        isNew = False
        if self.playList is None:
            isNew = True
            self.playList = playlistWidget(self.player)
            self.playList.fullScreenWidget = self.fullScreenWidget
            self.playList.picFromUrlThread = self.picFromUrlThread
            self.playList.trackChanged.connect(self.player.setPlaylistTrack)

        self.playList.showMediaList()
            
        if isNew or showOnlyIfNew==False: 
            self.playList.show()
            self.playList.activateWindow()


    def showHistory(self):
        if self.histoWidget is None:
            self.histoWidget = historyWidget(self.musicBase)
             
        self.histoWidget.show()
        self.histoWidget.activateWindow()


    def showFullScreen(self):
        print("showFullScreen")
        if self.fullScreenWidget is None:
            self.fullScreenWidget = fullScreenWidget(self.player)
             
        self.fullScreenWidget.show()
        self.fullScreenWidget.activateWindow()


    def onCurrentTrackChanged(self,event=None):
        
        if not self.player.radioMode:
            title = None
            trk = self.player.getCurrentTrackPlaylist()
            if trk is not None:
                self.musicBase.history.insertTrackHistory(trk.parentAlbum.albumID,trk.getFilePathInAlbumDir())
        else:
            title = event
            if not title in ["...","","-"]:
                self.musicBase.history.insertRadioHistory(self.player.currentRadioName,title)

        if self.playList is not None:
            self.playList.setCurrentTrack(title)
        if self.fullScreenWidget is not None:
            self.fullScreenWidget.setCurrentTrack(title)
        if self.playerControl is not None:
            self.playerControl.setCurrentTrack(title)


    def onPlayerMediaChangedVLC(self,event):
        print("onPlayerMediaChangedVLC")
        self.currentTrackChanged.emit("")



    def onPlayerMediaChangedStreamObserver(self,title):
        print("onPlayerMediaChangedStreamObserver="+title)
        self.currentTrackChanged.emit(title)


    def onPlayAlbum(self,item):
        print("onPlayAlbum "+self.currentAlbum.getAlbumDir())
        self.playAlbum(self.currentAlbum)


    def onAddAlbum(self,item):
        print("onAddAlbum "+self.currentAlbum.getAlbumDir())
        self.addAlbum(self.currentAlbum)


    def onSearchCoverAlbum(self):

        self.coverFinder = coverArtFinderDialog(self.currentAlbum)
        self.coverFinder.picFromUrlThread = self.picFromUrlThread
        self.coverFinder.signalCoverSaved.connect(self.showAlbumCover)
        self.coverFinder.show()
        

    def onOpenDir(self):
        openFile(self.currentAlbum.getAlbumDir())


    '''
    Miscellanious UI functions 
    '''

    def setTitleLabel(self,artName="",albTitle="",year=""):

        if self.currentArtist is not None and artName=="":
            artName = self.currentArtist.name
        if self.currentAlbum is not None and albTitle=="":  
            albTitle = self.currentAlbum.title
            year = self.currentAlbum.year

        sAlbum = albTitle
        sYear =str(year)
        if(not sYear in ["0",""]): sAlbum += " ("+sYear+")"
        sTitle = '''<html><head/><body>
        <p><span style=\" font-size:14pt; font-weight:600;\">{Artist}</span></p>
        <p><span style=\" font-style:italic;\">{Album}</span></p>
        </body></html>'''
        sTitle = sTitle.format(Artist=artName,Album=sAlbum)
        
        self.ui.labelArtist.setText(sTitle)



    def showCover(self,path):
        
        if path == "":
            self.coverPixmap = self.defaultPixmap
        else:
            print("MyCover="+path)
            self.coverPixmap = QtGui.QPixmap(path)

        scaledCover = self.coverPixmap.scaled(self.ui.cover.size(),
                                                Qt.KeepAspectRatio,
                                                Qt.SmoothTransformation)
        self.ui.cover.setPixmap(scaledCover)
        self.ui.cover.show()

    

    def resizeEvent(self,event):
        self.resizeCover()


    def resizeCover(self):
        if (not self.coverPixmap.isNull()):
            scaledCover = self.coverPixmap.scaled(self.ui.cover.size(),
                                                    Qt.KeepAspectRatio,
                                                    Qt.SmoothTransformation)
            self.ui.cover.setPixmap(scaledCover)

    def initPlayerButtons(self):
        
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

        self.ui.playButton.setMaximumSize(QtCore.QSize(40, 25))
        self.ui.openDirButton.setMaximumSize(QtCore.QSize(40, 25))
        self.ui.addAlbumButton.setMaximumSize(QtCore.QSize(40, 25))
        self.ui.searchCoverButton.setMaximumSize(QtCore.QSize(40, 25))

        self.ui.playButton.setMinimumSize(QtCore.QSize(27, 27))
        self.ui.openDirButton.setMinimumSize(QtCore.QSize(27, 27))
        self.ui.addAlbumButton.setMinimumSize(QtCore.QSize(27, 27))
        self.ui.searchCoverButton.setMinimumSize(QtCore.QSize(27, 27))
        



    def closeEvent(self, event):
        if self.playList is not None: self.playList.close()
        if self.histoWidget is not None: self.histoWidget.close()
        if self.searchRadio is not None: self.searchRadio.close()
        self.saveSettings()

    def saveSettings(self):

        if self.player is not None :
            curVolume = self.player.getVolume()
        else:
            curVolume = self.volume

        if curVolume is not None and curVolume > 0:
            self.settings.setValue('volume', curVolume)

    def loadSettings(self):
        if self.settings.contains('volume'):
            self.volume = self.settings.value('volume', type=int)
        else:
            self.volume = 100

    def changeLanguage(self,locale):
        # translator for built-in qt strings
        self.translator.unInstallTranslators()
        self.translator.installTranslators(locale)
        self.retranslateUi()
        self.initPlayerButtons()
        if self.playList is not None: self.playList.retranslateUi()
        if self.histoWidget is not None: self.histoWidget.retranslateUi()
        if self.searchRadio is not None: self.searchRadio.retranslateUi()
        if self.playerControl is not None: self.playerControl.retranslateUi()


        self.update()
        self.setWindowTitle("Pyzik")
        self.setTitleLabel()

    def retranslateUi(self):

        self.ui.menuFavRadios.setTitle(_translate("radio","Favorite radios"))
        self.ui.retranslateUi(self)


    

if __name__ == '__main__':
    from pyzik import *
    main()
