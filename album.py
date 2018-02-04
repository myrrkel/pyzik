#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def representInt(s):
	#True if string s could be converted as an int
	try: 
		int(s)
		return True
	except ValueError:
		return False

def year(s):
	"""
	Convert a string made of numbers into a year
	Return 0 if string s is not a year, else return the year on 4 digits. ex: "73"-->1973
	"""
	res = 0
	if representInt(s):
		if len(s) == 4: 
			res = int(s)
		else:
			if len(s) == 2: res = int("19"+s)
			#If year is 69 it means 1969.
			#Sounds ridiculous to have 16 instead of 2016.
	return res


def fstrip(s):
	return s.strip()


def replaceSpecialChars(text):
	#Replace strings in given text according to the dictionary 'rep'
	
	rep = {"_": " ", "#": "@",\
	 "-(": "@", ")-": "@", "- (": "@", ") -": "@",\
	 "-[": "@", "]-": "@", "- [": "@", "] -": "@",\
	 "(": "@", ")": "@", "[": "@", "]": "@",\
	 " - ": "@", "@ @": "@", "@@": "@"} 

	rep = dict((re.escape(k), v) for k, v in rep.items())
	pattern = re.compile("|".join(rep.keys()))
	return pattern.sub(lambda match: rep[re.escape(match.group(0))], text)

class album:
	"""
	Album's class, each album is in a directory name.
	"""

	def __init__(self,dirname):
		self.albumID = 0
		self.title = ""
		self.dirName = dirname
		self.dirPath = ""
		self.artistID = ""
		self.artistName = ""
		self.year = 0
		self.cover = ""
		self.toVerify = False

		if dirname!="":
			self.extractDataFromDirName()

	def load(self,row):
		self.albumID = row[0]
		self.title = row[1]
		self.artistID = row[2]

	def formatTitle(self,title):
		return title.title()

	def printInfos(self):
		print("Title: "+self.title+"  # Artist: "+self.artistName\
			+"  # ArtistID: "+str(self.artistID)+"  # Year: "+str(self.year))


	def extractDataFromDirName(self):
		pos1 = self.dirName.find(" - [")
		pos2 = self.dirName.find("] - ")
		pos_separator = self.dirName.find("@")
		print(self.dirName+" pos1:"+str(pos1))

		if 0<pos1 and pos1<pos2 and pos_separator < 0:
			#The name of the directory is correct like 'DEEP PURPLE - [1972] - Machine Head'
			self.title = self.dirName[pos2+4:]
			self.artistName = self.dirName[:pos1]
			self.year = year(self.dirName[pos1+4:pos2])
		else:
			#Replace caracters that could be separtors in directory name by char @
			salb = replaceSpecialChars(self.dirName)
			salb.strip()
			if salb[len(salb)-1] == "@": salb = salb[:len(salb)-1]
			if salb[0] == "@": salb = salb[1:]

			#Split datas separeted by @
			datas = salb.split("@")
			datas = [fstrip(data) for data in datas]
			
			
			if len(datas)>=3:
				'''With 3 or more informations in the directory name,
				we suppose that the fisrt one is the artist name,
				If the second is a year, the third is the title'''
				
				print(datas[0]+";"+datas[1]+";"+datas[2]+";")
				if representInt(datas[1]):
					self.title = datas[2]
					self.year = year(datas[1])
					self.artistName = datas[0]
				elif representInt(datas[2]):
					self.title = datas[1]
					self.year = year(datas[2])
					self.artistName = datas[0]

			elif len(datas)==2:
				'''With 2 informations in the directory name,
				we suppose that the fisrt one is the artist name,
				the second is the title'''
				self.title = datas[1]
				self.year = 0
				self.artistName = datas[0]

			else:
				#No synthaxe does match with this dirname
				print("No matching: "+salb)
				self.toVerify = True


		
		self.title = self.formatTitle(self.title)
		
			
			