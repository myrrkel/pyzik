#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math, sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class waitOverlay(QWidget):
    timer = 0

    def __init__(self, parent=None, nbDots=15, circleSize=30, color=None, backgroundOpacity=40, hideOnClick = False):

        QWidget.__init__(self, parent)

        self.counter = 0

        self.parent = parent
        self.nbDots = nbDots
        self.circleSize = circleSize
        self.hideOnClick = hideOnClick

        if color is None:
            self.color = QColor(100, 100, 100)
        else:
            self.color = color

        self.colorLight = self.color.lighter(150)
        self.colorLight.setAlpha(200)

        self.backgroundOpacity = backgroundOpacity

        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)

    def paintEvent(self, event=None):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255, self.backgroundOpacity)))
        painter.setPen(QPen(Qt.NoPen))

        for i in range(self.nbDots):
            if self.counter % self.nbDots == i:
                painter.setBrush(QBrush(self.color))
            else:
                painter.setBrush(QBrush(self.colorLight))

            painter.drawEllipse(
                (self.width() - 0) / 2 + self.circleSize * math.cos(2 * math.pi * i / self.nbDots) - 5,
                (self.height() - 0) / 2 + self.circleSize * math.sin(2 * math.pi * i / self.nbDots) - 5,
                10, 10)

        painter.end()

    def showEvent(self, event):

        event.accept()

    def showOverlay(self):
        if self.timer == 0:
            self.timer = self.startTimer(800 / self.nbDots)

        self.show()

    def timerEvent(self, event):

        self.counter += 1
        self.update()

    def mouseReleaseEvent(self, event):
        if self.hideOnClick:
            self.hide()


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        widget = QWidget(self)
        self.editor = QTextEdit()
        self.editor.setPlainText("0123456789" * 100)
        layout = QGridLayout(widget)
        layout.addWidget(self.editor, 0, 0, 1, 3)
        button = QPushButton("Wait")
        layout.addWidget(button, 1, 1, 1, 1)

        self.setCentralWidget(widget)
        self.overlay = waitOverlay(self.centralWidget(), hideOnClick=True)
        self.overlay.hide()
        button.clicked.connect(self.overlay.showOverlay)

    def resizeEvent(self, event):
        self.overlay.resize(event.size())
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
