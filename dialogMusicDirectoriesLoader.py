from PyQt5 import QtWidgets, QtGui, QtCore
import dialogMusicDirectories
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

        sel = self.ui.DirListView.selectionModel().selectedIndexes()
        #if len(sel)==1:
        #index = self.ui.listViewArtists.selectionModel().selectedIndexes()[0]
        index = item
        nrow = item.row()
        model = self.ui.DirListView.model()
                
        md = model.item(nrow).musicDir
        self.ui.wRight.setEnabled(True)
        self.ui.Name.setText(md.dirName)
        self.ui.DirEdit.setText(md.dirPath)
        i = self.ui.DirStyle.findData(md.styleID)
        self.ui.DirStyle.setCurrentIndex(i)
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