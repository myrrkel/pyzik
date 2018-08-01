#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtSvg
from PyQt5.QtCore import Qt


orange = QtGui.QColor(216, 119, 0)

def getSvgIcon(fileName):
    svg = QtGui.QPixmap("img/"+fileName)
    mask = svg.createMaskFromColor(QtGui.QColor('black'), Qt.MaskOutColor)
    svg.fill(orange)
    svg.setMask(mask)


    return QtGui.QIcon(svg)