#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from track import *

from vlc import EventType as vlcEventType

orange = QtGui.QColor(216, 119, 0)
white = QtGui.QColor(255, 255, 255)



class playerControlsWidget(QtWidgets.QWidget):
    
    player = None

    def __init__(self,parent=None):
        QtWidgets.QWidget.__init__(self,parent=parent)

        lay = QtWidgets.QHBoxLayout(self)
        
        _translate = QtCore.QCoreApplication.translate

        self.pauseButton = QtWidgets.QPushButton(_translate("playlist", "Pause"))
        lay.addWidget(self.pauseButton)

        self.previousButton = QtWidgets.QPushButton(_translate("playlist", "Previous"))
        lay.addWidget(self.previousButton)

        self.nextButton = QtWidgets.QPushButton(_translate("playlist", "Next"))
        lay.addWidget(self.nextButton)

        self.volumeSlider = QtWidgets.QSlider()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.volumeSlider.sizePolicy().hasHeightForWidth())
        self.volumeSlider.setSizePolicy(sizePolicy)
        self.volumeSlider.setMinimumSize(QtCore.QSize(80, 0))
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.volumeSlider.setObjectName("volumeSlider")
        lay.addWidget(self.volumeSlider)


class playlistWidget(QtWidgets.QDialog):
    
    mediaList = None
    player = None
    nextPosition = 0
    isTimeSliderDown = False
    trackChanged = pyqtSignal(int, name='trackChanged')

    def __init__(self,player):
        QtWidgets.QDialog.__init__(self)
        self.player = player
        self.mediaList = self.player.mediaList

        

        self.initUI()

    def initUI(self):

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        self.setSizePolicy(sizePolicy)
        self.resize(550,400)
        self.initTableWidgetTracks()

        self.playerControls = playerControlsWidget()
        self.playerControls.pauseButton.clicked.connect(self.onPause)
        self.playerControls.previousButton.clicked.connect(self.player.previous)
        self.playerControls.nextButton.clicked.connect(self.player.next)
        self.playerControls.volumeSlider.setValue(self.player.getVolume())
        self.playerControls.volumeSlider.valueChanged.connect(self.setVolume)

        
        self.timeSlider = QtWidgets.QSlider(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timeSlider.sizePolicy().hasHeightForWidth())
        self.timeSlider.setSizePolicy(sizePolicy)
        self.timeSlider.setMinimumSize(QtCore.QSize(60, 0))
        self.timeSlider.setMinimum(0)
        self.timeSlider.setMaximum(1000)
        self.timeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.timeSlider.setObjectName("timeSlider")

        #self.timeSlider.mousePressEvent=self.setIsTimeSliderDown
        #self.timeSlider.mouseReleaseEvent=self.onTimeSliderIsReleased

        self.timeSlider.sliderPressed.connect(self.setIsTimeSliderDown)
        self.timeSlider.sliderReleased.connect(self.onTimeSliderIsReleased)
        self.timeSlider.sliderMoved.connect(self.setPlayerPosition)
        self.player.mpEnventManager.event_attach(vlcEventType.MediaPlayerPositionChanged, self.onPlayerPositionChanged)

        layout.addWidget(self.tableWidgetTracks)
        layout.addWidget(self.timeSlider)
        layout.addWidget(self.playerControls)
        

        self.tableWidgetTracks.cellDoubleClicked.connect(self.changeTrack)
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("playlist", "Playlist"))

        #self.resizeEvent = self.onResize

    def onPause(self,event):
        self.player.pause()

    
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
        hHeader.resizeSections(QtWidgets.QHeaderView.Stretch)
        

    def initTableWidgetTracks(self):

        self.tableWidgetTracks = QtWidgets.QTableWidget(self)

        self.tableWidgetTracks.setGeometry(0, 0, 550, 300)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        #sizePolicy.setHeightForWidth(self.tableWidgetTracks.sizePolicy().hasHeightForWidth())
        self.tableWidgetTracks.setSizePolicy(sizePolicy)
        self.tableWidgetTracks.setMinimumSize(QtCore.QSize(50, 0))
        self.tableWidgetTracks.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tableWidgetTracks.setObjectName("tableWidgetTracks")
        self.tableWidgetTracks.setColumnCount(5)
        self.tableWidgetTracks.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetTracks.setHorizontalHeaderItem(4, item)

        _translate = QtCore.QCoreApplication.translate
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

        #self.tableWidgetTracks.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        #self.tableWidgetTracks.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        #self.tableWidgetTracks.setRowCount(0)

        self.initColumnHeaders()


    def initColumnHeaders(self):

        hHeader = self.tableWidgetTracks.horizontalHeader()
        vHeader = self.tableWidgetTracks.verticalHeader()
        vHeader.hide()

        hHeader.resizeSections(QtWidgets.QHeaderView.ResizeToContents)
        hHeader.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        #hHeader.hideSection(3)
        hHeader.hideSection(4)




    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
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

    def showAlbumTracks(self,tracks):      
        self.tableWidgetTracks.setStyleSheet("selection-background-color: black;selection-color: white;") 
        self.tableWidgetTracks.setColumnCount(5)
        self.tableWidgetTracks.setRowCount(0)
        i=0
        for track in tracks:
            self.tableWidgetTracks.insertRow(i)
            titleItem = QtWidgets.QTableWidgetItem(track.getTrackTitle())
            titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidgetTracks.setItem(i,0,titleItem)
            
            if track.radioName == "":
                artistItem = QtWidgets.QTableWidgetItem(track.getArtistName())
                artistItem.setFlags(artistItem.flags() ^ QtCore.Qt.ItemIsEditable)
                self.tableWidgetTracks.setItem(i,1,artistItem)

                albumItem = QtWidgets.QTableWidgetItem(track.getAlbumTitle())
                albumItem.setFlags(albumItem.flags() ^ QtCore.Qt.ItemIsEditable)
                self.tableWidgetTracks.setItem(i,2,albumItem)

                durationItem = QtWidgets.QTableWidgetItem(track.getDurationText())
                durationItem.setFlags(durationItem.flags() ^ QtCore.Qt.ItemIsEditable)
                self.tableWidgetTracks.setItem(i,3,durationItem)
            else:
                print("radioName="+track.radioName)
                artistItem = QtWidgets.QTableWidgetItem(track.getTrackTitle())
                artistItem.setFlags(artistItem.flags() ^ QtCore.Qt.ItemIsEditable)
                self.tableWidgetTracks.setItem(i,1,artistItem)

                albumItem = QtWidgets.QTableWidgetItem(track.getTrackTitle())
                albumItem.setFlags(albumItem.flags() ^ QtCore.Qt.ItemIsEditable)
                self.tableWidgetTracks.setItem(i,2,albumItem)

                durationItem = QtWidgets.QTableWidgetItem(track.getDurationText())
                durationItem.setFlags(durationItem.flags() ^ QtCore.Qt.ItemIsEditable)
                self.tableWidgetTracks.setItem(i,3,durationItem)

            i+=1

    def showMediaList(self):
        tracks = []

        self.mediaList = self.player.mediaList
        for i in range(self.mediaList.count()):
            m = self.mediaList.item_at_index(i)
            if m is None:
                print("BREAK ShowMediaList media="+str(i))
                break
            
            mrl = m.get_mrl()
            print("ShowMediaList mrl="+mrl)
            t = self.player.getTrackFromMrl(mrl)
            if t is None:
                t = track()
                t.setMRL(mrl)
                t.title = self.player.getTitle()

            # t.albumObj = player.getAlbumFromMrl(mrl)
            # t.setMRL(mrl)
            # t.getMutagenTags()
            tracks.append(t)

        self.showAlbumTracks(tracks)
        
        self.setCurrentTrack()

        self.initColumnHeaders()


    def setCurrentTrack(self,title=""):

        if self.player is None : return 

        index = self.player.getCurrentIndexPlaylist()
        print("setCurrentTrack:"+str(index))

        trk = self.player.getCurrentTrackPlaylist()


        for i in range(self.mediaList.count()):

            item = self.tableWidgetTracks.item(i,0)
            if item is None:
                print("BREAK setCurrentTrack item="+str(i))
                break

            if trk is not None and trk.radioName != "" and i==index:
                if title != "":
                    item.setText(title)
                else:
                    nowPlaying = self.player.getNowPlaying()
                    item.setText(nowPlaying)


            f = item.font()
            if i == index:
                f.setBold(True)
                f.setItalic(True)
                color = orange
            else:
                f.setBold(False)
                f.setItalic(False)
                color = white

            item.setFont(f)
            self.tableWidgetTracks.item(i,1).setFont(f)
            self.tableWidgetTracks.item(i,2).setFont(f)
            self.tableWidgetTracks.item(i,3).setFont(f)

            self.tableWidgetTracks.item(i,0).setForeground(color)
            self.tableWidgetTracks.item(i,1).setForeground(color)
            self.tableWidgetTracks.item(i,2).setForeground(color)
            self.tableWidgetTracks.item(i,3).setForeground(color)

            if i == index: self.tableWidgetTracks.setCurrentItem(item)

        self.tableWidgetTracks.scrollTo(self.tableWidgetTracks.currentIndex(), QtWidgets.QAbstractItemView.PositionAtCenter)

            
        self.update()




    def changeTrack(self,item):
        i = self.tableWidgetTracks.currentRow()

        self.trackChanged.emit(i)


    def onTimeSliderIsReleased(self,event=None):
        print('onTimeSliderIsReleased')
        self.isTimeSliderDown = False
        #self.player.setPosition(self.nextPosition)


    def setPlayerPosition(self,pos):
        print(str(pos))
        self.nextPosition = pos/1000
        self.player.setPosition(self.nextPosition)
        
    

    def onPlayerPositionChanged(self,event=None):
        if not self.isTimeSliderDown:

            pos = self.player.getPosition()
            #print('onPlayerPositionChanged='+str(pos))
            self.timeSlider.setValue(pos*1000)
       