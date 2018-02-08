#!/usr/bin/env python3
# -*- coding: utf-8 -*-



##############################################
#           Play mp3 with VLC                #
##############################################

import sys
import vlc

class playerVLC:

	def __init__(self):

		# creating a basic vlc instance
		self.instance = vlc.Instance()
		# creating an empty vlc media player
		self.mediaPlayer = self.instance.media_player_new()

		
		self.mediaList = self.instance.media_list_new()
		
		self.mediaListPlayer = self.instance.media_list_player_new()
		self.mediaListPlayer.set_media_list(self.mediaList) 


		self.mediaPlayer.audio_set_volume(100)
	


	def playFile(self,sfile):
		#create the media
		print(sys.version)
		if(sys.version < '3'):
			sfile = unicode(sfile)

		media = self.instance.media_new(sfile)
		# put the media in the media player
		self.mediaPlayer.set_media(media)

		# parse the metadata of the file
		media.parse()
		self.mediaPlayer.play()	

	def addFile(self,sfile):
		self.mediaList.add_media(self.instance.media_new(sfile))

	def addFileList(self,fileList):
		for sfile in fileList:
			self.mediaList.add_media(self.instance.media_new(sfile))


	def playMediaList(self):
		self.mediaListPlayer.play()


	def initMediaList(self):
		self.mediaList.release()
		self.mediaListPlayer.release()
		self.mediaList = self.instance.media_list_new()
		self.mediaListPlayer = self.instance.media_list_player_new()
		self.mediaListPlayer.set_media_list(self.mediaList) 
