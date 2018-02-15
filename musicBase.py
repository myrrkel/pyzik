#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from albumCollection import *
from artistCollection import *
from musicDirectoryCollection import *
import os.path




class musicBase:
	"""
	musicBase manage albums and artists from
	 the music directories to the database'''
	"""

	def __init__(self):
		self.albumCol = albumCollection()
		self.artistCol = artistCollection()
		self.musicDirectoryCol = musicDirectoryCollection()

	def loadMusicBase(self):
		self.musicDirectoryCol.loadMusicDirectories()
		self.artistCol.loadArtists()
		self.albumCol.loadAlbums()
		self.addAlbumsToArtists()


	def exploreAlbumsDirectories(self):
		for mdir in self.musicDirectoryCol.musicDirectories:
			print("Dir="+mdir.dirPath)
			self.exploreAlbumsDirectory(mdir)
			self.artistCol.sortArtists()




	def exploreAlbumsDirectory(self,musicDir):
		
		dirlist = next(os.walk(musicDir.dirPath))[1]

		for sDirName in dirlist:
			curAlb = album(sDirName)
			curAlb.musicDirectoryID = musicDir.musicDirectoryID
			curAlb.dirPath = os.path.join(musicDir.dirPath,sDirName)

			
			if curAlb.toVerify == False:
				#Artist name et album title has been found
				curArt = self.artistCol.getArtist(curAlb.artistName)
				#GetArtist return a new artist if if doesn't exists in artistsCol
				if curArt != None:				
					curAlb.artistID = curArt.artistID
					curAlb.artistName = curArt.name

					albumList = self.albumCol.findAlbums(curAlb.title,curAlb.artistID)
					if len(albumList)==0:
						print("Add "+curAlb.title+" in "+curArt.name+" discography. ArtID="+str(curArt.artistID))
						self.albumCol.addAlbum(curAlb)
						curArt.albums.append(curAlb)
					else:
						print("Album "+curAlb.title+" already exists for "+curArt.name+" ArtistID="+str(curArt.artistID))
				else:
					print("No artist for "+sDirName)


	def addAlbumsToArtists(self):
		for alb in self.albumCol.albums:
			artists_found = self.artistCol.getArtistByID(alb.artistID)
			if (len(artists_found) == 1):
				artists_found[0].albums.append(alb)


	def emptyDatas(self):
		self.artistCol.artists = []
		self.albumCol.albums = []
		self.musicDirectoryCol.musicDirectories = []