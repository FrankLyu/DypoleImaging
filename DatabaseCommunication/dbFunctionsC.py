# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 12:31:50 2020

@author: Dypole
"""

import clr
import sys
import os

# this file is to interface python with the dbHelper written in C# by Will

memcachedServerIP = "192.168.1.133"
#assemblyPath = r"C:/Users/Dypole/Desktop/ImagingAndor/DatabaseSaver/DatabaseHelperPython/DatabaseHelperPython/bin/Release"
print(os.path.dirname(__file__))
print(os.path.abspath(os.path.dirname(__file__)))
#assemblyPath = os.path.abspath(os.path.dirname(__file__)) + "\\DatabaseHelperPython\\DatabaseHelperPython\\bin\\Release"
assemblyPath = os.path.abspath(os.path.dirname(__file__)) + "/DatabaseHelperPython/DatabaseHelperPython/bin/Release"
print(assemblyPath)
sys.path.append(assemblyPath)
clr.AddReference("DatabaseHelperPython")
from dbHelperNamespace import dbHelperClass
dbHelper = dbHelperClass()


def writeImageToCacheC(atoms, noAtoms, dark, width, height, cameraID, runID, seqID):
    dbHelper.writeImageDataToCache(memcachedServerIP, atoms, noAtoms, dark, width, height, cameraID, runID, seqID)
    print("New images written to cache")
