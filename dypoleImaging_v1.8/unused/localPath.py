# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 10:27:05 2020

@author: Dypole_Imaging
"""

import platform
import datetime
today = datetime.date.today()

if platform.system() == 'Darwin': # MAC OS
    LOCAL_PATH = '/Users/pierre/Documents/Scolaire/MIT/Graduate/AndorCamera/AndorTransfer/'
    LOCAL_PATH = LOCAL_PATH + str(today.year) + "/" + str(today.month) + "/" + str(today.day)
    SPACER = '/'

if platform.system() == 'Linux':
    LOCAL_PATH = '~/Dropbox (MIT)/Documents/MIT/dypole-imaging/AndorTransfer/' # Please add the Linux typical path
    SPACER = '/'

# if platform.system() == 'Windows':
#     LOCAL_PATH = 'C:\\Users\\Dypole_Imaging\\Desktop\\ImagingAndor\\Images\\AndorTransfer\\'
#     LOCAL_PATH = LOCAL_PATH + str(today.year) + "\\" + str(today.month) + "\\" + str(today.day) # same definition as in BEC3's code, eventually combine the 2 in the same object.
#     SPACER = '\\'

if platform.system() == 'Windows':
    LOCAL_PATH = 'C:\\Users\\Dypole\\Desktop\\ImagingAndor\\Images\\AndorTransfer\\'
    LOCAL_PATH = LOCAL_PATH + str(today.year) + "\\" + str(today.month) + "\\" + str(today.day) # same definition as in BEC3's code, eventually combine the 2 in the same object.
    SPACER = '\\'
