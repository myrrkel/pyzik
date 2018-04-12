from PyQt5 import QtWidgets, QtGui, QtCore
import dialogMusicDirectories
from musicBase import * 
from musicDirectory import *
from database import *



class DialogMusicDirectoriesLoader(QtWidgets.QDialog):

    def __init__(self,mb):
        QtWidgets.QDialog.__init__(self)
        self.mb = mb
        self.currentDir = None
        self.ui = dialogMusicDirectories.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("PyZic")
        self.ui.wRight.setEnabled(False)

        self.ui.AddButton.clicked.connect(self.onAddDir)
        self.ui.DirButton.clicked.connect(self.onChangeDir)
        self.ui.Name.textChanged.connect(self.onNameChanged)
        self.ui.comboStyle.currentIndexChanged.connect(self.onChangeGenre)

        self.loadDirList()
        self.showGenres()

        

    def onNameChanged(self,item):
        self.currentDir.dirName = self.ui.Name.text()
        
    def onDirChanged(self,item):
        if self.currentDir != None :
            self.currentDir.updateMusicDirectoryDB()
        sel = self.ui.DirListView.selectionModel().selectedIndexes()
        #if len(sel)==1:
        #index = self.ui.listViewArtists.selectionModel().selectedIndexes()[0]
        index = item
        nrow = item.row()
        model = self.ui.DirListView.model()
                
        md = model.item(nrow).musicDir
        self.currentDir = md
        self.ui.wRight.setEnabled(True)
        self.ui.Name.setText(md.dirName)
        self.ui.DirEdit.setText(md.dirPath)
        print("Current Style ID="+str(md.styleID))
        if md.styleID != None :
            #i = self.ui.comboStyle.findData(md.styleID)
            #print("found index="+str(i))
            self.ui.comboStyle.setCurrentIndex(md.styleID)
        else:
            self.ui.comboStyle.setCurrentIndex(-1)

        self.ui.wRight.setEnabled(True)

    def onAddDir(self):
        
        sDir = self.selectDir()
        if(sDir != ""):
            md = musicDirectory(sDir)
            
            md.dirName, ok = QtWidgets.QInputDialog.getText(self, 'Give a name to your directory', 
            'Directory name:')
            if((md.dirName != "") & ok):
                self.mb.musicDirectoryCol.addMusicDirectory(md)
                self.loadDirList()
        
                print("Directory="+sDir+" DirName="+md.dirName)


    def onChangeDir(self):
        sDir = self.selectDir()
        self.ui.DirEdit.text = sDir
        self.currentDir.dirPath = sDir

    def onChangeGenre(self):
        if self.currentDir != None:
            self.currentDir.styleID = self.ui.comboStyle.currentIndex()
            print("New Genre ID="+str(self.currentDir.styleID))


    def selectDir(self):
        sDir = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        return sDir


    def loadDirList(self):
        
        model = QtGui.QStandardItemModel(self.ui.DirListView)
        for musicDir in self.mb.musicDirectoryCol.musicDirectories:
            itemDir = QtGui.QStandardItem(musicDir.dirName)
            itemDir.musicDir = musicDir
            model.appendRow(itemDir)
        self.ui.DirListView.setModel(model)
        self.ui.DirListView.selectionModel().currentChanged.connect(self.onDirChanged)

    def showGenres(self):
        model = QtGui.QStandardItemModel(self.ui.comboStyle)
        for genre in musicGenres:
            item = QtGui.QStandardItem(genre)
             
            # Add the item to the model
            model.appendRow(item)
        self.ui.comboStyle.setModel(model)
        self.ui.comboStyle.setCurrentIndex(9)


if __name__ == '__main__':
    import sys
    from darkStyle import darkStyle

    app = QtWidgets.QApplication(sys.argv)

    translator = QtCore.QTranslator(app)
    locale = QtCore.QLocale.system().name()

    translator.load('pyzik_%s.qm' % locale)

    app.installTranslator(translator)

    #Load & Set the DarkStyleSheet
    app.setStyleSheet(darkStyle.darkStyle.load_stylesheet_pyqt5())
   
    mb = musicBase()

    mb.musicDirectoryCol.loadMusicDirectories()
    
    window = DialogMusicDirectoriesLoader(mb)

    window.show()

    sys.exit(app.exec_())