#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import Qt, QTimer, QSize, QCoreApplication
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QSizePolicy, QPushButton, QLineEdit, QGridLayout, QFileDialog, QLabel


class directoryWidget(QWidget):

    def __init__(self, parent=None):

        QWidget.__init__(self, parent)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QSize(0, 27))
        self.setMaximumSize(QSize(16777215, 27))

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName("gridLayout")

        self.labelDir = QLabel(self)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.labelDir.setSizePolicy(sizePolicy)
        self.labelDir.setMinimumSize(QSize(50, 27))
        self.labelDir.setMaximumSize(QSize(16777215, 27))
        self.labelDir.setObjectName("labelDir")
        self.labelDir.setAlignment(Qt.AlignLeft | Qt.AlignTrailing | Qt.AlignVCenter)
        self.gridLayout.addWidget(self.labelDir, 0, 1)

        self.DirEdit = QLineEdit(self)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        self.DirEdit.setSizePolicy(sizePolicy)
        self.DirEdit.setMinimumSize(QSize(25, 27))
        self.DirEdit.setMaximumSize(QSize(16777215, 27))
        self.DirEdit.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.DirEdit.setObjectName("DirEdit")
        self.gridLayout.addWidget(self.DirEdit, 0, 2)



        self.DirButton = QPushButton(self)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DirButton.sizePolicy().hasHeightForWidth())
        self.DirButton.setSizePolicy(sizePolicy)
        self.DirButton.setMinimumSize(QSize(25, 27))
        self.DirButton.setMaximumSize(QSize(25, 27))
        self.DirButton.setObjectName("DirButton")
        self.gridLayout.addWidget(self.DirButton, 0, 3)

        self.labelDir.setText('Directory')
        self.DirButton.setText("...")

        self.DirButton.clicked.connect(self.onChangeDir)

    def setText(self, text):
        self.labelDir.setText(text)

    def selectDir(self):
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        return directory

    def onChangeDir(self):
        directory = self.selectDir()
        self.DirEdit.setText(directory)


class TestMainWindow(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        widget = QWidget(self)
        self.directory_selector = directoryWidget(self)

        layout = QGridLayout(widget)
        layout.addWidget(self.directory_selector)
        self.directory_selector.setText('My Directory')

        self.setCentralWidget(widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestMainWindow()
    window.show()
    sys.exit(app.exec_())