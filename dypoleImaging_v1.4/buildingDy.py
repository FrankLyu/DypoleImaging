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

from fitTool import *
from Monitor import Monitor
from defringer_v2 import*

from degenerateFitter import*   # This one was missing at first... WHY ???
from selectionRectangle import *
from cmapManager import todayscmap

from camera import Camera, mimicRunning
from config import LOCAL_CAMERA_PATH_FLIR, LOCAL_CAMERA_PATH_ANDOR
from imgFunc_v6 import deleteFiles, readDBData, readFileData

import textwrap
import platform

systemeType = platform.system()     # platform.system() = Darwin for MacOS, otherwise Linux or Windows

# Local funtions for database

from DatabaseCommunication.dbFunctions import getLastImageID, getLastImageIDs, getTimestamp, getLastID, updateNewImage, writeAnalysisToDB, updateAnalysisOnDB, getNCount
from DatabaseCommunication.dbFunctionsC import writeImageToCacheC

# FLIR Camera control
from FLIRCommand.runHardwareTrigger import mainRunHardwareTrigger
#import packages.imagedatamanager as imagedata
#import packages.fitmanager as fit

# Camera run
import FLIRCommand.AcquireAndDisplay as acquire


import threading

class ImageUI(wx.Frame):
    def __init__(self, parent, title):
        super(ImageUI, self).__init__(parent, title = title, size=(1700, 1120))
        
        ## New parameters added by Pierre
        self.checkLocalFiles = False    # True = check the local harddrive, False = looks at the database
        
        self.isDummyImage = False  # when the image is simply a 1 by 1 pixel or that
                                    # no image has yet been selected
        self.cameraPosition = "TEST" # HORIZONTAL or VERTICAL
        self.cameraType = "FLIR" # FLIR or Andor. It is the starting default variable
        #self.camera = Camera(self.cameraType, self.cameraPosition) # check if I can bind that to the original button position
        self.pathWrittenImages = LOCAL_CAMERA_PATH_FLIR # folder where all the images get written by the cameras
        self.listOfValidImagesWaiting = []
        self.imageTimestamp = None
        self.isFluorescenceOn = False
        #self.imageDataManager = imagedata.ImageDataManager(None)
        #self.fitManager = fit.FitManager()
        
        # ROI when you save a cropped image, all the edge pixels will be included so don't start at 0 and start at 1
        self.cropXStart = 801
        self.cropXEnd = 1300
        self.cropYStart = 1
        self.cropYEnd = 2160
        
        # Zoomed imaged based coordinates
        self.xZoomCenter = 50
        self.yZoomCenter = 50
        self.zoomWidth = 20
        
        self.tempAOI1 = 1
        self.tempAOI2 = 1
        self.tempAOI3 = 1
        self.tempAOI4 = 1
        # Binning for automatic finding and fitting of the cloud
        self.binning = 3
        self.AOI_TertiaryWidthRatio = 3
        self.AOI_TertiaryImage = None
        self.AOI_Tertiary = None
        self.smallestTertiaryAOI = 40
        
        ## new parameters added by Hyungmok
        self.atom = 'Dy'
        self.magnification = 4.38
        self.pixelSize = 6.5
        self.clebschGordan = 0.5*(1 + 1/153)
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
        
        self.selectedAOI = 0

        self.fitOverlay = None
        self.quickFitBool = False
        
        self.primaryAOI = selectionRectangle(id_num = 1)
        #self.primaryAOI.position[0] = None
        #self.primaryAOI.position[2] = None
        #self.primaryAOI.position[3] = None
        #self.primaryAOI.position[1] = None
        
        #self.rect_Primary =  None
        # self.Bind(wx.EVT_PAINT, self.OnPaint)
        
        self.secondaryAOI = selectionRectangle(dashed = True)
        self.primaryAOI.attachSecondaryAOI(self.secondaryAOI)
        #self.secondaryAOI.position[0] = None
        #self.secondaryAOI.position[2] = None
        #self.secondaryAOI.position[3] = None
        #self.secondaryAOI.position[1] = None

        self.AOIList = [self.primaryAOI]
        self.doubleAOIs = False

        self.AOI_Primary = [[self.primaryAOI.position[0], self.primaryAOI.position[1]],[self.primaryAOI.position[2], self.primaryAOI.position[3]]]
        self.AOI_Secondary = [[self.secondaryAOI.position[0], self.secondaryAOI.position[1]],[self.secondaryAOI.position[2], self.secondaryAOI.position[3]]]

        #self.rect_Secondary =  None
        self.rect_Tertiary =  None
        
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
        self.TestCamera = wx.RadioButton(self.panel, label="Test")
        self.TestCamera.SetValue(True)
        
        cameraPositionBoxSizer.Add(self.verticalCamera, flag=wx.ALL, border=5)
        cameraPositionBoxSizer.Add(self.horizontalCamera, flag=wx.ALL, border=5)
        cameraPositionBoxSizer.Add(self.TestCamera, flag=wx.ALL, border=5)
        
        self.Bind(wx.EVT_RADIOBUTTON, self.setCameraPosition, id = self.verticalCamera.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.setCameraPosition, id = self.horizontalCamera.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.setCameraPosition, id = self.TestCamera.GetId())
        
        imageCroppedOrNot = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSaveFull = wx.RadioButton(self.panel, label="Save full image", style = wx.RB_GROUP )
        self.buttonSaveCropped = wx.RadioButton(self.panel, label="Save crop")
        self.buttonSaveDummy = wx.RadioButton(self.panel, label="Save dummy")
        #self.Bind(wx.EVT_RADIOBUTTON, self.updateImageOnUI(1, hasFileSizeChanged), id=self.buttonSaveFull.GetId())
        #self.Bind(wx.EVT_RADIOBUTTON, lambda e: self.updateImageOnUI(2, hasFileSizeChanged), id=self.buttonSaveCropped.GetId())
        #self.Bind(wx.EVT_RADIOBUTTON, lambda e: self.updateImageOnUI(3, hasFileSizeChanged), id=self.buttonSaveDummy.GetId())
        imageCroppedOrNot.Add(self.buttonSaveFull, flag=wx.ALL, border=5)
        imageCroppedOrNot.Add(self.buttonSaveCropped, flag=wx.ALL, border=5)
        imageCroppedOrNot.Add(self.buttonSaveDummy, flag=wx.ALL, border=5)
        self.buttonSaveDummy.SetValue(True)
        
        #self.checkBoxSaveDummy = wx.CheckBox(self.panel, label="Save dummy")
        #self.saveDummy = False
        #self.checkBoxSaveDummy.SetValue(False)

        self.startCameraButton = wx.Button(self.panel, label = 'Start FLIR camera')
        self.startCameraButton.Bind(wx.EVT_BUTTON, self.startCamera_trigger)
        self.endCameraButton = wx.Button(self.panel, label = 'End FLIR camera')
        self.endCameraButton.Bind(wx.EVT_BUTTON, self.endCamera_trigger)
        hbox155 = wx.BoxSizer(wx.HORIZONTAL)
        hbox155.Add(self.startCameraButton, flag = wx.ALL, border = 5)
        hbox155.Add(self.endCameraButton, flag = wx.ALL, border = 5)
        
        
        cameraConfigBoxSizer.Add(cameraTypeBoxSizer, flag=wx.ALL| wx.EXPAND, border = 5)
        cameraConfigBoxSizer.Add(cameraPositionBoxSizer, flag=wx.ALL| wx.EXPAND, border = 5)
        #cameraConfigBoxSizer.Add(self.checkBoxSaveDummy, border=5)
        cameraConfigBoxSizer.Add(imageCroppedOrNot, border=5)
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

        ### Fluorescence monitor
        fluorescenceBox = wx.StaticBox(self.panel, label = 'Fluorescence monitor')
        fluorescenceBoxSizer = wx.StaticBoxSizer(fluorescenceBox,  wx.VERTICAL)
        self.snapButton = wx.Button(self.panel, label = 'Snap')
        self.snapButton.Bind(wx.EVT_BUTTON, self.snap)
        self.fluorescenceButton = wx.Button(self.panel, label = 'Turn On')
        self.isFluorescence = False
        self.fluorescenceButton.Bind(wx.EVT_BUTTON, self.autoFluorescenceRun)
        fluorescenceBoxSizer.Add(self.snapButton, flag=wx.ALL|wx.EXPAND, border= 5)
        fluorescenceBoxSizer.Add(self.fluorescenceButton, flag=wx.ALL|wx.EXPAND, border= 5)

        bigfont_fluorescence = wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        fluorescenceNumberText = wx.StaticText(self.panel, label='Total nCount: ')
        self.fluorescenceNumberBox = wx.TextCtrl(self.panel,  style=wx.TE_READONLY|wx.TE_CENTRE, size=(100,34))
        self.fluorescenceNumberBox.SetFont(bigfont_fluorescence)
        fluorescenceBoxSizer.Add(fluorescenceNumberText, flag=wx.ALL, border=5)
        fluorescenceBoxSizer.Add(self.fluorescenceNumberBox, flag=wx.ALL, border=5)
        
        
        self.figure_fluorescence = Figure(figsize = (2,2))
        self.axes_fluorescence = self.figure_fluorescence.add_subplot(111)
        self.axes_fluorescence.set_title('Fluorescence count', fontsize=12)
        for label in (self.axes_fluorescence.get_xticklabels() + self.axes_fluorescence.get_yticklabels()):
            label.set_fontsize(10)
        self.linePlot_fluorescence, = self.axes_fluorescence.plot(np.zeros(20))
        self.canvas_fluorescence = FigureCanvas(self.panel, -1, self.figure_fluorescence)
        fluorescenceBoxSizer.Add(self.canvas_fluorescence, flag=wx.ALL|wx.EXPAND, border=5)

        vbox0.Add(fluorescenceBoxSizer, 0, wx.ALL|wx.EXPAND, 5)


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
                
        self.snippetPath = "~\Dropbox (MIT)\Documents\MIT\dypole-imaging\Andor\snippet.txt"
        snippetText = wx.StaticText(self.panel, label='Text file path for Snippet Server:')
        self.snippetTextBox = wx.TextCtrl(self.panel, value = self.snippetPath)
        self.snippetTextBox.Bind(wx.EVT_TEXT, self.setSnippetPath)
        fittingBoxSizer.Add(snippetText, flag=wx.ALL | wx.EXPAND, border=5)
        fittingBoxSizer.Add(self.snippetTextBox, flag=wx.ALL | wx.EXPAND, border=5)

        listText = wx.StaticText(self.panel, label='Image List')
        self.imageListBox = wx.ListBox(self.panel, size = (265, 100))
        self.Bind(wx.EVT_LISTBOX, self.chooseImg, self.imageListBox)
        fittingBoxSizer.Add(listText, flag=wx.ALL, border=5)
        fittingBoxSizer.Add(self.imageListBox, 1, wx.ALL | wx.EXPAND, border=5)
        self.updateImageListBox()
        vbox0.Add(fittingBoxSizer, 0, wx.ALL|wx.EXPAND, 5)
        # TOF fitting
        # TOFFitBox = wx.StaticBox(self.panel, label = 'TOF fitting')
        # TOFFitBoxSizer = wx.StaticBoxSizer(TOFFitBox, wx.VERTICAL)
        
        # self.TOFFitList = wx.TextCtrl(self.panel, value = str(-1), style = wx.TE_MULTILINE)
        # TOFFitButton= wx.Button(self.panel, label = 'TOF fit')
        # TOFFitButton.Bind(wx.EVT_BUTTON, self.showTOFFit)
        # TOFFitBoxSizer.Add(self.TOFFitList, flag = wx.ALL|wx.EXPAND, border = 5)
        # TOFFitBoxSizer.Add(TOFFitButton, flag = wx.ALL|wx.EXPAND, border = 5)
        # vbox0.Add(TOFFitBoxSizer, 0, wx.ALL|wx.EXPAND, 5)
        
#        self.true_x_width_list = np.zeros(self.iamgeListBox.GetCount())
#        self.true_y_width_list = np.zeros(self.iamgeListBox.GetCount())
        ## update the imageListBox
        

        hbox.Add(vbox0, 2, wx.ALL|wx.EXPAND, 5)  # 2 here means that the relative width of the box will be 2
 
######### images ##################
        
#        self.initImageUI()
        imagesBox = wx.StaticBox(self.panel, label='Images')
        imagesBoxSizer = wx.StaticBoxSizer(imagesBox, wx.VERTICAL)
       
        self.figure = Figure(figsize = (8,8))
#        figure.tight_layout(h_pad=1.0)
        #gs = gridspec.GridSpec(5, 5)
        gs = gridspec.GridSpec(2, 2, width_ratios=(7, 2), height_ratios=(7, 2), wspace = 0.05, hspace = 0.08)
        #gs.update(wspace = 0.05, hspace = 0.05)
        #self.axes1 = figure.add_subplot(gs[:-1, :-1])
        self.axes1 = self.figure.add_subplot(gs[0, 0])
        self.axes1.set_title('Original Image', fontsize=12)
        self.cmap = todayscmap()

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
        
        clebschGordan = wx.StaticText(self.panel, label = "Clebsch")
        self.clebschGordanText = wx.TextCtrl(self.panel, value= str(self.clebschGordan), size=(35,22))
        self.clebschGordanText.Bind(wx.EVT_TEXT, self.setClebschGordan)
        
        atomKind = ['Dy']       # Old thing from BEC 3, we could delete this selection, it used to be ['Na, 'Li']
        self.atomRadioBox = wx.RadioBox(self.panel, choices = atomKind, majorDimension = 1)
        self.atomRadioBox.Bind(wx.EVT_RADIOBOX, self.onAtomRadioClicked)
        
        hbox43.Add(self.atomRadioBox, flag = wx.ALL, border = 5)
        hbox43.Add(magnif, flag = wx.ALL, border = 5)
        hbox43.Add(self.magnif, flag = wx.ALL, border = 5)
        hbox43.Add(pixelSize, flag = wx.ALL, border = 5)
        hbox43.Add(self.pxSize, flag = wx.ALL, border = 5)
        hbox43.Add(clebschGordan, flag = wx.ALL, border = 5)
        hbox43.Add(self.clebschGordanText, flag = wx.ALL, border = 5)  
        
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
        #bigNcountText3 = wx.StaticText(self.panel, label='Atom #\n(million):')
        bigNcountText3 = wx.StaticText(self.panel, label='Atom #:')
        self.bigNcount3 = wx.TextCtrl(self.panel, style=wx.TE_READONLY|wx.TE_CENTRE, size=(115,34))
        bigNcountText4 = wx.StaticText(self.panel, label = 'Atom #2:')
        self.bigNcount4 = wx.TextCtrl(self.panel, style = wx.TE_READONLY|wx.TE_CENTRE, size = (114, 34))
        self.bigNcount4.Enable(False)
        #        self.bigNcount.SetFont(bigfont)
        for (txt, ctrl) in zip([bigNcountText2, bigNcountText3, bigNcountText4], [self.bigNcount2, self.bigNcount3, self.bigNcount4]):
            ctrl.SetFont(bigfont)
            hbox43.Add(txt, flag=wx.ALL, border=5)
            hbox43.Add(ctrl, flag=wx.ALL, border=5)

#        atomNumDisplayBoxSizer.Add(hbox44, flag=wx.ALL|wx.EXPAND)
        
        ##
#        atomNumBoxSizer.Add(atomNumParamBoxSizer, flag=wx.ALL|wx.EXPAND, border=5)
#        atomNumBoxSizer.Add(atomNumDisplayBoxSizer, flag=wx.ALL|wx.EXPAND, border=5)
        imagesBoxSizer.Add(atomNumBoxSizer, flag=wx.ALL| wx.EXPAND, border=5)


        ### DIALS FOR SELECTING AOI SETS
        self.aoiDialBox = wx.StaticBox(self.panel, label = "AOI Controls")
        aoiDialBoxSizer = wx.StaticBoxSizer(self.aoiDialBox, wx.HORIZONTAL)
        hbox15_Primary = wx.BoxSizer(wx.HORIZONTAL)

        # self.toggleAOIButton = wx.Button(self.panel, label = "Moving N1 ROI")
        # self.toggleAOIButton.Bind(wx.EVT_BUTTON, self.toggleActiveAOI)
        # hbox15_Primary.Add(self.toggleAOIButton)

        activateDoubleAOICheck = wx.CheckBox(self.panel, label = "Use two AOI's?")
        activateDoubleAOICheck.Bind(wx.EVT_CHECKBOX, self.activateDoubleAOI)
        hbox15_Primary.Add(activateDoubleAOICheck)

        self.AOIRadioBox = wx.RadioBox(self.panel, choices = ['1', '2'], majorDimension = 0)
        # self.AOIRadioBox.Bind(wx.EVT_RADIOBOX, lambda e: self.toggleAOISelection())
        self.AOIRadioBox.Enable(False)
        hbox15_Primary.Add(self.AOIRadioBox)

        self.panel.Bind(wx.EVT_MIDDLE_DOWN, lambda e: self.toggleAOISelection())

        aoiDialBoxSizer.Add(hbox15_Primary, flag = wx.EXPAND|wx.ALL, border = 5)
        imagesBoxSizer.Add(aoiDialBoxSizer, flag = wx.ALL|wx.EXPAND, border = 5)

        ### PRIMARY AOI
        aoi_Box = wx.StaticBox(self.panel, label = "Manual AOI")
        hbox14_Primary = wx.BoxSizer(wx.HORIZONTAL)
        aoi_BoxSizer = wx.StaticBoxSizer(aoi_Box, wx.HORIZONTAL)
        aoi_PrimaryText = wx.StaticText(self.panel, label = 'Primary AOI: (x,y)->(x,y)')

        hbox14_Primary.Add(aoi_PrimaryText, flag=wx.ALL, border=5)
        self.AOI1_Primary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
        self.AOI2_Primary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
        self.AOI3_Primary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
        self.AOI4_Primary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
        hbox14_Primary.Add(self.AOI1_Primary, flag=wx.ALL, border=2)
        hbox14_Primary.Add(self.AOI2_Primary, flag=wx.ALL, border=2)
        hbox14_Primary.Add(self.AOI3_Primary, flag=wx.ALL, border=2)
        hbox14_Primary.Add(self.AOI4_Primary, flag=wx.ALL, border=2)
        self.AOI1_Primary.Bind(wx.EVT_TEXT, self.settempAOI1)
        self.AOI2_Primary.Bind(wx.EVT_TEXT, self.settempAOI2)
        self.AOI3_Primary.Bind(wx.EVT_TEXT, self.settempAOI3)
        self.AOI4_Primary.Bind(wx.EVT_TEXT, self.settempAOI4)
        aoi_BoxSizer.Add(hbox14_Primary, flag=wx.EXPAND|wx.ALL, border=5)
        
        ### SECONDARY AOI
        #aoi_SecondaryBox = wx.StaticBox(self.panel)
        hbox14_Secondary = wx.BoxSizer(wx.HORIZONTAL)
        #aoi_SecondaryBoxSizer = wx.StaticBoxSizer(aoi_Box, wx.HORIZONTAL)
        aoi_SecondaryText = wx.StaticText(self.panel, label = 'Secondary AOI: (x,y)->(x,y)')
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
        
        self.checkBoxAutoAOI = wx.CheckBox(self.panel, label=" Auto AOI?")
        self.checkBoxAutoAOI.SetValue(False)
        aoi_BoxSizer.Add(self.checkBoxAutoAOI, flag=wx.EXPAND|wx.ALL, border=5)
        
        self.updateButton = wx.Button(self.panel, label = 'Update pAOI')
        self.updateButton.Bind(wx.EVT_BUTTON, self.typedAOI)
        aoi_BoxSizer.Add(self.updateButton, flag=wx.ALL|wx.EXPAND, border= 5)

        hbox43_Secondary = wx.BoxSizer(wx.HORIZONTAL)
        aoi_BoxSizer.Add(hbox43_Secondary,flag=wx.ALL|wx.EXPAND)

        imagesBoxSizer.Add(aoi_BoxSizer, flag=wx.ALL| wx.EXPAND, border= 5)

                
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
        
       
        # CHANGE THIS LINE TO ADD BACK THE FITTING RESULT DISPLAYER
        # imagesBoxSizer.Add(fittingResultDisplaySizer, flag=wx.ALL| wx.EXPAND, border=5)
        ## final step to add everything
        hbox.Add(imagesBoxSizer, 4, wx.ALL|wx.EXPAND)




        vbox2 = wx.BoxSizer(wx.VERTICAL)    # this is the file vertical box
        
        fileBox = wx.StaticBox(self.panel, label = "File")
        fileBoxSizer = wx.StaticBoxSizer(fileBox, wx.VERTICAL)

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
        
        
        # image zoom
        
        imageZoomBox = wx.StaticBox(self.panel, label = "Image zoom")
        imageZoomBoxSizer = wx.StaticBoxSizer(imageZoomBox, wx.VERTICAL)
        
        self.figureZoom = Figure(figsize = (4,4))
        self.axesZoom = self.figureZoom.add_subplot()
        self.axesZoom.set_title('Zoomed Image', fontsize=12)
        for label in (self.axesZoom.get_xticklabels() + self.axesZoom.get_yticklabels()):
            label.set_fontsize(10)
        
        self.canvasZoom = FigureCanvas(self.panel, -1, self.figureZoom)
        imageZoomBoxSizer.Add(self.canvasZoom, flag=wx.ALL|wx.EXPAND, border=5)
        self.canvasZoom.mpl_connect('motion_notify_event', self.showImgValueZoom)
        hboxZoomInput = wx.BoxSizer(wx.HORIZONTAL)
        xZoomCenterText = wx.StaticText(self.panel, label='X center:')
        self.xZoomCenterBox = wx.TextCtrl(self.panel, value = str(self.xZoomCenter), style=wx.TE_CENTRE, size = (50, 22))
        self.xZoomCenterBox.Bind(wx.EVT_TEXT, self.setZoomCenterX)
        yZoomCenterText = wx.StaticText(self.panel, label='Y center:')
        self.yZoomCenterBox = wx.TextCtrl(self.panel, value = str(self.yZoomCenter), style=wx.TE_CENTRE, size = (50, 22))
        self.yZoomCenterBox.Bind(wx.EVT_TEXT, self.setZoomCenterY)
        zoomWidthText = wx.StaticText(self.panel, label='Width:')
        self.zoomWidthBox = wx.TextCtrl(self.panel, value = str(self.zoomWidth), style=wx.TE_CENTRE, size = (50, 22))
        self.zoomWidthBox.Bind(wx.EVT_TEXT, self.setZoomWidth)
        
        hboxZoomInput.Add(xZoomCenterText, flag=wx.ALL, border=5)
        hboxZoomInput.Add(self.xZoomCenterBox, flag=wx.ALL, border=5)
        hboxZoomInput.Add(yZoomCenterText, flag=wx.ALL, border=5)
        hboxZoomInput.Add(self.yZoomCenterBox, flag=wx.ALL, border=5)
        hboxZoomInput.Add(zoomWidthText, flag=wx.ALL, border=5)
        hboxZoomInput.Add(self.zoomWidthBox, flag=wx.ALL, border=5)
        
        imageZoomBoxSizer.Add(hboxZoomInput, flag=wx.TE_CENTRE| wx.EXPAND)

        
        hboxZoomOutput = wx.BoxSizer(wx.HORIZONTAL)
        stX_Zoom = wx.StaticText(self.panel, label='X:')
        self.cursorX_Zoom = wx.TextCtrl(self.panel,  style=wx.TE_READONLY|wx.TE_CENTRE, size = (50, 22))
        stY_Zoom = wx.StaticText(self.panel, label='Y:')
        self.cursorY_Zoom = wx.TextCtrl(self.panel, style=wx.TE_READONLY|wx.TE_CENTRE,  size = (50, 22))
        stZ_Zoom = wx.StaticText(self.panel, label='Value:')
        self.cursorZ_Zoom = wx.TextCtrl(self.panel, style=wx.TE_READONLY|wx.TE_CENTRE,  size = (80, 22))
        self.cursorX_Zoom.SetFont(boldFont)
        self.cursorY_Zoom.SetFont(boldFont)
        self.cursorZ_Zoom.SetFont(boldFont)
        hboxZoomOutput.Add(stX_Zoom, flag=wx.ALL, border=5)
        hboxZoomOutput.Add(self.cursorX_Zoom, flag=wx.ALL, border=5)
        hboxZoomOutput.Add(stY_Zoom, flag=wx.ALL, border=5)
        hboxZoomOutput.Add(self.cursorY_Zoom, flag=wx.ALL, border=5)
        hboxZoomOutput.Add(stZ_Zoom, flag=wx.ALL, border=5)
        hboxZoomOutput.Add(self.cursorZ_Zoom, flag=wx.ALL, border=5)
        
        imageZoomBoxSizer.Add(hboxZoomOutput, flag=wx.TE_CENTRE| wx.EXPAND)
        vbox2.Add(imageZoomBoxSizer,flag=wx.ALL|wx.TE_CENTRE| wx.EXPAND, border = 5)
        
        
        hbox.Add(vbox2, 2, wx.ALL|wx.EXPAND, 5)  # 2 here means that the relative width of the box will be 2


        self.panel.SetSizer(hbox)
        
        

        # added by Pierre, to start with a non-null image
        
        print("L image courante est " + str(self.currentImg))



    def updateFileInfoBox(self):
        self.fileInfoImageIDBox.SetValue(str(self.imageID))
        self.updateFileInfoFromDB()
        self.fileInfoTimestampBox.SetValue(self.imageTimestamp)
        self.fileInfoNCountBox.SetValue(np.format_float_scientific(getNCount(self.imageID), precision = 2))
        
    def updateFileInfoFromDB(self):
        self.imageTimestamp = getTimestamp(self.imageID)
    
        
    def initializeDummyData(self):
        def generateNoise(shape):
            return np.maximum( np.random.normal(10, 2, shape), np.zeros(shape) )

        size = 500
        sigmax, sigmay = 10, 20
        X, Y = np.meshgrid(np.arange(size), np.arange(size))
        dummyPWA = 256 * (1 - 0.8*np.exp(-(X-size/2)**2/(2*sigmax**2) - (Y-size/2)**2/(2*sigmay**2))) - generateNoise(np.shape(X))
        dummyPWOA = 256 * np.ones_like(X) - generateNoise(np.shape(X))
        dummyDark = generateNoise(np.shape(X))
        self.imageData = [dummyPWA, dummyPWOA, dummyDark]
        self.atomImage = -np.log((dummyPWA - dummyDark) / (dummyPWOA - dummyDark))

        
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
            self.defringer.setRoiIndex(self.primaryAOI.position)
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
        activeAOI = self.primaryAOI
        temp = str(int(activeAOI.x_peakHeight)) + ",  " + str(int(activeAOI.y_peakHeight))
        self.peakBox.SetValue(temp)
        
    def updateTrueWidths(self):
        activeAOI = self.primaryAOI
        activeAOI.true_x_width = activeAOI.x_width * self.pixelToDistance
        activeAOI.true_y_width = activeAOI.y_width * self.pixelToDistance
        
        activeAOI.true_x_width_std = activeAOI.x_width_std * self.pixelToDistance
        activeAOI.true_y_width_std = activeAOI.y_width_std * self.pixelToDistance

        print("")
        print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(" The true X width = " + str("%.3f"%(activeAOI.true_x_width*1E6)) + " um / " + str("%.3f"%(activeAOI.true_x_width_std*1E6)) + " um")
        print(" The true Y width = " + str("%.3f"%(activeAOI.true_y_width*1E6)) + " um / " + str("%.3f"%(activeAOI.true_y_width_std*1E6)) + " um")
        
        try:
            std_avg = (activeAOI.true_x_width_std/activeAOI.true_x_width + activeAOI.true_y_width_std/activeAOI.true_y_width)/2
        except Exception as ex:
            print(ex)
            std_avg = 0
        print(" 2 x (std/avg) averaged between x and y = " + str("%.3f"%(2. * std_avg)))
        print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("")

        temp = str("%.1f"%(activeAOI.true_x_width*1E6)) +",   " + str("%.1f"%(activeAOI.true_y_width*1E6))
        self.widthBox.SetValue(temp)
              
    def updateTemp(self):
#        self.updateTrueWidths()
        activeAOI = self.primaryAOI
        if activeAOI.isXFitSuccessful is False:
            activeAOI.true_x_width = 0
        if activeAOI.isYFitSuccessful is False:
            activeAOI.true_y_width = 0

        ## temperature calculation with trap frequencies
        activeAOI.temperature[0] = 1E+6 * self.mass *(activeAOI.true_x_width* 2 * np.pi * self.xTrapFreq)**2/(kB * (1 + (2* np.pi* self.xTrapFreq * self.TOF * 1E-3)**2))
        activeAOI.temperature[1] = 1E+6 * self.mass *(activeAOI.true_y_width* 2 * np.pi * self.yTrapFreq)**2/(kB * (1 + (2* np.pi* self.yTrapFreq * self.TOF * 1E-3)**2))

        temp = "(" + str("%.3f"%(activeAOI.temperature[0])) +", " + str("%.3f"%(activeAOI.temperature[1])) + ")"
        self.tempBox.SetValue(temp)

        ## long time limit calculation
        activeAOI.tempLongTime[0] = 1E+6 * self.mass *(activeAOI.true_x_width*1E+3/self.TOF)**2/kB
        activeAOI.tempLongTime[1] = 1E+6 * self.mass *(activeAOI.true_y_width*1E+3/self.TOF)**2/kB
        
        temp2 = "(" + str("%.3f"%(activeAOI.tempLongTime[0])) +", " + str("%.3f"%(activeAOI.tempLongTime[1])) + ")"
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
        cmap = todayscmap()
        if hasFileSizeChanged or self.currentImg is None:
#            print("====1====")
            print(self.currentImg)
            print(data)
            print("showing image")
            self.axes1.cla()
            self.currentImg = self.axes1.imshow(data, cmap=self.cmap, aspect='equal', vmin=-0.1, vmax=0.3)
            self.setZoomImage(data)
#            self.currentImg.autoscale()
#            print("====2====")
            print(self.currentImg)
        else:
            print(data)
            print("reshowing that image")
            self.axes1.cla()
            self.currentImg = self.axes1.imshow(data, cmap=self.cmap, aspect='equal', vmin=-0.1, vmax=0.3)
            self.setZoomImage(data)
        self.initializeAOI()
    
    def setZoomedCoordinates(self):
        self.xMinZoom = self.xZoomCenter - self.zoomWidth//2
        self.xMaxZoom = self.xZoomCenter + self.zoomWidth//2
        self.yMinZoom = self.yZoomCenter - self.zoomWidth//2
        self.yMaxZoom = self.yZoomCenter + self.zoomWidth//2
        
    def setZoomImage(self, data):
        self.setZoomedCoordinates()
        dataZoom = data[self.yMinZoom:self.yMaxZoom, self.xMinZoom:self.xMaxZoom]
        self.axesZoom.cla()
        self.currentZoomImage = self.axesZoom.imshow(dataZoom, cmap=self.cmap, aspect='equal', vmin=-0.1, vmax=0.3, extent=[self.xMinZoom, self.xMaxZoom, self.yMaxZoom, self.yMinZoom])
        #self.axesZoom.set_xticks(list(range(self.xMinZoom, self.xMaxZoom + 1, self.zoomWidth//5)))
        #self.axesZoom.set_yticks(list(range(self.yMinZoom, self.yMaxZoom + 1, self.zoomWidth//5)))
        self.canvasZoom.draw()
        
    def setZoomCenterX(self, e):
        try:
            value = int(e.GetEventObject().GetValue())
            if value > 0:
                self.xZoomCenter = value
                self.setZoomImage(self.atomImage)
        except:
            pass
                
    def setZoomCenterY(self, e):
        try:
            value = int(e.GetEventObject().GetValue())
            if value > 0:
                self.yZoomCenter = value
                self.setZoomImage(self.atomImage)
        except:
            pass
        
    def setZoomWidth(self, e):
        try:
            value = int(e.GetEventObject().GetValue())
            if value > 0:
                self.zoomWidth = value
                self.setZoomImage(self.atomImage)
        except:
            pass
    
    def settempAOI1(self,e):
        try:
            value = int(e.GetEventObject().GetValue())
            if value > 0:
                self.tempAOI1 = value
        except:
            pass

    def settempAOI2(self,e):
        try:
            value = int(e.GetEventObject().GetValue())
            if value > 0:
                self.tempAOI2 = value
        except:
            pass

    def settempAOI3(self,e):
        try:
            value = int(e.GetEventObject().GetValue())
            if value > 0:
                self.tempAOI3 = value
        except:
            pass

    def settempAOI4(self,e):
        try:
            value = int(e.GetEventObject().GetValue())
            if value > 0:
                self.tempAOI4 = value
        except:
            pass
    

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
        self.imageAngle = float(rotation)
        
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
    
    def setClebschGordan(self, e):
        mg = e.GetEventObject()
        self.clebschGordan = float(mg.GetValue())
        
        self.setConstants()
        self.setAtomNumber()
        self.updateFittingResults()
        
        print("CLEBSCH GORDAN:")
        print(self.clebschGordan)
    
    def setConstants(self):
        self.pixelToDistance = self.pixelSize / self.magnification * 10**-6
        
        massUnit = 1.66E-27
        wavelength = 421E-9
        self.mass = 164*massUnit
        self.crossSection = 6. * np.pi * (wavelength/(2*np.pi))**2 * self.clebschGordan

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
            
            
    def getLastIDinDB(self, n = 20):
        return getLastImageIDs(n)
    
    
    def setImageIDText(self):
        self.imageIDText.SetValue('In the database')

    def updateLatestImageID(self):
        self.updateImageIDList()
        self.imageID = self.imageIDList[-1] #this is the filename
        self.setImageIDText()

    def isAOI_PrimaryOutside(self):
        shape = self.atomImage.shape
        flag = self.primaryAOI.isOutside(shape)
        return flag
       
    def isAOI_SecondaryOutside(self):
        flag = False
        shape = self.atomImage.shape
        if int(self.AOI1_Secondary.GetValue()) >= shape[1] or int(self.AOI1_Secondary.GetValue()) < 0:
            print("case 1")
            self.secondaryAOI.position[0] = 20
            flag = True
        
        if int(self.AOI2_Secondary.GetValue()) >= shape[0] or int(self.AOI2_Secondary.GetValue()) < 0:
            print("case 2")
            self.secondaryAOI.position[1] = 20
            flag = True
                
        if int(self.AOI3_Secondary.GetValue()) >= shape[1] or int(self.AOI3_Secondary.GetValue()) < 0 :
            print("case 3")
            self.secondaryAOI.position[2] = shape[1] - 20
            flag = True
            
        if int(self.AOI4_Secondary.GetValue()) >= shape[0] or int(self.AOI4_Secondary.GetValue()) < 0:
            print("case 4")
            self.secondaryAOI.position[3] = shape[0] - 20
            flag = True
        return flag
            

                   
    def initializeAOI(self):
        if (self.isAOI_PrimaryOutside() and self.isAOI_SecondaryOutside()):
            print("#################################################")
            print("AOI_Primary initializing....")
            print("#################################################")

            self.AOI1_Primary.SetValue(str(self.primaryAOI.position[0]))
            self.AOI2_Primary.SetValue(str(self.primaryAOI.position[1]))
            self.AOI3_Primary.SetValue(str(self.primaryAOI.position[2]))
            self.AOI4_Primary.SetValue(str(self.primaryAOI.position[3]))

            print("#################################################")
            print("AOI_Secondary initializing....")
            print("#################################################")

            self.AOI1_Secondary.SetValue(str(self.secondaryAOI.position[0]))
            self.AOI2_Secondary.SetValue(str(self.secondaryAOI.position[1]))
            self.AOI3_Secondary.SetValue(str(self.secondaryAOI.position[2]))
            self.AOI4_Secondary.SetValue(str(self.secondaryAOI.position[3]))
            
            for activeAOI in self.AOIList:
                # self.axes1.add_patch(activeAOI.patch)
                self.drawAOIPatch(activeAOI)
                if hasattr(activeAOI, "secondaryAOI"):
                    self.drawAOIPatch(activeAOI.secondaryAOI)
                    # self.axes1.add_patch(activeAOI.secondaryAOI.patch)
                    
                    # activeAOI.secondaryAOI.update_patch()

            self.canvas.draw()
            
            self.setAtomNumber()
    
        else:   # This whole thing should be simplified by looking at isAOI_PrimaryOutside and rationalize things
            print("REUSE THE PREVIOUS AOI")
            print("#################################################")
            print("AOI_Primary initializing....")
            print("#################################################")
            self.AOI1_Primary.SetValue(str(self.primaryAOI.position[0]))
            self.AOI2_Primary.SetValue(str(self.primaryAOI.position[1]))
            self.AOI3_Primary.SetValue(str(self.primaryAOI.position[2]))
            self.AOI4_Primary.SetValue(str(self.primaryAOI.position[3]))
           
            print("#################################################")
            print("AOI_Secondary initializing....")
            print("#################################################")
            self.AOI1_Secondary.SetValue(str(self.secondaryAOI.position[0]))
            self.AOI2_Secondary.SetValue(str(self.secondaryAOI.position[1]))
            self.AOI3_Secondary.SetValue(str(self.secondaryAOI.position[2]))
            self.AOI4_Secondary.SetValue(str(self.secondaryAOI.position[3]))

            for activeAOI in self.AOIList:
                # self.axes1.add_patch(activeAOI.patch)
                # activeAOI.update_patch()
                self.drawAOIPatch(activeAOI)
                if hasattr(activeAOI, "secondaryAOI"):
                    self.drawAOIPatch(activeAOI.secondaryAOI)
                    # self.axes1.add_patch(activeAOI.secondaryAOI.patch)
            
            self.canvas.draw()
            
            self.setAtomNumber()
        
    def applyFilter(self):
        self.isMedianFilterOn = self.checkMedianFilter.GetValue()
        self.setDataAndUpdate()
          
    def update1DProfilesAndFit(self, i = 0):
        if not self.checkBoxAutoAOI.GetValue():  # this is the regular fitting on the preselected AOI
            self.calc1DProfiles()
            self.calc1DRadialAvgAndRefit()
            self.update1DProfiles()
            self.updateFittingResults()
        else:   # we use here the binning
            self.backUpPrimaryAOI()
            self.setPrimaryBinImage()
            self.fitPrimaryBinImage()
            self.setPrimaryImageAfterBinning()
            self.drawTertiaryAOI()
            #self.xLeft_Tertiary, self.xRight_Tertiary, self.yLeft_Tertiary, self.yRight_Tertiary = self.setTertiaryAOI()
            self.calc1DProfiles()
            self.calc1DRadialAvgAndRefit()
            self.update1DProfiles()
            self.updateFittingResults()
            self.reloadPrimaryAOI()
    
    def binImage(self, image, binning): # I should revome this function from the classe
        ySize, xSize = np.shape(image)
        ySizeSmall = ySize//binning
        xSizeSmall = xSize//binning
        imageSmall = np.empty((ySizeSmall,xSizeSmall))   
        print(ySize, xSize, ySizeSmall, xSizeSmall)
        for smallIndexY, indexY in enumerate(np.arange(0,ySize,binning)[:-1]):  # waisting the last line for the sake of simplicity
            for smallIndexX, indexX in enumerate(np.arange(0,xSize,binning)[:-1]):
                imageSmall[smallIndexY,smallIndexX] = np.mean(image[indexY:indexY+binning,indexX:indexX+binning])
        return imageSmall
    
    
    def setPrimaryBinImage(self):
        self.AOI_PrimaryBinImage = self.binImage(self.AOI_PrimaryImage, self.binning)
    
    def fitPrimaryBinImage(self):
        self.x_basis_bin =  np.linspace(self.primaryAOI.position[0], self.primaryAOI.position[2], self.AOI_PrimaryBinImage.shape[1])
        self.x_basis_bin =  np.linspace(0, self.AOI_PrimaryBinImage.shape[1], self.AOI_PrimaryBinImage.shape[1])
        self.x_summed_bin = np.sum(self.AOI_PrimaryBinImage,axis=0)
        self.y_basis_bin =  np.linspace(self.primaryAOI.position[1], self.primaryAOI.position[3], self.AOI_PrimaryBinImage.shape[0])
        self.y_basis_bin =  np.linspace(0, self.AOI_PrimaryBinImage.shape[0], self.AOI_PrimaryBinImage.shape[0])
        self.y_summed_bin = np.sum(self.AOI_PrimaryBinImage,axis=1)
        self.x_center_bin, self.x_width_bin, self.x_offset_bin, self.x_peakHeight_bin, self.x_fitted_bin, self.isXFitSuccessful_bin, self.x_slope_bin, err_x = gaussianFit(self.x_basis_bin, self.x_summed_bin, aoi = [[0,0],[0,0]], axis = 'x')
        self.y_center_bin, self.y_width_bin, self.y_offset_bin, self.y_peakHeight_bin, self.y_fitted_bin, self.isYFitSuccessful_bin, self.y_slope_bin, err_y = gaussianFit(self.y_basis_bin, self.y_summed_bin, aoi = [[0,0],[0,0]], axis = 'y')
    
    def backUpPrimaryAOI(self):
        pass

    def reloadPrimaryAOI(self):
        pass
    
    def setPrimaryImageAfterBinning(self):
        x_center = self.primaryAOI.position[0] + int(self.binning*(self.x_center_bin + 1/2))
        y_center = self.primaryAOI.position[1] + int(self.binning*(self.y_center_bin + 1/2))
        x_width = int(self.binning*self.AOI_TertiaryWidthRatio*self.x_width_bin)
        y_width = int(self.binning*self.AOI_TertiaryWidthRatio*self.y_width_bin)
        self.primaryAOI.position[0] = x_center - x_width
        self.primaryAOI.position[2] = x_center + x_width
        self.primaryAOI.position[1] = y_center - y_width
        self.primaryAOI.position[3] = y_center + y_width
        self.checkTertiarySmallerThanPrimary()
        self.AOI_Primary = [[self.primaryAOI.position[0], self.primaryAOI.position[1]],[self.primaryAOI.position[2], self.primaryAOI.position[3]]]
        self.AOI_PrimaryImage = self.atomImage[self.primaryAOI.position[1]:self.primaryAOI.position[3], self.primaryAOI.position[0]:self.primaryAOI.position[2]]
        self.AOI_Tertiary = [[self.primaryAOI.position[0], self.primaryAOI.position[1]],[self.primaryAOI.position[2], self.primaryAOI.position[3]]]
        self.AOI_TertiaryImage = self.atomImage[self.primaryAOI.position[1]:self.primaryAOI.position[3], self.primaryAOI.position[0]:self.primaryAOI.position[2]]
        # i'm doing this weird thing of having a tertiary image just here in order to have the correct atom counting
        # since setAtomNumber is called multiple times in the code, while still having all fitting capacities with using the Primary
        # imaged modified, and then set back to the normal one. THis should be changed in the v2

    def checkTertiarySmallerThanPrimary(self):
        pass
        
            
    def drawTertiaryAOI(self):
        pass
        
    def fit(self, axis = 'xy'):
        try:
            self.doGaussianFit(axis)
            activeAOI = self.primaryAOI
            print("x center is " + str(activeAOI.x_center))
            print("x width is" + str(activeAOI.x_width))
            print("")
            print("y center is " + str(activeAOI.y_center))
            print("y width is " + str(activeAOI.y_width))
            
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
                for activeAOI in self.AOIList:
                    activeAOI.atomNumFromFitX = activeAOI.atomNumFromGaussianX
                    activeAOI.atomNumFromFitY = activeAOI.atomNumFromGaussianY
#                return
#            elif self.fitMethodGaussian.GetValue():
##                self.doGaussianFit(axis)
#                print("do nothing by default..")
        except IndentationError as err:
            print("------ Fitting Failed -------")
#            msg = wx.MessageDialog(self, 'Non-least square fit of python scipy library failed..','Fitting Error', wx.OK)
#            if msg.ShowModal() == wx.ID_OK:
#                msg.Destroy()
    
    def doGaussianFit(self, axis = 'xy'):
        if axis == 'xy': # Regular fit on 2 axis
            for activeAOI in self.AOIList:
                activeAOI.x_center, activeAOI.x_width, activeAOI.x_offset, activeAOI.x_peakHeight, activeAOI.x_fitted, activeAOI.isXFitSuccessful, activeAOI.x_slope, err_x = gaussianFit(activeAOI.x_basis, activeAOI.x_summed, activeAOI, axis = 'x')
                activeAOI.atomNumFromGaussianX = activeAOI.x_peakHeight *np.sqrt(2 * np.pi) * activeAOI.x_width * (self.pixelToDistance**2)/self.crossSection
                activeAOI.x_width_std = err_x[2]
                activeAOI.y_center, activeAOI.y_width, activeAOI.y_offset, activeAOI.y_peakHeight, activeAOI.y_fitted, activeAOI.isYFitSuccessful, activeAOI.y_slope , err_y= gaussianFit(activeAOI.y_basis, activeAOI.y_summed, activeAOI, axis = 'y')
                activeAOI.atomNumFromGaussianY = activeAOI.y_peakHeight *np.sqrt(2 * np.pi) * activeAOI.y_width * (self.pixelToDistance**2)/self.crossSection
                activeAOI.y_width_std = err_y[2]
            
        elif axis == 'x': # regular fit on only one of the axis
            self.x_center, self.x_width, self.x_offset, self.x_peakHeight, self.x_fitted, self.isXFitSuccessful, self.x_slope, err_x = gaussianFit(self.x_basis, self.x_summed, self.AOI_Primary, axis = 'x')
            self.atomNumFromGaussianX = self.x_peakHeight *np.sqrt(2 * np.pi) * self.x_width * (self.pixelToDistance**2)/self.crossSection
            self.x_width_std = err_x[2]
        else:
            self.y_center, self.y_width, self.y_offset, self.y_peakHeight, self.y_fitted, self.isYFitSuccessful, self.y_slope, err_y = gaussianFit(self.y_basis, self.y_summed, self.AOI_Primary, axis = 'y')
            self.atomNumFromGaussianY = self.y_peakHeight *np.sqrt(2 * np.pi) * self.y_width * (self.pixelToDistance**2)/self.crossSection
            self.y_width_std = err_y[2]
   
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
            lightDifferencePerPixel = self.lightDifferencePerPixel()
            correctedNoAtom = self.imageData[1]*lightDifferencePerPixel - self.imageData[2]
    
        if correctedNoAtom is None:
            correctedNoAtom = self.imageData[1] - self.imageData[2]
    
        absorbImg = np.maximum(self.imageData[0]-self.imageData[2], .1)/(np.maximum(correctedNoAtom, .1))
        ###  Replace extremely low transmission pixels with a minimum meaningful transmission. 
        self.atomImage = np.maximum(absorbImg, np.exp(-9))
        
    def setRawDataFromDB(self):
        #defringing = self.checkApplyDefringing.GetValue()
        defringing = False # This need to be changed and debugged
        del self.imageData
        time_before = time.time()
        self.imageData = readDBData(self.imageID, [defringing, self.betterRef])
        print("IT TOOK " + str(round((time.time()-time_before),3)) + " SECONDS TO READ THE IMAGE")
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
                    except Exception:
                        raise Exception("======= PCA ERROR ========")
                    
                if gaussianFilter is True:
                    try:
                        print("1111111111")
                        tempp = -np.log(absorbImg)
                        print("22222222222")
                        signal = tempp[self.primaryAOI.position[1]:self.primaryAOI.position[3], self.primaryAOI.position[0]:self.primaryAOI.position[2]]
                        print(signal)
                        print("33333333333")
                        filtered = gaussian_filter(tempp, 2, order = 0, truncate = 2)
                        print("44444444444")
                        print("55555555555")
                        temp = filtered
                        
                        print('====== Gaussian filter success ======')
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
                    temp = -np.log(createNormalizedAbsorbImg(self.imageData, self.primaryAOI))
        
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
        self.initializeAOI() # does setAtomNumber at the end (but not yet third AOI)
        [aoi.update_image(self.imageData) for aoi in self.AOIList]

        ## set self.AOIImage, which is the image array confined in the AOI
        self.updateAOI_PrimaryImage()
        self.update1DProfilesAndFit()
        self.updateFittingResults()
        print("Done with setFitting and setting atom number")
        print(self.atomNumber)
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
        # if (self.currentXProfile is not None):
        #     self.axes2.lines.remove(self.currentXProfile)

        # if (self.currentXProfileFit is not None):
        #     self.axes2.lines.remove(self.currentXProfileFit)

        # if (self.currentYProfile is not None):
        #     self.axes3.lines.remove(self.currentYProfile)

        # if (self.currentYProfileFit is not None):
        #     self.axes3.lines.remove(self.currentYProfileFit)
        self.axes2.clear()
        self.axes3.clear()
        for activeAOI in self.AOIList:
            ## if the fitting failed, show flat lines
            if activeAOI.isXFitSuccessful is False:
                activeAOI.x_fitted = activeAOI.x_offset * np.ones(activeAOI.x_summed.shape[0])
                activeAOI.x_peakHeight = 0
                activeAOI.x_width = 0
                print("x_width has been set to 0")
            if activeAOI.isYFitSuccessful is False:
                activeAOI.y_fitted = activeAOI.y_offset * np.ones(activeAOI.y_summed.shape[0])
                activeAOI.y_peakHeight = 0
                activeAOI.y_width = 0

            #ysize, xsize = activeAOI.absImg.shape
            xsize, ysize = self.atomImage.shape

            ## x profile
            self.currentXProfile, = self.axes2.plot(activeAOI.x_basis, activeAOI.x_summed, c = activeAOI.color)

            self.currentXProfileFit, = self.axes2.plot(activeAOI.x_basis, activeAOI.x_fitted, c = 'gray', label = str("%.3f"%(activeAOI.atomNumFromFitX/1E6)))
            lx = self.axes2.legend(loc = "upper right")
            print(str("%.3f"%(activeAOI.atomNumFromFitX/1E6)) + "         %%%%%%%%%%%%%%%")
            if activeAOI.isXFitSuccessful is False:
                for text in lx.get_texts():
                    text.set_color("red")
            try:                           
                xMax = np.maximum(activeAOI.x_summed.max(), activeAOI.x_fitted.max())
                xMin = np.minimum(activeAOI.x_summed.min(), activeAOI.x_fitted.min())
            except: 
                xMax = 2
                xMin = 1
            self.axes2.set_xlim([0, xsize])
            self.axes2.set_ylim([xMin, xMax])
            self.axes2.set_yticks(np.linspace(xMin, xMax, 4))

            ## y profile
            self.currentYProfile, = self.axes3.plot(activeAOI.y_summed, activeAOI.y_basis, c = activeAOI.color)
            self.currentYProfileFit, = self.axes3.plot(activeAOI.y_fitted, activeAOI.y_basis, c = 'gray', label =str("%.3f"%(self.atomNumFromFitY/1E6)))
            ly = self.axes3.legend(loc = "upper right")
            if activeAOI.isYFitSuccessful is False:
                for text in ly.get_texts():
                    text.set_color("red")

            print(str("%.3f"%(self.atomNumFromGaussianY/1E6)) + "         %%%%%%%%%%%%%%%")

            try:                           
                yMax = np.maximum(activeAOI.y_summed.max(), activeAOI.y_fitted.max())
                yMin = np.minimum(activeAOI.y_summed.min(), activeAOI.y_fitted.min())
            except: 
                yMax = 2
                yMin = 1

            self.axes3.set_xlim([yMin, yMax])
            self.axes3.set_ylim([ysize, 0])
            self.axes3.set_xticks(np.linspace(yMin, yMax, 3))
            self.axes3.xaxis.set_ticks_position('top')

        self.deletePrev2DContour()                ## draw newly set data
        print("TIME BEFORE DRAW UPDATE1D " + str(time.time()))
        temp = time.time()
        self.canvas.draw()
        print("TIME TAKEN DRAW UPDATE1D " + str(time.time()-temp))
        # self.canvas.flush_events()
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
            #self.magnification = 2
        elif rb.GetLabel() == "Horizontal":
            self.cameraPosition = "HORIZONTAL"
            #self.magnification = 3
        elif rb.GetLabel() == "Test":
            self.cameraPosition = "TEST"
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
    
    
    def on_press(self, event):
        if (event.xdata is None) or (event.ydata is None):
            return
        print("Clicked xpos =")
        print(event.xdata)
        print("Clicked ypos =")
        print(event.ydata)
        if event.button == 1: # 1 corresponds to MouseButton.LEFT
            print("PRESSING PRIMARY")
            if self.doubleAOIs and (self.AOIRadioBox.GetSelection() == 1):
                activeAOI = self.primaryAOI_2
            else:
                activeAOI = self.primaryAOI
        elif event.button == 3: # 3 corresponds to MouseButton.RIGHT
            print("PRESSING SECONDARY")
            if self.doubleAOIs and (self.AOIRadioBox.GetSelection() == 1):
                activeAOI = self.secondaryAOI_2
            else:
                activeAOI = self.secondaryAOI
        elif event.button == 2: # 2 corresponds to scroll wheel click
            self.toggleAOISelection()
        x0 = activeAOI.position[0] = int(event.xdata)
        y0 = activeAOI.position[1] = int(event.ydata)
        self.press = x0, y0, event.xdata, event.ydata

    def on_motion(self, event):
        #'on motion we will move the rect if the mouse is over us'
        if (self.press is None) or (event.inaxes != self.axes1):
            return

        if event.button == 1: # 1 corresponds to MouseButton.LEFT
            if self.doubleAOIs and (self.AOIRadioBox.GetSelection() == 1):
                activeAOI = self.primaryAOI_2
            else:
                activeAOI = self.primaryAOI
        elif event.button == 3: # 3 corresponds to MouseButton.RIGHT
            if self.doubleAOIs and (self.AOIRadioBox.GetSelection() == 1):
                activeAOI = self.secondaryAOI_2
            else:
                activeAOI = self.secondaryAOI

        x0, y0, xpress, ypress = self.press
        self.x1 = event.xdata
        self.y1 = event.ydata
        activeAOI.position[2] = int(self.x1)
        activeAOI.position[3] = int(self.y1)
        activeAOI.update_patch()
        self.canvas.draw()

    def on_release(self, event):
        if (event.xdata is None) or (event.ydata is None):
            return
        self.press = None

        if event.button == 1: # 1 corresponds to MouseButton.LEFT
            if self.doubleAOIs and (self.AOIRadioBox.GetSelection() == 1):
                activeAOI = self.primaryAOI_2
            else:
                activeAOI = self.primaryAOI
        elif event.button == 3: # 3 corresponds to MouseButton.RIGHT
            if self.doubleAOIs and (self.AOIRadioBox.GetSelection() == 1):
                activeAOI = self.secondaryAOI_2
            else:
                activeAOI = self.secondaryAOI

        self.x1 = event.xdata
        self.y1 = event.ydata
        activeAOI.position[2] = int(self.x1)
        activeAOI.position[3] = int(self.y1)
        if activeAOI.position[2] < activeAOI.position[0]:
            activeAOI.position[2], activeAOI.position[0] = activeAOI.position[0], activeAOI.position[2]
        if activeAOI.position[3] < activeAOI.position[1]:
            activeAOI.position[3], activeAOI.position[1] = activeAOI.position[1], activeAOI.position[3]

        if activeAOI.position[0] < 1: activeAOI.position[0] = 1
        if activeAOI.position[1] < 1: activeAOI.position[1] = 1
        if activeAOI.position[2] + 1 >= self.imageData[0].shape[1]: activeAOI.position[2] = self.imageData[0].shape[1] - 2
        if activeAOI.position[3] + 1 >= self.imageData[0].shape[0]: activeAOI.position[3] = self.imageData[0].shape[0] - 2

        activeAOI.update_patch()
        activeAOI.update_image(self.imageData)
        print("TIME BEFORE DRAW RELEASE " + str(time.time()))
        temp = time.time()
        self.canvas.draw()
        print("TIME TAKEN DRAW RELEASE " + str(time.time()-temp))
        self.canvas.flush_events()

        if event.button == 1:
            self.AOI1_Primary.SetValue(str(self.primaryAOI.position[0]))
            self.AOI2_Primary.SetValue(str(self.primaryAOI.position[1]))
            self.AOI3_Primary.SetValue(str(self.primaryAOI.position[2]))
            self.AOI4_Primary.SetValue(str(self.primaryAOI.position[3]))
            self.AOI_Primary = [[self.primaryAOI.position[0], self.primaryAOI.position[1]],[self.primaryAOI.position[2], self.primaryAOI.position[3]]]
            self.updateAOI_PrimaryImage()
        elif event.button == 3:
            self.AOI1_Secondary.SetValue(str(self.secondaryAOI.position[0]))
            self.AOI2_Secondary.SetValue(str(self.secondaryAOI.position[1]))
            self.AOI3_Secondary.SetValue(str(self.secondaryAOI.position[2]))
            self.AOI4_Secondary.SetValue(str(self.secondaryAOI.position[3]))
            self.AOI_Secondary = [[self.secondaryAOI.position[0], self.secondaryAOI.position[1]],[self.secondaryAOI.position[2], self.secondaryAOI.position[3]]]
            self.setAtomImage(defringing = False)
            self.updateAOI_PrimaryImage()

        self.setAtomNumber()
        self.update1DProfilesAndFit()

    def typedAOI(self, event):
        activeAOI = self.primaryAOI  # Now this new function is only available for one spin, primary patch 08/16/2023

        activeAOI.position[0]=self.tempAOI1
        activeAOI.position[1]=self.tempAOI2
        activeAOI.position[2]=self.tempAOI3
        activeAOI.position[3]=self.tempAOI4

        if activeAOI.position[2] < activeAOI.position[0]:
            activeAOI.position[2], activeAOI.position[0] = activeAOI.position[0], activeAOI.position[2]
        if activeAOI.position[3] < activeAOI.position[1]:
            activeAOI.position[3], activeAOI.position[1] = activeAOI.position[1], activeAOI.position[3]

        if activeAOI.position[0] < 1: activeAOI.position[0] = 1
        if activeAOI.position[1] < 1: activeAOI.position[1] = 1
        if activeAOI.position[2] + 1 >= self.imageData[0].shape[1]: activeAOI.position[2] = self.imageData[0].shape[1] - 2
        if activeAOI.position[3] + 1 >= self.imageData[0].shape[0]: activeAOI.position[3] = self.imageData[0].shape[0] - 2

        activeAOI.update_patch()
        activeAOI.update_image(self.imageData)
        self.canvas.draw()
        self.canvas.flush_events()

        self.AOI1_Primary.SetValue(str(self.primaryAOI.position[0]))
        self.AOI2_Primary.SetValue(str(self.primaryAOI.position[1]))
        self.AOI3_Primary.SetValue(str(self.primaryAOI.position[2]))
        self.AOI4_Primary.SetValue(str(self.primaryAOI.position[3]))
        self.AOI_Primary = [[self.primaryAOI.position[0], self.primaryAOI.position[1]],[self.primaryAOI.position[2], self.primaryAOI.position[3]]]
        self.updateAOI_PrimaryImage()

        self.setAtomNumber()
        self.update1DProfilesAndFit()
    def setAtomNumber(self):
    #def setAtomNumberBox(self):
#        print ""
#        print ""
#        print self.pixelToDistance
#        print self.crossSection
        self.setConstants()
        self.setRawAtomNumber()
        self.atomNumber = self.rawAtomNumber *  (self.pixelToDistance**2)/self.crossSection
        for aoi in self.AOIList:
            aoi.atomNumber = aoi.rawAtomNumber * (self.pixelToDistance**2)/self.crossSection
        print("Atom number set")
        print(self.atomNumber)
        [print(aoi.atomNumber) for aoi in self.AOIList]

        self.bigNcount2.SetValue(str("%.0f"%(self.rawAtomNumber)))
        self.bigNcount3.SetValue(str('%1.2e'%(self.atomNumber)))
        if self.doubleAOIs:
            self.bigNcount4.SetValue(str("%1.2e" % (self.primaryAOI_2.atomNumber)))
        
    def calc1DRadialAvgAndRefit(self):
        if self.checkDisplayRadialAvg.GetValue() is False: # Regular summation and fit
            self.fit()
        
        else:   # radial fit
            xCenter = self.x_center
            yCenter = self.y_center
            if self.isXFitSuccessful is False:
                xCenter = np.argmax(self.x_summed)
            
            if self.isYFitSuccessful is False:
                yCenter = np.argmax(self.y_summed)
            
            yarr = radialAverage(self.AOI_PrimaryImage, center = [xCenter, yCenter], boundary = [self.primaryAOI.position[0], self.primaryAOI.position[1], self.primaryAOI.position[2], self.primaryAOI.position[3]])
           
            num = len(yarr)
            self.x_basis = np.linspace(xCenter - num + 1, xCenter +  num - 1, 2* num - 2)
            self.x_summed = self.x_peakHeight * np.concatenate((np.flipud(yarr)[:-2], yarr), axis = 0)
            self.fit('x')
        
    def calc1DProfiles(self):

        for activeAOI in self.AOIList:
            y_size, x_size = activeAOI.ODImg.shape
            activeAOI.x_summed = np.sum(activeAOI.ODImg, axis = 0)
            activeAOI.x_basis = np.linspace(activeAOI.position[0], activeAOI.position[2], x_size)
            activeAOI.y_summed = np.sum(activeAOI.ODImg, axis = 1)
            activeAOI.y_basis = np.linspace(activeAOI.position[1], activeAOI.position[3], y_size)


    def updateAOI_SecondaryImage(self):
        self.AOI_SecondaryImage = self.atomImage[self.secondaryAOI.position[1]:self.secondaryAOI.position[3], self.secondaryAOI.position[0]:self.secondaryAOI.position[2]]
        self.setRawAtomNumber()

    def updateAOI_PrimaryImage(self):
        self.AOI_PrimaryImage = self.atomImage[self.primaryAOI.position[1]:self.primaryAOI.position[3], self.primaryAOI.position[0]:self.primaryAOI.position[2]]
        

    def lightDifferencePerPixel(self):  # Computes the ligth level difference in the secondary AOI between the atom and light shot
        atomLight = np.mean(self.imageData[0][self.secondaryAOI.position[1]:self.secondaryAOI.position[3], self.secondaryAOI.position[0]:self.secondaryAOI.position[2]])
        lightLight = np.mean(self.imageData[1][self.secondaryAOI.position[1]:self.secondaryAOI.position[3], self.secondaryAOI.position[0]:self.secondaryAOI.position[2]])
        return atomLight/lightLight
    
    def setRawAtomNumber(self):
        try:
            if  self.checkBoxAutoAOI.GetValue():
                self.rawAtomNumber = np.sum((self.AOI_TertiaryImage > -10)*self.AOI_TertiaryImage)
            else:
                self.rawAtomNumber = np.sum((self.AOI_PrimaryImage > -10)*self.AOI_PrimaryImage)
                for aoi in self.AOIList:
                    aoi.rawAtomNumber = np.sum( (aoi.ODImg > -10) * aoi.ODImg )
            #self.rawAtomNumber = np.sum(self.AOI_PrimaryImage)
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
                    self.currentImg.set_clim(vmin=-0.1, vmax=0.3)
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
                self.canvasZoom.draw()
                self.backgrounds = [self.canvas.copy_from_bbox(ax.bbox) for ax in [self.axes1, self.axes2, self.axes3]]
                # self.canvas.flush_events()
    
    def setDataAndUpdate(self):
        if self.checkApplyDefringing.GetValue() is True:
            self.defringing()
            
        self.setDataNewImageSelection()
        hasFileSizeChanged = self.checkIfFileSizeChanged()
#        print "sizechange??????????? ---- chooseImg"
#        print hasFileSizeChanged
        
        # draw the newly set data
        self.updateImageOnUI(self.chosenLayerNumber, hasFileSizeChanged)
        self.setAtomNumber()
            
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

    def showImgValueZoom(self, e):
        if e.xdata and e.ydata:
            x = int(e.xdata)
            y = int(e.ydata)
            if self.imageData and (x >= 0  and x < self.imageData[0].shape[1]) and (y >= 0 and y < self.imageData[0].shape[0]):
                self.cursorX_Zoom.SetValue(str(x))
                self.cursorY_Zoom.SetValue(str(y))
                self.cursorZ_Zoom.SetValue('%0.4f'%self.atomImage[y][x])

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
                # self.canvas.flush_events()
            return True
        
        if self.quickFitBool==False:
            self.quickFitBool=True
        return False
        
    def show2DContour(self, e):
        if self.deletePrev2DContour():
            return
#
        y_size, x_size = self.AOI_PrimaryImage.shape
        x_basis = np.linspace(self.primaryAOI.position[0], self.primaryAOI.position[2], x_size)
        y_basis = np.linspace(self.primaryAOI.position[1], self.primaryAOI.position[3], y_size)
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
        # self.canvas.flush_events()
        
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
            
    def saveAsRef(self):
        if self.checkSaveAsRef.GetValue() is True:
            path = self.path[:-2] + "_ref\\"
            if not os.path.exists(path):
                os.makedirs(path)
            shutil.copy2(self.imageID, path)
            self.defringingRefPath = path

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
        self.canvasZoom.draw()
        # self.canvas.flush_events()
        self.Update()
            
        self.benchmark_endTime=time.time()
        print("This shot took " + str(abs(self.benchmark_startTime-self.benchmark_endTime)) + " seconds")
        gc.collect()

    def startCamera_trigger(self, event):
        self.camera.cameraDevice.shouldCameraRun = True
        self.cameraThread = threading.Thread(target = self.camera.cameraDevice.run_single_camera_trigger) #, args=[i])
        self.cameraThread.start()
    
    def endCamera_trigger(self, event):
        self.camera.cameraDevice.shouldCameraRun = False # that will change the value of the loop to acquire images
                                                        # and eventually end the acquisition process in a few seconds depending on the wait time for trigger
        self.cameraThread.join()    # this waits for the acquisition process to end
    
    def startAutoRun(self, e):
#        self.AOIImage = None
        #self.atomImage = None
        self.imageIDText.SetValue('')
        self.updateImageListBox()
        self.fileSizeValue.SetValue(str(self.expectedFileSize))
        try:
            if self.autoRunning == False:
                self.snippetTextBox.Disable()
                self.chooseFileButton.Disable()
                self.choosePathButton.Disable()
                self.fileSizeValue.Disable()
                print("Start Auto Run.. Begin Watching File Changes in the Folder...")
                self.autoButton.SetLabel('Watching File Changes in the Folder...')
                print("Observing " + self.imageFolderPath.GetValue())
#                self.observer = Observer()
#                self.observer.schedule(MyHandler(self.autoRun, self, self.expectedFileSize), path = self.path)
#
#                self.observer.start()
              
                self.monitor = Monitor(self.camera.pathWrittenImages, self.autoRun, self.expectedFileSize, self.camera)
                print("I created an monitor")
                self.monitor.createObserverAndStart()
                #self.observer.join()
                print("I created an observer")
                self.autoRunning = True
            elif self.autoRunning == True:  # note, if the if statement above has been evaluated to True then this is skipped
                                            # if think it could be simply replaced by else.
                self.snippetTextBox.Enable()
                self.chooseFileButton.Enable()
                self.choosePathButton.Enable()
                self.fileSizeValue.Enable()
                print("Stop Watching Folder.")
                
                self.autoButton.SetLabel('Auto Fit')

#                self.observer.join()
#                self.observer = None
                if self.monitor:
                    self.monitor.stop()
                    self.monitor.join()
                    
#                    self.monitor.observer.join()
                else:
                    print("------------There's NO monitor pointer-----------")
                # self.observer.
                # self.observer.restart()
                self.autoRunning = False
        except Exception as e:
            print(e)
            print("Sorry. There is some problem about auto fit. Please just restart the ram.")


    def autoRun(self):
        if self.monitor.oldObserver is not None:
#            print "----------Let's kill the old observer---------------------"
            self.monitor.oldObserver.stop()
        imageFilesToLoad = self.monitor.handlerToCall.listOfValidImagesWaiting
        self.setRawDataFromCamera(imageFilesToLoad)  # set the imageData and the divided image (no log)
        self.setTransformedData() # do the log
        self.setFitting()  # AOI and atom number
        deleteFiles(imageFilesToLoad)
        self.monitor.handlerToCall.listOfValidImagesWaiting = []
        # add here the tranfer of the image to the database
        print("########################## Found new image #########################")
        #self.fitImage()
        self.showImg()
        # add the import of the result to the database
        lastRunID, lastSequenceID = getLastID()
        if self.buttonSaveDummy.GetValue(): # if you save a dummy image
            print("saving dummy")
            writeImageToCacheC([1],
                           [1],
                           [0],
                           1,
                           1,
                           2,
                           lastRunID,
                           lastSequenceID)
        elif self.buttonSaveCropped.GetValue(): # if you save a cropped image
            try:
                print("saving crop")
                atomShotCropList, lightShotCropList, darkShotCropList = self.convertCropImagesToList()
                writeImageToCacheC(atomShotCropList,
                               lightShotCropList,
                               darkShotCropList,
                               self.cropXEnd - self.cropXStart + 1,
                               self.cropYEnd - self.cropYStart + 1,
                               6,
                               lastRunID,
                               lastSequenceID)
            except:
                print("Problem in saving the cropped image")
        else:
            if self.buttonSaveFull.GetValue():
                atomShotList, lightShotList, darkShotList = self.convertImagesToList()
                print("saving real image")
                writeImageToCacheC(atomShotList,
                               lightShotList,
                               darkShotList,
                               self.camera.width,
                               self.camera.height,
                               self.camera.cameraID,
                               lastRunID,
                               lastSequenceID)
            else:
                print("Problem with the radioButton of image saving")
        self.analysisResults = self.dictionnaryAnalysisResults()
        writeAnalysisToDB(self.analysisResults, lastRunID)
        updateNewImage() # clear signal for Zeus
        print("Saved images to database with runID, seqID, cameraID = " + str(lastRunID) + str(lastSequenceID) + str(self.camera.cameraID))
        self.updateImageListBox() # probably put it after the fitm once the db is updated
        #if self.camera.cameraType == 'FLIR':
        #    os.system('python FLIRCommand/runHardwareTrigger.py')
        
    def saveResult(self, e):
        if self.fitMethodFermion.GetValue():
            self.saveFermionResult(e)
        elif self.fitMethodBoson.GetValue():
            self.saveBosonResult(e)
        elif self.fitMethodGaussian.GetValue():
            self.saveGaussianResult(e)

    def saveBosonResult(self, e):
        f = open("C:\\AndorImg\\boson_data.txt", "a")
        f.writelines(self.timeString + '\t' + self.tof.GetValue() + '\t'\
         # + self.omegaAxial.GetValue() + ' , ' + self.omegaRadial.GetValue() + ' , '\
         # + str(self.gVals[0][0]) + ' , ' + str(self.gVals[0][1]) + ' , ' \
         + self.atomNumberInt.GetValue() + '\t' \
         + str(self.bosonParams[2]) + '\t' + str(self.bosonParams[3]) + '\t' \
         + str(1/np.sqrt(self.bosonParams[7])) + '\t' + str(1/np.sqrt(self.bosonParams[8]))  \
            + '\n')
        
        f.close()

    def saveFermionResult(self, e):
        f = open("C:\\AndorImg\\fermion_data.txt", "a")
        
        f.writelines(self.timeString + '\t' + self.tof.GetValue() + '\t'\
         # + self.omegaAxial.GetValue() + ' , ' + self.omegaRadial.GetValue() + ' , '\
         + str(self.gaussionParams[0]) + '\t' + str(self.gaussionParams[1]) + '\t' \
         + self.atomNumberInt.GetValue() + '\t' \
         + str(self.fermionParams[2]) + '\t' + str(self.fermionParams[3]) + '\t' \
         + str(self.fermionParams[4]) + '\n')
        
        f.close()

    def saveGaussianResult(self, e):
        f = open("C:\\AndorImg\\gaussian_data.txt", "a")
        f.writelines(self.timeString + '\t' + self.tof.GetValue() + '\t'\
         # + self.omegaAxial.GetValue() + ' , ' + self.omegaRadial.GetValue() + ' , '\
         + str(self.gaussionParams[0]) + '\t' + str(self.gaussionParams[1]) + '\t' \
         + str(self.atomNumberInt.GetValue()) + '\t' + str(self.atomNumberIntFit.GetValue()) + '\t'\
         + str(self.gaussionParams[2]) + '\t' + str(self.gaussionParams[3]) \
         + '\n')
        
        f.close()

    def cleanData(self, e):
        if self.fitMethodFermion.GetValue():
            f = open("C:\\AndorImg\\fermion_data.txt", "w")
        elif self.fitMethodBoson.GetValue():
            f = open("C:\\AndorImg\\boson_data.txt", "w")
        f.close()
    
    def dictionnaryAnalysisResults(self):
        analysisResults = {
            "nCount" : int(self.atomNumber),
            "xWidth" : self.primaryAOI.x_width,
            "yWidth" : self.primaryAOI.y_width,
            "xPos" : self.primaryAOI.x_center,
            "yPos" : self.primaryAOI.y_center,
            "PSD" : 0
            }
        if self.doubleAOIs:
            analysisResults["nCount2"] = int(self.primaryAOI_2.atomNumber)
            analysisResults["xWidth2"] = self.primaryAOI_2.x_width
            analysisResults["yWidth2"] = self.primaryAOI_2.y_width
            analysisResults["xPos2"] = self.primaryAOI_2.x_center
            analysisResults["yPos2"] = self.primaryAOI_2.y_center
        # "INSERT INTO nCounts (nCount,xWidth,yWidth,xPos,yPos,runID_fk,PSD) VALUES (@nC,@widthX,@widthY,@xPos,@yPos,@runID,@PSD)"
        return analysisResults
    
    def updateAnalysisDB(self, event): # event is the button click
        self.analysisResults = self.dictionnaryAnalysisResults()
        updateAnalysisOnDB(self.analysisResults, self.imageID)
        self.updateFileInfoBox()

    def snippetCommunicate(self, N_intEdge):
        self.setConstants()
        try:
            f = open(self.snippetPath, "w")
        except:
            msg = wx.MessageDialog(self, 'The file path for SnippetServer is not correct','Incorrect File Path', wx.OK)
            if msg.ShowModal() == wx.ID_OK:
                msg.Destroy()
            return
            
        if not N_intEdge:
            N_intEdge = -1
            N_count = -1
        else:
#            N_count = N_intEdge/((pixelToDistance**2)/crossSection)/(16/6.45)**2
            N_count = N_intEdge * (self.pixelToDistance**2)/self.crossSection
            
        
#        f.writelines(self.timeString + '\t' + str(N_intEdge) + '\t-1' + '\t' + str(N_count) + '\t-1' + '\t' + str(N_count) + '\t-1' + '\t' + str("%.2f"%(self.true_y_width*1E6)) + '\n')
#        f.writelines(self.timeString + '\t' + str(N_intEdge) + '\t-1' + '\t' + str(N_count) + '\t-1' + '\t' + str(self.atomNumFromGaussianY) + '\t-1' + '\t' + str("%.2f"%(self.true_y_width*1E6)) + '\n')
        f.writelines(self.timeString + '\t' + str(N_intEdge) + '\t-1' + '\t' + str(N_count) + '\t-1' + '\t' + str(self.atomNumFromGaussianX) + '\t-1' + '\t' + str(self.atomNumFromGaussianY) + '\t-1' + '\t' + str("%.3f"%(self.temperature[0])) + '\t-1' + '\t' + str("%.3f"%(self.temperature[1])) + '\t-1' + '\t' + str("%.3f"%(self.tempLongTime[0])) + '\t-1' + '\t' + str("%.3f"%(self.tempLongTime[1])) + '\n')
        
#        f.writelines(self.timeString + '\t' + str(N_intEdge) + '\t-1' + '\t' + str(N_count) + '\t-1' + '\t' + str(self.y_center) + '\t-1' + '\t' + str(self.x_center) + '\n')
#        f.writelines(self.timeString + '\t' + str(N_intEdge) + '\t-1' + '\t' + str(self.x_width) + '\t-1' + '\t' + str(self.x_center) + '\t-1' + '\t' + str("%.2f"%(self.true_y_width*1E6)) + '\n')
    def rotateImage(self, img, angle, pivot):
        padX = [int(img.shape[1] - pivot[0]), int(pivot[0])]
        padY = [int(img.shape[0] - pivot[1]), int(pivot[1])]
        imgP = np.pad(img, [padY, padX], 'constant', constant_values=[(0,0), (0,0)])
        imgR = ndimage.rotate(imgP, angle, reshape = False)
        return imgR[padY[0] : -padY[1], padX[0] : -padX[1]]
#        return imgP
                  
#######################################
    def copy3Layer(self):
        pass
        #src = "C:\\shared_data\\AndorTransfer\\andor_img.tif"
        #
        #
        #dst = "C:\\AndorImg\\originalImgbackup\\" + self.timeString + ".tif"
        #copyfile(src, dst)
    
    def saveAbsorbImg(self, atomImage):
        pass
        #abImg = Image.fromarray(atomImage)
        #dst = "C:\\AndorImg\\absorbImgbackup\\" + self.timeString + ".tif"
        #abImg.save(dst)
    
            
    def readListData(self, e):
        if self.fitMethodFermion.GetValue():
            f = open("C:\\AndorImg\\fermion_data.txt", "r")
            self.data = f.readlines()
        elif self.fitMethodBoson.GetValue():
            f = open("C:\\AndorImg\\boson_data.txt", "r")
            self.data = f.readlines()
        elif self.fitMethodGaussian.GetValue():
            f = open("C:\\AndorImg\\guassian_data.txt", "r")
            self.data = f.readlines()
        # f = open("../data.txt", "r")

        
        
        self.dataReadedText.SetValue("input: %i"%len(self.data))
        
        for i in range(len(self.data)):
            self.data[i] = self.data[i].split(' , ')
        
    
        f.close()

    def fitListData(self, e):
        tofList = []
        RXList = []
        RYList = []
       
        atom = ""

        n = len(self.data)
        for i in self.data:
            tofList.append(float(i[1])/1000.)
            RXList.append(float(i[3]) * self.pixelToDistance)
            RYList.append(float(i[4]) * self.pixelToDistance)
           
        if self.fitMethodBoson.GetValue():
            atom = "Na"
        elif self.fitMethodFermion.GetValue():
            atom = "Li"

        tx, ty, wx, wy = dataFit(atom, tofList, RXList, RYList)
        self.fitTempText.SetValue('(%.1f' %(tx*1E9) + ' , ' + '%.1f )' %(ty*1E9))

        self.fitTrapAxialFreqText.SetValue(str('%.1f' % (wy/(2*np.pi))))
        self.fitTrapRadialFreqText.SetValue(str('%.1f' % (wx/(2*np.pi))))
        # self.fitrho0Text.SetValue(str('%.1f' % (t[2]*1E6)))

    def drawAtomNumber(self, e):
        atomNumberI = []
        n = len(self.data)
        for i in self.data:
            atomNumberI.append(int(i[2]))
            # atomNumberC.append(int(i[11]))
        atomNumberPlot(n, atomNumberI)

    def convertImagesToList(self):
        return self.imageData[0].astype(np.int16).ravel().tolist(), self.imageData[1].astype(np.int16).ravel().tolist(), self.imageData[2].astype(np.int16).ravel().tolist()
    
    def convertCropImagesToList(self):
        return self.imageData[0].astype(np.int16)[self.cropYStart-1:self.cropYEnd, self.cropXStart-1:self.cropXEnd].ravel().tolist(), self.imageData[1].astype(np.int16)[self.cropYStart-1:self.cropYEnd, self.cropXStart-1:self.cropXEnd].ravel().tolist(), self.imageData[2][self.cropYStart-1:self.cropYEnd, self.cropXStart-1:self.cropXEnd].astype(np.int16).ravel().tolist()
    
    
    def snap(self, event):
        return
    
    def autoFluorescenceRun(self, event):
        if self.isFluorescenceOn:
            print("I stop the camera")
            self.endCamera_fluorescence()
            self.isFluorescenceOn = False
            self.fluorescenceButton.SetLabel("Turn On")
        else:
            print("I start the camera")
            self.startCamera_fluorescence()
            self.isFluorescenceOn = True
            self.fluorescenceButton.SetLabel("Turn Off")
        return
    
    def startCamera_fluorescence(self):
        self.camera.cameraDevice.shouldCameraRun_fluorescence = True
        self.cameraThread_fluorescence = threading.Thread(target = self.camera.cameraDevice.main_fluorescence, args = [self.axes1, self.canvas, self.fluorescenceNumberBox, self.axes_fluorescence, self.canvas_fluorescence]) #, args=[i])
        self.cameraThread_fluorescence.start()
    
    def endCamera_fluorescence(self):
        print("Called the end camera")
        self.camera.cameraDevice.shouldCameraRun_fluorescence = False # that will change the value of the loop to acquire images
                                                        # and eventually end the acquisition process in a few seconds depending on the wait time for trigger
        time.sleep(0.5)
        self.cameraThread_fluorescence.join()    # this waits for the acquisition process to end
        print("UI ready to be used again")
        
    def turnFluorescenceOn(self):
        acquire.main(self.axes1, self.canvas)

    def activateDoubleAOI(self, e):
        if e.IsChecked():
            self.doubleAOIs = e.IsChecked()
            self.primaryAOI_2 = selectionRectangle(color = "#d9294f", id_num = 2)
            self.secondaryAOI_2 = selectionRectangle(color = "#d9294f", dashed = True)
            self.primaryAOI_2.attachSecondaryAOI(self.secondaryAOI_2)
            self.AOIList.append( self.primaryAOI_2 )
            [self.drawAOIPatch(sR) for sR in [self.primaryAOI_2, self.secondaryAOI_2]]
            self.bigNcount4.Enable(True)
            self.canvas.draw()
            self.toggleAOISelection()
        else:
            if self.AOIRadioBox.GetSelection() == 1:
                self.toggleAOISelection()
            self.AOIList.pop()
            self.primaryAOI_2.patch.remove()
            self.secondaryAOI_2.patch.remove()
            self.primaryAOI_2.labelText.remove()
            self.primaryAOI_2 = None
            self.secondaryAOI_2 = None
            self.bigNcount4.Enable(False)
            self.bigNcount4.SetValue("")
            self.canvas.draw()
            self.doubleAOIs = e.IsChecked()


    def toggleAOISelection(self):
        if self.doubleAOIs:
            newAOI_id = self.AOIRadioBox.GetSelection()
            if newAOI_id == 0:
                aoi0 = self.AOIList[1]
                aoi1 = self.AOIList[0]
            else:
                aoi0 = self.AOIList[0]
                aoi1 = self.AOIList[1]
            aoi0.labelText.set_bbox(dict(facecolor = aoi0.color, edgecolor = "none", pad = aoi0.labelTextPadding, alpha = 1.0))
            aoi0.patch.set_alpha(1.0)
            aoi0.secondaryAOI.patch.set_alpha(1.0)
            aoi1.labelText.set_bbox(dict(facecolor = aoi1.color, edgecolor = "none", pad = aoi1.labelTextPadding, alpha = 0.5))
            aoi1.patch.set_alpha(0.5)
            aoi1.secondaryAOI.patch.set_alpha(0.5)
            aoi0.update_patch()
            aoi1.update_patch()
            self.canvas.draw()
            self.AOIRadioBox.SetSelection((self.AOIRadioBox.GetSelection() + 1) % 2)            

    def drawAOIPatch(self, aoi):
        self.axes1.add_patch(aoi.patch)
        if not aoi.id_num == 0:
            aoi.labelText = self.axes1.text(aoi.position[0] + 2*aoi.labelTextPadding,
                            aoi.position[1] + 2*aoi.labelTextPadding,
                            str(aoi.id_num),
                            color = "white",
                            horizontalalignment = "left",
                            verticalalignment = "top",
                            bbox = dict(facecolor = aoi.color, edgecolor = "none", pad = aoi.labelTextPadding))
        aoi.update_patch()
#self.currentImg = self.axes1.imshow(data, cmap='gray_r', aspect='auto', vmin=-1, vmax=1)


class dbCommunicator():
    def __init__():
        self.serverIP = "192.168.1.133"
        self.password = "w0lfg4ng"

########################################
## Execute the UI

if __name__ == '__main__':
    print("here1")
    app = wx.App()
    print("here2")
    ui = ImageUI(None, title='Atom Image Analysis Dy v1')
    print("here3")
    #if ui.camera.cameraType == 'FLIR':
    #    os.system('python FLIRCommand/runHardwareTrigger.py')
    #if ui.camera.cameraType == 'FLIR':
    #    exec(open('FLIRcommand/runHardwareTrigger.py').read())
    #ui.fitImage(wx.EVT_BUTTON)
    ui.fitImage()
    print("here4")
    app.MainLoop()
    print("here5")

