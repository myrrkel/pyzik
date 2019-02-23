#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PyQt5.QtCore import Qt, pyqtSignal, QCoreApplication, QSize
from PyQt5.QtWidgets import QDialog, QWidget, QShortcut, QAction, QWidget, QMainWindow, \
                            QSizePolicy, QLabel, QFrame, QVBoxLayout, QHBoxLayout, QApplication
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence



class fullScreenCoverWidget(QDialog):
    
    coverPixmap = None

    def __init__(self):
        QDialog.__init__(self)
        
        self.setWindowFlags(
                            Qt.Window | 
                            Qt.WindowStaysOnTopHint | 
                            Qt.MaximizeUsingFullscreenGeometryHint | 
                            Qt.FramelessWindowHint )


        self.initUI()

        #self.shortcutPause = QShortcut(QtGui.QKeySequence("Space"), self)
        #self.shortcutPause.activated.connect(self.player.pause)
        self.shortcutClose = QShortcut(QKeySequence("Escape"), self)
        self.shortcutClose.activated.connect(self.close)

        self.setBackgroundBlack()
        #self.cover.show()

    def show(self):
        self.showFullScreen()
        self.setBackgroundBlack()


    def setBackgroundBlack(self):
        self.setStyleSheet("background-color:black;")

    def initUI(self):

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)

        self.vLayout = QVBoxLayout()
        self.vLayout.setContentsMargins(6, 6, 6, 6)
        self.vLayout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.vLayout)


        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        
        self.cover = QLabel()
        self.cover.setSizePolicy(sizePolicy)
        self.cover.setMinimumSize(QSize(300, 300))
        self.cover.setAlignment(Qt.AlignCenter)
        self.coverPixmap = QPixmap()

        self.cover.setPixmap(self.coverPixmap)
        self.vLayout.addWidget(self.cover)



    def mousePressEvent(self, event):
        self.close()


    def resizeEvent(self,event):
        self.resizeCover()


    def resizeCover(self):
        if (not self.coverPixmap.isNull()):
            scaledCover = self.coverPixmap.scaled(self.cover.size(),
                                                    Qt.KeepAspectRatio,
                                                    Qt.SmoothTransformation)
            self.cover.setPixmap(scaledCover)



    def setPixmapFromUri(self,path):
        self.coverPixmap = QPixmap(path)
        self.showCover()
        

    def showCover(self):
        if not self.coverPixmap.isNull():
            print("Pic size="+str(self.cover.size()))
            scaledCover = self.coverPixmap.scaled(self.cover.size(),
                                                    Qt.KeepAspectRatio,
                                                    Qt.SmoothTransformation)
            self.cover.setPixmap(scaledCover)
        else:
            self.cover.setPixmap(QPixmap())
        self.cover.show()



if __name__ == "__main__":
    import sys
    from picDownloader import *

    app = QApplication(sys.argv)


    fs = fullScreenCoverWidget()

    fs.show()

    url = "https://i3.radionomy.com/radios/400/ce7c17ce-4b4b-4698-8ed0-c2881eaf6e6b.png"
    pd = picDownloader()
    tempPath = pd.getPic(url)
    fs.setPixmapFromUri(tempPath)


    sys.exit(app.exec_())
