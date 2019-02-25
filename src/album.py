#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import fnmatch
from track import *
from globalConstants import *
import formatString as FS
from database import *
from PyQt5.QtGui import QPixmap


def year(s):
    """
    Convert a string made of numbers into a year
    Return 0 if string s is not a year, else return the year on 4 digits. ex: "73"-->1973
    """
    res = 0
    if str.isdigit(s):
        if len(s) == 4: 
            res = int(s)
        else:
            if len(s) == 2: res = int("19"+s)
            #If year is 69 it means 1969.
            #Sounds ridiculous to have 16 instead of 2016.
    return res

def isYear(s):
    return s.isdigit() and (len(s) in (4,2))

def countDigitInDatas(datas):
    return len( list(d for d in datas if d.isdigit()==True))

def getFileName(path):
    
    filename = os.path.basename(path)
    filename, file_extension = os.path.splitext(filename)
    #print("getFileName = "+filename)
    return filename


def capitaliseWord(word):
    res =""
    for i,l in enumerate(word):
        if i==0:
            res += l.upper()
        else:
            res += l
    return res


def titleExcept(title):
    exceptions = ['a', 'an', 'of', 'the', 'is', 'in', 'to']
    word_list = re.split(' ', title)

    final = [capitaliseWord(word_list[0])]
    for word in word_list[1:]:
        if str.lower(word) in exceptions:
            final.append(word.lower())
        else:
            final.append(capitaliseWord(word))
    return " ".join(final)



def replaceSpecialChars(text):
    #Replace strings in given text according to the dictionary 'rep'
    
    rep = {"_": " ", "  ": " ", "#": "@",\
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

    def __init__(self,dirname="",musicDirectory=None):
        self.albumID = 0
        self.title = ""
        self.dirName = dirname
        self.dirPath = dirname
        self.artistID = ""
        self.artistName = ""
        self.year = 0
        self.cover = ""
        self.toVerify = False
        self.tracks = []
        self.images = []
        self.styleIDSet = set()
        self.doStop = False
        self.musicDirectory = musicDirectory
        if musicDirectory:
            self.musicDirectoryID = musicDirectory.musicDirectoryID
        else:
            self.musicDirectoryID = 0
        self.searchKey = ""


        if dirname!="":
            self.extractDataFromDirName()

    def load(self,row):
        self.albumID = row[0]
        self.title = row[1]
        self.year = row[2]
        self.dirPath = row[3]
        self.artistID = row[4]
        self.musicDirectoryID = row[5]

    def formatTitle(self,title):
        return titleExcept(title)


    def getCoverSearchText(self):
        txt = self.artistName
        if int(self.year) > 0 : txt = txt + " " + str(self.year)
        txt = txt + " " + self.title
        return txt


    def getSearchKey(self):
        if self.searchKey =="":
            self.searchKey = FS.getSearchKey(self.title.upper())
        return self.searchKey

    def printInfos(self):
        print("Title: "+self.title+"  # Artist: "+self.artistName\
            +"  # ArtistID: "+str(self.artistID)\
            +"  # Year: "+str(self.year)\
            +"  # musicDirectoryID: "+str(self.musicDirectoryID)
            +"  # dirPath: "+str(self.dirPath))


    def extractDataFromDirName(self):
        pos1 = self.dirName.find(" - [")
        pos2 = self.dirName.find("] - ")
        
        if 0<pos1 and pos1<pos2:
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
            datas = [str.strip(data) for data in datas]
            
            
            #if len(datas)>3:
            #    print("extractDataFromDirName: more than 3 datas = "+str(datas))

            if len(datas)>=3:
                '''With 3 or more informations in the directory name,
                we suppose that the fisrt one is the artist name,
                If the second is a year, the third is the title'''
                self.title = ""
                self.artistName = datas[0]

                for i in range(1,len(datas)):
                
                    if(datas[i].isdigit()):
                        if isYear(datas[i]):
                            self.year = year(datas[i])
                    else:
                        if self.title != "": self.title += " - "
                        self.title += datas[i]


            elif len(datas)==2:
                '''With 2 informations in the directory name,
                we suppose that the fisrt one is the artist name,
                the second is the title'''
                self.title = datas[1]
                self.year = 0
                self.artistName = datas[0]

            else:
                #No synthaxe does match with this dirname
                print("No matching: "+salb+" for currentDir: "+self.dirPath)
                self.toVerify = True


        self.title.strip()
        self.artistName.strip()
        self.title = self.formatTitle(self.title)


    def getTracks(self,player,subdir=""):
        self.doStop = False
        if(not self.checkDir()): return False

        if(subdir==""): 
            self.tracks = []
            currentDir = self.getAlbumDir()
        else:
            currentDir = os.path.join(self.getAlbumDir(),subdir)


        files = os.listdir(currentDir)
        files.sort()
        
        nTrack = track("","")
    
        for file in files:
            if self.doStop: break
            if os.path.isdir(os.path.join(currentDir,str(file))):
                #file is a directory
                self.getTracks(player,os.path.join(subdir,str(file)))
            else:

                for ext in musicFilesExtension:
                    if fnmatch.fnmatch(file.lower(), '*.'+ext):
                        #if subdir != "":
                        #    sfile = os.path.join(currentDir,file)
                        #else:
                        #    sfile = str(file)
                        sfile = str(file)

                        if("." in sfile):
                            filename, file_extension = os.path.splitext(sfile)
                            itrack = track(filename,file_extension,subdir)
                            itrack.path = currentDir
                            #itrack.extractDataFromTags(player,currentDir)
                            itrack.getMutagenTags(self.getAlbumDir())
                            itrack.parentAlbum = self
                            self.tracks.append(itrack)
                            break


    def getImages(self,subdir=""):
        self.doStop = False
        if(not self.checkDir()): return False

        if(subdir==""): 
            self.images = []
            currentDir = self.getAlbumDir()
        else:
            currentDir = os.path.join(self.getAlbumDir(),subdir)

        files = os.listdir(currentDir)
        

        files.sort()
    
        for file in files:
            if self.doStop: break
            if os.path.isdir(os.path.join(currentDir,str(file))):
                #file is a directory
                self.getImages(os.path.join(subdir,file))
            else:
                if file == "cover":
                    os.rename(os.path.join(currentDir,file),os.path.join(currentDir,"cover.jpg"))


                for ext in imageFilesExtension:
                    if fnmatch.fnmatch(file.lower(), '*.'+ext):
                        sfile = os.path.join(currentDir,file)
                        self.images.append(sfile)
                        break


    def getCover(self):

        if(len(self.images)>0):
            keywords = ["cover","front","artwork","capa","caratula","recto","frente editada","frente","folder","f"]


            for keyword in keywords:
                coverFound = next((x for x in self.images if keyword == getFileName(x.lower())), "")
                if (coverFound!=""):
                    print("Image found equal="+keyword)
                    self.cover = coverFound
                    break

            if (coverFound==""):
                for keyword in keywords:
                    coverFound = next((x for x in self.images if (keyword in getFileName(x.lower()) and "back" not in getFileName(x.lower()))), "")
                    if (coverFound!=""):
                        self.cover = coverFound
                        break
            #print("getCover cover="+self.cover)

            if self.cover == "":
                print("getCover GetDefault="+self.images[0])
                self.cover = self.images[0]

    def getCoverPath(self):
        return os.path.join(self.getAlbumDir(),self.cover)


    def getCoverPixmap(self):
        print("ALBUM - getCoverPixmap")
        tempPath = ""
        path = self.getCoverPath()
        if path:
            self.coverPixmap = QPixmap(path)

        return self.coverPixmap

    def checkDir(self):
        if self.musicDirectory:
            albDir = self.getAlbumDir()
            if albDir:
                return os.path.exists(albDir)
        else:
            return False

    def setDoStop(self):
        self.doStop = True

    def getAlbumDir(self):
        if self.musicDirectory:
            albumDir = os.path.join(self.musicDirectory.getDirPath(),self.dirPath)
            return albumDir
        else:
            return self.dirPath

    def getTracksFilePath(self):
        files =[]
        for track in self.tracks:
            files.append(track.getFilePath())
        return files
        

    def addStyle(self,idSet):
        self.styleIDSet = self.styleIDSet.union(idSet)


    def updateTitle(self):
        db = database()
        db.updateValue("albums","title",self.title,"albumID",self.albumID)

    def updateYear(self):
        db = database()
        db.updateValue("albums","year",self.year,"albumID",self.albumID)

    def update(self):
        self.updateTitle()
        self.updateYear()


if __name__ == '__main__':


    alb = album("ACDC - [1975] - TNT")
    print(alb.title)  
    alb = album("ACDC - [1983] - a tribute to")
    print(alb.title)        

    
            
            