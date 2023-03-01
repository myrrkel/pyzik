import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread

import time

from radio_manager import RadioManager


class SearchRadioThread(QThread):
    """search radios"""

    do_stop = False
    search = ""
    radio_manager = RadioManager()

    res_radios = []

    machine_nb = 0

    search_progress = pyqtSignal(int, name="searchProgress")
    search_current_machine = pyqtSignal(str, name="searchCurrentMachine")
    search_completed = pyqtSignal(int, name="searchCompleted")

    def emit_current_machine(self, txt):
        self.search_current_machine.emit(txt + " - Results = " + str(len(self.res_radios)))

    def emit_progress(self, val):
        if val != 0:
            self.search_progress.emit((100 / self.machine_nb) * val)
        else:
            self.search_progress.emit(0)

    def run(self):
        self.res_radios = []
        self.do_stop = False
        i = 0
        self.emit_progress(0)
        if self.machines is None:
            self.machines = self.radio_manager.machines
        self.machine_nb = len(self.machines)
        for machine in self.machines:
            print(machine)
            i = i + 1
            self.search_machine(machine)
            self.emit_progress(i)
            if self.do_stop:
                break

        self.search_completed.emit(1)

    def search_machine(self, machine):
        self.emit_current_machine(machine)
        self.res_radios.extend(self.radio_manager.search(self.search, machine))

    def stop(self):
        self.do_stop = True
        self.search_completed.emit(1)
