#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtGui
import mainWindow  # import of mainWindow.py made with pyuic5
from musicBase import * 
from musicDirectory import *
from database import *
from playerVLC import *
from dialogMusicDirectoriesLoader import *



class MainWindowLoader(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        
        self.ui = mainWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("PyZic")

        self.showArtists()
        

        self.initAlbumTableWidget()

        self.ui.listViewArtists.selectionModel().currentChanged.connect(self.onArtistChange)
        self.ui.listViewArtists.clicked.connect(self.onArtistChange)
        self.ui.actionMusic_directories.triggered.connect(self.onMenuMusicDirectories)
        self.ui.actionExplore_music_directories.triggered.connect(self.onMenuExplore)
        self.ui.actionDelete_database.triggered.connect(self.onDelete_database)
        self.ui.playButton.clicked.connect(self.onPlayAlbum)

        
        

        #Write message in status bar
        self.ui.statusBar.showMessage("PyZic")
        

    def onMenuMusicDirectories(self):
        dirDiag = DialogMusicDirectoriesLoader(mb)
        dirDiag.show()
        dirDiag.exec_()
        #self.ui.statusBar.showMessage("Action Bouton")
    
    def onMenuExplore(self):
        mb.exploreAlbumsDirectories()
        self.showArtists()
        #self.ui.statusBar.showMessage("Action Bouton")
    
    def onDelete_database(self):
        db.dropAllTables()
        mb.emptyDatas()
        self.showArtists()
        self.initAlbumTableWidget()
        #self.ui.statusBar.showMessage("Action Bouton")

    def getAlbumFromTable(self):
        selAlbItems = self.ui.tableWidgetAlbums.selectedItems()
        for item in selAlbItems:
            r = item.row()
            albumIDSel = self.ui.tableWidgetAlbums.item(r,2).text()
            print("AlbumIDSel="+str(albumIDSel))
            alb = mb.albumCol.getAlbum(albumIDSel)
            if(alb.albumID == 0): 
                print("Album is Empty. Item:"+str(item))
            return alb


    def onPlayAlbum(self,item):
        alb = self.getAlbumFromTable()
        player.initMediaList()
        if(alb.albumID != 0):
            for track in alb.tracks:
                player.addFile(alb.dirPath+'/'+track.getFileName())
                player.playMediaList()
            


    def onArtistChange(self,item):
        sel = self.ui.listViewArtists.selectionModel().selectedIndexes()
        if len(sel)==1:
            #index = self.ui.listViewArtists.selectionModel().selectedIndexes()[0]
            index = item
            nrow = index.row()
            model = self.ui.listViewArtists.model()
            self.ui.statusBar.showMessage(  "selected: "+model.data(index) \
                                        +" id="+str(model.item(nrow).artist.artistID))
            self.ui.labelArtist.setText(model.item(nrow).artist.name)
        
            self.showAlbums(self.ui.listViewArtists.model().item(nrow).artist)

    def onAlbumChange(self,item):

        selItems = self.ui.tableWidgetAlbums.selectedItems()
        for item in selItems:
            r = item.row()
            albumIDSel = self.ui.tableWidgetAlbums.item(r,2).text()
            print("AlbumIDSel="+str(albumIDSel))
            alb = mb.albumCol.getAlbum(albumIDSel)
            if(alb.albumID != 0):
                self.showAlbum(alb)
            else:
                print("No album to show")



    def showAlbums(self,artist):
        # Add albums in the QTableView
        self.ui.tableWidgetAlbums.setRowCount(0)
        i=0
        for alb in artist.albums:
            self.ui.tableWidgetAlbums.insertRow(i)
            self.ui.tableWidgetAlbums.setItem(i,0,QtWidgets.QTableWidgetItem(alb.title))
            self.ui.tableWidgetAlbums.setItem(i,1,QtWidgets.QTableWidgetItem(str(alb.year)))
            self.ui.tableWidgetAlbums.setItem(i,2,QtWidgets.QTableWidgetItem(str(alb.albumID)))

            i+=1

        # On click show album details
        self.ui.tableWidgetAlbums.clicked.connect(self.onAlbumChange)
        #self.ui.tableWidgetAlbums.setModel(model)
        self.ui.tableWidgetAlbums.show()

    def showAlbum(self,album):
        self.ui.statusBar.showMessage("selected: "+album.title)
        album.getTracks()
        i=0
        self.ui.tableWidgetTracks.setColumnCount(1)        
        self.ui.tableWidgetTracks.setRowCount(0)
        for track in album.tracks:
            

            self.ui.tableWidgetTracks.insertRow(i)
            self.ui.tableWidgetTracks.setItem(i,0,QtWidgets.QTableWidgetItem(track.title))
            #self.ui.tableWidgetTracks.setItem(i,1,QtWidgets.QTableWidgetItem(str(alb.year)))

            i+=1


    def showArtists(self):   
        # Add artists in the QListView
        model = QtGui.QStandardItemModel(self.ui.listViewArtists)
        for art in mb.artistCol.artists:
            itemArt = QtGui.QStandardItem(art.name)
            itemArt.artist = art
            model.appendRow(itemArt)

        self.ui.listViewArtists.setModel(model)
        self.ui.listViewArtists.show()


    def initAlbumTableWidget(self):
        self.ui.tableWidgetAlbums.setRowCount(0)
        hHeader = self.ui.tableWidgetAlbums.horizontalHeader()
        vHeader = self.ui.tableWidgetAlbums.verticalHeader()
        vHeader.hide()
        hHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        hHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        hHeader.hideSection(2)
        #header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

    

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    mb = musicBase()

    db = database()
    
    mb.loadMusicBase()

    player = playerVLC()

    #Load & Set the DarkStyleSheet
    app.setStyleSheet(qdarkgraystyle.load_stylesheet_pyqt5())

    
    translator = QtCore.QTranslator(app)
    locale = QtCore.QLocale.system().name()
    # translator for built-in qt strings
    translator.load('pyzik_%s.qm' % locale)

    app.installTranslator(translator)


    window = MainWindowLoader()
    window.show()
    sys.exit(app.exec_())