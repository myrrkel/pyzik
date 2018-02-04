from PyQt5 import QtWidgets, QtGui
import mainWindow  # import of mainWindow.py made with pyuic5
from musicBase import * 
from musicDirectory import *
from database import *
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
        sel = self.ui.tableWidgetAlbums.selectionModel().selectedIndexes()
        if len(sel)==1:
            #index = self.ui.listViewArtists.selectionModel().selectedIndexes()[0]
            index = item
            nrow = index.row()
            model = self.ui.tableWidgetAlbums.model()
                    
            self.showAlbum(mb.albumCol.albums[nrow])

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
        header = self.ui.tableWidgetAlbums.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.hideSection(2)
        #header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

    

if __name__ == '__main__':
    import sys
    import vlc
    # creating a basic vlc instance
    instance = vlc.Instance()
    # creating an empty vlc media player
    mediaplayer = instance.media_player_new()
    # create the media
    filename = "/home/myrrkel/Workspace/Python/pyzik/TEST/BLOODROCK - [1972] - Passage/03 - Little Lover.mp3"
    if sys.version < '3':
        filename = unicode(filename)
    media = instance.media_new(filename)
    # put the media in the media player
    mediaplayer.set_media(media)
    
    # parse the metadata of the file
    media.parse()
    #mediaplayer.play()

    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('plastique')
    mb = musicBase()

    db = database()
    
    mb.loadMusicBase()


    #mb.exploreAlbumsDirectories()


    window = MainWindowLoader()

    window.show()
    sys.exit(app.exec_())