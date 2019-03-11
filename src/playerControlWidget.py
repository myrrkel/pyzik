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
from waitOverlayWidget import *

import threading
from vlc import EventType as vlcEventType
from svgIcon import *

white = QtGui.QColor(255, 255, 255)

_translate = QCoreApplication.translate

class playerControlsWidget(QWidget):
    
    player = None
    defaultPixmap = None


    def __init__(self,parent=None):
        QWidget.__init__(self,parent=parent)
        self.parent = parent

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self.frameBt = QFrame(self)
        layBt = QHBoxLayout(self.frameBt)
        layBt.setContentsMargins(0, 0, 0, 0)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        self.frameBt.setSizePolicy(sizePolicy)


        self.currentTrack = None
        
        self.pauseButton = QPushButton()
        self.pauseButton.setToolTip(_translate("playlist", "Pause"))
        self.pauseButton.setIcon(getSvgIcon("pause.svg"))

        layBt.addWidget(self.pauseButton)

        self.previousButton = QPushButton()
        self.previousButton.setToolTip(_translate("playlist", "Previous"))
        self.previousButton.setIcon(getSvgIcon("step-backward.svg"))
        layBt.addWidget(self.previousButton)

        self.nextButton = QPushButton()
        self.nextButton.setToolTip(_translate("playlist", "Next"))
        self.nextButton.setIcon(getSvgIcon("step-forward.svg"))
        layBt.addWidget(self.nextButton)

        self.fullscreenButton = QPushButton()
        self.fullscreenButton.setToolTip(_translate("playlist", "Full screen"))
        self.fullscreenButton.setIcon(getSvgIcon("fullscreen.svg"))
        layBt.addWidget(self.fullscreenButton)

        self.playlistButton = QPushButton()
        self.playlistButton.setToolTip(_translate("playlist", "Playlist"))
        self.playlistButton.setIcon(getSvgIcon("playlist.svg"))
        layBt.addWidget(self.playlistButton)


        self.frameBt.setMaximumSize(QSize(300, 40))
        lay.addWidget(self.frameBt)

        self.volumeSlider = QSlider()
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        #sizePolicy.setHeightForWidth(self.volumeSlider.sizePolicy().hasHeightForWidth())
        self.volumeSlider.setSizePolicy(sizePolicy)
        self.volumeSlider.setMinimumSize(QSize(80, 0))
        self.volumeSlider.setMaximumSize(QSize(200, 40))
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setOrientation(Qt.Horizontal)
        self.volumeSlider.setObjectName("volumeSlider")
        lay.addWidget(self.volumeSlider)

        self.frameEmpty = QFrame(self)
        lay.addWidget(self.frameEmpty)


class playerControlWidget(QWidget):
    
    mediaList = None
    player = None
    picFromUrlThread = None
    nextPosition = 0
    isTimeSliderDown = False
    trackChanged = pyqtSignal(int, name='trackChanged')
    coverChanged = pyqtSignal(int, name='coverChanged')

    def __init__(self,player,parent):
        QDialog.__init__(self)
        self.parent = parent
        self.picBufferManager = parent.picBufferManager

        self.currentCoverPath = ""
        
        self.setWindowFlags(Qt.Window)
        self.player = player
        self.mediaList = self.player.mediaList

        self.isWaitingCover = False

        self.defaultRadioPix = getSvgWithColorParam("radio.svg","","#000000")        

        self.initUI()

        self.parent.isPlayingSignal.connect(self.isPlaying)
        self.parent.currentTrackChanged.connect(self.onCurrentTrackChanged)
        self.parent.currentRadioChanged.connect(self.onCurrentRadioChanged)

    def isPlaying(self,event):
        print("PlayerControlWidget isPlaying")
        self.refreshWaitOverlay()
        


    def onCurrentTrackChanged(self,event):
        print("PlayerControlWidget Currenttrack changed!")
        self.setCurrentTrack(event)

    def refreshWaitOverlay(self):
        if self.player.radioMode:
            if (self.isWaitingCover == False and self.player.isPlayingRadio() == True) :
                print("PlayerControlWidget refresh show wait")
                self.hideWaitOverlay()
            else:
                self.showWaitingOverlay()

        else:
            print("PlayerControlWidget refresh show wait")
            self.hideWaitOverlay()



    def onCurrentRadioChanged(self,event):
        print("PlayerControlWidget CurrentRadio changed!")

        self.setRadioLabeLText()

        self.labelTitle.setText(sTitle)

        self.currentCoverPath = ""
        self.refreshWaitOverlay()


    def coverMouseDoubleClickEvent(self,event):
        self.showFullScreen()

    def resizeEvent(self, event):
    
        if self.waitOverlay is not None:
            self.waitOverlay.resize(self.cover.size())
        
        event.accept()

    def initUI(self):
        
        self.hMainLayout = QHBoxLayout()
        self.hMainLayout.setContentsMargins(0, 4, 0, 0)
        self.hMainLayout.setSpacing(0)


        self.vLayout = QVBoxLayout()
        self.vLayout.setContentsMargins(4, 0, 0, 0)
        self.vLayout.setSpacing(4)
        
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)
        #self.resize(550,400)


        self.playerControls = playerControlsWidget()
        self.playerControls.pauseButton.clicked.connect(self.onPause)
        self.playerControls.previousButton.clicked.connect(self.player.previous)
        self.playerControls.nextButton.clicked.connect(self.player.next)
        self.playerControls.playlistButton.clicked.connect(self.parent.showPlaylist)
        #self.playerControls.deleteButton.clicked.connect(self.onClearPlaylist)
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

        self.timeSlider.sliderPressed.connect(self.setIsTimeSliderDown)
        self.timeSlider.sliderReleased.connect(self.onTimeSliderIsReleased)
        self.timeSlider.sliderMoved.connect(self.setPlayerPosition)


        self.hMainFrame = QWidget()
        self.hMainFrame.setLayout(self.hMainLayout)


        self.mainFrame = QWidget()
        self.hLayout = QHBoxLayout()
        self.hLayout.setContentsMargins(0, 0, 0, 0)
        self.hLayout.setSpacing(6)

        self.coverPixmap = QtGui.QPixmap()

        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        
        self.cover = QLabel()
        self.cover.setSizePolicy(sizePolicy)
        self.cover.setMinimumSize(QSize(100, 100))
        self.cover.setMaximumSize(QSize(100, 100))
        self.cover.setAlignment(Qt.AlignCenter)
        self.cover.setPixmap(self.coverPixmap)
        self.cover.show()
        self.cover.mouseDoubleClickEvent = self.coverMouseDoubleClickEvent
        self.waitOverlay = waitOverlay(self.cover,12,25,orange,0)
        #self.hideWaitOverlay()

        self.labelTitle = QLabel()
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        self.labelTitle.setSizePolicy(sizePolicy)
        self.labelTitle.setTextFormat(Qt.RichText)
        self.labelTitle.setScaledContents(True)
        self.labelTitle.setWordWrap(True)

        self.hMainLayout.addWidget(self.cover)

        self.setLayout(self.hMainLayout)

        #self.vLayout.addWidget(self.mainFrame)
        
        self.vLayout.addWidget(self.labelTitle)
        self.vLayout.addWidget(self.playerControls)
        self.vLayout.addWidget(self.timeSlider)
        self.mainFrame.setLayout(self.vLayout)
        self.hMainLayout.addWidget(self.mainFrame)
        
        if self.picFromUrlThread is None:
            self.picFromUrlThread = picFromUrlThread()


        self.retranslateUi()


    def connectPicDownloader(self,picDl):
        self.picFromUrlThread = picDl
        self.picFromUrlThread.downloadCompleted.connect(self.onPicDownloaded)

    def onPause(self,event):
        self.player.pause()

    def showDefaultPixmap(self):
        if self.player.radioMode:
            self.coverPixmap = self.defaultRadioPix
        else:
            self.coverPixmap = self.defaultPixmap
        
        self.showSizedCover()


    def onPicDownloaded(self,path):
        #self.isWaitingCover = False
        if path == "":
            self.showDefaultPixmap()
            self.isWaitingCover = False
            #self.hideWaitOverlay()
        else:
            self.coverPixmap = self.picBufferManager.getPic(path,"playerControl")
            self.isWaitingCover = False
            self.showScaledCover()

        self.refreshWaitOverlay()


    def hideWaitOverlay(self):
        self.waitOverlay.hide()
        self.showScaledCover()


    def showWaitingOverlay(self):
        #print("showWaitingOverlay")

        pix = QPixmap(100,100)
        pix.fill(QtGui.QColor("transparent"))
        self.cover.setPixmap(pix)

        self.waitOverlay.showOverlay()
        self.waitOverlay.resize(self.cover.size())
        #self.show()


    def showScaledCover(self):
        if not self.coverPixmap.isNull():
            scaledCover = self.coverPixmap.scaled(self.cover.size(),
                                                    Qt.KeepAspectRatio,
                                                    Qt.SmoothTransformation)
            self.cover.setPixmap(scaledCover)
            
        else:
            self.cover.clear()


    def showSizedCover(self,width=50,height=50):
        if not self.coverPixmap.isNull():
            scaledCover = self.coverPixmap.scaled(width,height,
                                                    Qt.KeepAspectRatio,
                                                    Qt.SmoothTransformation)
            self.cover.setPixmap(scaledCover)
            
        else:
            self.cover.clear()

    
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


    def showFullScreen(self):
        if self.parent.fullScreenWidget:
            self.parent.fullScreenWidget.show()
            self.parent.fullScreenWidget.activateWindow()




    def onClearPlaylist(self,event):
        #Remove all medias from the playlist except the current track
        self.player.removeAllTracks()
        self.showMediaList()


    def retranslateUi(self):
        

        self.playerControls.pauseButton.setToolTip(_translate("playlist", "Pause"))   
        self.playerControls.previousButton.setToolTip(_translate("playlist", "Previous"))
        self.playerControls.nextButton.setToolTip(_translate("playlist", "Next"))
        self.playerControls.playlistButton.setToolTip(_translate("playlist", "Playlist"))
        self.playerControls.fullscreenButton.setToolTip(_translate("playlist", "Full screen"))




    def setCurrentTrackInThread(self,title):
        processThread = threading.Thread(target=self.setCurrentTrack, args=[title])
        processThread.start()



    def setCurrentTrack(self,title=""):

        if self.player is None : return 

        index = self.player.getCurrentIndexPlaylist()
        print("PlayerControl setCurrentTrack:",index)

        trk = self.player.getCurrentTrackPlaylist()
        self.currentTrack = trk

        self.setTitleLabel()

        self.showCover(trk)


    def showCover(self,trk):

        if self.player.radioMode:

            coverUrl = self.player.getLiveCoverUrl()
            if coverUrl == "":
                rad = self.player.getCurrentRadio()
                if rad is not None:
                    coverUrl = rad.getRadioPic()

            if coverUrl is None: coverUrl = ""

            if self.currentCoverPath == coverUrl:
                self.isWaitingCover = False
                self.refreshWaitOverlay()
                return

            if coverUrl != "":
                self.currentCoverPath = coverUrl
                self.picFromUrlThread.url = coverUrl
                self.isWaitingCover = True
                self.picFromUrlThread.start()

   

        else:
            self.isWaitingCover = False
            if trk is not None and trk.parentAlbum is not None:
                if trk.parentAlbum.cover == "" or trk.parentAlbum.cover is None:
                    self.coverPixmap = self.defaultPixmap
                else:
                    coverPath = trk.parentAlbum.getCoverPath()
                    self.coverPixmap = self.picBufferManager.getPic(coverPath,"playerControl")
                    
                self.showScaledCover()

            self.refreshWaitOverlay()



    def setTitleLabel(self,title=""):

        if title != "":
            self.setRadioLabeLText(title)
            return

        if self.currentTrack:
            if self.currentTrack.isRadio():
               self.setRadioLabeLText()
               self.timeSlider.setVisible(False)
            else:
                self.setTrackLabelText()
                self.timeSlider.setVisible(True)
        
            


    def setTrackLabelText(self):
        artName = self.currentTrack.getArtistName()
        albTitle = self.currentTrack.getAlbumTitle()
        trkTitle = self.currentTrack.getTrackTitle()
        year = self.currentTrack.getAlbumYear()

        if albTitle != "":
            sAlbum = " - "+albTitle
        sYear =str(year)
        if(not sYear in ["0",""]): sAlbum += " ("+sYear+")"
        sTitle = '''<html><head/><body>
        <p><span style=\" font-size:15pt; text-shadow:white 0px 0px 4px; font-weight:600;\">{artName}</span>
        <span style=\" font-size:12pt; font-style:italic;\">{trkTitle}</span></p>
        <span style=\" font-size:12pt; font-style:bold;\">{Album}</span></p>
        </body></html>'''
        sTitle = sTitle.format(artName=artName,trkTitle=trkTitle,Album=sAlbum)
        
        self.labelTitle.setText(sTitle)


    def setRadioLabeLText(self,title=""):

        if title == "":
            radioName = self.currentTrack.radio.name
            trkTitle = self.currentTrack.radio.liveTrackTitle
            if trkTitle == "":
                trkTitle = self.player.getNowPlaying()
            if trkTitle == "NO_META": trkTitle = ""
        else:
            radioName = title
            trkTitle = ""

        sTitle = '''<html><head/><body>
        <p><span style=\" font-size:15pt; text-shadow:white 0px 0px 4px; font-weight:600;\">{radioName}</span>
        <span style=\" font-size:12pt; font-style:italic;\">{trkTitle}</span></p>
        </body></html>'''
        sTitle = sTitle.format(radioName=radioName,trkTitle=trkTitle)

        self.labelTitle.setText(sTitle)



    def onTimeSliderIsReleased(self,event=None):
        print('onTimeSliderIsReleased')
        
        self.player.setPosition(self.nextPosition)
        self.isTimeSliderDown = False
        #self.player.setPosition(self.nextPosition)


    def setPlayerPosition(self,pos):
        print(str(pos))
        self.nextPosition = pos/1000
        #self.player.setPosition(self.nextPosition)

    def getVolume(self):
        return self.playerControls.volumeSlider.value()

    def setVolume(self,vol):
        self.playerControls.volumeSlider.setValue(vol)
        
    

    def onPlayerPositionChanged(self,event=None):
        if not self.isTimeSliderDown:

            pos = self.player.getPosition()
            #print('onPlayerPositionChanged='+str(pos))
            self.timeSlider.setValue(pos*1000)
       




