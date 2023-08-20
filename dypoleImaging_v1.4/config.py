# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 10:27:05 2020

@author: Dypole_Imaging
"""

import platform
import datetime
import os
today = datetime.date.today()

# if platform.system() == 'Darwin': # MAC OS
#     LOCAL_PATH = '/Users/pierre/Documents/Scolaire/MIT/Graduate/AndorCamera/AndorTransfer/'
#     LOCAL_PATH = LOCAL_PATH + str(today.year) + "/" + str(today.month) + "/" + str(today.day)
#     SPACER = '/'
#     MYSQLserverIP = "127.0.0.1"

if platform.system() == 'Linux' or platform.system() == 'Darwin':
    LOCAL_PATH = '~/Dropbox (MIT)/Documents/MIT/dypole-imaging/AndorCamera/AndorTransfer/'
    LOCAL_CAMERA_PATH_FLIR = '~/Dropbox (MIT)/Documents/MIT/dypole-imaging/FLIRCommand/'
    LOCAL_CAMERA_PATH_ANDOR = '~/Dropbox (MIT)/Documents/MIT/dypole-imaging/AndorCamera/'
    SPACER = '/'
    MYSQLserverIP = "127.0.0.1"

if platform.system() == 'Windows':
    LOCAL_CAMERA_PATH_FLIR = os.getcwd() + "\\FLIRCommand"
    LOCAL_CAMERA_PATH_ANDOR = "C:\\Users\\Dypole\\Desktop\\dypole-imaging\\andorCommand\\image"
    #LOCAL_CAMERA_PATH = "C:\\Users\\Dypole\\Desktop\\ImagingAndor\\dypole-imaging\\FLIRCommand"
    LOCAL_PATH = 'C:\\Users\\Dypole\\Desktop\\ImagingAndor\\Images\\AndorTransfer\\'
    LOCAL_PATH = LOCAL_PATH + str(today.year) + "\\" + str(today.month) + "\\" + str(today.day) # same definition as in BEC3's code, eventually combine the 2 in the same object.
    SPACER = '\\'
    MYSQLserverIP = "192.168.1.133"



# set minimum file size // connect that later on to BEC3's code 
minimumFileSize = 30*10**6
typeOfConnection = 'global'

# memcachedServerIP = "192.168.1.133"   This is actually defined now in the DatabaseCommunication dbFunctionsC.py file

username = "root"
password = "w0lfg4ng"
databaseName = "dypoledatabase"

waitTimeStep = 0.1 # in seconds, the wait time between different 
height = 2160   # pixel height of Andor camera
width = 2560    # pixel width of Andor camera
cameraID = 4    # camera ID of Andor camera in the DB

imagingWavelength = 421*10**(-9)
