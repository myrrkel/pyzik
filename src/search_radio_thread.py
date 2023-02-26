import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread

import time

from radio_manager import RadioManager


class SearchRadioThread(QThread):
    """search radios"""

    doStop = False
    search = ""
    rm = RadioManager()

    resRadios = []

    machineNb = 0

    searchProgress = pyqtSignal(int, name="searchProgress")
    searchCurrentMachine = pyqtSignal(str, name="searchCurrentMachine")
    searchCompleted = pyqtSignal(int, name="searchCompleted")

    def emit_current_machine(self, txt):
        self.searchCurrentMachine.emit(txt + " - Results = " + str(len(self.resRadios)))

    def emit_progress(self, val):
        if val != 0:
            self.searchProgress.emit((100 / self.machineNb) * val)
        else:
            self.searchProgress.emit(0)

    def run(self):
        self.resRadios = []
        self.doStop = False
        i = 0
        self.emit_progress(0)
        if self.machines is None:
            self.machines = self.rm.machines
        self.machineNb = len(self.machines)
        for machine in self.machines:
            print(machine)
            i = i + 1
            self.search_machine(machine)
            self.emit_progress(i)
            if self.doStop:
                break

        self.searchCompleted.emit(1)

    def search_machine(self, machine):
        self.emit_current_machine(machine)
        self.resRadios.extend(self.rm.search(self.search, machine))

    def stop(self):
        self.doStop = True
        self.searchCompleted.emit(1)
