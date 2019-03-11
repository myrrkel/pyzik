#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize, QCoreApplication
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QPushButton, QVBoxLayout, \
QHeaderView, QHBoxLayout, QSlider, QSizePolicy, QFrame, QLabel, QShortcut
from track import *
import requests
from picFromUrlThread import *
from tableWidgetDragRows import *

from vlc import EventType as vlcEventType
from svgIcon import *

#orange = QtGui.QColor(216, 119, 0)
white = QtGui.QColor(255, 255, 255)

_translate = QCoreApplication.translate

class playerControlsWidget(QWidget):
    
    player = None

    def __init__(self,parent=None):
        QWidget.__init__(self,parent=parent)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        
        self.pauseButton = QPushButton()
        self.pauseButton.setToolTip(_translate("playlist", "Pause"))
        self.pauseButton.setIcon(getSvgIcon("pause.svg"))

        lay.addWidget(self.pauseButton)

        self.previousButton = QPushButton()
        self.previousButton.setToolTip(_translate("playlist", "Previous"))
        self.previousButton.setIcon(getSvgIcon("step-backward.svg"))
        lay.addWidget(self.previousButton)

        self.nextButton = QPushButton()
        self.nextButton.setToolTip(_translate("playlist", "Next"))
        self.nextButton.setIcon(getSvgIcon("step-forward.svg"))
        lay.addWidget(self.nextButton)

        self.deleteButton = QPushButton()
        self.deleteButton.setToolTip(_translate("playlist", "Delete all tracks"))
        self.deleteButton.setIcon(getSvgIcon("bin.svg"))
        lay.addWidget(self.deleteButton)

        self.fullscreenButton = QPushButton()
        self.fullscreenButton.setToolTip(_translate("playlist", "Full screen"))
        self.fullscreenButton.setIcon(getSvgIcon("fullscreen.svg"))
        lay.addWidget(self.fullscreenButton)

        self.volumeSlider = QSlider()
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        #sizePolicy.setHeightForWidth(self.volumeSlider.sizePolicy().hasHeightForWidth())
        self.volumeSlider.setSizePolicy(sizePolicy)
        self.volumeSlider.setMinimumSize(QSize(80, 0))
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setOrientation(Qt.Horizontal)
        self.volumeSlider.setObjectName("volumeSlider")
        lay.addWidget(self.volumeSlider)


class playlistWidget(QDialog):
    
    picFromUrlThread = None
    currentCoverPath = ""
    picBufferManager = None
    mediaList = None
    player = None
    nextPosition = 0
    isTimeSliderDown = False
    trackChanged = pyqtSignal(int, name='trackChanged')

    def __init__(self,player):
        QDialog.__init__(self)
        self.setWindowFlags(Qt.Window)
        self.player = player
        self.mediaList = self.player.mediaList
        self.fullScreenWidget = None

        if self.picFromUrlThread is None:
            self.picFromUrlThread = picFromUrlThread()


        

        self.initUI()
        self.tableWidgetTracks.cellDoubleClicked.connect(self.changeTrack)
        self.cover.mouseDoubleClickEvent = self.mouseDoubleClickEvent

    def mouseDoubleClickEvent(self,event):
        self.showFullScreen()

    def initUI(self):

        self.picFromUrlThread.downloadCompleted.connect(self.onPicDownloaded)

        self.vLayout = QVBoxLayout()
        self.vLayout.setContentsMargins(6, 6, 6, 6)
        self.setLayout(self.vLayout)
        
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        self.setSizePolicy(sizePolicy)
        self.resize(550,400)
        self.initTableWidgetTracks()

        self.playerControls = playerControlsWidget()
        self.playerControls.pauseButton.clicked.connect(self.onPause)
        self.playerControls.previousButton.clicked.connect(self.player.previous)
        self.playerControls.nextButton.clicked.connect(self.player.next)
        self.playerControls.deleteButton.clicked.connect(self.onClearPlaylist)
        self.playerControls.fullscreenButton.clicked.connect(self.showFullScreen)

        self.playerControls.volumeSlider.setValue(self.player.getVolume())
        self.playerControls.volumeSlider.sliderMoved.connect(self.setVolume)

        
        self.timeSlider = QSlider(self)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timeSlider.sizePolicy().hasHeightForWidth())
        self.timeSlider.setSizePolicy(sizePolicy)
        self.timeSlider.setMinimumSize(QSize(60, 0))
        self.timeSlider.setMinimum(0)
        self.timeSlider.setMaximum(1000)
        self.timeSlider.setOrientation(Qt.Horizontal)
        self.timeSlider.setObjectName("timeSlider")

        #self.timeSlider.mousePressEvent=self.setIsTimeSliderDown
        #self.timeSlider.mouseReleaseEvent=self.onTimeSliderIsReleased

        self.timeSlider.sliderPressed.connect(self.setIsTimeSliderDown)
        self.timeSlider.sliderReleased.connect(self.onTimeSliderIsReleased)
        self.timeSlider.sliderMoved.connect(self.setPlayerPosition)
        #self.player.mpEnventManager.event_attach(vlcEventType.MediaPlayerPositionChanged, self.onPlayerPositionChanged)

        self.shortcutPause = QShortcut(QtGui.QKeySequence("Space"), self)
        self.shortcutPause.activated.connect(self.player.pause)
        self.shortcutFullScreen = QShortcut(QtGui.QKeySequence("Ctrl+F"), self)
        self.shortcutFullScreen.activated.connect(self.showFullScreen)

        self.mainFrame = QFrame()
        self.hLayout = QHBoxLayout()
        self.hLayout.setContentsMargins(0, 0, 0, 0)
        self.hLayout.setSpacing(6)
        self.mainFrame.setLayout(self.hLayout)

        self.coverPixmap = QtGui.QPixmap()

        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        #sizePolicy.setWidthForHeight(True)
        
        self.cover = QLabel()
        self.cover.setSizePolicy(sizePolicy)
        self.cover.setMinimumSize(QSize(200, 200))
        self.cover.setMaximumSize(QSize(200, 200))
        self.cover.setPixmap(self.coverPixmap)

        self.hLayout.addWidget(self.cover)
        self.hLayout.addWidget(self.tableWidgetTracks)


        self.vLayout.addWidget(self.mainFrame)
        self.vLayout.addWidget(self.timeSlider)
        self.vLayout.addWidget(self.playerControls)
        


        self.retranslateUi()

        #self.resizeEvent = self.onResize


    def onPause(self,event):
        self.player.pause()


    def connectPicDownloader(self,picDl):
        self.picFromUrlThread = picDl
        self.picFromUrlThread.downloadCompleted.connect(self.onPicDownloaded)


    def onPicDownloaded(self,path):
        
        self.showCoverPixmap(path)


    
    def setVolume(self, volume):
        self.player.setVolume(volume)

    def setIsTimeSliderDown(self,event=None):
        print('setIsTimeSliderDown')
        self.isTimeSliderDown = True
        if event is not None: return event.accept()

    def setIsTimeSliderReleased(self,event=None):
        print('setIsTimeSliderReleased')
        self.isTimeSliderDown = False
        if event is not None: return event.accept()

    def onResize(self,event):
        hHeader = self.tableWidgetTracks.horizontalHeader()
        hHeader.resizeSections(QHeaderView.Stretch)
        

    def showFullScreen(self):
        if self.fullScreenWidget:
            self.fullScreenWidget.show()
            self.fullScreenWidget.activateWindow()

    def initTableWidgetTracks(self):

        self.tableWidgetTracks = TableWidgetDragRows(self)

        self.tableWidgetTracks.setGeometry(0, 0, 550, 300)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)

        self.tableWidgetTracks.setSizePolicy(sizePolicy)
        self.tableWidgetTracks.setMinimumSize(QSize(50, 0))

        self.tableWidgetTracks.setObjectName("tableWidgetTracks")
        self.tableWidgetTracks.setColumnCount(5)
        self.tableWidgetTracks.setRowCount(0)
        item = QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(1, item)
        item = QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(2, item)
        item = QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(3, item)
        item = QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(4, item)

        self.initColumnHeaders()

        self.tableWidgetTracks.trackMoved.connect(self.onTrackMoved)
        self.tableWidgetTracks.beforeTrackMove.connect(self.onBeforeTrackMove)



    def initColumnHeaders(self):

        hHeader = self.tableWidgetTracks.horizontalHeader()
        vHeader = self.tableWidgetTracks.verticalHeader()
        vHeader.hide()

        hHeader.resizeSections(QHeaderView.ResizeToContents)
        hHeader.setSectionResizeMode(QHeaderView.Interactive)
        hHeader.hideSection(4)

        if self.tableWidgetTracks.columnWidth(0) < 100:
            self.tableWidgetTracks.setColumnWidth(0,100)
        else:
            if self.tableWidgetTracks.columnWidth(0) > 300:
                self.tableWidgetTracks.setColumnWidth(0,300)     


    def onBeforeTrackMove(self,param):
        for i in range(0,self.tableWidgetTracks.rowCount()):
            idLine = self.tableWidgetTracks.item(i,4).setText(str(i))

    def onTrackMoved(self,trackMove: (int,int)):

        self.mediaList.lock()
        #Get new order of tracks
        new_order = []
        for i in range(0,self.tableWidgetTracks.rowCount()):
            idLine = self.tableWidgetTracks.item(i,4).text()
            new_order.append(int(idLine))

        newCurrent = 0
        currentIndex = self.player.getCurrentIndexPlaylist()

        #Backup current vlc media list
        tmp_mediaList = []
        for i in range(0,self.mediaList.count()):
            tmp_mediaList.append(self.mediaList.item_at_index(i))

        self.player.removeAllTracks()
        
        #Add tracks in new order
        for i, idLine in enumerate(new_order):
            if idLine != currentIndex:
                self.mediaList.insert_media(tmp_mediaList[idLine],i)
            else:
                newCurrent = i

        self.mediaList.unlock()   

        print("newCurrent="+str(newCurrent))
        
        self.player.refreshMediaListPlayer()    
        #self.player.resetCurrentItemIndex(newCurrent)

    def onClearPlaylist(self,event):
        #Remove all medias from the playlist except the current track
        self.player.removeAllTracks()
        self.showMediaList()


    def retranslateUi(self):
        
        item = self.tableWidgetTracks.horizontalHeaderItem(0)
        item.setText(_translate("playlist", "Title"))
        item = self.tableWidgetTracks.horizontalHeaderItem(1)
        item.setText(_translate("playlist", "Artist"))
        item = self.tableWidgetTracks.horizontalHeaderItem(2)
        item.setText(_translate("playlist", "Album"))
        item = self.tableWidgetTracks.horizontalHeaderItem(3)
        item.setText(_translate("playlist", "Duration"))
        item = self.tableWidgetTracks.horizontalHeaderItem(4)
        item.setText(_translate("playlist", "ID"))


        self.playerControls.pauseButton.setToolTip(_translate("playlist", "Pause"))   
        self.playerControls.previousButton.setToolTip(_translate("playlist", "Previous"))
        self.playerControls.nextButton.setToolTip(_translate("playlist", "Next"))
        self.playerControls.fullscreenButton.setToolTip(_translate("playlist", "Full screen"))
        self.playerControls.deleteButton.setToolTip(_translate("playlist", "Delete all tracks"))

        self.setWindowTitle(_translate("playlist", "Playlist"))

    def showTracks(self,tracks):      
        self.tableWidgetTracks.setStyleSheet("selection-background-color: black;selection-color: white;") 
        self.tableWidgetTracks.setColumnCount(5)
        self.tableWidgetTracks.setRowCount(0)
        i=0
        for track in tracks:
            self.tableWidgetTracks.insertRow(i)
            titleItem = QTableWidgetItem(track.getTrackTitle())
            titleItem.setFlags(titleItem.flags() ^ Qt.ItemIsEditable)
            self.tableWidgetTracks.setItem(i,0,titleItem)
            
            if track.radioName == "":
                artistItem = QTableWidgetItem(track.getArtistName())
                artistItem.setFlags(artistItem.flags() ^ Qt.ItemIsEditable)
                self.tableWidgetTracks.setItem(i,1,artistItem)

                albumItem = QTableWidgetItem(track.getAlbumTitle())
                albumItem.setFlags(albumItem.flags() ^ Qt.ItemIsEditable)
                self.tableWidgetTracks.setItem(i,2,albumItem)

                durationItem = QTableWidgetItem(track.getDurationText())
                durationItem.setFlags(durationItem.flags() ^ Qt.ItemIsEditable)
                self.tableWidgetTracks.setItem(i,3,durationItem)
            else:
                print("radioName="+track.radioName)
                artistItem = QTableWidgetItem(self.player.currentRadioName)
                artistItem.setFlags(artistItem.flags() ^ Qt.ItemIsEditable)
                self.tableWidgetTracks.setItem(i,1,artistItem)

                albumItem = QTableWidgetItem(self.player.currentRadioName)
                albumItem.setFlags(albumItem.flags() ^ Qt.ItemIsEditable)
                self.tableWidgetTracks.setItem(i,2,albumItem)

                durationItem = QTableWidgetItem(track.getDurationText())
                durationItem.setFlags(durationItem.flags() ^ Qt.ItemIsEditable)
                self.tableWidgetTracks.setItem(i,3,durationItem)


            orderItem = QTableWidgetItem(str(i))
            orderItem.setFlags(orderItem.flags() ^ Qt.ItemIsEditable)
            self.tableWidgetTracks.setItem(i,4,orderItem)

            i+=1

    def showMediaList(self):
        tracks = []

        self.mediaList = self.player.mediaList
        for i in range(self.mediaList.count()):
            m = self.mediaList.item_at_index(i)
            if m is None:
                print("BREAK ShowMediaList media=",i)
                break
            
            mrl = m.get_mrl()
            #print("ShowMediaList mrl="+mrl)
            t = self.player.getTrackFromMrl(mrl)
            if t is None:
                t = track()
                t.setMRL(mrl)
                t.title = self.player.getTitle()

            # t.albumObj = player.getAlbumFromMrl(mrl)
            # t.setMRL(mrl)
            # t.getMutagenTags()
            tracks.append(t)

        self.showTracks(tracks)
        
        self.setCurrentTrack()




    def setCurrentTrack(self,title=""):
        if self.isVisible() == False: return

        if title == "": 
            trk = self.player.getCurrentTrackPlaylist()
            if trk: title = trk.getTrackTitle()
            
        if title != "" :
            self.setWindowTitle(title)
        else:
            self.setWindowTitle(_translate("playlist", "Playlist"))

        index = self.player.getCurrentIndexPlaylist()
        #print("setCurrentTrack:",index)

        trk = self.player.getCurrentTrackPlaylist()

        #print("Playlist count="+str(self.mediaList.count()))

        for i in range(0,self.mediaList.count()):

            item = self.tableWidgetTracks.item(i,0)
            if item is None:
                print("BREAK setCurrentTrack item=",i)
                break

            if trk is None:
                print("trk is None")

            if trk is not None and trk.radioName != "" and i==index:
                if title != "":
                    if title == "NO_META": title = trk.radioName
                    item.setText(title)
                else:
                    nowPlaying = self.player.getNowPlaying()
                    if nowPlaying == "NO_META": nowPlaying = trk.radioName
                    item.setText(nowPlaying)

                item1 = self.tableWidgetTracks.item(i,1)
                item1.setText(self.player.currentRadioName)
                item2 = self.tableWidgetTracks.item(i,2)
                item2.setText(self.player.currentRadioName)


            f = item.font()
            if i == index:
                if trk is not None: self.showCover(trk)
                f.setBold(True)
                f.setItalic(True)
                color = orange
            else:
                f.setBold(False)
                f.setItalic(False)
                color = white

            item.setFont(f)

            for j in range(0,2):
                self.tableWidgetTracks.item(i,j).setFont(f)

            for j in range(0,3):
                self.tableWidgetTracks.item(i,j).setForeground(color)

            if i == index: self.tableWidgetTracks.setCurrentItem(item)


        self.tableWidgetTracks.scrollTo(self.tableWidgetTracks.currentIndex())

            
        self.update()

        self.initColumnHeaders()



    def showCover(self,trk):

        if self.player.radioMode:
            coverUrl = self.player.getLiveCoverUrl()
            if coverUrl == "":
                rad = self.player.getCurrentRadio()
                if rad is not None:
                    coverUrl = rad.getRadioPic()

            if self.currentCoverPath == coverUrl:
                return

            if coverUrl != "":
                self.currentCoverPath = coverUrl
                self.picFromUrlThread.url = coverUrl
                self.picFromUrlThread.start()

        else:
            #self.picFromUrlThread.resetLastURL()
            if trk is not None and trk.parentAlbum is not None:
                print("fullscreenWidget trk.parentAlbum.cover="+trk.parentAlbum.cover)
                if trk.parentAlbum.cover == "" or trk.parentAlbum.cover is None:
                    self.coverPixmap = self.defaultPixmap
                else:
                    coverPath = trk.parentAlbum.getCoverPath()
                    
                    self.showCoverPixmap(coverPath)
                    



    def showCoverPixmap(self,path):

        self.coverPixmap = self.picBufferManager.getPic(path,"fullscreenWidget")
        scaledCover = self.coverPixmap.scaled(self.cover.size(),
                                Qt.KeepAspectRatio,
                                Qt.SmoothTransformation)
        self.cover.setPixmap(scaledCover)
        self.cover.show()




    def changeTrack(self,item):
        i = self.tableWidgetTracks.currentRow()

        self.trackChanged.emit(i)


    def onTimeSliderIsReleased(self,event=None):
        print('onTimeSliderIsReleased')
        
        self.player.setPosition(self.nextPosition)
        self.isTimeSliderDown = False
        #self.player.setPosition(self.nextPosition)


    def setPlayerPosition(self,pos):
        print(str(pos))
        self.nextPosition = pos/1000
        #self.player.setPosition(self.nextPosition)
        
    

    def onPlayerPositionChanged(self,event=None):
        if not self.isTimeSliderDown:

            pos = self.player.getPosition()
            #print('onPlayerPositionChanged='+str(pos))
            self.timeSlider.setValue(pos*1000)
       






if __name__ == "__main__":
    import sys
    from playerVLC import *

    player = playerVLC()


    app = QApplication(sys.argv)

    playlist = playlistWidget(player)

    playlist.tableWidgetTracks.setColumnCount(4)
    playlist.tableWidgetTracks.setRowCount(5)

    for i in range(5):
        playlist.tableWidgetTracks.setItem(i, 0, QTableWidgetItem("test"+str(i)))
        playlist.tableWidgetTracks.setItem(i, 1, QTableWidgetItem("toto"+str(i)))

    playlist.show()

    url = "/tmp/tmp8mfrufdl"
    playlist.onPicDownloaded(url)


    sys.exit(app.exec_())
