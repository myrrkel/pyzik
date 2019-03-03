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

#orange = QtGui.QColor(216, 119, 0)
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
        self.setWindowFlags(Qt.Window)
        self.player = player
        self.mediaList = self.player.mediaList
        self.fullScreenWidget = None
        self.isWaitingCover = False

        self.defaultRadioPix = QPixmap("img/radio2.svg")        

        self.initUI()

        self.parent.isPlayingSignal.connect(self.isPlaying)
        self.parent.currentTrackChanged.connect(self.onCurrentTrackChanged)
        self.parent.currentRadioChanged.connect(self.onCurrentRadioChanged)

    def isPlaying(self,event):
        #print("PlayerControlWidget isPlaying!")
        if self.player.radioMode and (self.isWaitingCover or self.player.isPlaying() == False):
            self.showWaitingOverlay()
        else:
            print("isPlaying state="+self.player.getState())
            self.hideWaitOverlay()

    def onCurrentTrackChanged(self,event):
        #print("PlayerControlWidget Currenttrack changed!")
        self.setCurrentTrack(event)


    def onCurrentRadioChanged(self,event):
        #print("PlayerControlWidget CurrentRadio changed!")
        if self.player.radioMode and (self.isWaitingCover or self.player.isPlaying() == False):
            self.showWaitingOverlay()



    def mouseDoubleClickEvent(self,event):
        self.showFullScreen()

    def resizeEvent(self, event):
    
        if self.waitOverlay is not None:
            self.waitOverlay.resize(self.cover.size())
        
        event.accept()

    def initUI(self):
        
        self.hMainLayout = QHBoxLayout()
        self.hMainLayout.setContentsMargins(0, 4, 0, 0)
        self.hMainLayout.setSpacing(0)
        #self.setLayout(self.hMainLayout)

        self.vLayout = QVBoxLayout()
        self.vLayout.setContentsMargins(4, 0, 0, 0)
        self.vLayout.setSpacing(4)
        #self.setLayout(self.vLayout)
        
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
        self.cover.setPixmap(self.coverPixmap)
        self.cover.show()

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
        self.showScaledCover()


    def onPicDownloaded(self,path):
        
        if path == "":
            self.showDefaultPixmap()
            self.hideWaitOverlay()
            return
       
        self.coverPixmap = QtGui.QPixmap(path)
        if self.player.isPlaying():
            self.showScaledCover()
            self.hideWaitOverlay()


    def hideWaitOverlay(self):
        self.waitOverlay.hide()

    def showScaledCover(self):
        if not self.coverPixmap.isNull():
            scaledCover = self.coverPixmap.scaled(self.cover.size(),
                                                    Qt.KeepAspectRatio,
                                                    Qt.SmoothTransformation)
            self.cover.setPixmap(scaledCover)
            
        else:
            self.cover.clear()
            #self.showDefaultPixmap()
    
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
        print("setCurrentTrack PlayerControl:",index)

        trk = self.player.getCurrentTrackPlaylist()
        self.currentTrack = trk

        self.setTitleLabel()

        if not self.player.radioMode:
            self.showCover(trk)


    def showWaitingOverlay(self):
        print("showWaitingOverlay")
        self.isWaitingCover = True

        pix = QPixmap(100,100)
        pix.fill(QtGui.QColor("transparent"))
        self.cover.setPixmap(pix)

        self.waitOverlay.showOverlay()
        self.waitOverlay.resize(self.cover.size())
        self.show()

    def showCoverInThread(self,trk):
        processThread = threading.Thread(target=self.showCover, args=[trk])
        processThread.start()


    def showCover(self,trk):

        

        if self.player.radioMode:
            coverUrl = self.player.getLiveCoverUrl()
            if coverUrl != "":
                self.picFromUrlThread.url = coverUrl
                self.picFromUrlThread.start()
                self.isWaitingCover = True
            else:
                rad = self.player.getCurrentRadio()
                if rad is not None:
                    radPicUrl = rad.getRadioPic()
                    if radPicUrl != "":
                        self.picFromUrlThread.url = radPicUrl
                        self.picFromUrlThread.start()
                        self.isWaitingCover = True
                    else:
                        self.isWaitingCover = False
                else:
                    self.isWaitingCover = False
        else:
            self.isWaitingCover = False
            self.picFromUrlThread.resetLastURL()
            if trk is not None and trk.parentAlbum is not None:
                print("showCover trk.parentAlbum.cover="+trk.parentAlbum.cover)
                if trk.parentAlbum.cover == "" or trk.parentAlbum.cover is None:
                    self.coverPixmap = self.defaultPixmap
                else:
                    coverPath = trk.parentAlbum.getCoverPath()
                    self.coverPixmap = QtGui.QPixmap(coverPath)
                    
                self.showScaledCover()


    def setTitleLabel(self):
        if self.currentTrack:
            if self.currentTrack.isRadio():
               sTitle = self.getRadioLabeLText()
               self.timeSlider.setVisible(False)
            else:
                sTitle = self.getTrackLabelText()
                self.timeSlider.setVisible(True)
        
            self.labelTitle.setText(sTitle)


    def getTrackLabelText(self):
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
        return sTitle


    def getRadioLabeLText(self):
        radioName = self.currentTrack.radio.name
        trkTitle = self.currentTrack.radio.liveTrackTitle
        if trkTitle == "":
            trkTitle = self.player.getNowPlaying()

        sTitle = '''<html><head/><body>
        <p><span style=\" font-size:15pt; text-shadow:white 0px 0px 4px; font-weight:600;\">{radioName}</span>
        <span style=\" font-size:12pt; font-style:italic;\">{trkTitle}</span></p>
        </body></html>'''
        sTitle = sTitle.format(radioName=radioName,trkTitle=trkTitle)
        return sTitle



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
       




