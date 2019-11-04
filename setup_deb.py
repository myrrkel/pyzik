#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Install file """
import os, sys, glob
#import setuptools
from setuptools import setup, find_packages
#from distutils.core import setup


path = sys.path.append("src")
includes = []

includefiles = ["src/img","src/darkStyle","src/translation"]
includefiles = includefiles+ glob.glob("src/translation/*.qm")
excludes = [#"setuptools","cx_Freeze",
                        "PyQt5.QtWebEngine",
                        "PyQt5.QtWebEngineCore",
                        "PyQt5.QtWebEngineWidgets"]
packages = find_packages()
packages.append("idna")
packages.append("sqlite3")
packages.append("multiprocessing")


for package in packages:
    print("package found= "+str(package))

for inc in includefiles:
    print("include found= "+str(inc))




# call setup function
setup(
    name = "pyzik",
    version = "0.3.1",
    url = "https://github.com/myrrkel/pyzik",
    author = "myrrkel",
    author_email='myrrkel@gmail.com',
    description = "Music manager for big album collections and webradios",
    options = {"build_exe": {"includes": includes,
                 "excludes": excludes,
                 "packages": packages,
                 'include_files':includefiles,
                 "path": path,
                 },
    },
)
