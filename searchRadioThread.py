import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread

import time

from radioManager import *


class searchRadioThread(QThread):


    """search radios"""

    doStop = False 
    search = ""
    rm = radioManager()

    resRadios = []

    machines = ['Dar','Dirble','Tunein','RadioBrowser']

    machineNb = len(machines)

    searchProgress = pyqtSignal(int, name='searchProgress')
    searchCurrentMachine = pyqtSignal(str, name='searchCurrentMachine')
    searchCompleted = pyqtSignal(int, name='searchCompleted')

    def emitCurrentMachine(self,txt):
        self.searchCurrentMachine.emit(txt+' - Results = '+str(len(self.resRadios)))

    def emitProgress(self,val):
        if val != 0:
            self.searchProgress.emit((100/self.machineNb)*val)
        else:
            self.searchProgress.emit(0)

    def run(self):
        self.resRadios = []
        self.doStop = False
        i=0
        self.emitProgress(0)
        for machine in self.machines:
            print(machine)
            i=i+1
            self.searchMachine(machine)
            self.emitProgress(i)
            if self.doStop: return 1

        self.searchCompleted.emit(1)
        return 1
        
    def searchMachine(self,machine):
        self.emitCurrentMachine(machine)
        self.resRadios.extend(self.rm.search(self.search,machine))


    def stop(self):
        self.doStop = True
        self.searchCompleted.emit(1)

