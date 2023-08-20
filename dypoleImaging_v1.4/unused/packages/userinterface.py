#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division
#####SYSTEM IMPORTS#####
#os- provides a portable way of using operating system dependent functionality.
#sys- provides access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter.
#glob- finds all the pathnames matching a specified pattern according to the rules used by the Unix shell.
#gc- provides an interface to the optional garbage collector.
import os, sys, glob, gc
#os.listdir- returns a list containing the names of the entries in the directory given by path.
from os import listdir
#os.path.isfile- return True if path is an existing regular file.
#os.path.join- join one or more path components intelligently.
from os.path import isfile, join

#####WX IMPORTS#####
#wx- GUI toolkit for the Python programming language. wxPython can be used  to create graphical user interfaces (GUI).
import wx, numpy
#wx.lib.rcsizer- pure-Python Sizer that lays out items in a grid similar to wx.FlexGridSizer but item position is not implicit but explicitly specified by row and column.
import wx.lib.rcsizer  as rcs
#wx.lib.scrolledpanel- fills a “hole” in the implementation of ScrolledWindow.
#providing automatic scrollbar and scrolling behavior and the tab traversal management that ScrolledWindow lacks.
import wx.lib.scrolledpanel

import wx.grid

#####TIME IMPORTS#####
import datetime
import time

#####SKLEARN IMPORTS#####
#Principal component analysis (PCA).  Linear dimensionality reduction using Singular Value Decomposition of the data to project it to a lower dimensional space.
#from sklearn.decomposition import PCA as sklearnPCA

#####MATPLOTLIB IMPORTS#####
import matplotlib
#matplotlib.use- sets the matplotlib backend to one of the known backends.
matplotlib.use('WXAgg')

#matplotlib.mlab.PCA- PCA calculates principal component (PC) axes such that the origins of PC axes is at the mean of the distribution along each axis.
#from matplotlib.mlab import PCA
#####
# THE PCA FROM MLAB LOOKS DEPRICATED SINCE PYTHON 2.2
#####


#FigureCanvas- the FigureCanvas contains the figure and does event handling.
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
#I honestlt can't find this in documentation.

# CAN I ERASE THAT ????
#from matplotlib.backends.backend_wx import NavigationToolbar2Wx
#from matplotlib.backends.backend_wx import NavigationToolbar2WxAgg
#Figure- provides the top-level Artist, the Figure, which contains all the plot elements.

import numpy as np

from matplotlib.figure import Figure
#matplotlib.pyplot- provides a MATLAB-like plotting framework.
import matplotlib.pyplot as plt
#matplotlib.cm- provides colormaps.
import matplotlib.cm as cm
#matplotlib.gridspec- a class that specifies the geometry of the grid that a subplot will be placed.
from matplotlib import gridspec
#matplotlib.rc- sets the current rc params
from matplotlib import rc

#####SCIPY IMPORTS#####
#scipy.linalg- linear algebra module.
from scipy import linalg as LA
#scipy.ndimage- multi-dimensional image processing.
from scipy import ndimage
#scipy.ndimage.filter.convolve- multidimensional convolution.
from scipy.ndimage.filters import convolve
#scipy.ndimage.filter.gaussian_filter- calculate a multidimensional Gaussian filter.
from scipy.ndimage.filters import gaussian_filter
#scipy.ndimage.filters.median_filter- calculate a multidimensional median filter.
from scipy.ndimage.filters import median_filter
#scipy.optimize.curve_fit- use non-linear least squares to fit a function, f, to data.
from scipy.optimize import curve_fit
#scipy.interpolate.interp1d- interpolate a 1-D function.
from scipy.interpolate import interp1d
#scipy.signal.medfilt- form a median filter on an N-dimensional array.
from scipy.signal import medfilt

#####PIL IMPORTS#####
#PIL.Image- functions to load images from files, and to create new images.
from PIL import Image

#####SHUTIL IMPORTS#####
#shutil- offers a number of high-level operations on files and collections of files.
import shutil
#shutil.copyfile- copy the contents (no metadata) of the file named src to a file named dst and return dst.
from shutil import copyfile

#####LOCAL IMPORTS#####
from imagePlot import *
from imgFunc_v6 import *
from watchforchange import *
from localPath import *
from exp_params import *
from fitTool import *
from Monitor import Monitor
from defringer_v2 import*
from canvasPanel import *
from figurePanel import *
from canvasFrame import *
from degenerateFitter import*   # This one was missing at first... WHY ???

from camera import Camera, mimicRunning
from config import LOCAL_CAMERA_PATH
from imgFunc_v6 import deleteFiles, readDBData, readFileData
#from run import *


import textwrap


#import winsound


import platform

systemeType = platform.system()     # platform.system() = Darwin for MacOS, otherwise Linux or Windows

# Local funtions for database

from DatabaseCommunication.dbFunctions import getLastImageID, getLastImageIDs, getTimestamp, getLastID, updateNewImage, writeAnalysisToDB, updateAnalysisOnDB, getNCount
from DatabaseCommunication.dbFunctionsC import writeImageToCacheC

# FLIR Camera control
from FLIRCommand.runHardwareTrigger import mainRunHardwareTrigger
import packages.imagedatamanager as imagedata
import packages.fitmanager as fit


import threading


#from eventemitter import EventEmitter

#####################################################
### Global Variables (default values)
### NOTE: pixelToDistance is (pixel per distance)/(magnification)
#pixelToDistance = 6.45E-6 #(um)
#crossSection = 6. * np.pi * (589E-9  / (2 * np.pi))**2
#####################################################

#def single_G(x, A, center, sigma, offset):
#    return A*np.exp(-1*((x-center)**2)/(2*sigma**2))+offset
    
class ImageUI(wx.Frame):
    def __init__(self, parent, title):
        super(ImageUI, self).__init__(parent, title = title, size=(1600, 1120))
        
        ## New parameters added by Pierre
        self.checkLocalFiles = False    # True = check the local harddrive, False = looks at the database
        
        self.isDummyImage = True  # when the image is simply a 1 by 1 pixel or that
                                    # no image has yet been selected
        self.cameraPosition = "HORIZONTAL" # HORIZONTAL or VERTICAL
        self.cameraType = "FLIR" # FLIR or Andor
        self.camera = Camera(self.cameraType, self.cameraPosition) # check if I can bind that to the original button position
        self.pathWrittenImages = LOCAL_CAMERA_PATH # folder where all the images get written by the cameras
        self.listOfValidImagesWaiting = []
        self.imageTimestamp = None
        self.imageDataManager = imagedata.ImageDataManager(None)
        self.fitManager = fit.FitManager()
        
        ## new parameters added by Hyungmok
        self.atom = 'Dy'
        self.magnification = 1.5
        self.pixelSize = 6.5
        self.pixelToDistance = self.pixelSize/self.magnification
        self.crossSection = 1.0E-13
        self.mass = 164 * massUnit
        self.rawAtomNumber = 1
        self.atomNumber_Secondary = 1
        
        self.timeChanged = False
        self.chosenLayerNumber = 4
        self.expectedFileSize = 0.01 ## in MB
        #self.actualFileSize = 31.6 ## in MB
        # I don't think it is necessary to create it here
        # if systemeType == 'Darwin': # MAC OS
        #     self.monitor = Monitor("/Users/pierre", self.autoRun, self.expectedFileSize, self.cameraType)
        
        # if systemeType == 'Linux':
        #     self.monitor = Monitor("/", self.autoRun, self.expectedFileSize, self.cameraType) # Please add the Linux typical path
        
        # if systemeType == 'Windows':
        #     self.monitor = Monitor("C:\\ ", self.autoRun, self.expectedFileSize, self.cameraType)
        
        self.gVals = None
        self.pVals = None
        self.fVals = None
        self.imageData = None
        self.atomImage = None
        self.AOI_PrimaryImage = None    # AOI_PrimaryImage refers to the image enclosed in the Primary AOI
        self.AOI_SecondaryImage = None  # This is not really needed as only used to calculate the difference between 2 images
        self.x_summed = None
        self.y_summed = None
        self.currentXProfile = None
        self.currentYProfile = None
        self.currentXProfileFit = None
        self.currentYProfileFit = None
        self.x_fitted = None
        self.y_fitted = None
        
        self.isRotationNeeded = False
        self.prevImageAngle = 0.
        self.imageAngle = 0.
        self.imagePivotX = 1
        self.imagePivotY = 1
        
        self.atomNumFromFitX = -1
        self.atomNumFromFitY = -1
        
        self.atomNumFromGaussianX = -1
        self.atomNumFromGaussianY = -1
        
        self.atomNumFromDegenFitX = -1
        self.atomNumFromDegenFitY = -1
        
        self.isXFitSuccessful = False
        self.isYFitSuccessful = False
        
        self.x_center = 0.
        self.y_center = 0.
        self.x_width = 1.
        self.y_width = 1.
        
        self.x_width_std = 1.
        self.y_width_std = 1.
        
        self.x_offset = 0.
        self.y_offset = 0.
        self.x_peakHeight = 1.
        self.y_peakHeight = 1.
        self.x_slope = 0.
        self.y_slope = 0.
        
        self.true_x_width = 1.
        self.true_y_width = 1.
        
        self.true_x_width_std = 1.
        self.true_y_width_std = 1.
        
        self.true_x_width_list = []
        self.true_y_width_list = []
        
        self.TOF = 1
        self.temperature = [0, 0]
        self.tempLongTime = [0, 0]
        self.xTrapFreq = 50
        self.yTrapFreq = 2000
        
        self.AOI_Primary = None
        
        self.fitOverlay = None
        self.quickFitBool = False
        
        self.xLeft_Primary = None
        self.xRight_Primary = None
        self.yBottom_Primary = None
        self.yTop_Primary = None
        
        self.rect_Primary =  None
        # self.Bind(wx.EVT_PAINT, self.OnPaint)
        
        self.xLeft_Secondary = None
        self.xRight_Secondary = None
        self.yBottom_Secondary = None
        self.yTop_Secondary = None
        
        self.rect_Secondary =  None
        
        self.isFitSuccessful = False

        #benchmarking variables
        self.benchmark_startTime=0
        self.benchmark_endTime=0

        self.q = None
        self.gaussionParams = None
        self.fermionParams = None
        self.bosonParams = None

        self.path = None
        self.defringingRefPath = None
        self.imageID = None
        self.imageIDIndex = 0
        self.Tmp = None
        self.data = None
        self.currentImg = None

    
        # set the default file type as "fits"
        #self.fileType = "fits"
        #self.fileType = "dbFile"  # looks at the database
        
        # The list of files in the chosen filetype
        self.imageIDList = []

        ######
        ## Initialize dummy data and image
        self.initializeDummyData()

        #################
        ## Initialize the UI
        self.InitUI()
        self.Centre()
        self.Show()
        # self.AOI = [(None,None),(None,None)]
        
#        self.observer = None
#        self.observer = Observer()
#        self.observer.schedule(MyHandler(self.autoRun, self, self.expectedFileSize), path = self.path)
        self.timeString = None
        
        self.fitMethodGaussian.SetValue(True)
        self.layer4Button.SetValue(True)
        self.autoRunning = False
        self.modifiedImageID = None

        self.currentfitImage = None
        self.imageList = []
        self.imageListFlag = 0
        # self.FermionFitChosen(e)

        #self.fitsFile.SetValue(True)
        #self.dbFile.SetValue(True)
        self.FLIRCamera.SetValue(True)
        
        ####################
        ## for defringing ##
        self.defringer = defringer()
        self.betterRef = None
        
        ## degenerate Fitter
        self.degenFitter = degenerateFitter()
        self.x_tOverTc = -1.
        self.x_thomasFermiRadius = 1.
        self.x_becPopulationRatio= 0.
        
        self.y_tOverTc = -1.
        self.y_thomasFermiRadius = 1.
        self.y_becPopulationRatio= 0.
        
        #####################
        ## for filters ##
        self.isMedianFilterOn = False
        self.isNormalizationOn = False


    def InitUI(self):
#        self.panel = wx.Panel(self)
        self.panel = wx.lib.scrolledpanel.ScrolledPanel(self, id = -1, size = (1,1)) # does the size even matter?
        self.panel.SetupScrolling()
        
               
        font1 = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        # font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        # font.SetPointSize(9)
######### file ############
        # set data path

        hbox = wx.BoxSizer(wx.HORIZONTAL)  # this is the general box: its left part are the setting, 
                                            # and its right part the image/Ncounts

        vbox0 = wx.BoxSizer(wx.VERTICAL)    # this is the setting vertical box

        settingBox = wx.StaticBox(self.panel, label = 'Setting')
        settingBoxSizer = wx.StaticBoxSizer(settingBox, wx.VERTICAL)

        
        ## camera configuration
        cameraConfigBox = wx.StaticBox(self.panel, label = 'Camera Configuration')
        cameraConfigBoxSizer = wx.StaticBoxSizer(cameraConfigBox, wx.VERTICAL)
        
        # Camera Type
        cameraTypeBox = wx.StaticBox(self.panel, label = 'Camera Type')
        cameraTypeBoxSizer = wx.StaticBoxSizer(cameraTypeBox, wx.HORIZONTAL)
        self.FLIRCamera = wx.RadioButton(self.panel, label="FLIR", style = wx.RB_GROUP)
        self.AndorCamera = wx.RadioButton(self.panel, label="Andor")
        self.AndorCamera.SetValue(True)
        cameraTypeBoxSizer.Add(self.FLIRCamera, flag=wx.ALL, border=5)
        cameraTypeBoxSizer.Add(self.AndorCamera, flag=wx.ALL, border=5)
        self.Bind(wx.EVT_RADIOBUTTON, self.setCameraType, id = self.FLIRCamera.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.setCameraType, id = self.AndorCamera.GetId())
        
        # camera position (for FLIR camera)
        cameraPositionBox = wx.StaticBox(self.panel, label = 'Camera Position')
        cameraPositionBoxSizer = wx.StaticBoxSizer(cameraPositionBox, wx.HORIZONTAL)
        self.verticalCamera = wx.RadioButton(self.panel, label="Vertical", style = wx.RB_GROUP)
        self.horizontalCamera = wx.RadioButton(self.panel, label="Horizontal")
        self.horizontalCamera.SetValue(True)
        cameraPositionBoxSizer.Add(self.verticalCamera, flag=wx.ALL, border=5)
        cameraPositionBoxSizer.Add(self.horizontalCamera, flag=wx.ALL, border=5)
        self.Bind(wx.EVT_RADIOBUTTON, self.setCameraPosition, id = self.verticalCamera.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.setCameraPosition, id = self.horizontalCamera.GetId())
        
        self.startCameraButton = wx.Button(self.panel, label = 'Start FLIR camera')
        self.startCameraButton.Bind(wx.EVT_BUTTON, self.startCamera)
        self.endCameraButton = wx.Button(self.panel, label = 'End FLIR camera')
        self.endCameraButton.Bind(wx.EVT_BUTTON, self.endCamera)
        hbox155 = wx.BoxSizer(wx.HORIZONTAL)
        hbox155.Add(self.startCameraButton, flag = wx.ALL, border = 5)
        hbox155.Add(self.endCameraButton, flag = wx.ALL, border = 5)
        
        
        cameraConfigBoxSizer.Add(cameraTypeBoxSizer, flag=wx.ALL| wx.EXPAND, border = 5)
        cameraConfigBoxSizer.Add(cameraPositionBoxSizer, flag=wx.ALL| wx.EXPAND, border = 5)
        cameraConfigBoxSizer.Add(hbox155, wx.ALL|wx.EXPAND, 5)
        
        settingBoxSizer.Add(cameraConfigBoxSizer, flag=wx.ALL| wx.EXPAND, border = 5)
        
        fermionOrBosonBox = wx.StaticBox(self.panel, label = 'Fermion/Boson/Gaussian')
        fermionOrBosonBoxSizer = wx.StaticBoxSizer(fermionOrBosonBox, wx.HORIZONTAL)
        self.fitMethodFermion = wx.RadioButton(self.panel, label="Fermion", style = wx.RB_GROUP )
        self.fitMethodBoson = wx.RadioButton(self.panel, label="Boson")
        self.fitMethodGaussian = wx.RadioButton(self.panel, label="Gaussian")
        
        ######################
        ## TEXT BUTTON ##
#        self.testButton = wx.Button(self.panel, label="test")
#        self.testButton.Bind(wx.EVT_BUTTON, self.test)
#        settingBoxSizer.Add(self.testButton)
        self.checkDisplayRadialAvg = wx.CheckBox(self.panel, label="Display radially averaged profile")
        self.Bind(wx.EVT_CHECKBOX, self.displayRadialAvg, id = self.checkDisplayRadialAvg.GetId())
        
        self.checkNormalization = wx.CheckBox(self.panel, label="Normalization (matching " + u"\u03BC" + " , " + u"\u03C3"+ " of atom shot && ref.)")
        self.Bind(wx.EVT_CHECKBOX, self.displayNormalization, id = self.checkNormalization.GetId())
        
        ######################
        
#        self.show2DContourButton = wx.Button(self.panel, label = "Show 2D contour fitting")
#        self.show2DContourButton.Bind(wx.EVT_BUTTON, self.show2DContour)
#        self.show2DContourButton.Disable()
        ######################
        
        self.fitMethodFermion.Disable()
#        self.fitMethodBoson.Disable()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.update1DProfilesAndFit, id = self.fitMethodFermion.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.update1DProfilesAndFit, id = self.fitMethodBoson.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.update1DProfilesAndFit, id = self.fitMethodGaussian.GetId())
        
        fermionOrBosonBoxSizer.Add(self.fitMethodFermion, flag=wx.ALL, border=5)
        fermionOrBosonBoxSizer.Add(self.fitMethodBoson, flag=wx.ALL, border=5)
        fermionOrBosonBoxSizer.Add(self.fitMethodGaussian, flag=wx.ALL, border=5)
        
        settingBoxSizer.Add(fermionOrBosonBoxSizer, flag=wx.ALL| wx.EXPAND, border = 5)
#        settingBoxSizer.Add(self.show2DContourButton, flag=wx.ALL| wx.EXPAND, border = 5)
        settingBoxSizer.Add(self.checkNormalization, flag = wx.ALL | wx.EXPAND, border = 5)
        settingBoxSizer.Add(self.checkDisplayRadialAvg, flag = wx.ALL | wx.EXPAND, border = 5)
        

        vbox0.Add(settingBoxSizer, 0, wx.ALL|wx.EXPAND,  5)
        ###############################
        fittingBox = wx.StaticBox(self.panel, label = 'Reading')
#        fittingBox.SetMaxSize((250, 400))
        fittingBoxSizer = wx.StaticBoxSizer(fittingBox,  wx.VERTICAL)

#        self.showImgButton = wx.Button(self.panel,  label = 'Read Image')
#        self.showImgButton.Bind(wx.EVT_BUTTON, self.fitImage)Fself.
#        fittingBoxSizer.Add(self.showImgButton, flag=wx.ALL|wx.EXPAND, border=5)

        
        self.autoButton = wx.Button(self.panel, label = 'Auto Read')
        self.autoButton.Bind(wx.EVT_BUTTON, self.startAutoRun)
        fittingBoxSizer.Add(self.autoButton, flag=wx.ALL|wx.EXPAND, border= 5)
                
        self.snippetPath = "C:\\shared_data\\AndorImg\\SnippetLookHereNa.txt"
        snippetText = wx.StaticText(self.panel, label='Text file path for Snippet Server:')
        self.snippetTextBox = wx.TextCtrl(self.panel, value = self.snippetPath)
        self.snippetTextBox.Bind(wx.EVT_TEXT, self.setSnippetPath)
        fittingBoxSizer.Add(snippetText, flag=wx.ALL | wx.EXPAND, border=5)
        fittingBoxSizer.Add(self.snippetTextBox, flag=wx.ALL | wx.EXPAND, border=5)
        
        listText = wx.StaticText(self.panel, label='Image List')
        self.imageListBox = wx.ListBox(self.panel, size = (265, 300))
        self.Bind(wx.EVT_LISTBOX, self.chooseImg, self.imageListBox)
        fittingBoxSizer.Add(listText, flag=wx.ALL, border=5)
        fittingBoxSizer.Add(self.imageListBox, 1, wx.ALL | wx.EXPAND, border=5)
        self.updateImageListBox()
        vbox0.Add(fittingBoxSizer, 0, wx.ALL|wx.EXPAND, 5)
        
       
        # TOF fitting
        TOFFitBox = wx.StaticBox(self.panel, label = 'TOF fitting')
        TOFFitBoxSizer = wx.StaticBoxSizer(TOFFitBox, wx.VERTICAL)
        
        self.TOFFitList = wx.TextCtrl(self.panel, value = str(-1), style = wx.TE_MULTILINE)
        TOFFitButton= wx.Button(self.panel, label = 'TOF fit')
        TOFFitButton.Bind(wx.EVT_BUTTON, self.showTOFFit)
        TOFFitBoxSizer.Add(self.TOFFitList, flag = wx.ALL|wx.EXPAND, border = 5)
        TOFFitBoxSizer.Add(TOFFitButton, flag = wx.ALL|wx.EXPAND, border = 5)
        vbox0.Add(TOFFitBoxSizer, 0, wx.ALL|wx.EXPAND, 5)
        
#        self.true_x_width_list = np.zeros(self.iamgeListBox.GetCount())
#        self.true_y_width_list = np.zeros(self.iamgeListBox.GetCount())
        ## update the imageListBox
        


        hbox.Add(vbox0, 2, wx.ALL|wx.EXPAND, 5)  # 2 here means that the relative width of the box will be 2

    
#         #Fitting result
        
        #fittingResult = wx.StaticBox(self.panel, label='Fitting Result')
        #fittingResultSizer = wx.StaticBoxSizer(fittingResult, wx.VERTICAL)

#        gaussResult = wx.StaticBox(self.panel, label='Gaussian Fit')
#        gaussResultBox = wx.StaticBoxSizer(gaussResult, wx.VERTICAL)
#
#        hbox121 = wx.BoxSizer(wx.HORIZONTAL)
#        st5 = wx.StaticText(self.panel, label='Center at')
#        self.gCenter = wx.TextCtrl(self.panel, value='', style=wx.TE_READONLY)
#        hbox121.Add(st5, flag=wx.ALL, border=5)
#        hbox121.Add(self.gCenter, flag=wx.ALL, border=0)
#
#        hbox122 = wx.BoxSizer(wx.HORIZONTAL)
#        st6 = wx.StaticText(self.panel, label='Sigma')
#        self.gSigma = wx.TextCtrl(self.panel, value='', style=wx.TE_READONLY)
#        hbox122.Add(st6, flag=wx.ALL, border=5)
#        hbox122.Add(self.gSigma, flag=wx.ALL, border=0)
#
#        hbox126 = wx.BoxSizer(wx.HORIZONTAL)
#        hbox131 = wx.BoxSizer(wx.HORIZONTAL)
#        hbox145 = wx.BoxSizer(wx.HORIZONTAL)
#        st7 = wx.StaticText(self.panel, label='Atom#')
#        st22 = wx.StaticText(self.panel, label='NormNcount')
#        st8 = wx.StaticText(self.panel, label='Atom#from fit')
#        self.atomNumberInt = wx.TextCtrl(self.panel, value='', style=wx.TE_READONLY)
#        self.atomNumberIntFit = wx.TextCtrl(self.panel, value='', style=wx.TE_READONLY)
#        self.normNcount = wx.TextCtrl(self.panel, value='', style=wx.TE_READONLY)
#        hbox126.Add(st7, flag=wx.LEFT | wx.TOP, border=5)
#        hbox126.Add(self.atomNumberInt, flag=wx.LEFT | wx.TOP, border=0)
#        hbox131.Add(st8, flag=wx.LEFT | wx.TOP, border=5)
#        hbox131.Add(self.atomNumberIntFit, flag=wx.LEFT | wx.TOP, border=0)
#        hbox145.Add(st22, flag=wx.LEFT | wx.TOP, border=5)
#        hbox145.Add(self.normNcount, flag=wx.LEFT | wx.TOP, border=0)
#
#        hbox130 = wx.BoxSizer(wx.HORIZONTAL)
#        st12 = wx.StaticText(self.panel, label='Temperature(nK)')
#        self.gTemperature = wx.TextCtrl(self.panel, value='', style=wx.TE_READONLY)
#        hbox130.Add(st12, flag=wx.ALL, border=5)
#        hbox130.Add(self.gTemperature, flag=wx.ALL, border=0)
#
#        gaussResultBox.Add(hbox121, flag=wx.ALL, border=5)
#        gaussResultBox.Add(hbox122, flag=wx.ALL, border=5)
#        gaussResultBox.Add(hbox126, flag=wx.ALL, border=5)
#        gaussResultBox.Add(hbox145, flag=wx.ALL, border=5)
#        gaussResultBox.Add(hbox131, flag=wx.ALL, border=5)
#        gaussResultBox.Add(hbox130, flag=wx.ALL, border=5)
#        fittingResultSizer.Add(gaussResultBox, flag=wx.ALL|wx.EXPAND, border=5)
##
#        self.fermionResult = wx.StaticBox(self.panel, label='Fermion Fit')
#        fermionResultBox = wx.StaticBoxSizer(self.fermionResult, wx.VERTICAL)
#
#        hbox127 = wx.BoxSizer(wx.HORIZONTAL)
#        self.fText1 = wx.StaticText(self.panel, label='Size')
#        self.fWidth = wx.TextCtrl(self.panel, value='', style=wx.TE_READONLY)
#        hbox128 = wx.BoxSizer(wx.HORIZONTAL)
#        self.fText2 = wx.StaticText(self.panel, label='Fugacity')
#        self.fq = wx.TextCtrl(self.panel, value='', style=wx.TE_READONLY)
#        hbox129 = wx.BoxSizer(wx.HORIZONTAL)
#        self.tOverTFLabel = wx.StaticText(self.panel, label='T/T_F')
#        self.tOverTF = wx.TextCtrl(self.panel, value='', style=wx.TE_READONLY)
#        # self.tOverTFLabelguess = wx.StaticText(self.panel, label='T/T_F from guess')
#        # self.tOverTFguess = wx.TextCtrl(self.panel, value='', style=wx.TE_READONLY)
#        hbox127.Add(self.fText1, flag=wx.LEFT | wx.TOP, border=5)
#        hbox127.Add(self.fWidth, flag=wx.LEFT | wx.TOP, border=5)
#        hbox128.Add(self.fText2, flag=wx.LEFT | wx.TOP, border=5)
#        hbox128.Add(self.fq, flag=wx.LEFT | wx.TOP, border=5)
#        hbox129.Add(self.tOverTFLabel, flag=wx.LEFT | wx.TOP, border=5)
#        hbox129.Add(self.tOverTF, flag=wx.LEFT | wx.TOP, border=5)
#        # hbox129.Add(self.tOverTFLabelguess, flag=wx.LEFT | wx.TOP, border=5)
#        # hbox129.Add(self.tOverTFguess, flag=wx.LEFT | wx.TOP, border=5)
#
#        fermionResultBox.Add(hbox127, flag=wx.LEFT | wx.TOP, border=5)
#        fermionResultBox.Add(hbox128, flag=wx.LEFT | wx.TOP, border=5)
#        fermionResultBox.Add(hbox129, flag=wx.LEFT | wx.TOP, border=5)
#        fittingResultSizer.Add(fermionResultBox, flag=wx.ALL|wx.EXPAND, border=5)

        # bosonResult = wx.StaticBox(fittingBox, label='Boson Fit')
        # bosonResultBox = wx.StaticBoxSizer(bosonResult, wx.VERTICAL)

        # hbox123 = wx.BoxSizer(wx.HORIZONTAL)
        # self.pText1 = wx.StaticText(fittingBox, label='Thermal Size')
        # self.pWidth1 = wx.TextCtrl(fittingBox, value='', style=wx.TE_READONLY)
        # hbox124 = wx.BoxSizer(wx.HORIZONTAL)
        # self.pText2 = wx.StaticText(fittingBox, label='Condensate Size')
        # self.pWidth2 = wx.TextCtrl(fittingBox, value='', style=wx.TE_READONLY)
        # hbox125 = wx.BoxSizer(wx.HORIZONTAL)
        # self.becFractionLabel = wx.StaticText(fittingBox, label='BEC Fraction')
        # self.becFraction = wx.TextCtrl(fittingBox, value='', style=wx.TE_READONLY)

        # hbox123.Add(self.pText1, flag=wx.LEFT | wx.TOP, border=5)
        # hbox123.Add(self.pWidth1, flag=wx.LEFT | wx.TOP, border=5)
        # hbox124.Add(self.pText2, flag=wx.LEFT | wx.TOP, border=5)
        # hbox124.Add(self.pWidth2, flag=wx.LEFT | wx.TOP, border=5)
        # hbox125.Add(self.becFractionLabel, flag=wx.LEFT | wx.TOP, border=5)
        # hbox125.Add(self.becFraction, flag=wx.LEFT | wx.TOP, border=5)
        # bosonResultBox.Add(hbox123, flag=wx.LEFT | wx.TOP, border=5)
        # bosonResultBox.Add(hbox124, flag=wx.LEFT | wx.TOP, border=5)
        # bosonResultBox.Add(hbox125, flag=wx.LEFT | wx.TOP, border=5)

        # fittingResultSizer.Add(bosonResultBox, flag=wx.ALL|wx.EXPAND, border=5)



        #fittingBoxSizer.Add(fittingResultSizer, flag=wx.ALL|wx.EXPAND, border=5)

#
#        dataBox = wx.StaticBox(self.panel, label='Save Data')
#        dataBoxSizer = wx.StaticBoxSizer(dataBox, wx.VERTICAL)
#
#
#        self.saveFermionButton = wx.Button(self.panel,  label = 'Save Above Results')
#        self.saveFermionButton.Bind(wx.EVT_BUTTON, self.saveResult)
#        cleanButton = wx.Button(self.panel,  label = 'Remove all saved data')
#        cleanButton.Disable()
#        cleanButton.Bind(wx.EVT_BUTTON, self.cleanData)
#
#        dataBoxSizer.Add(self.saveFermionButton, flag=wx.ALL|wx.EXPAND, border=5)
#        dataBoxSizer.Add(cleanButton, flag=wx.ALL|wx.EXPAND, border=5)
#
#        fittingBoxSizer.Add(dataBoxSizer, flag=wx.ALL|wx.EXPAND, border=5)
# 
######### images ##################
        
#        self.initImageUI()
        imagesBox = wx.StaticBox(self.panel, label='Images')
        imagesBoxSizer = wx.StaticBoxSizer(imagesBox, wx.VERTICAL)
        '''
        figure = Figure()
#        figure.tight_layout(h_pad=1.0)
        #gs = gridspec.GridSpec(5, 5)
        gs = gridspec.GridSpec(2, 2, width_ratios=(7, 2), height_ratios=(7, 2), wspace = 0.05, hspace = 0.05)
        #gs.update(wspace = 0.05, hspace = 0.05)
        #self.axes1 = figure.add_subplot(gs[:-1, :-1])
        self.axes1 = figure.add_subplot(gs[0, 0])
        self.axes1.set_title('Original Image', fontsize=12)

        for label in (self.axes1.get_xticklabels() + self.axes1.get_yticklabels()):
            label.set_fontsize(10)
            
        #self.axes2 = figure.add_subplot(gs[-1, 0:-1])
        self.axes2 = figure.add_subplot(gs[1, 0])
        self.axes2.grid(True)
        for label in (self.axes2.get_xticklabels() + self.axes2.get_yticklabels()):
            label.set_fontsize(10)

        #self.axes3 = figure.add_subplot(gs[:-1, -1])
        self.axes3 = figure.add_subplot(gs[0, 1])
        self.axes3.grid(True)
        for label in (self.axes3.get_xticklabels()):
            label.set_fontsize(10)
        
        for label in (self.axes3.get_yticklabels()):
            label.set_visible(False)
            
        self.canvas1 =  FigureCanvas(self.panel, -1, figure)
        self.canvas1.mpl_connect('button_press_event', self.on_press)
        self.canvas1.mpl_connect('button_release_event', self.on_release)
        self.canvas1.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas1.mpl_connect('motion_notify_event', self.showImgValue)
        imagesBoxSizer.Add(self.canvas1, flag=wx.ALL|wx.EXPAND, border=5)
        '''
        
        self.figure = Figure(figsize = (8,8))
#        figure.tight_layout(h_pad=1.0)
        #gs = gridspec.GridSpec(5, 5)
        gs = gridspec.GridSpec(2, 2, width_ratios=(7, 2), height_ratios=(7, 2), wspace = 0.05, hspace = 0.08)
        #gs.update(wspace = 0.05, hspace = 0.05)
        #self.axes1 = figure.add_subplot(gs[:-1, :-1])
        self.axes1 = self.figure.add_subplot(gs[0, 0])
        self.axes1.set_title('Original Image', fontsize=12)

        for label in (self.axes1.get_xticklabels() + self.axes1.get_yticklabels()):
            label.set_fontsize(10)
            
        #self.axes2 = figure.add_subplot(gs[-1, 0:-1])
        self.axes2 = self.figure.add_subplot(gs[1, 0])
        self.axes2.grid(True)
        for label in (self.axes2.get_xticklabels() + self.axes2.get_yticklabels()):
            label.set_fontsize(10)

        #self.axes3 = figure.add_subplot(gs[:-1, -1])
        self.axes3 = self.figure.add_subplot(gs[0, 1])
        self.axes3.grid(True)
        for label in (self.axes3.get_xticklabels()):
            label.set_fontsize(10)
        
        for label in (self.axes3.get_yticklabels()):
            label.set_visible(False)
            
        self.canvas = FigureCanvas(self.panel, -1, self.figure)
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('motion_notify_event', self.showImgValue)
        imagesBoxSizer.Add(self.canvas, flag=wx.ALL|wx.EXPAND, border=5)
        
        # self.canvas_Secondary =  FigureCanvas(self.panel, -1, self.figure)
        # self.canvas_Secondary.mpl_connect('button_press_event', self.on_press_Secondary)
        # self.canvas_Secondary.mpl_connect('button_release_event', self.on_release)
        # self.canvas_Secondary.mpl_connect('motion_notify_event', self.on_motion_Secondary)
        # self.canvas_Secondary.mpl_connect('motion_notify_event', self.showImgValue)
        # imagesBoxSizer.Add(self.canvas_Secondary, flag=wx.ALL|wx.EXPAND, border=5)
        
#        imagesBox1 = wx.StaticBox(self.panel)
#        imagesBoxSizer = wx.StaticBoxSizer(imagesBox1, wx.VERTICAL)
#        figure2 = Figure()
#        self.axes2 = figure.add_subplot(111)
#        for label in (self.axes2.get_xticklabels() + self.axes2.get_yticklabels()):
#            label.set_fontsize(5)
#        self.canvas2 = FigureCanvas(self.panel, -1, figure2)
#        imagesBoxSizer.Add(self.canvas2, flag=wx.ALL|wx.EXPAND, border=5)
        

        self.press= None

# 4 layer radio buttons

        hbox41 = wx.BoxSizer(wx.HORIZONTAL)
        self.layer1Button = wx.RadioButton(self.panel, label="Probe With Atoms", style = wx.RB_GROUP )
        self.layer2Button = wx.RadioButton(self.panel, label="Probe Without Atoms")
        self.layer3Button = wx.RadioButton(self.panel, label="Dark Field")
        self.layer4Button = wx.RadioButton(self.panel, label="Absorption Image")
        hasFileSizeChanged = False
        self.Bind(wx.EVT_RADIOBUTTON, lambda e: self.updateImageOnUI(1, hasFileSizeChanged), id=self.layer1Button.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, lambda e: self.updateImageOnUI(2, hasFileSizeChanged), id=self.layer2Button.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, lambda e: self.updateImageOnUI(3, hasFileSizeChanged), id=self.layer3Button.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, lambda e: self.updateImageOnUI(4, hasFileSizeChanged), id=self.layer4Button.GetId())
        # default setting
        self.layer4Button.SetValue(True)
        self.chosenLayerNumber = 4

        hbox41.Add(self.layer1Button, flag=wx.ALL, border=5)
        hbox41.Add(self.layer2Button, flag=wx.ALL, border=5)
        hbox41.Add(self.layer3Button, flag=wx.ALL, border=5)
        hbox41.Add(self.layer4Button, flag=wx.ALL, border=5)

        imagesBoxSizer.Add(hbox41,flag= wx.CENTER, border=5)

# 4 layer radio buttons

        hbox421 = rcs.RowColSizer()
        hbox42 = wx.BoxSizer(wx.HORIZONTAL)
        boldFont = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        st17 = wx.StaticText(self.panel, label='X:')
        self.cursorX = wx.TextCtrl(self.panel,  style=wx.TE_READONLY|wx.TE_CENTRE, size = (50, 22))
        st18 = wx.StaticText(self.panel, label='Y:')
        self.cursorY = wx.TextCtrl(self.panel, style=wx.TE_READONLY|wx.TE_CENTRE,  size = (50, 22))
        st19 = wx.StaticText(self.panel, label='Value:')
        self.cursorZ = wx.TextCtrl(self.panel, style=wx.TE_READONLY|wx.TE_CENTRE,  size = (80, 22))
        hbox42.Add(st17, flag=wx.ALL, border=5)
        hbox42.Add(self.cursorX, flag=wx.ALL, border=5)
        hbox42.Add(st18, flag=wx.ALL, border=5)
        hbox42.Add(self.cursorY, flag=wx.ALL, border=5)
        hbox42.Add(st19, flag=wx.ALL, border=5)
        hbox42.Add(self.cursorZ, flag=wx.ALL, border=5)
#        hbox42.Add(st17, flag=wx.ALL, row=5, col=5)
#        hbox42.Add(self.cursorX, flag=wx.ALL, row=5, col=5)
#        hbox42.Add(st18, flag=wx.ALL, row=5, col=5)
#        hbox42.Add(self.cursorY, flag=wx.ALL, row=5, col=5)
#        hbox42.Add(st19, flag=wx.ALL, row=5, col=5)
#        hbox42.Add(self.cursorZ, flag=wx.ALL, border=5)
        
        self.cursorX.SetFont(boldFont)
        self.cursorY.SetFont(boldFont)
        self.cursorZ.SetFont(boldFont)
        
        #########
        ## defringing option ##
        hbox43 = wx.BoxSizer(wx.HORIZONTAL)
        defringingBox = wx.StaticBox(self.panel)
        defringingBoxSizer = wx.StaticBoxSizer(defringingBox, wx.HORIZONTAL)
        
        self.checkApplyDefringing = wx.CheckBox(self.panel, label = "Apply defringing")
        self.checkResetAOI = wx.CheckBox(self.panel, label = "Reset AOI")
        self.checkMedianFilter = wx.CheckBox(self.panel, label = "Median filter")
#        self.checkSaveAsRef = wx.CheckBox(self.panel, label = "Save as ref")
        
        self.Bind(wx.EVT_CHECKBOX, lambda e: self.applyDefringing(), id = self.checkApplyDefringing.GetId())
        self.checkResetAOI.Enable(False)
        self.Bind(wx.EVT_CHECKBOX, lambda e: self.applyFilter(), id = self.checkMedianFilter.GetId())

        defringingBoxSizer.Add(self.checkApplyDefringing, flag = wx.ALL, border = 5)
        defringingBoxSizer.Add(self.checkResetAOI, flag = wx.ALL, border = 5)
        defringingBoxSizer.Add(self.checkMedianFilter, flag = wx.ALL, border = 5)
        
        hbox421.Add(hbox42,  flag= wx.ALL, border = 8, row=0, col=0)
        hbox421.Add(defringingBoxSizer, flag = wx.ALL, row = 0 , col = 1)

#        defringingBoxSizer.Add(self.checkSaveAsRef, flag = wx.ALL, border = 5)
        
#        hbox43.Add(self.checkApplyDefrinfing, flag = wx.ALL, border = 5)
#        hbox43.Add(self.checkSaveAsRef, flag = wx.ALL, border = 5)
#        hbox43.Add(self.checkResetAOI, flag = wx.ALL, border = 5)
#        imagesBoxSizer.Add(defringingBoxSizer, flag = wx.ALL|wx.EXPAND, border = 5)
        ########
      
        imagesBoxSizer.Add(hbox421,flag= wx.CENTER, border=5)
#        imagesBoxSizer.Add(defringingBoxSizer,flag= wx.CENTER, border=5)
      
        rotationBox = wx.StaticBox(self.panel)
        rotationBoxSizer = wx.StaticBoxSizer(rotationBox, wx.HORIZONTAL)
        
        angle = wx.StaticText(self.panel, label = "Image angle (" + u"\u00b0" + "):")
        self.angleBox = wx.TextCtrl(self.panel, value = str(self.imageAngle), size = (40, 22))
        pivot = wx.StaticText(self.panel, label = "Rotation pivot index (x, y):")
        self.pivotXBox = wx.TextCtrl(self.panel, value = str(self.imagePivotX), size = (40, 22))
        self.pivotYBox = wx.TextCtrl(self.panel, value = str(self.imagePivotY), size = (40, 22))
        arrorText = wx.StaticText(self.panel, label = u"\u27A4" + u"\u27A4")
        self.rotationButton= wx.Button(self.panel, label ="Set angle && pivot")

        self.angleBox.Bind(wx.EVT_TEXT, self.setImageAngle)
        self.pivotXBox.Bind(wx.EVT_TEXT, self.setImagePivotX)
        self.pivotYBox.Bind(wx.EVT_TEXT, self.setImagePivotY)
        self.rotationButton.Bind(wx.EVT_BUTTON, self.setImageRotationParams)
        
        rotationBoxSizer.Add(angle, flag = wx.ALL, border = 5)
        rotationBoxSizer.Add(self.angleBox, flag = wx.ALL, border = 5)
        rotationBoxSizer.Add(pivot, flag = wx.ALL, border = 5)
        rotationBoxSizer.Add(self.pivotXBox, flag = wx.ALL, border = 5)
        rotationBoxSizer.Add(self.pivotYBox, flag = wx.ALL, border = 5)
        rotationBoxSizer.Add(arrorText, flag = wx.ALL, border = 10)
        rotationBoxSizer.Add(self.rotationButton, flag = wx.ALL, border = 2)
     
        ##
        atomNum = wx.StaticBox(self.panel, label='# of Atoms')
        atomNumBoxSizer = wx.StaticBoxSizer(atomNum, wx.VERTICAL)
        
        ##
        hbox43 = wx.BoxSizer(wx.HORIZONTAL)
#        atomNumParam = wx.StaticBox(self.panel)
#        atomNumParamBoxSizer = wx.StaticBoxSizer(atomNumParam, wx.HORIZONTAL)
#
        magnif = wx.StaticText(self.panel, label = 'Mag:')
        self.magnif = wx.TextCtrl(self.panel, value= str(self.magnification), size=(30,22))
        self.magnif.Bind(wx.EVT_TEXT, self.setMagnification)
        
        pixelSize= wx.StaticText(self.panel, label = u"\u00B5"+"m/pix:")
        self.pxSize = wx.TextCtrl(self.panel, value= str(self.pixelSize), size=(35,22))
        self.pxSize.Bind(wx.EVT_TEXT, self.setPixelSize)
        
        atomKind = ['Dy']       # Old thing from BEC 3, we could delete this selection, it used to be ['Na, 'Li']
        self.atomRadioBox = wx.RadioBox(self.panel, choices = atomKind, majorDimension = 1)
        self.atomRadioBox.Bind(wx.EVT_RADIOBOX, self.onAtomRadioClicked)
        
        hbox43.Add(self.atomRadioBox, flag = wx.ALL, border = 5)
        hbox43.Add(magnif, flag = wx.ALL, border = 5)
        hbox43.Add(self.magnif, flag = wx.ALL, border = 5)
        hbox43.Add(pixelSize, flag = wx.ALL, border = 5)
        hbox43.Add(self.pxSize, flag = wx.ALL, border = 5)
        
        atomNumBoxSizer.Add(hbox43, flag=wx.ALL|wx.EXPAND)

        ##
        hbox44 = wx.BoxSizer(wx.HORIZONTAL)
        atomNumDisplay = wx.StaticBox(self.panel)
        atomNumDisplayBoxSizer = wx.StaticBoxSizer(atomNumDisplay, wx.HORIZONTAL)

#        bigNcountText = wx.StaticText(self.panel, label='NormNcount:')
#        self.bigNcount = wx.TextCtrl(self.panel,  style=wx.TE_READONLY)
        bigfont = wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        bigNcountText2 = wx.StaticText(self.panel, label='Norm Ncount: \n (pure integral)')
        self.bigNcount2 = wx.TextCtrl(self.panel,  style=wx.TE_READONLY|wx.TE_CENTRE, size=(100,34))
        bigNcountText3 = wx.StaticText(self.panel, label='Atom #\n(million):')
        self.bigNcount3 = wx.TextCtrl(self.panel, style=wx.TE_READONLY|wx.TE_CENTRE, size=(92,34))
#        self.bigNcount.SetFont(bigfont)
        self.bigNcount2.SetFont(bigfont)
        self.bigNcount3.SetFont(bigfont)
#        hbox44.Add(bigNcountText, flag=wx.ALL, border=5)
#        hbox44.Add(self.bigNcount, flag=wx.ALL, border=5)
        hbox43.Add(bigNcountText2, flag=wx.ALL, border=5)
        hbox43.Add(self.bigNcount2, flag=wx.ALL, border=5)
        hbox43.Add(bigNcountText3, flag=wx.ALL, border=5)
        hbox43.Add(self.bigNcount3, flag=wx.ALL, border=5)

#        atomNumDisplayBoxSizer.Add(hbox44, flag=wx.ALL|wx.EXPAND)
        
        ##
#        atomNumBoxSizer.Add(atomNumParamBoxSizer, flag=wx.ALL|wx.EXPAND, border=5)
#        atomNumBoxSizer.Add(atomNumDisplayBoxSizer, flag=wx.ALL|wx.EXPAND, border=5)
        imagesBoxSizer.Add(atomNumBoxSizer, flag=wx.ALL| wx.EXPAND, border=5)
        
        ### PRIMARY AOI
        
        aoi_Box = wx.StaticBox(self.panel)
        hbox14_Primary = wx.BoxSizer(wx.HORIZONTAL)
        aoi_BoxSizer = wx.StaticBoxSizer(aoi_Box, wx.HORIZONTAL)
        aoi_PrimaryText = wx.StaticText(self.panel, label = 'Primary (blue) AOI: (x,y)->(x,y)')
        hbox14_Primary.Add(aoi_PrimaryText, flag=wx.ALL, border=5)

        self.AOI1_Primary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
        self.AOI2_Primary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
        self.AOI3_Primary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
        self.AOI4_Primary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
        hbox14_Primary.Add(self.AOI1_Primary, flag=wx.ALL, border=2)
        hbox14_Primary.Add(self.AOI2_Primary, flag=wx.ALL, border=2)
        hbox14_Primary.Add(self.AOI3_Primary, flag=wx.ALL, border=2)
        hbox14_Primary.Add(self.AOI4_Primary, flag=wx.ALL, border=2)
        aoi_BoxSizer.Add(hbox14_Primary, flag=wx.EXPAND|wx.ALL, border=5)
        
        # For calculating the edge offset in calculating atom number
        # hbox43_Primary = wx.BoxSizer(wx.HORIZONTAL)
        # self.leftRightEdge_Primary = wx.CheckBox(self.panel, label="Use Left/Right")
        # self.updownEdge_Primary = wx.CheckBox(self.panel, label="Use Top/Bottom")
        # self.Bind(wx.EVT_CHECKBOX, self.edgeUpdate_Primary, id = self.leftRightEdge_Primary.GetId())
        # self.Bind(wx.EVT_CHECKBOX, self.edgeUpdate_Primary, id = self.updownEdge_Primary.GetId())
        # hbox43_Primary.Add(self.leftRightEdge_Primary, flag=wx.ALL, border=5)
        # hbox43_Primary.Add(self.updownEdge_Primary, flag=wx.ALL, border=5)
        # self.leftRightEdge_Primary.SetValue(True)
        # self.updownEdge_Primary.SetValue(True)
        # #self.edgeUpdateButton = wx.Button(self.panel, label="Update")
        # #hbox43.Add(self.edgeUpdateButton, flag=wx.ALL, border=5)
        # #self.edgeUpdateButton.Bind(wx.EVT_BUTTON, self.edgeUpdate)
        # aoi_PrimaryBoxSizer.Add(hbox43_Primary,flag=wx.ALL|wx.EXPAND)
        

        ### SECONDARY AOI
        
        #aoi_SecondaryBox = wx.StaticBox(self.panel)
        hbox14_Secondary = wx.BoxSizer(wx.HORIZONTAL)
        #aoi_SecondaryBoxSizer = wx.StaticBoxSizer(aoi_Box, wx.HORIZONTAL)
        aoi_SecondaryText = wx.StaticText(self.panel, label = 'Secondary (color) AOI: (x,y)->(x,y)')
        hbox14_Secondary.Add(aoi_SecondaryText, flag=wx.ALL, border=5)

        self.AOI1_Secondary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
        self.AOI2_Secondary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
        self.AOI3_Secondary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
        self.AOI4_Secondary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
        hbox14_Secondary.Add(self.AOI1_Secondary, flag=wx.ALL, border=2)
        hbox14_Secondary.Add(self.AOI2_Secondary, flag=wx.ALL, border=2)
        hbox14_Secondary.Add(self.AOI3_Secondary, flag=wx.ALL, border=2)
        hbox14_Secondary.Add(self.AOI4_Secondary, flag=wx.ALL, border=2)
        aoi_BoxSizer.Add(hbox14_Secondary, flag=wx.EXPAND|wx.ALL, border=5)
        
        hbox43_Secondary = wx.BoxSizer(wx.HORIZONTAL)
#        self.leftRightEdge_Secondary = wx.CheckBox(self.panel, label="Use Left/Right")
#        self.updownEdge_Secondary = wx.CheckBox(self.panel, label="Use Top/Bottom")
#        self.Bind(wx.EVT_CHECKBOX, self.edgeUpdate_Secondary, id = self.leftRightEdge_Secondary.GetId())
#        self.Bind(wx.EVT_CHECKBOX, self.edgeUpdate_Secondary, id = self.updownEdge_Secondary.GetId())
#        hbox43_Secondary.Add(self.leftRightEdge_Secondary, flag=wx.ALL, border=5)
#        hbox43_Secondary.Add(self.updownEdge_Secondary, flag=wx.ALL, border=5)
#        self.leftRightEdge_Secondary.SetValue(True)
#        self.updownEdge_Secondary.SetValue(True)
        #self.edgeUpdateButton = wx.Button(self.panel, label="Update")
        #hbox43.Add(self.edgeUpdateButton, flag=wx.ALL, border=5)
        #self.edgeUpdateButton.Bind(wx.EVT_BUTTON, self.edgeUpdate)
        aoi_BoxSizer.Add(hbox43_Secondary,flag=wx.ALL|wx.EXPAND)

        imagesBoxSizer.Add(aoi_BoxSizer, flag=wx.ALL| wx.EXPAND, border= 5)
        #imagesBoxSizer.Add(aoi_SecondaryBoxSizer, flag=wx.ALL| wx.EXPAND, border= 5)
        imagesBoxSizer.Add(rotationBoxSizer, flag = wx.ALL | wx.EXPAND, border = 5)
        
        
        
                
        #####################
        #### fiting part ####
        #####################
        fittingResultDisplay = wx.StaticBox(self.panel, label = "Fitting results")
        fittingResultDisplaySizer = wx.StaticBoxSizer(fittingResultDisplay, wx.VERTICAL)
        
#        widthPeakStaticBox = wx.StaticBox(self.panel)
#        widthPeakSizer = wx.StaticBoxSizer(widthPeakStaticBox, wx.HORIZONTAL)
#
#        paramStaticBox = wx.StaticBox(self.panel)
#        parameterSettingSizer = wx.StaticBoxSizer(paramStaticBox, wx.HORIZONTAL)
#        tempStaticBox = wx.StaticBox(self.panel)
#        tempSizer = wx.StaticBoxSizer(tempStaticBox, wx.HORIZONTAL)
                
        TOFText = wx.StaticText(self.panel, label = 'TOF (ms): ' )
        self.TOFBox = wx.TextCtrl(self.panel, value = str(self.TOF), size=(40,22))
        self.TOFBox.Bind(wx.EVT_TEXT, self.setTOF)
        
        xTrapFreqText = wx.StaticText(self.panel, label = 'X trap freq.(Hz): ')
        self.xTrapFreqBox = wx.TextCtrl(self.panel, value = str(self.xTrapFreq), size=(40,22))
        self.xTrapFreqBox.Bind(wx.EVT_TEXT, self.setXTrapFreq)
        
        yTrapFreqText = wx.StaticText(self.panel, label = 'Y trap freq.(Hz): ')
        self.yTrapFreqBox = wx.TextCtrl(self.panel, value = str(self.yTrapFreq), size=(40,22))
        self.yTrapFreqBox.Bind(wx.EVT_TEXT, self.setYTrapFreq)

        widthText = wx.StaticText(self.panel, label = "Width (" + u"\u00B5"+ "m):")
        self.widthBox = wx.TextCtrl(self.panel,value = str(1)+",  " + str(1) , style=wx.TE_READONLY|wx.TE_CENTRE, size = (90, 22))
        peakText = wx.StaticText(self.panel, label = 'Peak (arb.): ')
        self.peakBox = wx.TextCtrl(self.panel,value = str(1)+",  " +str(1), style=wx.TE_READONLY|wx.TE_CENTRE, size = (85, 22))
        
        TcText = wx.StaticText(self.panel, label = "(T/Tc, Nc/N) :")
#        self.TcBox = wx.TextCtrl(self.panel,value = str(1)+",  " +str(1), style=wx.TE_READONLY|wx.TE_CENTRE, size = (90, 22))
        self.TcBox = wx.TextCtrl(self.panel,value = str(1)+",  " +str(0), style=wx.TE_READONLY|wx.TE_CENTRE, size = (75, 22))
        TFRadiusText = wx.StaticText(self.panel, label = "TF rad. (" + u"\u00B5"+ "m):")
#        self.TFRadiusBox = wx.TextCtrl(self.panel,value = str(1)+",  " +str(1), style=wx.TE_READONLY|wx.TE_CENTRE, size = (90, 22))
        self.TFRadiusBox = wx.TextCtrl(self.panel,value = str(1), style=wx.TE_READONLY|wx.TE_CENTRE, size = (55, 22))
        
        TempText = wx.StaticText(self.panel, label = "Temperature (" + u"\u00B5"+"K): ")
        TempText2 = wx.StaticText(self.panel, label = "long time limit (" +u"\u00B5" + "K): ")
        self.tempBox = wx.TextCtrl(self.panel, value = "(" + str(self.temperature[0])+", " +str(self.temperature[1]) + ")", style=wx.TE_READONLY|wx.TE_CENTRE, size = (160, 35))
        self.tempBox2 = wx.TextCtrl(self.panel, value = "(" + str(self.temperature[0])+", " +str(self.temperature[1]) + ")", style=wx.TE_READONLY|wx.TE_CENTRE, size = (160, 35))
        bigfont2 = wx.Font(14, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        self.tempBox.SetFont(bigfont2)
        self.tempBox2.SetFont(bigfont2)
        
        hbox45 = wx.BoxSizer(wx.HORIZONTAL)
        hbox45.Add(widthText, flag = wx.ALL, border = 5)
        hbox45.Add(self.widthBox, flag = wx.ALL, border = 5)
        hbox45.Add(peakText, flag = wx.ALL, border = 5)
        hbox45.Add(self.peakBox, flag = wx.ALL, border = 5)
        hbox45.Add(TcText, flag = wx.ALL, border = 5)
        hbox45.Add(self.TcBox, flag = wx.ALL, border = 5)
        hbox45.Add(TFRadiusText, flag = wx.ALL, border = 5)
        hbox45.Add(self.TFRadiusBox, flag = wx.ALL, border = 5)
                        
        hbox455 = wx.BoxSizer(wx.HORIZONTAL)
        hbox455.Add(TOFText, flag = wx.ALL, border = 5)
        hbox455.Add(self.TOFBox, flag = wx.ALL, border = 5)
        hbox455.Add(xTrapFreqText, flag = wx.ALL, border = 5)
        hbox455.Add(self.xTrapFreqBox, flag = wx.ALL, border = 5)
        hbox455.Add(yTrapFreqText, flag = wx.ALL, border = 5)
        hbox455.Add(self.yTrapFreqBox, flag = wx.ALL, border = 5)
        
        hbox46 = wx.BoxSizer(wx.HORIZONTAL)
        hbox46.Add(TempText, flag = wx.ALL, border = 5)
        hbox46.Add(self.tempBox, flag = wx.ALL, border = 5)
        hbox46.Add(TempText2, flag = wx.ALL, border = 5)
        hbox46.Add(self.tempBox2, flag = wx.ALL, border = 5)
        
#        widthPeakSizer.Add(hbox45,  flag=wx.ALL|wx.EXPAND, border = 5)
#        parameterSettingSizer.Add(hbox455, flag=wx.ALL|wx.EXPAND, border = 5)
#        tempSizer.Add(hbox46, flag=wx.ALL|wx.EXPAND, border = 5)
        
        fittingResultDisplaySizer.Add(hbox45, flag=wx.ALL| wx.EXPAND, border=5)
        fittingResultDisplaySizer.Add(hbox455, flag=wx.ALL| wx.EXPAND, border=5)
        fittingResultDisplaySizer.Add(hbox46, flag=wx.ALL| wx.EXPAND, border=5)
        imagesBoxSizer.Add(fittingResultDisplaySizer, flag=wx.ALL| wx.EXPAND, border=5)
        ## final step to add everything
        hbox.Add(imagesBoxSizer, 4, wx.ALL|wx.EXPAND)




        vbox2 = wx.BoxSizer(wx.VERTICAL)    # this is the file vertical box
        
        fileBox = wx.StaticBox(self.panel, label = "File")
        fileBoxSizer = wx.StaticBoxSizer(fileBox, wx.VERTICAL)

        # ## file Type
        # aiaOrTifBox = wx.StaticBox(self.panel, label = 'File Type')
        # aiaOrTifBoxSizer = wx.StaticBoxSizer(aiaOrTifBox, wx.HORIZONTAL)
        # self.aiaFile = wx.RadioButton(self.panel, label="aia", style = wx.RB_GROUP )
        # self.tifFile = wx.RadioButton(self.panel, label="tif")
        # self.fitsFile = wx.RadioButton(self.panel, label="fits")
        # self.dbFile = wx.RadioButton(self.panel, label="dbFile")
        
        # aiaOrTifBoxSizer.Add(self.aiaFile, flag=wx.ALL, border=5)
        # aiaOrTifBoxSizer.Add(self.tifFile, flag=wx.ALL, border=5)
        # aiaOrTifBoxSizer.Add(self.fitsFile,flag=wx.ALL, border=5)
        # aiaOrTifBoxSizer.Add(self.dbFile, flag=wx.ALL, border=5)
        
        # self.Bind(wx.EVT_RADIOBUTTON, self.setFileType, self.aiaFile)
        # self.Bind(wx.EVT_RADIOBUTTON, self.setFileType, self.tifFile)
        # self.Bind(wx.EVT_RADIOBUTTON, self.setFileType, self.fitsFile)
        # self.Bind(wx.EVT_RADIOBUTTON, self.setFileType, self.dbFile)
        
        # fileBoxSizer.Add(aiaOrTifBoxSizer, flag=wx.ALL| wx.EXPAND, border = 5)

        ## file Size
        fileSizeUnit = wx.StaticText(self.panel, label = 'MB')
        fileSize = wx.StaticText(self.panel, label = 'File Size')
        self.fileSizeValue = wx.TextCtrl(self.panel, value= "31.6")
        self.fileSizeValue.Bind(wx.EVT_TEXT, self.setFileSize)
        
#        fileSizeBox = wx.StaticBox(self.panel)
        fileSizeBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        fileSizeBoxSizer.Add(fileSize, flag=wx.ALL, border=5)
        fileSizeBoxSizer.Add(self.fileSizeValue, flag=wx.ALL, border=5)
        fileSizeBoxSizer.Add(fileSizeUnit, flag=wx.ALL, border=5)
        
        fileBoxSizer.Add(fileSizeBoxSizer,  flag=wx.ALL| wx.EXPAND, border = 5)
        
        
        ## Database file info
        fileInfoDisplayText = wx.StaticText(self.panel,label='Currently displayed file informations')
        fileBoxSizer.Add(fileInfoDisplayText, flag=wx.ALL|wx.EXPAND, border=5)
        
        fileInfoImageIDText = wx.StaticText(self.panel, label = "imageID:")
        self.fileInfoImageIDBox = wx.TextCtrl(self.panel, value = "  ", style=wx.TE_READONLY|wx.TE_CENTRE, size = (50, 22))
        fileInfoTimestampText = wx.StaticText(self.panel, label = 'Timestamp:')
        self.fileInfoTimestampBox = wx.TextCtrl(self.panel,value = "  ", style=wx.TE_READONLY|wx.TE_CENTRE, size = (140, 22))
        fileInfoNCountText = wx.StaticText(self.panel, label = 'nCount:')
        self.fileInfoNCountBox = wx.TextCtrl(self.panel,value = "  ", style=wx.TE_READONLY|wx.TE_CENTRE, size = (140, 22))
        vbox11 = wx.BoxSizer(wx.VERTICAL)
        hbox151 = wx.BoxSizer(wx.HORIZONTAL)
        hbox151.Add(fileInfoImageIDText, flag = wx.ALL, border = 5)
        hbox151.Add(self.fileInfoImageIDBox, flag = wx.ALL, border = 5)
        hbox152 = wx.BoxSizer(wx.HORIZONTAL)
        hbox152.Add(fileInfoTimestampText, flag = wx.ALL, border = 5)
        hbox152.Add(self.fileInfoTimestampBox, flag = wx.ALL, border = 5)
        hbox153 = wx.BoxSizer(wx.HORIZONTAL)
        hbox153.Add(fileInfoNCountText, flag = wx.ALL, border = 5)
        hbox153.Add(self.fileInfoNCountBox, flag = wx.ALL, border = 5)
        vbox11.Add(hbox151, 0, wx.ALL|wx.EXPAND, 5)
        vbox11.Add(hbox152, 0, wx.ALL|wx.EXPAND, 5)
        vbox11.Add(hbox153, 0, wx.ALL|wx.EXPAND, 5)
        
        
        # self.infoDBGrid = wx.GridSizer(2,4,5,20)
        # fileInfoImageIDText2 = wx.StaticText(self.panel, label = "imageID:")
        # self.fileInfoImageIDBox2 = wx.TextCtrl(self.panel, value = "  ", style=wx.TE_READONLY|wx.TE_CENTRE, size = (50, 22))
        # # fileInfoTimestampText2 = wx.StaticText(self.panel, label = 'Timestamp:')
        # # self.fileInfoTimestampBox2 = wx.TextCtrl(self.panel,value = "  ", style=wx.TE_READONLY|wx.TE_CENTRE, size = (140, 22))
        # # fileInfoNCountText2 = wx.StaticText(self.panel, label = 'nCount:')
        # # self.fileInfoNCountBox2 = wx.TextCtrl(self.panel,value = "  ", style=wx.TE_READONLY|wx.TE_CENTRE, size = (140, 22))
        # self.infoDBGrid.Add(fileInfoImageIDText2)
        # self.infoDBGrid.Add(self.fileInfoImageIDBox2)
        # vbox11.Add(self.infoDBGrid, flag=wx.ALL| wx.EXPAND, border=0)
        
        #SpeciesTableSizer = wx.BoxSizer(wx.HORIZONTAL)
        infoDBGrid = wx.grid.Grid(self.panel, -1, size=(300,150))
        infoDBGrid.CreateGrid(5,2)
        infoDBGrid.SetColLabelValue(0, 'Variable')
        infoDBGrid.SetColLabelValue(1, 'DB Value')
        for i in range(5):
            infoDBGrid.SetReadOnly(i,0,True)
            infoDBGrid.SetReadOnly(i,1,True)
        infoDBGrid.SetCellValue(0,0,"imageID")
        infoDBGrid.SetCellValue(1,0,"runID")
        infoDBGrid.SetCellValue(2,0,"sequenceID")
        infoDBGrid.SetCellValue(3,0,"Timestamp")
        infoDBGrid.SetCellValue(4,0,"nCount")
        #self.fileInfoNCountBox = wx.TextCtrl(self.panel,value = "  ", style=wx.TE_READONLY|wx.TE_CENTRE, size = (140, 22))
        #infoDBGrid.SetCellValue(4,1,self.fileInfoNCountBox.Value())
        
        #infoDBGrid.SetColLabelValue(2, 'Local Value')
        infoDBGrid.SetRowLabelSize(0)
        vbox11.Add(infoDBGrid, wx.ALIGN_CENTER | wx.ALL,0 )
	
        fileBoxSizer.Add(vbox11, flag=wx.ALL| wx.EXPAND, border=0)

        
        hbox154 = wx.BoxSizer(wx.HORIZONTAL)
        self.updateAnalysisButton = wx.Button(self.panel, label = 'Update analysis')
        self.updateAnalysisButton.Bind(wx.EVT_BUTTON, self.updateAnalysisDB)
        hbox154.Add(self.updateAnalysisButton, flag=wx.ALL, border=5)
        fileBoxSizer.Add(hbox154, flag=wx.ALL| wx.EXPAND, border=0)
        
        ## image file path
        pathText = wx.StaticText(self.panel,label='Image Folder Path')
        fileBoxSizer.Add(pathText, flag=wx.ALL|wx.EXPAND, border=5)
        
    #     if self.checkLocalFiles:
    #         localPath = LOCAL_PATH
    #         ### WINDOWS VERSION ####
    #         if (LOCAL_PATH[-2:] != "\\"):
    #             localPath = LOCAL_PATH + "\\"
    #         ### MAC VERSION ###
    # #        if (LOCAL_PATH[-1:] != "/"):
    # #            localPath = LOCAL_PATH + "/"
    #         self.today = datetime.date.today()
    #         self.path = localPath + str(self.today.year) + "\\" + str(self.today.month) + "\\" + str(self.today.day) + "\\"
    # #        self.path = localPath + str(self.today.year) + "/" + str(self.today.month) + "/" + str(self.today.day) + "/"
    # #        self.path = "D:\\Dropbox (MIT)\\BEC3-CODE\\imageAnalyze\\working branch\\fitting test\\thermal\\"
    #         if not os.path.exists(self.path):
    #             try:
    #                 os.makedirs(self.path)
    #             except:
    #                 self.path = "/Users/pierre/lsls"
        if not self.checkLocalFiles:
            self.today = datetime.date.today()
            self.path = str(getLastImageID())
#        self.setDefringingRefPath()
                        
        self.imageFolderPath = wx.TextCtrl(self.panel, value = self.path)
          
        hbox13 = wx.BoxSizer(wx.HORIZONTAL)
        hbox13.Add(self.imageFolderPath, 1, flag=wx.ALL| wx.EXPAND , border=5)
        self.choosePathButton = wx.Button(self.panel, label = 'Choose Path')
        self.choosePathButton.Bind(wx.EVT_BUTTON, self.choosePath)
        hbox13.Add(self.choosePathButton, flag=wx.ALL, border=5)
        fileBoxSizer.Add(hbox13, flag=wx.ALL| wx.EXPAND, border=0)

        nameText = wx.StaticText(self.panel, label='Image File Name')
        fileBoxSizer.Add(nameText, flag=wx.ALL, border=5)

        hbox12 = wx.BoxSizer(wx.HORIZONTAL)
        self.imageIDText = wx.TextCtrl(self.panel)
        hbox12.Add(self.imageIDText, 1, flag=wx.ALL| wx.EXPAND , border=5)
        self.chooseFileButton = wx.Button(self.panel, label = 'Choose File')
        self.chooseFileButton.Bind(wx.EVT_BUTTON, self.chooseFile)
        hbox12.Add(self.chooseFileButton, flag=wx.ALL, border=5)
        fileBoxSizer.Add(hbox12,flag=wx.ALL| wx.EXPAND, border=0)

        vbox2.Add(fileBoxSizer,flag=wx.ALL| wx.EXPAND, border = 5)
        hbox.Add(vbox2, 2, wx.ALL|wx.EXPAND, 5)  # 2 here means that the relative width of the box will be 2





#        self.testFrame = None
######### images ##################
        
#        imagesBox2 = wx.StaticBox(self.panel, label='Images')
#        imagesBoxSizer2 = wx.StaticBoxSizer(imagesBox2, wx.VERTICAL)
#
#
#        figure = Figure()
#        self.axes2 = figure.add_subplot(211)
#        self.axes2.set_title('Gaussian', fontsize=10)
#        for label in (self.axes2.get_xticklabels() + self.axes2.get_yticklabels()):
#            label.set_fontsize(7)
#
#        self.axes4 = figure.add_subplot(212)
#        self.axes4.set_title('OD Distribution', fontsize=10)
#        for label in (self.axes4.get_xticklabels() + self.axes4.get_yticklabels()):
#            label.set_fontsize(7)
#        self.canvas2 =  FigureCanvas(self.panel, -1, figure)
#        imagesBoxSizer2.Add(self.canvas2, flag=wx.ALL|wx.EXPAND, border=5)
#
#
#        hbox.Add(imagesBoxSizer2, 4, wx.ALL|wx.EXPAND, 10)

####### multiple shoots functions ############
#        listFitBox = wx.StaticBox(self.panel, label='List Fit')
#        listFitBoxSizer = wx.StaticBoxSizer(listFitBox, wx.VERTICAL)
#
#        readDataBox = wx.StaticBox(self.panel, label='Read data')
#        readDataBoxSizer = wx.StaticBoxSizer(readDataBox, wx.HORIZONTAL)
#        readButton = wx.Button(self.panel, label = 'Read saved data')
#        readButton.Bind(wx.EVT_BUTTON, self.readListData)
#        self.dataReadedText = wx.TextCtrl(self.panel,value='input: 0', style=wx.TE_READONLY)
#        readDataBoxSizer.Add(readButton, flag=wx.LEFT | wx.TOP, border=5)
#        readDataBoxSizer.Add(self.dataReadedText, 1, flag=wx.LEFT | wx.TOP | wx.EXPAND, border=5)
#        listFitBoxSizer.Add(readDataBoxSizer, flag=wx.ALL|wx.EXPAND, border=5)
#
#
#        fitListButton = wx.Button(self.panel, label = 'List Data Fit')
#        fitListButton.Bind(wx.EVT_BUTTON, self.fitListData)
#        listFitBoxSizer.Add(fitListButton, flag=wx.ALL|wx.EXPAND, border=5)
#
#        listFitResultBox = wx.StaticBox(self.panel, label='List Fit Result')
#        listFitResultBoxSizer = wx.StaticBoxSizer(listFitResultBox, wx.VERTICAL)
#        hbox33 = wx.BoxSizer(wx.HORIZONTAL)
#        st13 = wx.StaticText(self.panel,label = 'Temperature(nK)')
#        self.fitTempText = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
#        st14 = wx.StaticText(self.panel,label = 'Trapping Frequency(Hz)')
#        hbox34 = wx.BoxSizer(wx.HORIZONTAL)
#        st15 = wx.StaticText(self.panel, label = 'Axial  ')
#        self.fitTrapAxialFreqText = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
#        hbox35 = wx.BoxSizer(wx.HORIZONTAL)
#        st16 = wx.StaticText(self.panel, label = 'Radial')
#        self.fitTrapRadialFreqText = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
#
#        hbox33.Add(st13, flag=wx.ALL, border=5)
#        hbox33.Add(self.fitTempText, flag=wx.ALL, border=5)
#        listFitResultBoxSizer.Add(hbox33, flag=wx.ALL, border=0)
#        listFitResultBoxSizer.Add(st14, flag=wx.ALL, border=5)
#        hbox34.Add(st15, flag=wx.ALL, border=5)
#        hbox34.Add(self.fitTrapAxialFreqText, flag=wx.ALL, border=0)
#        listFitResultBoxSizer.Add(hbox34, flag=wx.ALL, border=5)
#        hbox35.Add(st16, flag=wx.ALL, border=5)
#        hbox35.Add(self.fitTrapRadialFreqText, flag=wx.ALL, border=5)
#        listFitResultBoxSizer.Add(hbox35, flag=wx.ALL, border=0)
#
#        listFitBoxSizer.Add(listFitResultBoxSizer, flag=wx.ALL|wx.EXPAND, border=5)
#
#        hbox.Add(listFitBoxSizer, 1, wx.ALL|wx.EXPAND, 10)


# ######## show image on screen ############
        
        # vbox4 = wx.BoxSizer(wx.VERTICAL)
        # centerImage = wx.Image('../data/1.jpg', wx.BITMAP_TYPE_ANY)
        # self.imageBitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(centerImage))
        # # vbox4.Add(centerImage, flag=wx.LEFT | wx.TOP, border=5)

        # hbox.Add(vbox4, proportion=1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=20)


        self.panel.SetSizer(hbox)
        
        # added by Pierre, to start with a non-null image
        
        print("L image courante est " + str(self.currentImg))
        #self.updateImageOnUI(self.chosenLayerNumber, hasFileSizeChanged)
#        self.chooseAOI()
        
#################################################
############# FUNCTION BY HYUNGMOK ##############
#################################################
#    def test(self, e):
##        if self.testFrame is not None :
##            self.testFrame.Close()
#
#        self.testFrame = CanvasFrame(self)
#
#        x1, x2, y1, y2 = self.quickFit(e)
#        self.testFrame.setData(x1, x2, y1, y2)
#        self.testFrame.setIndexRange(self.AOI)
#        self.testFrame.draw()
###################################################

    def updateFileInfoBox(self):
        self.fileInfoImageIDBox.SetValue(str(self.imageID))
        self.updateFileInfoFromDB()
        self.fileInfoTimestampBox.SetValue(self.imageTimestamp)
        self.fileInfoNCountBox.SetValue(np.format_float_scientific(getNCount(self.imageID), precision = 2))
        
    def updateFileInfoFromDB(self):
        self.imageTimestamp = getTimestamp(self.imageID)
    
        
    def initializeDummyData(self):
        print(os.getcwd())
        img = Image.open('frankLloydWright.jpg')
        dummyImage = 256 - np.array(img)[:,:,0]
        shape = np.shape(dummyImage)
        self.imageData = [dummyImage, np.zeros(shape), np.zeros(shape)]
        self.atomImage = np.array(img)[:,:,0]
        #self.initializeAOI()
        #self.AOI_PrimaryImage = self.updateAOI_PrimaryImage()
        #self.AOI_SecondaryImage = self.updateAOI_SecondaryImage()
        
    def setDefringingRefPath(self):
        tempPath = self.path[:-1] + "_ref\\"
        if not os.path.exists(tempPath):
            os.makedirs(tempPath)
        self.defringingRefPath = tempPath
        
    def applyDefringing(self):
        if self.checkApplyDefringing.GetValue() is False:
            self.checkResetAOI.SetValue(False)
            self.checkResetAOI.Enable(False)
        else:
            self.checkResetAOI.Enable(True)
        
        self.setDataAndUpdate()
        
    def defringing(self):
#        defringing = self.checkApplyDefringing.GetValue()
#        if defringing is True:
        try:
#            print "###############"
#            print self.yTop
#            print self.yBottom
#            print self.xLeft
#            print self.xRight
#            print "###############"
            
            self.defringingRefPath = self.path
            self.defringer.setRoiIndex([self.xLeft_Primary, self.yTop_Primary, self.xRight_Primary, self.yBottom_Primary])
            self.defringer.setNoAtomFilePath(self.defringingRefPath)
            
            num = np.minimum(self.imageIDIndex + 15, len(self.imageIDList))
            self.betterRef = self.defringer.defringedRef(self.imageID, self.imageIDIndex, num, setRoiIndex = True)
        except Exception as e:
            self.checkApplyDefringing.SetValue(False)
            self.checkResetAOI.SetValue(False)
            self.checkResetAOI.Enable(False)
            msg = wx.MessageDialog(self, "Defringing failed: \n" + str(e),'Defringing Error', wx.OK)
            if msg.ShowModal() == wx.ID_OK:
                msg.Destroy()

#        self.setDataAndUpdate()
        
    def doFitList(self, numOfImages):
        
        return 0

    def showTOFFit(self, e):
        string = "\n" + self.TOFFitList.GetValue() + "\n"
##        commaIndex = []
        commaIndex = [pos for pos, char in enumerate(string) if char == '\n']
        TOFList = np.zeros(len(commaIndex) - 1)
        self.doFitList(len(TOFList))

        try:
            for i in np.arange(len(commaIndex) - 1):
                TOFList[i] =  float(string[(commaIndex[i] + 1): (commaIndex[i + 1])])
        except Exception as e:
            print("------TOF List format is wrong-----")
            msg = wx.MessageDialog(self, "TOF time input format is wrong!", 'TOF Time Input Error',wx.OK)
            if msg.ShowModal() == wx.ID_OK:
                msg.Destroy()


#        print self.imageListBox.GetString(0)
        print(TOFList)
    
    def setSnippetPath(self, e):
        snippetPath = e.GetEventObject()
        self.snippetPath = snippetPath.GetValue()
        print(self.snippetPath)
        
    def setXTrapFreq(self, e):
        omega = e.GetEventObject()
        self.xTrapFreq = float(omega.GetValue())
        self.updateTemp()
    
    def setYTrapFreq(self, e):
        omega = e.GetEventObject()
        self.yTrapFreq = float(omega.GetValue())
        self.updateTemp()

    def checkIfFileSizeChanged(self):
        # if self.checkLocalFiles:
        #     previousFileSize = self.actualFileSize
        #     self.actualFileSize = os.stat(self.imageID).st_size
        #     hasFileSizeChanged = False
        #     if self.actualFileSize != previousFileSize:
        #         hasFileSizeChanged = True
        # if not self.checkLocalFiles:
        #     hasFileSizeChanged = False
        hasFileSizeChanged = False
        return hasFileSizeChanged
            
    def setTOF(self, e):
        tof = e.GetEventObject()
        self.TOF = float(tof.GetValue())
        self.updateTemp()
        
    def updatePeakValues(self):
        temp = str(int(self.x_peakHeight)) + ",  " + str(int(self.y_peakHeight))
        self.peakBox.SetValue(temp)
        
    def updateTrueWidths(self):
        self.true_x_width = self.x_width * self.pixelToDistance
        self.true_y_width = self.y_width * self.pixelToDistance
        
        self.true_x_width_std = self.x_width_std * self.pixelToDistance
        self.true_y_width_std = self.y_width_std * self.pixelToDistance

        print("")
        print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(" The true X width = " + str("%.3f"%(self.true_x_width*1E6)) + " um / " + str("%.3f"%(self.true_x_width_std*1E6)) + " um")
        print(" The true Y width = " + str("%.3f"%(self.true_y_width*1E6)) + " um / " + str("%.3f"%(self.true_y_width_std*1E6)) + " um")
        
        try:
            std_avg = (self.true_x_width_std/self.true_x_width + self.true_y_width_std/self.true_y_width)/2
        except Exception as ex:
            print(ex)
            std_avg = 0
        print(" 2 x (std/avg) averaged between x and y = " + str("%.3f"%(2. * std_avg)))
        print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("")

        temp = str("%.1f"%(self.true_x_width*1E6)) +",   " + str("%.1f"%(self.true_y_width*1E6))
        self.widthBox.SetValue(temp)
              
    def updateTemp(self):
#        self.updateTrueWidths()
        if self.isXFitSuccessful is False:
            self.true_x_width = 0
        if self.isYFitSuccessful is False:
            self.true_y_width = 0

        ## temperature calculation with trap frequencies
        self.temperature[0] = 1E+6 * self.mass *(self.true_x_width* 2 * np.pi * self.xTrapFreq)**2/(kB * (1 + (2* np.pi* self.xTrapFreq * self.TOF * 1E-3)**2))
        self.temperature[1] = 1E+6 * self.mass *(self.true_y_width* 2 * np.pi * self.yTrapFreq)**2/(kB * (1 + (2* np.pi* self.yTrapFreq * self.TOF * 1E-3)**2))

        temp = "(" + str("%.3f"%(self.temperature[0])) +", " + str("%.3f"%(self.temperature[1])) + ")"
        self.tempBox.SetValue(temp)

        ## long time limit calculation
        self.tempLongTime[0] = 1E+6 * self.mass *(self.true_x_width*1E+3/self.TOF)**2/kB
        self.tempLongTime[1] = 1E+6 * self.mass *(self.true_y_width*1E+3/self.TOF)**2/kB
        
        temp2 = "(" + str("%.3f"%(self.tempLongTime[0])) +", " + str("%.3f"%(self.tempLongTime[1])) + ")"
        self.tempBox2.SetValue(temp2)
        
    def updateFittingResults(self):
        self.updateTrueWidths()
        self.updatePeakValues()
        self.updateTemp()
        
        if self.fitMethodBoson.GetValue() is True:
            self.updateBosonParams()
            print(" ~~~~ BEC population ratio: " + str(self.x_becPopulationRatio))
        elif self.fitMethodFermion.GetValue() is True:
            self.updateFermionParams()
            
    def updateTc(self):
        self.TcBox.SetValue(str("%.2f"%(self.x_tOverTc)) + ", " + str("%.2f"%(self.x_becPopulationRatio)))

    def updateTFRadius(self):
        self.TFRadiusBox.SetValue(str("%.2f"%(self.x_thomasFermiRadius * 1e6)))
        
    def updateBosonParams(self):
        self.updateTc()
        self.updateTFRadius()

    def updateFermionParams(self):
        print(" --------- DO NOTHING YET ----------")
    
    def setFileSize(self, e):
        try:
            fileSize = float(self.fileSizeValue.GetValue())
            self.expectedFileSize = fileSize
        except:
            print("Invalue File Size")
            print(self.expectedFileSize)
        
#     def setCurrentImg(self, data, hasFileSizeChanged):
#         if hasFileSizeChanged or self.currentImg is None:
# #            print("====1====")
#             print(self.currentImg)
#             print(data)
#             print("showing image")
#             self.currentImg = self.axes1.imshow(data, cmap='gray_r', aspect='auto', vmin=-1, vmax=1)
# #            self.currentImg.autoscale()
# #            print("====2====")
#             print(self.currentImg)
#         else:
#             self.currentImg.set_data(data)

    def setCurrentImg(self, data, hasFileSizeChanged):
        if hasFileSizeChanged or self.currentImg is None:
#            print("====1====")
            print(self.currentImg)
            print(data)
            print("showing image")
            self.currentImg = self.axes1.imshow(data, cmap='gray_r', aspect='auto', vmin=-1, vmax=1)
#            self.currentImg.autoscale()
#            print("====2====")
            print(self.currentImg)
        else:
            print(data)
            print("reshowing that image")
            self.currentImg = self.axes1.imshow(data, cmap='gray_r', aspect='auto', vmin=-1, vmax=1)

    def checkTimeChange(self):
        current = datetime.date.today()
        
        if (current != self.today):
            self.timeChanged = True
            self.today = current
        else:
            self.timeChanged = False
            
    def setImageAngle(self, e):
        tx = e.GetEventObject()
        rotation = tx.GetValue()
#        if (rotation[0] == "-"):
#            print rotation
#            print rotation[1:]
#            temp =  -1. * float(rotation[1:])
#            print temp
#        else:
#            temp = float(rotation)
#
        self.imageAngle = float(rotation)
#        self.setDataAndUpdate(e)
        
    def setImagePivotX(self, e):
        tx = e.GetEventObject()
        temp = int(tx.GetValue())
        
        x = self.atomImage.shape[0]
        if (x < temp) or (temp <= 0):
            temp = x/2
        
        self.imagePivotX = temp
        self.pivotXBox.SetValue(str(self.imagePivotX))
        
#        self.setDataAndUpdate(e)
        
    def setImagePivotY(self, e):
        tx = e.GetEventObject()
        temp = int(tx.GetValue())
        
        y = self.atomImage.shape[1]
        if (y < temp) or (temp <= 0):
            temp = y/2
        
        self.imagePivotY = temp
        self.pivotYBox.SetValue(str(self.imagePivotY))
        
    def setImageRotationParams(self, e):
        if self.imageAngle == 0.  and self.imageAngle == self.prevImageAngle:
            self.isRotationNeeded = False
        else:
            self.isRotationNeeded = True

        self.setDataAndUpdate()
        
    def setPixelSize(self, e):
        tx = e.GetEventObject()
        self.pixelSize = float(tx.GetValue())
        
        self.pixelToDistance = self.pixelSize / self.magnification * 10**-6
        self.setAtomNumber()
        self.updateFittingResults()
        
        print("PIXEL SIZE:")
        print(self.pixelSize)
        
    def setMagnification(self, e):
        mg = e.GetEventObject()
        self.magnification = float(mg.GetValue())

        self.pixelToDistance = self.pixelSize / self.magnification * 10**-6
        
        self.setAtomNumber()
        self.updateFittingResults()
        
        print("MAGNIFICATION:")
        print(self.magnification)
        
    def setConstants(self):
        self.pixelToDistance = self.pixelSize / self.magnification * 10**-6
        
        massUnit = 1.66E-27
        wavelength = 421E-9
        self.mass = 164*massUnit
        self.crossSection = 6. * np.pi * (wavelength/(2*np.pi))**2

    def onAtomRadioClicked(self,e):
        self.atom = self.atomRadioBox.GetStringSelection()
        print(self.atom)
        self.setAtomNumber()
        self.updateFittingResults()
        
        snippetPath = "C:\\shared_data\\AndorImg\\SnippetLookHere"  + self.atom + ".txt"
        self.snippetTextBox.SetLabel(snippetPath)
        
        print("new snippet path -----> " + self.snippetPath)

    def updateImageIDList(self):
        self.imageIDList = self.getLastIDinDB() # I changed fileList into imageIDList
    #     if self.checkLocalFiles:    # if we look at the local files> This should be deleted
    #         if not os.path.exists(self.path):
    #             os.makedirs(self.path)
    # #        print self.path + "----update File List"
    #         os.chdir(self.path)
    #         start = time.time()
    #         self.fileList =  sorted(glob.iglob(self.path + '*.' + self.fileType), key=os.path.getctime)
    #         end = time.time()
    #         print('file list sorting takes.....  ' + str(end - start) + " sec....")
    #     if not self.checkLocalFiles:    # if we look at the database files
    #         self.fileList = self.getLastIDinDB()
    #         #print(self.fileList)
            
            
    def getLastIDinDB(self, n = 20):
        return getLastImageIDs(n)
    
    
    def setImageIDText(self):
#        print self.filename.split('\\')[-1]
        # if self.checkLocalFiles:
        #     self.filenameText.SetValue(self.filename.split('\\')[-1])
        # if not self.checkLocalFiles:
        #     self.filenameText.SetValue('In the database')
        self.imageIDText.SetValue('In the database')

    def updateLatestImageID(self):
        self.updateImageIDList()
        self.imageID = self.imageIDList[-1] #this is the filename
        self.setImageIDText()

    def isAOI_PrimaryOutside(self):
        flag = False
        shape = self.atomImage.shape
#        print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
        if int(self.AOI1_Primary.GetValue()) >= shape[1] or int(self.AOI1_Primary.GetValue()) < 0:
            print("case 1")
            self.xLeft_Primary = 10
            flag = True
        
        if int(self.AOI2_Primary.GetValue()) >= shape[0] or int(self.AOI2_Primary.GetValue()) < 0:
            print("case 2")
            self.yTop_Primary = 10
            flag = True
                
        if int(self.AOI3_Primary.GetValue()) >= shape[1] or int(self.AOI3_Primary.GetValue()) < 0 :
            print("case 3")
            self.xRight_Primary = shape[1] - 10
            flag = True
            
        if int(self.AOI4_Primary.GetValue()) >= shape[0] or int(self.AOI4_Primary.GetValue()) < 0:
            print("case 4")
            self.yBottom_Primary = shape[0] - 10
            flag = True
        #        print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
        return flag
        
    def isAOI_SecondaryOutside(self):
        flag = False
        shape = self.atomImage.shape
        if int(self.AOI1_Secondary.GetValue()) >= shape[1] or int(self.AOI1_Secondary.GetValue()) < 0:
            print("case 1")
            self.xLeft_Secondary = 20
            flag = True
        
        if int(self.AOI2_Secondary.GetValue()) >= shape[0] or int(self.AOI2_Secondary.GetValue()) < 0:
            print("case 2")
            self.yTop_Secondary = 20
            flag = True
                
        if int(self.AOI3_Secondary.GetValue()) >= shape[1] or int(self.AOI3_Secondary.GetValue()) < 0 :
            print("case 3")
            self.xRight_Secondary = shape[1] - 20
            flag = True
            
        if int(self.AOI4_Secondary.GetValue()) >= shape[0] or int(self.AOI4_Secondary.GetValue()) < 0:
            print("case 4")
            self.yBottom_Secondary = shape[0] - 20
            flag = True
        return flag
            

                   
    def initializeAOI(self):

        if (self.isAOI_PrimaryOutside() and self.isAOI_SecondaryOutside()):
            print("#################################################")
            print("AOI_Primary initializing....")
            print("#################################################")
            self.AOI_Primary = [[self.xLeft_Primary,self.yTop_Primary],[self.xRight_Primary,self.yBottom_Primary]]

            self.AOI1_Primary.SetValue(str(self.xLeft_Primary))
            self.AOI2_Primary.SetValue(str(self.yTop_Primary))
            self.AOI3_Primary.SetValue(str(self.xRight_Primary))
            self.AOI4_Primary.SetValue(str(self.yBottom_Primary))
            
            if self.rect_Primary is None:
                self.rect_Primary = matplotlib.patches.Rectangle((0,0), 1, 1, facecolor="none",linewidth=2, edgecolor="#0000ff")
            
            self.axes1.add_patch(self.rect_Primary)
            self.rect_Primary.set_width(self.xRight_Primary - self.xLeft_Primary)
            self.rect_Primary.set_height(self.yBottom_Primary - self.yTop_Primary)
            self.rect_Primary.set_xy((self.xLeft_Primary, self.yTop_Primary))
            
            print("#################################################")
            print("AOI_Secondary initializing....")
            print("#################################################")
            self.AOI_Secondary = [[self.xLeft_Primary,self.yTop_Primary],[self.xRight_Primary,self.yBottom_Primary]]

            self.AOI1_Secondary.SetValue(str(self.xLeft_Primary))
            self.AOI2_Secondary.SetValue(str(self.yTop_Primary))
            self.AOI3_Secondary.SetValue(str(self.xRight_Primary))
            self.AOI4_Secondary.SetValue(str(self.yBottom_Primary))
            
            if self.rect_Secondary is None:
                self.rect_Secondary = matplotlib.patches.Rectangle((0,0), 1, 1, facecolor="none",linewidth=2, edgecolor="red")
            
            self.axes1.add_patch(self.rect_Secondary)
            self.rect_Secondary.set_width(self.xRight_Secondary - self.xLeft_Secondary)
            self.rect_Secondary.set_height(self.yBottom_Secondary - self.yTop_Secondary)
            self.rect_Secondary.set_xy((self.xLeft_Secondary, self.yTop_Secondary))


            self.canvas.draw()
            
            self.setAtomNumber()
    
    def applyFilter(self):
        self.isMedianFilterOn = self.checkMedianFilter.GetValue()
        self.setDataAndUpdate()
          
    def update1DProfilesAndFit(self, i = 0):
        self.calc1DProfiles()
#        self.fit()
        self.calc1DRadialAvgAndRefit()
        self.update1DProfiles()
        self.updateFittingResults()
            
    def fit(self, axis = 'xy'):
        try:
            self.doGaussianFit(axis)
            print("x center is " + str(self.x_center))
            print("x width is" + str(self.x_width))
            print("")
            print("y center is " + str(self.y_center))
            print("y width is " + str(self.y_width))
            
#            if self.fitMethodFermion.GetValue() is True:
#                return
#
            if self.fitMethodBoson.GetValue() is True:
                ###############################################################################
                ## by default, I'm applying BEC fit only on x-dir (axial directtion)
                ###############################################################################
                self.degenFitter.setInitialCenter(self.x_center)
                self.degenFitter.setInitialWidth(self.x_width)
                self.degenFitter.setInitialPeakHeight(self.x_peakHeight)
                self.degenFitter.setInitialOffset(self.x_offset)
                self.degenFitter.setInitialSlope(self.x_slope)
                
                self.degenFitter.setData(self.x_basis, self.x_summed)
                self.degenFitter.doDegenerateFit()
                self.x_fitted = self.degenFitter.getFittedProfile()
                self.x_tOverTc = self.degenFitter.getTOverTc()
                self.x_thomasFermiRadius = self.degenFitter.getThomasFermiRadius() * self.pixelToDistance
                self.x_becPopulationRatio = self.degenFitter.getBecPopulationRatio()
                self.atomNumFromDegenFitX = self.degenFitter.getTotalPopulation() * (self.pixelToDistance**2)/self.crossSection
                self.atomNumFromFitX = self.atomNumFromDegenFitX
                
                print("x_width -------" + str(self.x_width))
                self.x_width = self.degenFitter.getThermalWidth()
                print("x_width -------" + str(self.x_width))
                ###############################################################################
                ## I'm applying BEC fit on y-dir (radial directtion) AS WELL
                ###############################################################################
                self.degenFitter.setInitialCenter(self.y_center)
                self.degenFitter.setInitialWidth(self.y_width)
                self.degenFitter.setInitialPeakHeight(self.y_peakHeight)
                self.degenFitter.setInitialOffset(self.y_offset)
                self.degenFitter.setInitialSlope(self.y_slope)
                
                self.degenFitter.setData(self.y_basis, self.y_summed)
                self.degenFitter.doDegenerateFit()
                self.y_fitted = self.degenFitter.getFittedProfile()
                self.y_tOverTc = self.degenFitter.getTOverTc()
                self.y_thomasFermiRadius = self.degenFitter.getThomasFermiRadius() * self.pixelToDistance
                self.y_becPopulationRatio = self.degenFitter.getBecPopulationRatio()
                self.atomNumFromDegenFitY = self.degenFitter.getTotalPopulation() * (self.pixelToDistance**2)/self.crossSection
                self.atomNumFromFitY = self.atomNumFromDegenFitY
                                
                self.y_width = self.degenFitter.getThermalWidth()

#                self.atomNumFromFitY = self.atomNumFromGaussianY
                
#                self.updateTrueWidths()
            else:
                self.atomNumFromFitX = self.atomNumFromGaussianX
                self.atomNumFromFitY = self.atomNumFromGaussianY
#                return
#            elif self.fitMethodGaussian.GetValue():
##                self.doGaussianFit(axis)
#                print("do nothing by default..")
        except Exception as err:
            print("------ Fitting Failed -------")
#            msg = wx.MessageDialog(self, 'Non-least square fit of python scipy library failed..','Fitting Error', wx.OK)
#            if msg.ShowModal() == wx.ID_OK:
#                msg.Destroy()
    
    def doGaussianFit(self, axis = 'xy'):
        if axis == 'xy': # Regular fit on 2 axis
            self.x_center, self.x_width, self.x_offset, self.x_peakHeight, self.x_fitted, self.isXFitSuccessful, self.x_slope, err_x = gaussianFit(self.x_basis, self.x_summed, self.AOI_Primary, axis = 'x')
            self.atomNumFromGaussianX = self.x_peakHeight *np.sqrt(2 * np.pi) * self.x_width * (self.pixelToDistance**2)/self.crossSection
            self.x_width_std = err_x[2]
            print("")
            print("x fit err = " +str(err_x))
            self.y_center, self.y_width, self.y_offset, self.y_peakHeight, self.y_fitted, self.isYFitSuccessful, self.y_slope , err_y= gaussianFit(self.y_basis, self.y_summed, self.AOI_Primary, axis = 'y')
            self.atomNumFromGaussianY = self.y_peakHeight *np.sqrt(2 * np.pi) * self.y_width * (self.pixelToDistance**2)/self.crossSection
            self.y_width_std = err_y[2]
            print("y fit err = " +str(err_y))
            print("")
            
            print("------------------- see here -------------------------")
            print(self.x_center)
            print("------------------- see here -------------------------")
        elif axis == 'x': # regular fit on only one of the axis
            self.x_center, self.x_width, self.x_offset, self.x_peakHeight, self.x_fitted, self.isXFitSuccessful, self.x_slope, err_x = gaussianFit(self.x_basis, self.x_summed, self.AOI_Primary, axis = 'x')
            self.atomNumFromGaussianX = self.x_peakHeight *np.sqrt(2 * np.pi) * self.x_width * (self.pixelToDistance**2)/self.crossSection
            self.x_width_std = err_x[2]
        else:
            self.y_center, self.y_width, self.y_offset, self.y_peakHeight, self.y_fitted, self.isYFitSuccessful, self.y_slope, err_y = gaussianFit(self.y_basis, self.y_summed, self.AOI_Primary, axis = 'y')
            self.atomNumFromGaussianY = self.y_peakHeight *np.sqrt(2 * np.pi) * self.y_width * (self.pixelToDistance**2)/self.crossSection
            self.y_width_std = err_y[2]
#    def gaussianFit(self):
#        self.isXFitSuccessful = False
#        self.isYFitSuccessful = False
#############################################################################
##        x_mean = np.mean(self.x_summed)
##        x_std = np.std(self.x_summed)
##        x_idx = np.where(self.x_summed < (x_mean - x_std))
##        for i in range(len(x_idx)):
##            self.x_summed[x_idx[i]] = self.x_summed[x_idx[i]]/10
##
##        y_mean = np.mean(self.y_summed)
##        y_std = np.std(self.y_summed)
##        y_idx = np.where(self.y_summed < (y_mean - y_std))
##        print y_idx
##        for i in range(len(y_idx)):
##            self.y_summed[y_idx[i]] = self.y_summed[y_idx[i]]/10
################################################################################
#
#        y_size,x_size = self.AOIImage.shape
#
#        ## smoothing
#        N_smoothing= 10
#        x_summed_smooth = np.convolve(self.x_summed, np.ones((N_smoothing,))/N_smoothing, mode='valid')
#        y_summed_smooth = np.convolve(self.y_summed, np.ones((N_smoothing,))/N_smoothing, mode='valid')
#
##        x_basis = np.linspace(self.xLeft, self.xRight, x_size)
##        y_basis = np.linspace(self.yTop, self.yBottom, y_size)
#
##        print "ahahahahahahahhahahahaha"
##        print self.x_summed.shape
##        print self.y_summed.shape
##        print len(x_basis)
##        print len(self.x_summed)
##        print len(x_summed_smooth)
##        funcX = interp1d(x_basis, self.x_summed, kind = 'linear')
##        funcY = interp1d(y_basis, self.y_summed, kind = 'linear')
##        x_basis = np.linspace(self.xLeft, self.xRight, 2 * x_size)
##        y_basis = np.linspace(self.yTop, self.yBottom, 2 * y_size)
##        self.x_summed = funcX(x_basis)
##        self.y_summed = funcY(y_basis)
##        print self.x_summed.shape
##        print self.y_summed.shape
##        print "ahahahahahahahhahahahaha"
##        print len(x_new)
##        print len(y_summed_smooth)
#
#
##        print len(y_summed_smooth)
#
#        ## initial guess of the amplitude and the center index
#
##        x_max_index = x_max_index + self.xLeft
##        y_max_index = y_max_index + self.yTop
##
##        funcToMin = lambda (data, amp): abs(data - (amp - sum(data)/len(data))/2.)
##        funcToMinTwo = lambda (data, amp): abs(data - (amp - (data[0] + data[-1])/2.)/2.)
##        funcToMin = lambda (data, amp): abs(data - amp/2.)
#        def funcToMin (data, amp): return abs(data - amp/2.)
##        def widthFinder (amp, center, data): return abs(center - np.argmin(funcToMin((data, amp))))/np.sqrt(2*np.log(2))
#        def widthFinder (amp, center, data): return min(abs(center * np.ones(len(data)) - np.argsort(funcToMin(data, amp)))[:10])/np.sqrt(2*np.log(2))
################################################################################
#        x_max_index = np.argmax(x_summed_smooth)
#        x_max = self.x_summed[x_max_index]
#        y_max_index = np.argmax(y_summed_smooth)
#        y_max = self.y_summed[y_max_index]
#
#        xOffset = (x_summed_smooth[0] + x_summed_smooth[-1])/2.
#        yOffset = (y_summed_smooth[0] + y_summed_smooth[-1])/2.
#
#        y_max = y_max - yOffset
#        x_max = x_max - xOffset
#
#        xWidth =  widthFinder(x_max, x_max_index, x_summed_smooth)
#        yWidth =  widthFinder(y_max, y_max_index, y_summed_smooth)
##        print "================================================================="
##        array = funcToMin(y_summed_smooth, y_max)
##        print array
##        idx = np.argmin(array)
##        print idx
##        print np.argsort(array)
##        print array[idx]
##        print y_max_index
##        print abs(y_max_index * np.ones(len(y_summed_smooth)) - np.argsort(funcToMin(y_summed_smooth, y_max)))[:10]
##        print min(abs(y_max_index * np.ones(len(y_summed_smooth)) - np.argsort(funcToMin(y_summed_smooth, y_max)))[:10])
##        print "================================================================="
##        print xOffset
##        print sum(x_summed_smooth)/len(x_summed_smooth)
##        print sum(self.x_summed)/len(self.x_summed)
##        print yOffset
##        print sum(y_summed_smooth)/len(y_summed_smooth)
##        print sum(self.y_summed)/len(self.y_summed)
##        print "================================================================="
#
################################################################################
################################################################################
##        xWidth =  widthFinder(x_max, x_max_index, self.x_summed)
###        yWidth =  widthFinder(y_max, y_max_index, y_summed_smooth)
###        xWidth = 7.
##        yWidth = 1.
##
##        x_max_index = np.argmax(self.x_summed)
##        x_max = self.x_summed[x_max_index]
##        y_max_index = np.argmax(self.y_summed)
##        y_max = self.y_summed[y_max_index]
##
##        xOffset = (self.x_summed[0] +self.x_summed[-1])/2.
##        yOffset = (self.y_summed[0] + self.y_summed[-1])/2.
################################################################################
#
#
#
##        xOffset = sum(x_summed_smooth)/len(x_summed_smooth)
##        yOffset = sum(y_summed_smooth)/len(y_summed_smooth)
#
##        print "--------"
#        x_max_index = x_max_index + self.xLeft
#        y_max_index = y_max_index + self.yTop
#
#        try:
#            poptx, pcovx  = curve_fit(single_G, self.x_basis, self.x_summed, p0 = (x_max, x_max_index, xWidth, xOffset), bounds=([0., 0., 1., -np.inf], [5*x_max, np.inf, np.inf, x_max]))
#            self.x_center = float(poptx[1])
#            self.x_width = float(poptx[2])
#            self.x_offset = float(poptx[3])
#            self.x_peakHeight = float(poptx[0])
#            self.x_fitted = single_G(self.x_basis, self.x_peakHeight, self.x_center, self.x_width, self.x_offset)
#            self.atomNumFromGaussianX = self.x_peakHeight *np.sqrt(2 * np.pi) * self.x_width * (self.pixelToDistance**2)/self.crossSection
#            self.isXFitSuccessful = True
#        except Exception:
#            print "------ X fitting failed ------"
#            self.x_offset = xOffset
#            self.atomNumFromGaussianX = x_max *np.sqrt(2 * np.pi) * xWidth * (self.pixelToDistance**2)/self.crossSection
#            self.isXFitSuccessful = False
#
##        x_slope = int(poptx[-1])
#        try:
#            y_max_index_lb = 0.
#            y_max_index_ub = np.inf
#            yWidth_lb = 1.
#            yWidth_ub = np.inf
##            y_max_index_lb = 385
##            y_max_index_ub = 405
##            yWidth_lb = 1.
##            yWidth_ub = 12.
#            popty, pcovy = curve_fit(single_G, self.y_basis, self.y_summed, p0 = (y_max, y_max_index, yWidth, yOffset), bounds=([0., y_max_index_lb, yWidth_lb, -np.inf], [5*y_max, y_max_index_ub, yWidth_ub, y_max]))
##            popty, pcovy = curve_fit(single_G, y_basis, y_summed_smooth, p0 = (y_max, y_max_index, yWidth, yOffset), bounds=([0., 390., 0., -np.inf], [5*y_max, 400., 10., y_max]))
#            self.y_center = float(popty[1])
#            self.y_width = float(popty[2])
#            self.y_offset = float(popty[3])
#            self.y_peakHeight = float(popty[0])
#            self.y_fitted = single_G(self.y_basis, self.y_peakHeight, self.y_center, self.y_width, self.y_offset)
#            self.atomNumFromGaussianY = self.y_peakHeight *np.sqrt(2 * np.pi) * self.y_width * (self.pixelToDistance**2)/self.crossSection
#            self.isYFitSuccessful = True
#        except Exception:
#            print "------ Y fitting failed ------"
#            self.y_offset = yOffset
#            self.atomNumFromGaussianY = y_max *np.sqrt(2 * np.pi) * yWidth * (self.pixelToDistance**2)/self.crossSection
#            self.isYFitSuccessful = False
#        y_slope = int(popty[-1])
        
#        print ""
#        print ""
#        print "Y peak height: " + str("%.2f"%(self.y_peakHeight)) + ",  X peak Height: " + str("%.2f"%(self.x_peakHeight))
#        print ""
#        print ""
    
    def histogramEq(self, image, number_bins = 1000):
        # from http://www.janeriksolem.net/2009/06/histogram-equalization-with-python-and.html
#        print type(image)
#        image = image + 1
        # get image histogram
#        print "-------entered------"
#        print image.shape
#        print "------1-----"
#        print image.flatten().shape
#        print "-----0-----"
#        print image.flatten().flatten().shape
#        print "-----1-----"
        image_histogram, bins = np.histogram(image.flatten(), number_bins, normed=True)
#        print "-----2-----"
        cdf = image_histogram.cumsum() # cumulative distribution function
#        print "-----3-----"
        cdf =  cdf/cdf[-1] # normalize
#        print "-----4-----"
        # use linear interpolation of cdf to find new pixel values
        image_equalized = np.interp(image.flatten(), bins[:-1], cdf)
#        print "-----5-----"
        return image_equalized.reshape(image.shape)
    
#    if __name__ == '__main__':
#
#        # generate some test data with shape 1000, 1, 96, 96
#        data = np.random.rand(1000, 1, 96, 96)
#
#        # loop over them
#        data_equalized = np.zeros(data.shape)
#        for i in range(data.shape[0]):
#            image = data[i, 0, :, :]
#            data_equalized[i, 0, :, :] = image_histogram_equalization(image)[0]
    def testPCA(self, data, dims_rescaled_data=2):
        """
        returns: data transformed in 2 dims/columns + regenerated original data
        pass in: data as 2D NumPy array
        """
        m, n = data.shape
        # mean center the data
        data -= data.mean(axis=0)
        # calculate the covariance matrix
        R = np.cov(data, rowvar=False)
        # calculate eigenvectors & eigenvalues of the covariance matrix
        # use 'eigh' rather than 'eig' since R is symmetric,
        # the performance gain is substantial
        evals, evecs = LA.eigh(R)        # sort eigenvalue in decreasing order
        idx = np.argsort(evals)[::-1]
        evecs = evecs[:,idx]
        # sort eigenvectors according to same index
        evals = evals[idx]
        # select the first n eigenvectors (n is desired dimension
        # of rescaled data array, or dims_rescaled_data)
        evecs = evecs[:, :dims_rescaled_data]
        # carry out the transformation on the data using eigenvectors
        # and return the re-scaled data, eigenvalues, and eigenvectors
        return np.dot(evecs.T, data.T).T
    
    def setRawDataFromCamera(self, imagePathList):   # called when received images from camera
        #defringing = self.checkApplyDefringing.GetValue()
        defringing = False # This need to be changed and debugged
        #self.atomImage, self.imageData = readFileData(imagePathList, self.camera, [defringing, self.betterRef])

        self.imageData = readFileData(imagePathList, self.camera)
        self.setAtomImageAsDivision(defringing)
        self.isDummyImage = False
        print("Here image data after readout")
        print(self.imageData)

    def setAtomImage(self, defringing = False):
        self.setAtomImageAsDivision(defringing)
        self.setTransformedData()
        
    def setAtomImageAsDivision(self, defringing = False):
        if len(self.imageData) != 3:
            raise Exception("~~~~~~ Given image does not have three layers ~~~~~~~")
        if defringing is True:
            correctedNoAtom = self.betterRef
            if (correctedNoAtom is None) or (correctedNoAtom.shape != self.imageData[1].shape):
                correctedNoAtom = self.imageData[1] - self.imageData[2]
        else:
#            meanAtom = np.mean(imageData[0])
#            meanNoAtom = np.mean(imageData[1])
#            stdAtom = np.std(imageData[0])
#            stdNoAtom = np.std(imageData[1])
#
#            correctedNoAtom = (meanAtom + stdAtom/stdNoAtom *(imageData[1] - meanNoAtom)) - imageData[2]
            lightDifferencePerPixel = self.lightDifferencePerPixel()
            correctedNoAtom = self.imageData[1]*lightDifferencePerPixel - self.imageData[2]
    
        if correctedNoAtom is None:
            correctedNoAtom = self.imageData[1] - self.imageData[2]
    
        absorbImg = np.maximum(self.imageData[0]-self.imageData[2], .1)/(np.maximum(correctedNoAtom, .1))  
        #print absorbImg
        ###  Replace extremely low transmission pixels with a minimum meaningful transmission. 
        minT = np.exp(-9)
        temp = np.empty(self.imageData[0].shape)	
        temp.fill(minT)
        self.atomImage = np.maximum(absorbImg, temp)
        
    def setRawDataFromDB(self):
        #defringing = self.checkApplyDefringing.GetValue()
        defringing = False # This need to be changed and debugged
        self.imageData = readDBData(self.imageID, [defringing, self.betterRef])
        self.setAtomImageAsDivision(defringing)
        self.isDummyImage = False
        if np.shape(self.imageData[0]) == (1, 1):
            self.isDummyImage = True
            self.initializeDummyData()
    
    def setTransformedData(self, pca = False, gaussianFilter = False, histogramEqualization = False, rotation  = True):
        print("TRANFORMED DATA CALLED")
        try:
            absorbImg = self.atomImage # is that necessary?
            if not self.isDummyImage:
                if pca is True:
                    try:
                        print("----------------1=================")
                        pca = sklearnPCA('mle')
                        print("----------------2=================")
                        temp = pca.fit_transform(-np.log(absorbImg))
                        print("----------------3=================")
    #                    temp = pca.explained_varaince_
    #                    print temp.shape
    #                    print temp[0].type
                    except Exception:
                        raise Exception("======= PCA ERROR ========")
                    
                if gaussianFilter is True:
                    try:
                        print("1111111111")
                        tempp = -np.log(absorbImg)
                        print("22222222222")
                        signal = tempp[self.yTop_Primary:self.yBottom_Primary, self.xLeft_Primary:self.xRight_Primary]
                        print(signal)
                        print("33333333333")
                        filtered = gaussian_filter(tempp, 2, order = 0, truncate = 2)
                        print("44444444444")
    #                    filtered[self.yTop:self.yBottom, self.xLeft:self.xRight] = signal
                        print("55555555555")
                        temp = filtered
                        
                        print('====== Gaussian filter success ======')
    #                    temp2 = temp
                    except Exception:
                        raise Exception("========= Gaussian Filter ERROR =======")
                        
                if histogramEqualization is True:
                    try:
                        temp = self.histogramEq(temp)
                        print('====== histogram equalization success ======')
                    except Exception:
                        raise Exception("========= Histogram Equalization ERROR =======")
                        
                if (histogramEqualization is False) and (gaussianFilter is False) and (pca is False):
                    print('====== no filters IN ======')
                    temp = -np.log(absorbImg)
                    print('====== no filters OUT ======')
                    
                if self.isNormalizationOn is True:
                    print('tried to normalize')
                    temp = -np.log(createNormalizedAbsorbImg(self.imageData, self.AOI_Primary))
        
                if self.isMedianFilterOn is True:
                    try:
                        temp = medfilt(temp)
                    except Exception:
                        raise Exception("======= Median Filter ERROR ========")
    
                if rotation is True:
                    try:
                        if self.isRotationNeeded is True:
                            temp = self.rotateImage(temp, self.imageAngle, [self.imagePivotX, self.imagePivotY])
                            print("======= rotation executed =======")
                        else:
                            print("======= No Rotation required for 0 deg. =======")
                    except Exception:
                        raise Exception("========= rotation ERROR =======")
                
                self.atomImage = temp
            del absorbImg
        except:
            print("Fail to postprocess the image")
            
    def setFitting(self): # Is that a good name?
        ## initializeAOI and generate AOI rect. only at the beginning
        self.initializeAOI()
            
            ## set self.AOIImage, which is the image array confined in the AOI
        self.updateAOI_PrimaryImage()
        self.update1DProfilesAndFit()
        self.updateFittingResults()
        self.setAtomNumber()
    
    def setDataNewImageSelection(self, pca = False, gaussianFilter = False, histogramEqualization = False, rotation  = True):
        # setDataNewImageSelection is used after having loaded a new file from the database
        try:
            self.setRawDataFromDB()
            self.setTransformedData(pca, gaussianFilter, histogramEqualization, rotation)
            self.setFitting()
            
        except Exception as e:
            msg = wx.MessageDialog(self, str(e),'Setting Data failed', wx.OK)
            print("self.imageID is " + str(self.imageID))
            if msg.ShowModal() == wx.ID_OK:
                msg.Destroy()
            print("====== setDataNewImageSelection error =======")
    
    def setDataNewIncomingFile(self, pca = False, gaussianFilter = False, histogramEqualization = False, rotation  = True):
        # setDataNewIncomingFile is used after having loaded a new file from the camera
        try:
            # I do not update the raw data on this one, just the transformation
            self.setTransformedData(pca, gaussianFilter, histogramEqualization, rotation)
            self.setFitting()
            
        except Exception as e:
            msg = wx.MessageDialog(self, str(e),'Setting Data failed', wx.OK)
            print("self.imageID is " + str(self.imageID))
            if msg.ShowModal() == wx.ID_OK:
                msg.Destroy()
            print("====== setDataNewIncomingFile error =======")
    


    def update1DProfiles(self):
#        xbasis = np.linspace(self.xLeft, self.xRight, self.x_summed.shape[0])
#        ybasis = np.linspace(self.yTop, self.yBottom, self.y_summed.shape[0])
        
        ## if the fitting failed, show flat lines
        if self.isXFitSuccessful is False:
            self.x_fitted = self.x_offset * np.ones(self.x_summed.shape[0])
            self.x_peakHeight = 0
            self.x_width = 0
            print("x_width has been set to 0")
        if self.isYFitSuccessful is False:
            self.y_fitted = self.y_offset * np.ones(self.y_summed.shape[0])
            self.y_peakHeight = 0
            self.y_width = 0
            
        ysize, xsize = self.atomImage.shape
#        xsize, ysize = self.atomImage.shape

        ## x profile
        if (self.currentXProfile is not None):
            self.axes2.lines.remove(self.currentXProfile)
        
#        xarr, yarr = radial_profile_two(self.AOIImage, [self.x_center, self.y_center])
#        xarr, yarr = azimuthalAverage(self.AOIImage, center = [self.x_center, self.y_center], steps  = False)
#        xarr, yarr = radialAverage(self.AOIImage, center = [self.x_center, self.y_center], boundary = [self.xLeft, self.yTop, self.xRight, self.yBottom])
#        xarr = xarr + self.x_center
#        yarr = self.x_peakHeight * yarr
        
#        num = len(xarr)
#        print "====================================="
#        print num
#        xarr = np.linspace(self.x_center - num + 1, self.x_center + num - 1, 2*num - 2)
#        yarr = np.concatenate((np.flipud(yarr)[:-2], yarr), axis = 0)
#        print xarr.shape
#        print yarr.shape
#
#        print self.x_center
#        print self.y_center
#        print self.xLeft
#        print self.yTop
#        print self.x_center - self.xLeft
#        print self.y_center - self.yTop
#
#        print self.AOIImage.shape
#        print xbasis.shape
#        print ybasis.shape
##        print radial.shape
##        print len(r)
##        print nr.shape
##        print radial_prof.shape
#        print xarr.shape
#        print yarr.shape
#        print xbasis.shape
#        print "====================================="
#        xarr = xarr + self.xLeft
        
        self.currentXProfile, = self.axes2.plot(self.x_basis, self.x_summed, 'b')
            
        if (self.currentXProfileFit is not None):
            self.axes2.lines.remove(self.currentXProfileFit)
        
#        self.atomNumFromGaussianX = self.x_peakHeight *np.sqrt(2 * np.pi) * self.x_width * (self.pixelToDistance**2)/self.crossSection
#        self.currentXProfileFit, = self.axes2.plot(xarr, yarr, 'r', label = str("%.3f"%(self.atomNumFromGaussianX/1E6)))
            
        self.currentXProfileFit, = self.axes2.plot(self.x_basis, self.x_fitted, 'r', label = str("%.3f"%(self.atomNumFromFitX/1E6)))
#        self.currentXProfileFit, = self.axes2.plot(self.x_basis, self.x_fitted, 'r', label = str("%.3f"%(self.atomNumFromGaussianX/1E6)))
        lx = self.axes2.legend(loc = "upper right")
        print(str("%.3f"%(self.atomNumFromFitX/1E6)) + "         %%%%%%%%%%%%%%%")
        if self.isXFitSuccessful is False:
            for text in lx.get_texts():
                text.set_color("red")
        try:                           
            xMax = np.maximum(self.x_summed.max(), self.x_fitted.max())
            xMin = np.minimum(self.x_summed.min(), self.x_fitted.min())
        except: 
            xMax = 2
            xMin = 1
        self.axes2.set_xlim([0, xsize])
        self.axes2.set_ylim([xMin, xMax])
        self.axes2.set_yticks(np.linspace(xMin, xMax, 4))
        
        ## y profile
        if (self.currentYProfile is not None):
            self.axes3.lines.remove(self.currentYProfile)
        
        self.currentYProfile, = self.axes3.plot(self.y_summed, self.y_basis,'b')

        if (self.currentYProfileFit is not None):
            self.axes3.lines.remove(self.currentYProfileFit)

#        self.atomNumFromGaussianY = self.y_peakHeight *np.sqrt(2 * np.pi) * self.y_width * (self.pixelToDistance**2)/self.crossSection
#        self.currentYProfileFit, = self.axes3.plot(radial, ybasis, 'r', label =str("%.3f"%(self.atomNumFromGaussianY/1E6)))
            
        self.currentYProfileFit, = self.axes3.plot(self.y_fitted, self.y_basis, 'r', label =str("%.3f"%(self.atomNumFromFitY/1E6)))
#        self.currentYProfileFit, = self.axes3.plot(self.y_fitted, self.y_basis, 'r', label =str("%.3f"%(self.atomNumFromGaussianY/1E6)))
        ly = self.axes3.legend(loc = "upper right")
        if self.isYFitSuccessful is False:
            for text in ly.get_texts():
                text.set_color("red")
    
        print(str("%.3f"%(self.atomNumFromGaussianY/1E6)) + "         %%%%%%%%%%%%%%%")
        
        try:                           
            yMax = np.maximum(self.y_summed.max(), self.y_fitted.max())
            yMin = np.minimum(self.y_summed.min(), self.y_fitted.min())
        except: 
            yMax = 2
            yMin = 1
        
        #yMax = np.maximum(self.y_summed.max(), self.y_fitted.max())
        #yMin = np.minimum(self.y_summed.min(), self.y_fitted.min())
        self.axes3.set_xlim([yMin, yMax])
        self.axes3.set_ylim([ysize, 0])
        self.axes3.set_xticks(np.linspace(yMin, yMax, 3))
        self.axes3.xaxis.set_ticks_position('top')

        self.deletePrev2DContour()                ## draw newly set data
        self.canvas.draw()
#        self.axes3.set_ylim(self.axes3.get_ylim()[::-1])
    
    def updateImageListBox(self):
        self.imageListBox.Clear()
        self.updateImageIDList()
        # if self.checkLocalFiles:
        #     for imageID in reversed(self.imageIDList):
        #         self.imageListBox.Append(imageID.split('\\')[-1])
        # if not self.checkLocalFiles:
        #     for imageID in self.imageIDList:      # it's a bit weird that I do not need to reverse that one
        #         self.imageListBox.Append(str(imageID))
        for imageID in self.imageIDList:      # it's a bit weird that I do not need to reverse that one
                 self.imageListBox.Append(str(imageID))
        
    # def setFileType(self, e):
    #     rb = e.GetEventObject()
    #     self.fileType = rb.GetLabel()
    #     self.updateImageListBox()   # Is that thing necessary?
    #     print(self.fileType)

    def setCameraType(self, e):
        rb = e.GetEventObject()
        print("Camera type changed to: " + rb.GetLabel())
        self.cameraType = rb.GetLabel()
        self.camera = Camera(self.cameraType, self.cameraPosition)
        print(self.camera)

    def setCameraPosition(self, e):
        rb = e.GetEventObject()
        print("Camera position changed to: " + rb.GetLabel())
        if rb.GetLabel() == "Vertical":
            self.cameraPosition = "VERTICAL"
        elif rb.GetLabel() == "Horizontal":
            self.cameraPosition = "HORIZONTAL"
        self.camera = Camera(self.cameraType, self.cameraPosition)
        print(self.camera)

########################################
########################################
        
    def choosePath(self, e):
        myStyle = wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST
#        =wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON
#        print self.path
        dialog = wx.DirDialog(None,  "Choose a directory:", defaultPath = self.path, style = wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            if platform.system() == 'Darwin': # MAC OS
                self.path = dialog.GetPath() + '/'
            if platform.system() == 'Linux':
                self.path = dialog.GetPath() + '\\' # maybe not the correct one for linux
            if platform.system() == 'Windows':
                self.path = dialog.GetPath() + '\\'
            self.imageFolderPath.SetValue(self.path)
#            self.setDefringingRefPath()
#        else:
#            self.path = None
        
        self.updateImageListBox()
        dialog.Destroy()

    def chooseFile(self, e):
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        dialog = wx.FileDialog(self, 'Open', '', style=style)
        dialog.SetDirectory(self.path)
        if dialog.ShowModal() == wx.ID_OK:
            self.imageID = dialog.GetFilename()
            print(self.imageID + "---chooseFile")
            self.setImageIDText()
        else:
            self.imageID = None
        
        #self.fitImage(e)
        self.fitImage()
        dialog.Destroy()
    
    
#    def chooseAOI(self):
#        self.xLeft = int(self.AOI1.GetValue())
#            # print xLeft
#        self.xRight = int(self.AOI3.GetValue())
#            # print xRight
#        self.yTop = int(self.AOI2.GetValue())
#            # print yTop
#        self.yBottom = int(self.AOI4.GetValue())
#            # print yBottom
#        #self.ax = plt.gca()
#        self.rect = matplotlib.patches.Rectangle((0,0), 1, 1, facecolor="none",linewidth=2, edgecolor="#0000ff")
#        self.axes1.add_patch(self.rect)

#     def on_press(self, event):
#         #print 'press'
# #        self.rect.remove()
#         self.xLeft = int(event.xdata)
#         self.yTop = int(event.ydata)
#         x0 = self.xLeft
#         y0 = self.yTop
        
#         self.press = x0, y0, event.xdata, event.ydata
        
#        print self.press
    def on_press(self, event):
        if event.button == 1: # 1 corresponds to MouseButton.LEFT
            print("PRESSING PRIMARY")
            self.xLeft_Primary = int(event.xdata)
            self.yTop_Primary = int(event.ydata)
            x0 = self.xLeft_Primary
            y0 = self.yTop_Primary
            self.press = x0, y0, event.xdata, event.ydata
        elif event.button == 3: # 3 corresponds to MouseButton.RIGHT
            print("PRESSING SECONDARY")
            self.xLeft_Secondary = int(event.xdata)
            self.yTop_Secondary = int(event.ydata)
            x0 = self.xLeft_Secondary
            y0 = self.yTop_Secondary
            self.press = x0, y0, event.xdata, event.ydata
            
    def on_motion(self, event):
        #print("MOVING")
        #'on motion we will move the rect if the mouse is over us'
        if event.button == 1: # 1 corresponds to MouseButton.LEFT
            if self.press is None: return # pass if the mouse is not clicked
            if event.inaxes != self.axes1:
                return
            x0, y0, xpress, ypress = self.press
            self.x1 = event.xdata
            self.y1 = event.ydata
            
            self.rect_Primary.set_width(self.x1 - xpress)
            self.rect_Primary.set_height(self.y1 - ypress)
            self.rect_Primary.set_xy((xpress, ypress))
    
            self.rect_Primary.figure.canvas.draw()
            #self.canvas.draw()
        elif event.button == 3: # 3 corresponds to MouseButton.RIGHT
            if self.press is None: return
            if event.inaxes != self.axes1:
                return
            x0, y0, xpress, ypress = self.press
            self.x1 = event.xdata
            self.y1 = event.ydata
            
            self.rect_Secondary.set_width(self.x1 - xpress)
            self.rect_Secondary.set_height(self.y1 - ypress)
            self.rect_Secondary.set_xy((xpress, ypress))
    
            self.rect_Secondary.figure.canvas.draw()
            #self.canvas.draw()    # see if I can put a layer
   
    def on_release(self, event):
        #print 'release'
        self.press = None
        if event.button == 1: # 1 corresponds to MouseButton.LEFT
            self.x1 = event.xdata
            self.y1 = event.ydata
    #        self.xRight = int(event.xdata)
    #        self.yBottom = int(event.ydata)
            self.xRight_Primary = int(self.x1)
            self.yBottom_Primary = int(self.y1)
            
            if self.xRight_Primary < self.xLeft_Primary:
                temp = self.xRight_Primary
                self.xRight_Primary = self.xLeft_Primary
                self.xLeft_Primary = temp
            if self.yBottom_Primary < self.yTop_Primary:
                temp = self.yBottom_Primary
                self.yBottom_Primary = self.yTop_Primary
                self.yTop_Primary = temp
            
            if (self.xLeft_Primary - 3 < 0): self.xLeft_Primary = 3
            if (self.yTop_Primary - 3 < 0): self.yTop_Primary = 3
            if (self.xRight_Primary + 4 >= self.imageData[0].shape[1]): self.xRight_Primary = self.imageData[0].shape[1] - 5
            if (self.yBottom_Primary + 4 >= self.imageData[0].shape[0]): self.yBottom_Primary = self.imageData[0].shape[0] - 5
            
        
            self.AOI1_Primary.SetValue(str(self.xLeft_Primary))
            self.AOI2_Primary.SetValue(str(self.yTop_Primary))
            self.AOI3_Primary.SetValue(str(self.xRight_Primary))
            self.AOI4_Primary.SetValue(str(self.yBottom_Primary))
            self.AOI_Primary = [[self.xLeft_Primary,self.yTop_Primary],[self.xRight_Primary,self.yBottom_Primary]]
            
            self.rect_Primary.set_width(self.xRight_Primary - self.xLeft_Primary)
            self.rect_Primary.set_height(self.yBottom_Primary - self.yTop_Primary)
            self.rect_Primary.set_xy((self.xLeft_Primary, self.yTop_Primary))
            
            self.canvas.draw()
            
            self.updateAOI_PrimaryImage()
            self.setAtomNumber()
            self.update1DProfilesAndFit()
            # if self.checkResetAOI.GetValue() is True and self.checkApplyDefringing.GetValue() is True:
            #     #self.setDataAndUpdate()
            #     self.setAtomNumber()
            # else:
            #     self.setAtomNumber
            #     #self.setDataAndUpdate()
            #     self.updateAOI_PrimaryImageAndProfiles()

        elif event.button == 3: # 3 corresponds to MouseButton.RIGHT
            self.x1 = event.xdata
            self.y1 = event.ydata
    #        self.xRight = int(event.xdata)
    #        self.yBottom = int(event.ydata)
            self.xRight_Secondary = int(self.x1)
            self.yBottom_Secondary = int(self.y1)
            
            if self.xRight_Secondary < self.xLeft_Secondary:
                temp = self.xRight_Secondary
                self.xRight_Secondary = self.xLeft_Secondary
                self.xLeft_Secondary = temp
            if self.yBottom_Secondary < self.yTop_Secondary:
                temp = self.yBottom_Secondary
                self.yBottom_Secondary = self.yTop_Secondary
                self.yTop_Secondary = temp
            
            if (self.xLeft_Secondary - 3 < 0): self.xLeft_Secondary = 3
            if (self.yTop_Secondary - 3 < 0): self.yTop_Secondary = 3
            if (self.xRight_Secondary + 4 >= self.imageData[0].shape[1]): self.xRight_Secondary = self.imageData[0].shape[1] - 5
            if (self.yBottom_Secondary + 4 >= self.imageData[0].shape[0]): self.yBottom_Secondary = self.imageData[0].shape[0] - 5
            
            self.AOI1_Secondary.SetValue(str(self.xLeft_Secondary))
            self.AOI2_Secondary.SetValue(str(self.yTop_Secondary))
            self.AOI3_Secondary.SetValue(str(self.xRight_Secondary))
            self.AOI4_Secondary.SetValue(str(self.yBottom_Secondary))
            self.AOI_Secondary = [[self.xLeft_Secondary,self.yTop_Secondary],[self.xRight_Secondary,self.yBottom_Secondary]]
            
            self.rect_Secondary.set_width(self.xRight_Secondary - self.xLeft_Secondary)
            self.rect_Secondary.set_height(self.yBottom_Secondary - self.yTop_Secondary)
            self.rect_Secondary.set_xy((self.xLeft_Secondary, self.yTop_Secondary))
        
            self.setAtomImage(defringing = False)   # Redefines the atomImage with the secondary AOI informations
            self.updateAOI_PrimaryImage()
            self.canvas.draw()
            
            self.setAtomNumber()

#        del tempp
        #self.atomNumberInt.SetValue(str("%.0f" % N_intEdge))
        #self.normNcount.SetValue(str("%.0f" % (N_intEdge/((pixelToDistance**2)/crossSection))))
        
            self.setAtomNumber()

    def setAtomNumber(self):
    #def setAtomNumberBox(self):
#        print ""
#        print ""
#        print self.pixelToDistance
#        print self.crossSection
        self.setConstants()
        self.setRawAtomNumber()
        self.atomNumber = self.rawAtomNumber *  (self.pixelToDistance**2)/self.crossSection
#        print self.pixelToDistance
#        print self.crossSection
#        print ""
#        print ""

        #        self.bigNcount.SetValue(str("%.0f" % (rawValue)))
        self.bigNcount2.SetValue(str("%.0f"%(self.rawAtomNumber)))
        self.bigNcount3.SetValue(str("%.3f"%(self.atomNumber/1E6)))
#        print "value////////"
#        print value
#        print "rawAtomNumber////"
#        print self.rawAtomNumber
        
    def calc1DRadialAvgAndRefit(self):
        if self.checkDisplayRadialAvg.GetValue() is False: # Regular summation and fit
            self.x_basis =  np.linspace(self.xLeft_Primary, self.xRight_Primary, self.AOI_PrimaryImage.shape[1])
            self.x_summed = np.sum(self.AOI_PrimaryImage,axis=0)
            self.y_basis =  np.linspace(self.yTop_Primary, self.yBottom_Primary, self.AOI_PrimaryImage.shape[0])
            self.y_summed = np.sum(self.AOI_PrimaryImage,axis=1)

            self.fit()
        
        else:   # radial fit
            xCenter = self.x_center
            yCenter = self.y_center
            if self.isXFitSuccessful is False:
                xCenter = np.argmax(self.x_summed)
            
            if self.isYFitSuccessful is False:
                yCenter = np.argmax(self.y_summed)
            
            yarr = radialAverage(self.AOI_PrimaryImage, center = [xCenter, yCenter], boundary = [self.xLeft_Primary, self.yTop_Primary, self.xRight_Primary, self.yBottom_Primary])
           
            num = len(yarr)
            self.x_basis = np.linspace(xCenter - num + 1, xCenter +  num - 1, 2* num - 2)
            self.x_summed = self.x_peakHeight * np.concatenate((np.flipud(yarr)[:-2], yarr), axis = 0)
            self.fit('x')
        
    def calc1DProfiles(self):
        y_size,x_size = self.AOI_PrimaryImage.shape

        self.x_summed = np.sum(self.AOI_PrimaryImage,axis=0)
        self.x_basis =  np.linspace(self.xLeft_Primary, self.xRight_Primary, x_size)
        self.y_summed = np.sum(self.AOI_PrimaryImage,axis=1)
        self.y_basis = np.linspace(self.yTop_Primary, self.yBottom_Primary, y_size)

    def updateAOI_SecondaryImage(self):
        self.AOI_SecondaryImage = self.atomImage[self.yTop_Primary:self.yBottom_Primary, self.xLeft_Primary:self.xRight_Primary]
        self.setRawAtomNumber()

    def updateAOI_PrimaryImage(self):
#        shape = self.atomImage.shape
#        self.AOIImage = self.atomImage[max(0, self.yTop-3):min(shape[0], self.yBottom+4), max(0, self.xLeft-3):max(shape[1], self.xRight+4)]
        #self.AOI_PrimaryImage = self.atomImage[self.yTop_Primary-3:self.yBottom_Primary+4, self.xLeft_Primary-3:self.xRight_Primary+4]
        self.AOI_PrimaryImage = self.atomImage[self.yTop_Primary:self.yBottom_Primary, self.xLeft_Primary:self.xRight_Primary]
        #self.offsetEdge_Primary = aoiEdge(self.AOI_PrimaryImage, self.leftRightEdge_Primary.GetValue(), self.updownEdge_Primary.GetValue())
        # I have the impression the self.offsetEdge sums what is under the edge box at +/- 3 or 4 pixels... Why?
#        self.calc1DProfiles()
#        self.fit()
#        self.calc1DRadialAvgProfile()
#        self.update1DProfiles()
#        self.updateFittingResults()
        #self.update1DProfilesAndFit()
                   
    # def edgeUpdate_Primary(self):
    #     #shape = self.atomImage.shape
    #     #self.rawAtomNumber = atomNumberWithEdgeOffset(tempp, self.offsetEdge_Primary)
    #     #self.atomNumberInt.SetValue(str("%.0f" % N_intEdge))
    #     #self.normNcount.SetValue(str("%.0f" % (N_intEdge/((pixelToDistance**2)/crossSection))))
    #     self.atomNumberWithSecondaryAOI()
    #     self.setAtomNumber()

    def lightDifferencePerPixel(self):  # Computes the ligth level difference in the secondary AOI between the atom and light shot
        atomLight = np.mean(self.imageData[0][self.yTop_Secondary:self.yBottom_Secondary, self.xLeft_Secondary:self.xRight_Secondary])
        lightLight = np.mean(self.imageData[1][self.yTop_Secondary:self.yBottom_Secondary, self.xLeft_Secondary:self.xRight_Secondary])
        return atomLight/lightLight
    
    def setRawAtomNumber(self):
        try:
            self.rawAtomNumber = np.sum((self.AOI_PrimaryImage > 0)*self.AOI_PrimaryImage)
        except:
            self.rawAtomNumber = np.nan
            
    def displayRadialAvg(self, e):
        self.calc1DRadialAvgAndRefit()
        self.update1DProfiles()
        self.updateFittingResults()
        
    def displayNormalization(self, e):
        self.isNormalizationOn = self.checkNormalization.GetValue()
        self.setDataAndUpdate()
        
    def FermionFitChosen(self, e):
        print("Mode: Fermion Fit")
        self.cleanValue()
        self.fermionResult.SetLabel('Fermion Fit Result')
        self.fText1.SetLabel('Size')
        self.fText2.SetLabel('Fugacity')
        self.tOverTFLabel.SetLabel('T/T_F')

    def BosonFitChosen(self, e):
        print("Mode: Boson Fit")
        self.cleanValue()
        self.fermionResult.SetLabel('Boson Fit Result')
        self.fText1.SetLabel('Thermal Size')
        self.fText2.SetLabel('BEC Size')
        self.tOverTFLabel.SetLabel('BEC fraction')

    def GaussianFitChosen(self, e):
        print("Mode: Gaussian Fit")
        self.cleanValue()


    def cleanValue(self):
        self.fWidth.SetValue('')
        self.fq.SetValue('')
        self.tOverTF.SetValue('')
        self.gCenter.SetValue('')
        self.gSigma.SetValue('')
        #self.atomNumberInt.SetValue('')
        #self.normNcount.SetValue('')
#        self.bigNcount.SetValue('')
        self.gTemperature.SetValue('')
        #self.atomNumberIntFit.SetValue('')

            
    def updateImageOnUI(self, layerNumber, hasFileSizeChanged):
        self.chosenLayerNumber = layerNumber
        if self.isDummyImage:
            self.setCurrentImg(self.imageData[0], hasFileSizeChanged)
            print(np.shape(self.imageData[0]))
            self.currentImg.autoscale()
        else:
            if self.imageData:
                if layerNumber == 4:
                    self.setCurrentImg(self.atomImage, hasFileSizeChanged)
                    self.currentImg.set_clim(vmin=-1, vmax=1)
    #                self.currentImg.autoscale()
    
                else:
                    self.setCurrentImg(self.imageData[layerNumber - 1], hasFileSizeChanged)
                    self.currentImg.autoscale()
                ##
                ##
                ## DO NOT AUTOSCALE THE PROCESSED IMAGE (i.e. layer 4 )
                ##
                ##
    #            self.currentImg.autoscale()
                self.canvas.draw()

    def chooseImg(self, e):
        print("CHOOSED!!!!!")
        start = time.time()
        oldImagesNumber = len(self.imageIDList)
        ind = self.imageListBox.GetSelection()
        print(ind)
        self.imageIDIndex = ind
        self.updateImageIDList()
        newImagesNumber = len(self.imageIDList)
                
#        print oldFileNumber
#        print newFileNumber
        if (oldImagesNumber != newImagesNumber):
            msg = wx.MessageDialog(self, 'Such image file may not exist in the file directory','Index Error', wx.OK)
            if msg.ShowModal() == wx.ID_OK:
                msg.Destroy()
                self.updateImageListBox()

        self.imageID = self.imageIDList[ind] #this is the selected imageID
        print("----the imageID----")
        print(self.imageID)
#        print ""
#        print "+++++++++++++++++++++++++++++++++++++++"
#        print "Y CENTER"
#        print self.y_center
#        print "+++++++++++++++++++++++++++++++++++++++"
#        print ""
        self.setImageIDText()
        self.updateFileInfoBox()
#        self.setData()
#
##        self.imageData = self.imageList[-1-ind][0]
##        self.atomImage = self.imageList[-1-ind][1]
##
#        hasFileSizeChanged = self.checkIfFileSizeChanged()
#        print "sizechange??????????? ---- chooseImg"
#        print hasFileSizeChanged
#
#        # draw the newly set data
#        self.updateImageOnUI(e, self.chosenLayerNumber, hasFileSizeChanged)
#        self.edgeUpdate(e)
        end = time.time()
        print("it took " + str(end - start) + " sec before setDataAndUpdate().......")
        print(self.atomImage)
        self.setDataAndUpdate()

    def showImgValue(self, e):
        if e.xdata and e.ydata:
            x = int(e.xdata)
            y = int(e.ydata)
#            print "x ====" + str(x)
#            print "y ====" + str(y)
            if self.imageData and (x >= 0  and x < self.imageData[0].shape[1]) and (y >= 0 and y < self.imageData[0].shape[0]):
                self.cursorX.SetValue(str(x))
                self.cursorY.SetValue(str(y))
                if self.layer1Button.GetValue():
                    self.cursorZ.SetValue(str(int(self.imageData[0][y][x])))
                elif self.layer2Button.GetValue():
                    self.cursorZ.SetValue(str(int(self.imageData[1][y][x])))
                elif self.layer3Button.GetValue():
                    self.cursorZ.SetValue(str(int(self.imageData[2][y][x])))
                elif self.layer4Button.GetValue():
                    self.cursorZ.SetValue('%0.4f'%self.atomImage[y][x])

   # def fitImage(self, e):
    def fitImage(self):
        format = "%a-%b-%d-%H_%M_%S-%Y"
        today = datetime.datetime.today()
        self.timeString = today.strftime(format)
        
        self.benchmark_startTime=time.time()
        #+str(self.benchmark_startTime)
        if self.readImage():
            print("Begin to fit...")
            #self.showImg(e)
            self.showImg()
        tmp = time.time()
        # print "Read Image totally took " + str(tmp - self.benchmark_startTime)

    def deletePrev2DContour(self):
        if self.quickFitBool==True:
            self.quickFitBool=False
            if self.fitOverlay is not None:
                for coll in self.fitOverlay.collections:
                    coll.remove()
                self.canvas.draw()
            return True
        
        if self.quickFitBool==False:
            self.quickFitBool=True
        return False
        
    def show2DContour(self, e):
        if self.deletePrev2DContour():
            return
#
        y_size, x_size = self.AOI_PrimaryImage.shape
        x_basis = np.linspace(self.xLeft_Primary, self.xRight_Primary, x_size)
        y_basis = np.linspace(self.yTop_Primary, self.yBottom_Primary, y_size)
        x_basis, y_basis = np.meshgrid(x_basis, y_basis)

        ##drawing
        
        ###Center of mass rectangle marker
#        t_rect = matplotlib.patches.Rectangle((x_center,y_center),5, 5,facecolor="none",linewidth=2, edgecolor="#0000ff")
#        #facecolor="none",linewidth=2, edgecolor="#0000ff")
#        self.axes1.add_patch(t_rect)
        g = lambda x,y: np.exp(-1.0*((x - self.x_center)**2)/(2*self.x_width**2))*np.exp(-1.0*((y - self.y_center)**2)/(2*self.y_width**2))
        plot_overlay_data=g((x_basis,y_basis))
        self.fitOverlay = self.axes1.contour(x_basis, y_basis, plot_overlay_data.reshape(y_size, x_size), 8, cmap='afmhot')
        
        self.canvas.draw()
        
    def readImage(self):
        plotMin = 0.0
        plotMax = 0.3
        try:
            if self.autoRunning == False:
                print(self.path)
                if not self.path:
                    print("------------Wrong Folder!--------")
                    return None
                # self.alert
                self.updateLatestImageID()
                fileText = self.imageIDText.GetValue()     # This one is simply "In the database" if not checkLocalFiles
                if (len(fileText) == 0):    # ilf the file name has no length you just pick up the one on top of the list
                    latestImageID = max(self.imageIDList)
                    self.imageID = latestImageID[-1]
                self.setImageIDText()
                
            elif self.autoRunning == True:      # I believe it could simply be replaced by else
                self.updateLatestImageID()
            self.updateImageListBox()
            self.setDataNewIncomingFile()
            
#            if self.autoRunning == True:
##                self.imageList.append([self.imageData, self.atomImage])
#                if len(self.imageList) == 11:
#                    self.imageList.pop(0)
#
            ### Restrict to the are of interest
            print("Successfully read Image")
            return True
        except Exception as err:
            print("Failed to read this image.")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            #print str(err)
            

        ## view fit result
    def showImg(self):
        self.setAtomNumber()    # seemed to be done just beofre in readImage
        if (self.chosenLayerNumber == 4):
            imageToShow = self.atomImage
        else:
            imageToShow = self.imageData[self.chosenLayerNumber - 1]
        # if self.checkLocalFiles:        
        #     hasFileSizeChanged = self.checkIfFileSizeChanged()
        if not self.checkLocalFiles:
            hasFileSizeChanged = False

        self.setCurrentImg(imageToShow, hasFileSizeChanged)
        
        
        #if self.autoRunning:
#        print "Save for snippet server"
            #self.snippetCommunicate(self.rawAtomNumber)
        print("Success ---- ShowImg()")
        self.canvas.draw()
        self.Update()
            
        self.benchmark_endTime=time.time()
        print("This shot took " + str(abs(self.benchmark_startTime-self.benchmark_endTime)) + " seconds")
        gc.collect()



    
    def updateAnalysisDB(self, event): # event is the button click
        self.analysisResults = self.dictionnaryAnalysisResults()
        updateAnalysisOnDB(self.analysisResults, self.imageID)
        self.updateFileInfoBox()
