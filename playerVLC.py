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


	def playMediaList(self):
		#create the media

		self.mediaListPlayer.play()

		'''
		listPlayer = self.instance.media_list_player_new()
		# put the media in the media player
		listPlayer.set_media(self.instance.media_new(sDir))
		self.mediaPlayer.insert_media(media)

		p=i.media_list_player_new() 
		p.set_media_list(listPlayer) 

		# parse the metadata of the file
		#media.parse()
		#self.mediaPlayer.play()
		'''