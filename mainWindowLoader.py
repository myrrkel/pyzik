#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, subprocess, functools
from PyQt5 import QtWidgets, QtGui, QtCore
import mainWindow  # import of mainWindow.py made with pyuic5
from musicBase import *
from musicDirectory import *
from database import *
from playerVLC import *
from darkStyle import darkStyle
from dialogMusicDirectoriesLoader import *
from streamObserver import *
from albumThread import *
from musicBaseThread import *
from playlistWidget import *



def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener ="open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])



class MainWindowLoader(QtWidgets.QMainWindow):

    def __init__(self, parent=None,app=None):
        QtWidgets.QMainWindow.__init__(self, parent)


        self.firstShow = True
        self.playList = None

        self.app = app
        self.translators = []
        self.locale = QtCore.QLocale.system().name()
        self.currentArtist = artist("",0)
        self.currentAlbum = album("")
        self.coverPixmap = QtGui.QPixmap()
        self.defaultPixmap = QtGui.QPixmap()

        self.settings = QtCore.QSettings('pyzik', 'pyzik')
        self.loadSettings()

        self.ui = mainWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.changeLanguage(self.locale)





        self.setTitleLabel("")
        self.setWindowTitle("PyZik")
        self.initAlbumTableWidget()
        self.initTrackTableWidget()

        self.showArtists()
        

        #Connect UI triggers
        self.ui.listViewArtists.selectionModel().currentChanged.connect(self.onArtistChange)
        self.ui.actionMusic_directories.triggered.connect(self.onMenuMusicDirectories)
        self.ui.actionExplore_music_directories.triggered.connect(self.onMenuExplore)
        self.ui.actionRandom_album.triggered.connect(self.ramdomAlbum)
        self.ui.actionDelete_database.triggered.connect(self.onMenuDeleteDatabase)
        self.ui.actionFuzzyGroovy.triggered.connect(self.onPlayFuzzyGroovy)
        self.ui.actionPlaylist.triggered.connect(self.showPlaylist)
        self.ui.actionLanguageSpanish.triggered.connect(functools.partial(self.changeLanguage, 'es'))
        self.ui.actionLanguageFrench.triggered.connect(functools.partial(self.changeLanguage, 'fr'))
        self.ui.actionLanguageEnglish.triggered.connect(functools.partial(self.changeLanguage, 'en'))
        self.ui.playButton.clicked.connect(self.onPlayAlbum)
        self.ui.addAlbumButton.clicked.connect(self.onAddAlbum)
        self.ui.pauseButton.clicked.connect(self.onPauseAlbum)
        #self.ui.nextButton.clicked.connect(player.mediaListPlayer.next)
        self.ui.openDirButton.clicked.connect(self.onOpenDir)
        #self.ui.previousButton.clicked.connect(player.mediaListPlayer.previous)
        self.ui.searchEdit.textChanged.connect(self.onSearchChange)
        self.ui.searchEdit.returnPressed.connect(self.onSearchEnter)
        self.ui.tableWidgetAlbums.selectionModel().currentRowChanged.connect(self.onAlbumChange)
        self.ui.tableWidgetAlbums.customContextMenuRequested.connect(self.handleHeaderMenu)
        
        self.shortcutRandomAlbum = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+R"), self)
        self.shortcutRandomAlbum.activated.connect(self.ramdomAlbum)


        #Connect VLC triggers
        player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerMediaChanged, self.onPlayerMediaChangedVLC)
        player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerPaused, self.paused)
        player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerPlaying, self.isPlaying)
        #player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerPositionChanged, self.onPlayerPositionChanged)
        #player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerAudioVolume , self.setVolumeSliderFromPlayer)


        self.ui.volumeSlider.setMaximum(100)

        self.ui.volumeSlider.setValue(self.volume)
        player.setVolume(self.volume)
        self.ui.volumeSlider.valueChanged.connect(self.setVolume)
       
        
        #Write message in status bar
        self.ui.statusBar.showMessage("PyZik")


        self.threadStreamObserver = streamObserver()
        self.threadStreamObserver.player = player
        self.threadStreamObserver.titleChanged.connect(self.setStatus)
        
        player.mpEnventManager.event_attach(vlc.EventType.MediaPlayerStopped, self.threadStreamObserver.resetPreviousTitle)

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
        player.playFuzzyGroovy()
        self.showPlaylist(True)
        self.setVolume(self.getVolumeFromSlider())

        

    def ramdomAlbum(self):
        alb = mb.albumCol.getRandomAlbum()
        self.currentAlbum = alb
        if(alb != None):
            print("RamdomAlb="+alb.title)
            art = mb.artistCol.getArtistByID(alb.artistID)
            self.currentArtist = art
            self.selectArtistListView(art)
            self.showArtist(art)
            #self.showAlbum(alb)



    def setVolume(self, volume):
        player.setVolume(volume)

    def getVolumeFromSlider(self):
        return self.ui.volumeSlider.value()

    def setVolumeSliderFromPlayer(self,event):
        volume = player.getVolume()
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
        

    '''
    Menu Actions
    '''
    def onMenuMusicDirectories(self):
        dirDiag = DialogMusicDirectoriesLoader(mb)
        dirDiag.show()
        dirDiag.exec_()
        
    def onMenuExplore(self):
        self.exploreAlbumsDirectoriesThread.musicbase = mb 
        self.wProgress = progressWidget()
        self.exploreAlbumsDirectoriesThread.progressChanged.connect(self.wProgress.setValue)
        self.exploreAlbumsDirectoriesThread.directoryChanged.connect(self.wProgress.setDirectoryText)
        self.exploreAlbumsDirectoriesThread.exploreCompleted.connect(self.wProgress.close)
        self.wProgress.progressClosed.connect(self.exploreAlbumsDirectoriesThread.stop)
        self.exploreAlbumsDirectoriesThread.start()
        
    
    def onMenuDeleteDatabase(self):
        mb.db.dropAllTables()
        mb.emptyDatas()
        self.showArtists()
        self.initAlbumTableWidget()

    def handleHeaderMenu(self, pos):
        print('column(%d)' % self.ui.tableWidgetAlbums.horizontalHeader().logicalIndexAt(pos))
        menu = QtWidgets.QMenu()
        menu.addAction('Add')
        menu.addAction('Delete')
        menu.exec(QtGui.QCursor.pos())


    '''
    Artist listView functions
    '''
    def showArtists(self):
        # Add artists in the QListView
        model = QtGui.QStandardItemModel(self.ui.listViewArtists)
        for art in mb.artistCol.artists:
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
        if item != None:
            selModel = self.ui.listViewArtists.selectionModel()
            selModel.reset()
            selModel.select(item.index(), QtCore.QItemSelectionModel.Select)
            self.showArtist(item.artist)

    def onSearchChange(self,item):
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



    '''
    Album tableWidget functions
    '''
    def getAlbumFromTable(self):
        #Return the selected album
        selAlbItems = self.ui.tableWidgetAlbums.selectedItems()
        for item in selAlbItems:
            r = item.row()
            albumIDSel = self.ui.tableWidgetAlbums.item(r,2).text()
            
            alb = mb.albumCol.getAlbum(albumIDSel)
            if(alb.albumID == 0): 
                print("Album is Empty. Item:"+str(item))
            return alb


    def onAlbumChange(self,item):
        if item.row() >= 0:
            print("OnAlbumChange:"+str(item.row()))
            albumIDSel = self.ui.tableWidgetAlbums.item(item.row(),2).text()
            alb = mb.albumCol.getAlbum(albumIDSel)
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

        if(self.currentAlbum == None):
            self.currentAlbum = artist.getRandomAlbum()

        if(self.currentAlbum.artistID != artist.artistID):
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
        #self.currentArtist = mb.artistCol.getArtistByID(album.artistID)
        self.setTitleLabel(self.currentArtist.name,album.title,album.year)
        
        #Start a thread to load album datas from directory
        #When updated, triggers launch showAlbumCover and showAlbumTracks
        if self.loadAlbumFilesThread.isRunning() :
            print("Stop Thread loadAlbum")
            self.loadAlbumFilesThread.stop()
            self.loadAlbumFilesThread.wait()
        
        self.loadAlbumFilesThread.album = album
        self.loadAlbumFilesThread.player = player
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
            i+=1

    def showAlbumCover(self,result):
        album = self.currentAlbum
        if album.cover != "":
            self.showCover(os.path.join(album.getAlbumDir(),album.cover)) 
        else:
            self.showCover("")


    '''
    Interactions with vlc module
    '''
    def playAlbum(self,alb):
        '''Add tracks in playlist and start playing'''
        
        #player.dropMediaList()
        player.playAlbum(alb)
        self.setVolume(self.getVolumeFromSlider())
        self.showPlaylist(True)

    def addAlbum(self,alb):
        '''Add tracks in playlist and start playing'''
        player.addAlbum(alb)
        self.setVolume(self.getVolumeFromSlider())
        self.showPlaylist(True)


    def showPlaylist(self,showOnlyIfNew=False):
        isNew = False
        if self.playList == None:
            isNew = True
            self.playList = playlistWidget(player)
            self.playList.trackChanged.connect(player.setPlaylistTrack)
            self.threadStreamObserver.titleChanged.connect(self.onPlayerMediaChangedStreamObserver)

        self.playList.showMediaList()
            
        if isNew or showOnlyIfNew==False: self.playList.show()


    def onPlayerMediaChangedVLC(self,event):
        print("onPlayerMediaChangedVLC")
        if self.playList != None:
            self.playList.setCurrentTrack()


    def onPlayerMediaChangedStreamObserver(self,title):
        print("onPlayerMediaChangedStreamObserver="+title)
        if self.playList != None:
            self.playList.setCurrentTrack(title)



    def onPlayAlbum(self,item):
        print("onPlayAlbum "+self.currentAlbum.getAlbumDir())
        self.playAlbum(self.currentAlbum)


    def onAddAlbum(self,item):
        print("onAddAlbum "+self.currentAlbum.getAlbumDir())
        self.addAlbum(self.currentAlbum)


    def onPauseAlbum(self):
        player.pauseMediaList()

    def onOpenDir(self):
        open_file(self.currentAlbum.getAlbumDir())


    '''
    Miscellanious UI functions 
    '''

    def setTitleLabel(self,artName="",AlbTitle="",Year=""):

        if self.currentArtist != None and artName=="":
            artName = self.currentArtist.name
        if self.currentAlbum != None and AlbTitle=="":  
            AlbTitle = self.currentAlbum.title
            Year = self.currentAlbum.year

        sAlbum = AlbTitle
        sYear =str(Year)
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
        self.saveSettings()

    def saveSettings(self):
        self.settings.setValue('volume', player.getVolume())

    def loadSettings(self):
        if self.settings.contains('volume'):
            self.volume = self.settings.value('volume', type=int)
        else:
            self.volume = 100

    def changeLanguage(self,locale):
        # translator for built-in qt strings
        self.unInstallTranslators()
        self.installTranslator("pyzik",locale)
        self.installTranslator("playlistWidget",locale)
        self.ui.retranslateUi(self)
        if self.playList != None: self.playList.retranslateUi()
        
        self.update()
        self.setWindowTitle("PyZik")
        self.setTitleLabel()



    def installTranslator(self,filename,locale):
        translator = QtCore.QTranslator(self.app)
        translator.load('{0}_{1}.qm'.format(filename,locale))
        self.translators.append(translator)
        self.app.installTranslator(translator)

    
    def unInstallTranslators(self):
        for translator in self.translators:
            self.app.removeTranslator(translator)
        self.translators = []

    

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    #Load & Set the DarkStyleSheet
    app.setStyleSheet(darkStyle.darkStyle.load_stylesheet_pyqt5())

    mb = musicBase()
    print('loadMusicBase')
    mb.loadMusicBase()
    print('player')
    player = playerVLC()
    



    window = MainWindowLoader(None,app)
    print('show')
    window.show()

    app.exec()
    window.threadStreamObserver.stop()


    player.release()

    sys.exit()