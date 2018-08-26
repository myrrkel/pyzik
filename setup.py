#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Install file """
import sys, glob
import setuptools
from cx_Freeze import setup, Executable

path = sys.path.append("src")
includes = []
#includes = ["PyQt5","darkStyle"]
includefiles = ["src/img","src/darkStyle","src/translation"]
#includefiles = includefiles+ glob.glob("src/translation/*.qm")
#excludes = ["setuptools","cx_Freeze"]
packages = setuptools.find_packages()
packages.append("idna")
packages.append("sqlite3")

executables = [
        Executable("src/pyzik.py")
]


# call setup function
setup(
    name = "pyzik",
    version = "0.2",
    url = "https://github.com/myrrkel/pyzik",
    author = "myrrkel",
    description = "Music manager for big album collections and webradios",
    options = {"build_exe": {"includes": includes,
                 #"excludes": excludes,
                 "packages": packages,
                 'include_files':includefiles,
                 "path": path,

                 }
           },
    executables = executables,
)
