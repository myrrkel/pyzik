#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QDialog,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)
from src import svg_icon
from .labeled_widgets import LineEditLabeledWidget, SpinBoxLabeledWidget


class AlbumControlsWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        size_policy = QSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )
        size_policy.setHorizontalStretch(100)
        size_policy.setVerticalStretch(0)

        self.setSizePolicy(size_policy)

        _translate = QtCore.QCoreApplication.translate

        lay.addStretch()

        self.saveButton = QPushButton(_translate("album", "Save"))
        self.saveButton.setMinimumSize(QtCore.QSize(70, 27))
        # self.saveButton.setMaximumSize(QtCore.QSize(70, 27))
        self.saveButton.setIcon(svg_icon.get_svg_icon("save.svg"))

        size_policy = QSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed
        )
        size_policy.setHorizontalStretch(50)
        size_policy.setVerticalStretch(0)

        self.saveButton.setSizePolicy(size_policy)

        lay.addWidget(self.saveButton)

        lay.addStretch()


class AlbumFieldsWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        _translate = QtCore.QCoreApplication.translate
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(100)
        size_policy.setVerticalStretch(0)
        self.setSizePolicy(size_policy)

        self.title = LineEditLabeledWidget(self, "title", _translate("album", "Title"))
        lay.addWidget(self.title)
        self.year = SpinBoxLabeledWidget(self, "year", _translate("album", "Year"))
        lay.addWidget(self.year)


class AlbumWidget(QDialog):
    def __init__(self, album, parent=None):
        QDialog.__init__(self, parent)
        self.album = album
        self.setWindowFlags(QtCore.Qt.Window)

        self.init_ui()
        self.set_values()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        self.setSizePolicy(size_policy)
        self.setMinimumSize(QtCore.QSize(200, 120))
        self.resize(400, 120)

        self.album_fields = AlbumFieldsWidget(self)
        layout.addWidget(self.album_fields)

        self.album_controls = AlbumControlsWidget(self)
        self.album_controls.saveButton.clicked.connect(self.on_save)
        layout.addWidget(self.album_controls)

        self.retranslateUi()

    def set_values(self):
        self.album_fields.title.line_edit.setText(self.album.title)
        self.album_fields.year.spin_box.setValue(self.album.year)

    def on_save(self, event):
        self.album.title = self.album_fields.title.line_edit.text()
        self.album.year = self.album_fields.year.spin_box.value()
        self.album.update()
        self.close()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate

        self.setWindowTitle(_translate("album", "Album"))
        self.album_controls.saveButton.setText(_translate("album", "Save"))
        self.album_fields.title.label.setText(_translate("album", "Title"))
        self.album_fields.year.label.setText(_translate("album", "Year"))


if __name__ == "__main__":
    import sys
    from src.music_base import MusicBase
    mb = MusicBase()
    print("loadMusicBase")
    mb.load_music_base(False)

    alb = mb.album_col.get_album(1)
    app = QApplication(sys.argv)
    custWidget = AlbumWidget(alb)

    custWidget.show()
    sys.exit(app.exec_())
