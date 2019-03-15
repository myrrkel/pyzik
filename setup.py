#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Install file """
import os, sys, glob, platform
import setuptools
from cx_Freeze import setup, Executable

if platform.system() == "Windows":
    PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
    os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
    os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')


path = sys.path.append("src")
includes = []
#includes = ["PyQt5","darkStyle"]
includefiles = ["src/img","src/darkStyle","src/translation"]
includefiles = includefiles+ glob.glob("src/translation/*.qm")
excludes = ["setuptools","cx_Freeze",
                        "PyQt5.QtWebEngine",
                        "PyQt5.QtWebEngineCore",
                        "PyQt5.QtWebEngineWidgets",]
packages = setuptools.find_packages()
packages.append("idna")
packages.append("sqlite3")


for package in packages:
    print("package found= "+str(package))


exe1 = Executable (
        script="src/pyzik.py",
        base="Win32GUI",        
        )

#executables = [Executable("src/pyzik.py")]
executables = [exe1]


# call setup function
setup(
    name = "pyzik",
    version = "0.3",
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
