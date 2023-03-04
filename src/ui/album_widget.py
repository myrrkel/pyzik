#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from src import svg_icon


class AlbumControlsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)

        self.setSizePolicy(sizePolicy)

        _translate = QtCore.QCoreApplication.translate

        lay.addStretch()

        self.saveButton = QtWidgets.QPushButton(_translate("album", "Save"))
        self.saveButton.setMinimumSize(QtCore.QSize(70, 27))
        # self.saveButton.setMaximumSize(QtCore.QSize(70, 27))
        self.saveButton.setIcon(svg_icon.get_svg_icon("save.svg"))

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(50)
        sizePolicy.setVerticalStretch(0)

        self.saveButton.setSizePolicy(sizePolicy)

        lay.addWidget(self.saveButton)

        lay.addStretch()


class AlbumInfoControlsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        _translate = QtCore.QCoreApplication.translate

        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)

        self.setSizePolicy(sizePolicy)

        self.title = QtWidgets.QWidget(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)

        self.title.setSizePolicy(sizePolicy)
        self.title.setMinimumSize(QtCore.QSize(25, 27))
        self.title.setMaximumSize(QtCore.QSize(16777215, 27))
        self.title.setObjectName("title")
        lay.addWidget(self.title)

        lay1 = QtWidgets.QHBoxLayout(self.title)
        lay1.setContentsMargins(0, 0, 0, 0)

        self.titleLabel = QtWidgets.QLabel(self.title)
        self.titleLabel.setText(_translate("album", "Title"))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.titleLabel.setSizePolicy(sizePolicy)
        self.titleLabel.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        lay1.addWidget(self.titleLabel)

        self.titleEdit = QtWidgets.QLineEdit(self.title)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        self.titleEdit.setSizePolicy(sizePolicy)
        self.titleEdit.setMinimumSize(QtCore.QSize(50, 27))
        self.titleEdit.setMaximumSize(QtCore.QSize(16777215, 17000))
        lay1.addWidget(self.titleEdit)

        self.year = QtWidgets.QWidget(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        self.year.setSizePolicy(sizePolicy)
        self.year.setMinimumSize(QtCore.QSize(25, 27))
        self.year.setMaximumSize(QtCore.QSize(16777215, 27))
        self.year.setObjectName("year")
        lay.addWidget(self.year)

        lay2 = QtWidgets.QHBoxLayout(self.year)
        lay2.setContentsMargins(0, 0, 0, 0)

        self.yearLabel = QtWidgets.QLabel(self.year)
        self.yearLabel.setText(_translate("album", "Year"))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(100)
        self.yearLabel.setSizePolicy(sizePolicy)
        self.yearLabel.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        lay2.addWidget(self.yearLabel)

        self.yearSpin = QtWidgets.QSpinBox(self.year)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(100)
        self.yearSpin.setSizePolicy(sizePolicy)
        self.yearSpin.setMinimum(0)
        self.yearSpin.setMaximum(9999)
        self.yearSpin.setSingleStep(1)
        self.yearSpin.setMinimumSize(QtCore.QSize(70, 27))
        self.yearSpin.setMaximumSize(QtCore.QSize(70, 40))
        lay2.addWidget(self.yearSpin)

        # lay.addWidget(lay1)


class AlbumWidget(QtWidgets.QDialog):
    def __init__(self, album, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.album = album
        self.setWindowFlags(QtCore.Qt.Window)

        self.initUI()
        self.set_values()

        # self.showTableItems(self.mainItem.items)
        # self.initColumnHeaders()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        # layout.setContentsMargins(4, 4, 4, 4)
        self.setLayout(layout)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(200, 120))
        # self.setMaximumSize(QtCore.QSize(16777215, 27))
        self.resize(400, 120)
        # self.initTableWidgetItems()

        self.albumInfoControls = AlbumInfoControlsWidget(self)
        layout.addWidget(self.albumInfoControls)

        self.albumControls = AlbumControlsWidget(self)
        self.albumControls.saveButton.clicked.connect(self.on_save)

        # layout.addWidget(self.tableWidgetItems)

        layout.addWidget(self.albumControls)

        self.retranslateUi()

    def set_values(self):
        self.albumInfoControls.titleEdit.setText(self.album.title)
        self.albumInfoControls.yearSpin.setValue(self.album.year)

    def on_save(self, event):
        self.album.title = self.albumInfoControls.titleEdit.text()
        self.album.year = self.albumInfoControls.yearSpin.value()
        self.album.update()
        self.close()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate

        self.setWindowTitle(_translate("album", "Album"))
        self.albumControls.saveButton.setText(_translate("album", "Save"))
        self.albumInfoControls.titleLabel.setText(_translate("album", "Title"))
        self.albumInfoControls.yearLabel.setText(_translate("album", "Year"))


if __name__ == "__main__":
    import sys
    from music_base import MusicBase

    mb = MusicBase()
    print("loadMusicBase")
    mb.load_music_base(False)

    alb = mb.album_col.get_album(1)

    app = QtWidgets.QApplication(sys.argv)

    custWidget = AlbumWidget(alb)

    custWidget.show()
    sys.exit(app.exec_())
