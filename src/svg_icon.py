#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtSvg
from PyQt5.QtCore import QFile, QXmlStreamReader, QByteArray, QTextStream
from global_constants import *


# orange = QtGui.QColor(216, 119, 0) #d87700


def get_svg_icon(file_name):
    return QtGui.QIcon(get_colored_svg(file_name))


def get_colored_svg(file_name, color_to_replace="black"):
    svg = QtGui.QPixmap(appDir + "/img/" + file_name)
    mask = svg.createMaskFromColor(QtGui.QColor(color_to_replace), Qt.MaskOutColor)
    svg.fill(orange)
    svg.setMask(mask)

    return svg


def get_colored_svg2(file_name, color_to_replace="black"):
    svg = QtGui.QPixmap(appDir + "/img/" + file_name)
    mask = svg.createMaskFromColor(QtGui.QColor(color_to_replace), Qt.MaskInColor)

    p = QtGui.QPainter(svg)
    p.setPen(orange)
    p.drawPixmap(svg.rect(), mask, mask.rect())
    p.end()

    return svg


def get_svg_with_color_param(
    file_name, destName="logo.svg", color_to_replace="#color", newColor="#D87700"
):
    file = QFile(appDir + "/img/" + file_name)
    file.open(QFile.ReadOnly | QFile.Text)
    textStream = QTextStream(file)
    svgData = textStream.readAll()
    svgData = svgData.replace(color_to_replace, newColor)

    file.close()

    painter = QtGui.QPainter()
    img = QtGui.QImage()
    pix = QtGui.QPixmap(400, 400)
    pix.fill(QtGui.QColor("transparent"))

    painter.begin(pix)

    rend = QtSvg.QSvgRenderer(QByteArray(svgData.encode()))
    img = rend.render(painter)
    painter.end()

    if destName != "":
        pix.save(appDir + "/img/" + destName)

    return pix


def get_colored_pixmap_svg(file_name, color_to_replace="black"):
    svg = QtGui.QPixmap(50, 50)
    svg.fill(QtGui.QColor("transparent"))
    svg.load(appDir + "/img/" + file_name)
    mask = svg.createMaskFromColor(QtGui.QColor(color_to_replace), Qt.MaskOutColor)
    svg.fill(orange)
    svg.setMask(mask)
    svg.load(appDir + "/img/" + file_name)

    return svg


def get_logo():
    return QtGui.QIcon(get_svg_with_color_param("vinyl-record.svg"))
