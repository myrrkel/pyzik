#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Install file """
import sys
import setuptools
from cx_Freeze import setup, Executable

includes = ["PyQt5","darkStyle"]
packages = setuptools.find_packages()


executables = [
        Executable("pyzik.py")
]


# call setup function
setup(
    name = "pyzik",
    version = "0.2",
    description = "Music manager for big album collections and webradios",
    options = {"build_exe": {"includes": includes,
                 #"excludes": excludes,
                 "packages": packages
                 #"path": path
                 }
           },
    executables = executables,
)