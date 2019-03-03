#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtSvg
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QFile, QXmlStreamReader, QByteArray, QTextStream
from globalConstants import *

#orange = QtGui.QColor(216, 119, 0)

def getSvgIcon(fileName):
    return QtGui.QIcon(getColoredSvg(fileName))


def getColoredSvg(fileName, colorToReplace='black'):
    svg = QtGui.QPixmap(appDir+"/img/"+fileName)
    mask = svg.createMaskFromColor(QtGui.QColor(colorToReplace), Qt.MaskOutColor)
    svg.fill(orange)
    svg.setMask(mask)

    return svg


def getColoredSvg2(fileName, colorToReplace='black'):
    svg = QtGui.QPixmap(appDir+"/img/"+fileName)
    mask = svg.createMaskFromColor(QtGui.QColor(colorToReplace), Qt.MaskInColor)

    p = QtGui.QPainter(svg)
    p.setPen(orange)
    p.drawPixmap(svg.rect(), mask, mask.rect())
    p.end()

    return svg


def getSvgWithColorParam(fileName):
    file = QFile(appDir+"/img/"+fileName)
    file.open(QFile.ReadOnly | QFile.Text)
    textStream = QTextStream(file)
    svgData = textStream.readAll()
    svgData = svgData.replace("#color","#D87700")

    file.close()

    painter = QtGui.QPainter()
    img = QtGui.QImage()
    pix  = QtGui.QPixmap(400,400)
    pix.fill(QtGui.QColor("transparent"))

    painter.begin(pix)

    rend = QtSvg.QSvgRenderer(QByteArray(svgData.encode()))
    img = rend.render(painter)
    painter.end()

    pix.save("img/logo.png")
    return  pix
 

def getLogo():
    return QtGui.QIcon(getSvgWithColorParam("vinyl-record2.svg"))