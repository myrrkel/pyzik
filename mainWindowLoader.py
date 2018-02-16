#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtGui, QtCore
import mainWindow  # import of mainWindow.py made with pyuic5
from musicBase import * 
from musicDirectory import *
from database import *
from playerVLC import *
from darkStyle import darkStyle
from dialogMusicDirectoriesLoader import *



class MainWindowLoader(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

       
        self.currentArtist = artist("",0)
        self.coverPixmap = QtGui.QPixmap()
        self.defaultPixmap = QtGui.QPixmap()

        self.ui = mainWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setTitleLabel("")
        self.setWindowTitle("PyZik")
        self.initAlbumTableWidget()
        self.initTrackTableWidget()

        self.showArtists()
        

        #Connect UI triggers
        self.ui.listViewArtists.selectionModel().currentChanged.connect(self.onArtistChange)
        #self.ui.listViewArtists.clicked.connect(self.onArtistChange)
        self.ui.actionMusic_directories.triggered.connect(self.onMenuMusicDirectories)
        self.ui.actionExplore_music_directories.triggered.connect(self.onMenuExplore)
        self.ui.actionDelete_database.triggered.connect(self.onMenuDeleteDatabase)
        self.ui.playButton.clicked.connect(self.onPlayAlbum)
        self.ui.stopButton.clicked.connect(self.onPauseAlbum)
        self.ui.nextButton.clicked.connect(player.mediaListPlayer.next)
        self.ui.previousButton.clicked.connect(player.mediaListPlayer.previous)
        self.ui.searchEdit.textChanged.connect(self.onSearchChange)
        self.ui.searchEdit.returnPressed.connect(self.onSearchEnter)
        self.ui.tableWidgetAlbums.clicked.connect(self.onAlbumChange)

        self.ui.volumeSlider.setMaximum(100)
        self.ui.volumeSlider.setValue(player.mediaPlayer.audio_get_volume())
        self.ui.volumeSlider.valueChanged.connect(self.setVolume)
       
        
        #Write message in status bar
        self.ui.statusBar.showMessage("PyZik")





    def showEvent(self,event):
        #This function is called when the mainWindow is shown
        alb = mb.albumCol.getRandomAlbum()
        if(alb != None):
            print("RamdomAlb="+alb.title)
            self.showAlbum(alb)



    def setVolume(self, Volume):
        player.setVolume(Volume)
   


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
        mb.exploreAlbumsDirectories()
        self.showArtists()
    
    def onMenuDeleteDatabase(self):
        db.dropAllTables()
        mb.emptyDatas()
        self.showArtists()
        self.initAlbumTableWidget()


    '''
    Artist listView functions
    '''
    def showArtists(self):
        # Add artists in the QListView
        model = QtGui.QStandardItemModel(self.ui.listViewArtists)
        for art in mb.artistCol.artists:
            itemArt = QtGui.QStandardItem(art.name)
            itemArt.artist = art
            model.appendRow(itemArt)

        self.ui.listViewArtists.setModel(model)
        self.ui.listViewArtists.show()

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
        sel = self.ui.listViewArtists.selectionModel().selectedIndexes()
        if len(sel)==1:
            nrow = item.row()
            
            model = self.ui.listViewArtists.model()
            self.currentArtist = model.item(nrow).artist
        
            self.showAlbums(self.currentArtist)


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
            self.showAlbums(item.artist)

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
        print("OnAlbumChange")
        selItems = self.ui.tableWidgetAlbums.selectedItems()
        if(len(selItems)>0):
            r = selItems[0].row()
            albumIDSel = self.ui.tableWidgetAlbums.item(r,2).text()
            alb = mb.albumCol.getAlbum(albumIDSel)
            if(alb.albumID != 0):
                self.showAlbum(alb)
            else:
                print("No album to show")


    def showAlbums(self,artist):
        #Add albums in the QTableView

        print("Show albums")
        self.ui.tableWidgetAlbums.setRowCount(0)
        i=0
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


            if(i==0):
                self.ui.tableWidgetAlbums.selectRow(i)
                self.onAlbumChange(self.ui.tableWidgetAlbums.item(i,0)) 
            i+=1


        self.ui.tableWidgetAlbums.show()


    def showAlbum(self,album):
        print("showAlbum")
        self.ui.statusBar.showMessage("selected: "+album.title)
        self.setTitleLabel(self.currentArtist.name,album.title,album.year)
        
        album.getImages()
        album.getTracks(player)
        album.getCover()

        if album.cover != "":
            self.showCover(os.path.join(album.dirPath,album.cover))
        else:
            self.showCover("")
        
        self.ui.tableWidgetTracks.setColumnCount(1)
        self.ui.tableWidgetTracks.setRowCount(0)
        i=0
        for track in album.tracks:
            self.ui.tableWidgetTracks.insertRow(i)
            titleItem = QtWidgets.QTableWidgetItem(track.title)
            titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.ui.tableWidgetTracks.setItem(i,0,titleItem)
            i+=1


    '''
    Interactions with vlc module
    '''
    def onPlayAlbum(self,item):
        #Add tracks in playlist and start playing
        alb = self.getAlbumFromTable()
        player.dropMediaList()
        if(alb.albumID != 0):
            for track in alb.tracks:
                player.addFile(os.path.join(alb.dirPath,track.getFileName()))
                
        player.playMediaList()


    def onPauseAlbum(self):
        player.pauseMediaList()


    '''
    Miscellanious UI functions 
    '''

    def setTitleLabel(self,artName="",AlbTitle="",Year=""):
        if(artName==""):
            sTitle = ""
        else:
            sAlbum = AlbTitle
            sYear =str(Year)
            if(sYear != "0"): sAlbum += " ("+sYear+")"
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
        
    

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    mb = musicBase()

    db = database()
    
    mb.loadMusicBase()

    player = playerVLC()

    #Load & Set the DarkStyleSheet
    app.setStyleSheet(darkStyle.darkStyle.load_stylesheet_pyqt5())

    
    translator = QtCore.QTranslator(app)
    locale = QtCore.QLocale.system().name()
    # translator for built-in qt strings
    translator.load('pyzik_%s.qm' % locale)

    app.installTranslator(translator)


    window = MainWindowLoader()
    window.show()

    app.exec()