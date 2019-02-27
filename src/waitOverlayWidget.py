#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math, sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class waitOverlay(QWidget):

    def __init__(self, parent = None):
    
        QWidget.__init__(self, parent)
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)
    
    def paintEvent(self, event=None):
        print("paintEvent")
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        colorGreen = QColor(100, 100, 100)
        colorLightGreen =      QColor(130, 130, 130)

        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255, 127)))
        painter.setPen(QPen(Qt.NoPen))

        nbDots = 15
        circleSize = 30
        
        for i in range(nbDots):
            if self.counter % nbDots == i:
                painter.setBrush(QBrush(colorGreen))
            else:
                painter.setBrush(QBrush(colorLightGreen))

            painter.drawEllipse(
                self.width()/2 + circleSize * math.cos(2 * math.pi * i / nbDots) - 10,
                self.height()/2 + circleSize * math.sin(2 * math.pi * i / nbDots) - 10,
                10, 10)
        
        painter.end()
    
    def showEvent(self, event):
    
        self.timer = self.startTimer(50)
        self.counter = 0
    
    def timerEvent(self, event):

       
        self.counter += 1
        self.update()
        if self.counter == 500:
            self.killTimer(self.timer)
            self.hide()


class MainWindow(QMainWindow):

    def __init__(self, parent = None):
    
        QMainWindow.__init__(self, parent)
        
        widget = QWidget(self)
        self.editor = QTextEdit()
        self.editor.setPlainText("0123456789"*100)
        layout = QGridLayout(widget)
        layout.addWidget(self.editor, 0, 0, 1, 3)
        button = QPushButton("Wait")
        layout.addWidget(button, 1, 1, 1, 1)
        
        self.setCentralWidget(widget)
        self.overlay = waitOverlay(self.centralWidget())
        self.overlay.hide()
        button.clicked.connect(self.overlay.show)
    
    def resizeEvent(self, event):
    
        self.overlay.resize(event.size())
        event.accept()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())