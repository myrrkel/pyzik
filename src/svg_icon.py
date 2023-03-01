#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtSvg
from PyQt5.QtCore import Qt, QFile, QXmlStreamReader, QByteArray, QTextStream
from global_constants import *


def get_svg_icon(file_name):
    return QtGui.QIcon(get_colored_svg(file_name))


def get_colored_svg(file_name, color_to_replace="black"):
    svg = QtGui.QPixmap(APP_DIR + "/img/" + file_name)
    mask = svg.createMaskFromColor(QtGui.QColor(color_to_replace), Qt.MaskOutColor)
    svg.fill(ORANGE)
    svg.setMask(mask)

    return svg


def get_colored_svg2(file_name, color_to_replace="black"):
    svg = QtGui.QPixmap(APP_DIR + "/img/" + file_name)
    mask = svg.createMaskFromColor(QtGui.QColor(color_to_replace), Qt.MaskInColor)

    p = QtGui.QPainter(svg)
    p.setPen(ORANGE)
    p.drawPixmap(svg.rect(), mask, mask.rect())
    p.end()

    return svg


def get_svg_with_color_param(
    file_name, dest_name="logo.svg", color_to_replace="#color", new_color="#D87700"
):
    file = QFile(APP_DIR + "/img/" + file_name)
    file.open(QFile.ReadOnly | QFile.Text)
    text_stream = QTextStream(file)
    svg_data = text_stream.readAll()
    svg_data = svg_data.replace(color_to_replace, new_color)

    file.close()

    painter = QtGui.QPainter()
    img = QtGui.QImage()
    pix = QtGui.QPixmap(400, 400)
    pix.fill(QtGui.QColor("transparent"))

    painter.begin(pix)

    rend = QtSvg.QSvgRenderer(QByteArray(svg_data.encode()))
    img = rend.render(painter)
    painter.end()

    if dest_name != "":
        pix.save(APP_DIR + "/img/" + dest_name)

    return pix


def get_colored_pixmap_svg(file_name, color_to_replace="black"):
    svg = QtGui.QPixmap(50, 50)
    svg.fill(QtGui.QColor("transparent"))
    svg.load(APP_DIR + "/img/" + file_name)
    mask = svg.createMaskFromColor(QtGui.QColor(color_to_replace), Qt.MaskOutColor)
    svg.fill(ORANGE)
    svg.setMask(mask)
    svg.load(APP_DIR + "/img/" + file_name)

    return svg


def get_logo():
    return QtGui.QIcon(get_svg_with_color_param("vinyl-record.svg"))
