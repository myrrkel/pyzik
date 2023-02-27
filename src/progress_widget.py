#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt


class ProgressWidget(QtWidgets.QDialog):
    progressClosed = pyqtSignal(int, name="progressClosed")

    def __init__(self, parent, can_be_closed=True, with_file_progress=False):
        QtWidgets.QDialog.__init__(self)
        self.parent = parent
        self.can_be_closed = can_be_closed
        self.with_file_progress = with_file_progress
        self.initUI()

    def initUI(self):
        self.resize(350, 20)
        # self.setMaximumWidth(150)
        # self.setMaximumSize(QtCore.QSize(350, 150))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(100)

        self.setSizePolicy(sizePolicy)
        self.main_layout = QtWidgets.QVBoxLayout()

        self.setLayout(self.main_layout)

        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setGeometry(0, 0, 250, 20)
        self.progress.setValue(0)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        self.progress.setSizePolicy(sizePolicy)
        self.main_layout.addWidget(self.progress)

        self.progress_label = QtWidgets.QLabel("Progress:")
        self.progress_label.setMargin(0)
        self.progress_label.setContentsMargins(0, 0, 0, 0)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        self.progress_label.setSizePolicy(sizePolicy)
        self.progress_label.setGeometry(0, 30, 250, 20)
        # self.progress_label.setWordWrap(True)
        self.main_layout.addWidget(self.progress_label)

        self.directory = QtWidgets.QLineEdit("Directory")
        self.directory.setReadOnly(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        self.directory.setSizePolicy(sizePolicy)
        self.directory.setGeometry(0, 30, 250, 20)
        # self.directory.setWordWrap(True)
        self.main_layout.addWidget(self.directory)

        if self.with_file_progress:
            self.file = QtWidgets.QLineEdit("File")
            self.file.setReadOnly(True)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
            )
            sizePolicy.setHorizontalStretch(100)
            sizePolicy.setVerticalStretch(0)
            self.file.setSizePolicy(sizePolicy)
            self.file.setGeometry(0, 30, 250, 20)
            # self.file.setWordWrap(True)
            self.main_layout.addWidget(self.file)

        if self.can_be_closed:
            self.setWindowFlags(
                Qt.Window | Qt.WindowStaysOnTopHint | Qt.WindowTitleHint
            )
        else:
            self.setWindowFlags(
                Qt.Window
                | Qt.WindowStaysOnTopHint
                | Qt.CustomizeWindowHint
                | Qt.WindowTitleHint
            )

        self.show()

    def set_value(self, value):
        self.progress.setValue(value)
        self.setWindowTitle(str(value) + "%")

    def set_progress_label(self, value):
        self.progress_label.setText(value)

    def set_directory_text(self, value):
        self.directory.setText(value)

    def set_file_text(self, value):
        if self.with_file_progress:
            self.file.setText(value)

    def closeEvent(self, event):
        print("progressClosed=OnClose")
        self.progressClosed.emit(0)
        self.close()
        event.accept()


if __name__ == "__main__":
    from pyzik import *

    app = QtWidgets.QApplication(sys.argv)
    dark = darkStyle.darkStyle()
    app.setStyleSheet(dark.load_stylesheet_pyqt5())

    progress = ProgressWidget(app, can_be_closed=False, with_file_progress=True)

    progress.show()
    sys.exit(app.exec_())
