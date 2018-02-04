#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter

from musicBase import *
from albumCollection import * 
from artistCollection import * 
from mainWindowLoader import * 

def main():
	mb = musicBase()
	mb.artistCol.loadArtists()
	mb.albumCol.loadAlbums()
	mb.exploreAlbumsDirectory("./TEST")
	mb.albumCol.printAlbums()
	mb.artistCol.printArtists()

	
	'''albList.printAlbums()
	albList.connectDB()
	albList.createTableAlbums()'''




if __name__ == "__main__":


	main()

	'''
	import sys
	from PyQt5.QtWidgets import QApplication

	app = QApplication(sys.argv)
	print('test1')
	window = MainWindowLoader()
	window.show()
	sys.exit(app.exec_())
	'''
	