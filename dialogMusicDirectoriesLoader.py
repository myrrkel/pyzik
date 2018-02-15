from PyQt5 import QtWidgets, QtGui, QtCore
import dialogMusicDirectories  # import du fichier dialogMusicDirectories.py généré par pyuic5
from musicBase import * 
from musicDirectory import *
from database import *



class DialogMusicDirectoriesLoader(QtWidgets.QDialog):

    def __init__(self,mb):
        QtWidgets.QDialog.__init__(self)
        self.mb = mb
        self.ui = dialogMusicDirectories.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("PyZic")
        self.ui.wRight.setEnabled(False)

        self.ui.AddButton.clicked.connect(self.onAddDir)
        self.ui.DirButton.clicked.connect(self.onChangeDir)
        self.loadDirList()

        
        
    def onDirChanged(self,item):
        sel = self.ui.tableViewAlbums.selectionModel().selectedIndexes()
        if len(sel)==1:
            #index = self.ui.listViewArtists.selectionModel().selectedIndexes()[0]
            index = item
            nrow = index.row()
            model = self.ui.tableViewAlbums.model()
                    
            self.showAlbum(self.ui.tableViewAlbums.model().item(nrow).album)

    def onAddDir(self):
        
        sDir = self.selectDir()
        if(sDir != ""):
            md = musicDirectory(sDir)
            
            md.dirName, ok = QtWidgets.QInputDialog.getText(self, 'Give a name to your directoy', 
            'Directory name:')
            if((md.dirName != "") & ok):
                self.mb.musicDirectoryCol.addMusicDirectory(md)
                self.loadDirList()
        
                print("Directory="+sDir+" DirName="+md.dirName)


    def onChangeDir(self):
        sDir = self.selectDir()
        self.ui.DirEdit.text = sDir

    def selectDir(self):
        sDir = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        return sDir

    def loadDirList(self):
        

        model = QtGui.QStandardItemModel(self.ui.DirListView)
        for mDir in self.mb.musicDirectoryCol.musicDirectories:
            itemDir = QtGui.QStandardItem(mDir.dirName)
            itemDir.mDirist = mDir
            model.appendRow(itemDir)
        self.ui.DirListView.setModel(model)



if __name__ == '__main__':
    import sys
    from qdarkgraystyle import *
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle('Windows')

    translator = QtCore.QTranslator(app)
    locale = QtCore.QLocale.system().name()
    # translator for built-in qt strings
    #print(locale)
    translator.load('pyzik_%s.qm' % locale)

    app.installTranslator(translator)
    #sys.exit(app.exec_())

   


    #Load & Set the DarkStyleSheet
    app.setStyleSheet(qdarkgraystyle.load_stylesheet_pyqt5())


    mb = musicBase()

    mb.musicDirectoryCol.loadMusicDirectories()
    
    window = DialogMusicDirectoriesLoader(mb)

    window.show()

    #print(str(QtWidgets.QStyleFactory.keys()))

    sys.exit(app.exec_())