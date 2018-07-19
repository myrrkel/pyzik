#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, subprocess, functools
from PyQt5 import QtWidgets, QtGui, QtCore
from playerVLC import *
import mainWindow  # import of mainWindow.py made with pyuic5
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




def openFile(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener ="open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])



class MainWindowLoader(QtWidgets.QMainWindow):

    def __init__(self, parent=None,app=None,musicbase=None,player=None,translator=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.app = app
        self.translator = translator
        self.musicBase = musicbase
        self.player = player

        self.settings = QtCore.QSettings('pyzik', 'pyzik')
        self.firstShow = True
        self.playList = None
        self.searchRadio = None
        self.histoWidget = None
        self.currentArtist = artist("",0)
        self.currentAlbum = album("")

        self.coverPixmap = QtGui.QPixmap()
        self.defaultPixmap = QtGui.QPixmap()

        self.ui = mainWindow.Ui_MainWindow()
        self.ui.setupUi(self)

        
        self.setTitleLabel("")
        self.setWindowTitle("PyZik")

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
        self.ui.pauseButton.clicked.connect(self.onPauseAlbum)
        #self.ui.nextButton.clicked.connect(self.player.mediaListPlayer.next)
        self.ui.openDirButton.clicked.connect(self.onOpenDir)
        #self.ui.previousButton.clicked.connect(self.player.mediaListPlayer.previous)
        self.ui.searchEdit.textChanged.connect(self.filterArtists)
        self.ui.searchEdit.returnPressed.connect(self.onSearchEnter)
        self.ui.tableWidgetAlbums.selectionModel().currentRowChanged.connect(self.onAlbumChange)
        self.ui.tableWidgetAlbums.customContextMenuRequested.connect(self.handleHeaderAlbumsMenu)

        self.ui.comboBoxStyle.currentIndexChanged.connect(self.filterArtists)
                
        self.shortcutRandomAlbum = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+R"), self)
        self.shortcutRandomAlbum.activated.connect(self.ramdomAlbum)


        #Connect VLC triggers
        self.player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerMediaChanged, self.onPlayerMediaChangedVLC)
        self.player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerPaused, self.paused)
        self.player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerPlaying, self.isPlaying)
        #self.player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerPositionChanged, self.onPlayerPositionChanged)
        #self.player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerAudioVolume , self.setVolumeSliderFromPlayer)


        self.ui.volumeSlider.setMaximum(100)

        self.ui.volumeSlider.setValue(self.volume)
        self.player.setVolume(self.volume)
        self.ui.volumeSlider.valueChanged.connect(self.setVolume)
       
        
        #Write message in status bar
        self.ui.statusBar.showMessage("PyZik")


        self.threadStreamObserver = streamObserver()
        self.threadStreamObserver.player = self.player
        self.threadStreamObserver.musicBase = self.musicBase
        self.threadStreamObserver.titleChanged.connect(self.setStatus)
        self.threadStreamObserver.titleChanged.connect(self.onPlayerMediaChangedStreamObserver)
        
        self.player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerStopped, self.threadStreamObserver.resetPreviousTitle)

        self.threadStreamObserver.start()


        self.loadAlbumFilesThread = loadAlbumFilesThread()
        self.loadAlbumFilesThread.setTerminationEnabled(True)
        self.loadAlbumFilesThread.imagesLoaded.connect(self.showAlbumCover)
        self.loadAlbumFilesThread.tracksLoaded.connect(self.showAlbumTracks)

        self.exploreAlbumsDirectoriesThread = exploreAlbumsDirectoriesThread()
        #self.exploreAlbumsDirectoriesThread.progressChanged.connect(self.showAlbumTracks)
        self.exploreAlbumsDirectoriesThread.exploreCompleted.connect(self.showArtists)

        self.ui.coverWidget.resizeEvent = self.resizeEvent
        
    def showEvent(self,event):
        #This function is called when the mainWindow is shown
        if self.firstShow == True:
            self.ramdomAlbum()
            self.firstShow = False

    def onPlayFuzzyGroovy(self):   
        fg = self.musicBase.radioMan.getFuzzyGroovy()   
        self.player.playRadio(fg)
        self.showPlaylist(True)
        self.setVolume(self.getVolumeFromSlider())

        
    def onPlaySearchRadio(self):   

        if self.searchRadio is None:
            self.searchRadio = searchRadioWidget(self.musicBase,self.player)
            self.searchRadio.radioAdded.connect(self.onAddFavRadio)
            
        self.searchRadio.show()


    def onAddFavRadio(self):
        self.musicBase.db.initDataBase()
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
        return self.ui.volumeSlider.value()

    def setVolumeSliderFromPlayer(self,event):
        volume = self.player.getVolume()
        self.ui.volumeSlider.setValue(volume)

    def setStatus(self,msg):
        #self.ui.labelArtist.setText(msg)
        self.ui.statusBar.showMessage(msg)

    def paused(self,event):
        print("Paused!")

    def isPlaying(self,event):
        print("isPlaying!")
   


    '''
    Init widgets
    '''
    def initAlbumTableWidget(self):
        self.ui.tableWidgetAlbums.setRowCount(0)
        hHeader = self.ui.tableWidgetAlbums.horizontalHeader()
        vHeader = self.ui.tableWidgetAlbums.verticalHeader()
        vHeader.hide()
        hHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        hHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        hHeader.hideSection(2)

    def initTrackTableWidget(self):
        self.ui.tableWidgetTracks.setRowCount(0)
        hHeader = self.ui.tableWidgetTracks.horizontalHeader()
        vHeader = self.ui.tableWidgetTracks.verticalHeader()
        vHeader.hide()
        hHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        hHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        hHeader.hideSection(2)

    def initRadioFavMenu(self):

        if not hasattr(self.ui,"menuFavRadios") :
            self.ui.menuFavRadios = QtWidgets.QMenu(self.ui.menuRadios)
        else:
            for action in self.ui.menuFavRadios.actions():
                self.ui.menuFavRadios.removeAction(action)

        for rad in self.musicBase.radioMan.favRadios:

            self.ui.actionFavRadio = QtWidgets.QAction(self.ui.menuFavRadios)
            self.ui.actionFavRadio.setObjectName("actionFavRadio_"+rad.name)
            self.ui.actionFavRadio.setText(rad.name)
            self.ui.menuFavRadios.addAction(self.ui.actionFavRadio)
            self.ui.actionFavRadio.triggered.connect(functools.partial(self.onPlayFavRadio, rad.radioID))

        self.ui.menuRadios.addAction(self.ui.menuFavRadios.menuAction())
        self.ui.menuFavRadios.setTitle("Favorite radios")
        

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
    
    def onExploreCompleted(self,event):
        self.musicBase.db = database()

    
    def onMenuDeleteDatabase(self):
        self.musicBase.db.createConnection()
        self.musicBase.db.dropAllTables()
        self.musicBase.emptyDatas()
        self.showArtists()
        self.initAlbumTableWidget()

    def handleHeaderAlbumsMenu(self, pos):
        print('column(%d)' % self.ui.tableWidgetAlbums.horizontalHeader().logicalIndexAt(pos))
        menu = QtWidgets.QMenu()
        menu.addAction('Add')
        menu.addAction('Delete')
        menu.exec(QtGui.QCursor.pos())

    '''
    Genre comboBox functions
    '''

    def showGenres(self):
        _translate = QtCore.QCoreApplication.translate
        self.ui.comboBoxStyle.addItem(_translate("playlist","All styles"),-1)

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
        selModel.select(item.index(), QtCore.QItemSelectionModel.SelectCurrent)

        self.ui.listViewArtists.scrollTo(item.index(), QtWidgets.QAbstractItemView.PositionAtCenter)

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
            selModel.select(item.index(), QtCore.QItemSelectionModel.Select)
            self.showArtist(item.artist)

    def onSearchChange(self,event):
        #When user write a search, shows only matching artists
        search = self.ui.searchEdit.text()

        if(len(search)==0):
            self.setHiddenAllArtistItem(False)
        else:
            self.setHiddenAllArtistItem(True)
            items = self.ui.listViewArtists.model().findItems(search,QtCore.Qt.MatchContains)
            for item in items:
                i = item.row()
                self.ui.listViewArtists.setRowHidden(i,False)


    def filterArtists(self):
        genreID = self.ui.comboBoxStyle.currentData()
        search = self.ui.searchEdit.text()    

        if(genreID<0 and search==""):
            self.setHiddenAllArtistItem(False)
        else:
            #self.setHiddenAllArtistItem(True)
            
            model = self.ui.listViewArtists.model()
            for i in range(model.rowCount()):
                itemArt = model.item(i)
                i = itemArt.row()
                if ((genreID in itemArt.artist.styleIDSet or genreID<0)
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

        print("Show albums Art="+artist.name)

        if self.currentAlbum is None:
            self.currentAlbum = artist.getRandomAlbum()

        if self.currentAlbum.artistID is not artist.artistID:
            self.currentAlbum = artist.getRandomAlbum()

        self.ui.tableWidgetAlbums.setRowCount(0)
        indexToSel = 0
        i=0
        artist.sortAlbums()
        for alb in artist.albums:
            self.ui.tableWidgetAlbums.insertRow(i)

            titleItem = QtWidgets.QTableWidgetItem(alb.title)
            titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.ui.tableWidgetAlbums.setItem(i,0,titleItem)

            yearItem = QtWidgets.QTableWidgetItem(str(alb.year))
            yearItem.setFlags(yearItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.ui.tableWidgetAlbums.setItem(i,1,yearItem)
            
            idItem = QtWidgets.QTableWidgetItem(str(alb.albumID))
            idItem.setFlags(idItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.ui.tableWidgetAlbums.setItem(i,2,idItem)


            if(i==0 and self.currentAlbum == None):
                print("Show first album")
                
            elif(alb.albumID==self.currentAlbum.albumID):
                print("showAlbums() --> Select album="+alb.title)
                indexToSel = i
                #self.ui.tableWidgetAlbums.selectRow(i)

            i+=1

        self.ui.tableWidgetAlbums.selectRow(indexToSel)
        self.ui.tableWidgetAlbums.scrollTo(self.ui.tableWidgetAlbums.currentIndex(), QtWidgets.QAbstractItemView.PositionAtCenter)

        #self.ui.tableWidgetAlbums.show()


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

            titleItem = QtWidgets.QTableWidgetItem(track.title)
            titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.ui.tableWidgetTracks.setItem(i,0,titleItem)

            durationItem = QtWidgets.QTableWidgetItem(track.getDurationText())
            durationItem.setFlags(durationItem.flags() ^ QtCore.Qt.ItemIsEditable)
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
        
        #self.player.dropMediaList()
        self.musicBase.history.insertAlbumHistory(alb.albumID)
        self.player.playAlbum(alb)
        
        self.setVolume(self.getVolumeFromSlider())
        self.showPlaylist(True)

    def addAlbum(self,alb):
        '''Add tracks in playlist and start playing'''
        self.player.addAlbum(alb)
        self.setVolume(self.getVolumeFromSlider())
        self.showPlaylist(True)


    def showPlaylist(self,showOnlyIfNew=False):
        isNew = False
        if self.playList is None:
            isNew = True
            self.playList = playlistWidget(self.player)
            self.playList.trackChanged.connect(self.player.setPlaylistTrack)

        self.playList.showMediaList()
            
        if isNew or showOnlyIfNew==False: self.playList.show()


    def showHistory(self):
        if self.histoWidget is None:
            isNew = True
            self.histoWidget = historyWidget(self.musicBase)
             
        self.histoWidget.show()


    def onPlayerMediaChangedVLC(self,event):
        print("onPlayerMediaChangedVLC")
        trk = self.player.getCurrentTrackPlaylist()
        if not self.player.radioMode:
            self.musicBase.history.insertTrackHistory(trk.parentAlbum.albumID,trk.getFilePathInAlbumDir())
        if self.playList is not None:
            self.playList.setCurrentTrack()


    def onPlayerMediaChangedStreamObserver(self,title):
        print("onPlayerMediaChangedStreamObserver="+title)

        trk = self.player.getCurrentTrackPlaylist()
        
        self.musicBase.history.insertRadioHistory(self.player.currentRadioName,title)
        if self.playList is not None:
            self.playList.setCurrentTrack(title)



    def onPlayAlbum(self,item):
        print("onPlayAlbum "+self.currentAlbum.getAlbumDir())
        self.playAlbum(self.currentAlbum)


    def onAddAlbum(self,item):
        print("onAddAlbum "+self.currentAlbum.getAlbumDir())
        self.addAlbum(self.currentAlbum)


    def onPauseAlbum(self):
        self.player.pauseMediaList()

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
        
        if path != "":
            print("MyCover="+path)
            self.coverPixmap = QtGui.QPixmap(path)
            scaledCover = self.coverPixmap.scaled(self.ui.cover.size(),
                                                    QtCore.Qt.KeepAspectRatio,
                                                    QtCore.Qt.SmoothTransformation)
            self.ui.cover.setPixmap(scaledCover)
            self.ui.cover.show()
        else:
            self.ui.cover.setPixmap(self.defaultPixmap)
    

    def resizeEvent(self,event):
        self.resizeCover()


    def resizeCover(self):
        if (not self.coverPixmap.isNull()):
            scaledCover = self.coverPixmap.scaled(self.ui.cover.size(),
                                                    QtCore.Qt.KeepAspectRatio,
                                                    QtCore.Qt.SmoothTransformation)
            self.ui.cover.setPixmap(scaledCover)
        

    def closeEvent(self, event):
        if self.playList is not None: self.playList.close()
        if self.histoWidget is not None: self.histoWidget.close()
        self.saveSettings()

    def saveSettings(self):
        self.settings.setValue('volume', self.player.getVolume())

    def loadSettings(self):
        if self.settings.contains('volume'):
            self.volume = self.settings.value('volume', type=int)
        else:
            self.volume = 100

    def changeLanguage(self,locale):
        # translator for built-in qt strings
        self.translator.unInstallTranslators()
        self.translator.installTranslators(locale)
        self.ui.retranslateUi(self)
        if self.playList is not None: self.playList.retranslateUi()
        if self.histoWidget is not None: self.histoWidget.retranslateUi()
        
        self.update()
        self.setWindowTitle("PyZik")
        self.setTitleLabel()



    

if __name__ == '__main__':
    from pyzik import *
    main()
