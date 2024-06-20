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

####################################
##########LOCAL IMPORTS#############

#from imagePlot import *
from imgFunc_v6 import *
from watchforchange import *
#from localPath import *

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

# Camera run
import FLIRCommand.AcquireAndDisplay as acquire


import threading

class ImageUI(wx.Frame):
    
    def __init__(self, parent, title):

        #from _zoomstuff import setZoomCenterX, setZoomCenterY, setZoomedCoordinates, setZoomImage, setZoomWidth, showImgValueZoom

        super(ImageUI, self).__init__(parent, title = title, size=(1700, 1120))
        

        ## New parameters added by Pierre
        self.checkLocalFiles = False    # True = check the local harddrive, False = looks at the database
        self.isDummyImage = False  # when the image is simply a 1 by 1 pixel or that
                                    # no image has yet been selected
        self.cameraPosition = "HORIZONTAL" # HORIZONTAL or VERTICAL
        self.cameraType = "FLIR" # FLIR or Andor. It is the starting default variable
        self.camera = Camera(self.cameraType, self.cameraPosition) # check if I can bind that to the original button position
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
        
        self.vmax = 0.3
        ## new parameters added by Hyungmok
        self.atom = 'Dy'
        self.magnification = 5
        self.pixelSize = 6.5
        self.clebschGordan = 0.5*(1 + 1/153)
        self.pixelToDistance = self.pixelSize/self.magnification
        self.crossSection = 1.0E-13
        self.mass = 162 * 1.6605E-27
        self.rawAtomNumber = 1
        self.atomNumber_Secondary = 1
        
        self.timeChanged = False
        self.chosenLayerNumber = 4
        self.expectedFileSize = 0.01 ## in Mb
        self.gVals = None
        self.pVals = None
        self.fVals = None
        self.imageData = None
        self.atomImage = None
        self.absImage = None
        self.AOI_PrimaryImage = None    # AOI_PrimaryImage refers to the image enclosed in the Primary AOI, only needed for radial avg and 2D Fit
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
        self.secondaryAOI = selectionRectangle(dashed = True)
        self.secondaryAOI.issecondaryAOI = True
        self.primaryAOI.attachSecondaryAOI(self.secondaryAOI)

        self.AOIList = [self.primaryAOI]
        self.doubleAOIs = False

        self.AOI_Primary = [[self.primaryAOI.position[0], self.primaryAOI.position[1]],[self.primaryAOI.position[2], self.primaryAOI.position[3]]]
        self.AOI_Secondary = [[self.secondaryAOI.position[0], self.secondaryAOI.position[1]],[self.secondaryAOI.position[2], self.secondaryAOI.position[3]]]

        self.Zfit = []

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
        self.resultstring = None

        self.path = None
        self.defringingRefPath = None
        self.imageID = None
        self.imageIDIndex = 0
        self.Tmp = None
        self.data = None
        self.currentImg = None

        self.imageIDList = []

        ######
        ## Initialize dummy data and image
        self.initializeDummyData()

        ######################
        ## Initialize the UI##
        self.InitUI()
        self.Centre()
        self.Show()

        self.timeString = None
        
        self.fitMethodGaussian.SetValue(True)
        self.layer4Button.SetValue(True)
        self.autoRunning = False
        self.modifiedImageID = None

        self.currentfitImage = None
        self.imageList = []
        self.imageListFlag = 0
        # self.FermionFitChosen(e)

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

        #####################
        ####Open the GUI#####  
        #Bad code here, need modify in the future
        self.timeString = datetime.datetime.today().strftime("%a-%b-%d-%H_%M_%S-%Y")
        self.benchmark_startTime=time.time()
        try:
            if self.autoRunning == False:
                if not self.path:
                    print("------------Wrong Folder!--------")
                self.updateLatestImageID()
                fileText = self.imageIDText.GetValue()     # This one is simply "In the database" if not checkLocalFiles
                if (len(fileText) == 0):    # ilf the file name has no length you just pick up the one on top of the list
                    latestImageID = max(self.imageIDList)
                    self.imageID = latestImageID[-1]
                self.setImageIDText()

            elif self.autoRunning == True:      
                self.updateLatestImageID()

            self.updateImageListBox()
            #self.setDataNewIncomingFile()
            print("Successfully read Image")
        except Exception as err:
            print("Failed to read this image.")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

        self.showImg()

    from _zoomstuff import setZoomCenterX, setZoomCenterY, setZoomWidth, showImgValueZoom, setZoomedCoordinates, setZoomImage
    from _InitUIstuff import InitUI, startCamera_trigger, endCamera_trigger, onAtomRadioClicked, updateFittingResult, TOFcalc, Fit2Dshow, FermiTempcalc


    from defringer_v2 import setDefringingRefPath, applyDefringing, defringing
    from _AOIstuff import settempAOI1,settempAOI2,settempAOI3,settempAOI4, isAOI_PrimaryOutside, isAOI_SecondaryOutside, on_press, on_motion, on_release, typedAOI
    from _AOIstuff import updatePrimaryImage, activateDoubleAOI, toggleAOISelection, drawAOIPatch


    from _junkystuff import copy3Layer, saveAbsorbImg, snap, showTOFFit, setXTrapFreq, setYTrapFreq, setTOF, updateFittingResults, setDataAndUpdate
    from _junkystuff import autoFluorescenceRun, startCamera_fluorescence, endCamera_fluorescence, turnFluorescenceOn, updatePeakValues, updateTrueWidths
    from _junkystuff import setImageAngle, setImagePivotX, setImagePivotY, setImageRotationParams, saveAsRef, fitImage, setDataNewIncomingFile

#############################################################
######################Initialize#############################
    def initializeDummyData(self):
        def generateNoise(shape):
            return 0*np.maximum( np.random.normal(10, 2, shape), np.zeros(shape) )

        size = 500
        sigmax, sigmay = 20, 20
        X, Y = np.meshgrid(np.arange(size), np.arange(size))
        #Picture with atoms
        dummyPWA = 256 * (1 - 0.8*np.exp(-(X-size/2)**2/(2*sigmax**2) - (Y-size/2)**2/(2*sigmay**2))) - generateNoise(np.shape(X))
        dummyPWA = 256*np.exp(-np.exp(-(X-size/2)**2/(2*sigmax**2) - (Y-size/2)**2/(2*sigmay**2)))
        dummyPWOA = 256 * np.ones_like(X) - generateNoise(np.shape(X))
        dummyDark = generateNoise(np.shape(X))
        self.imageData = [dummyPWA, dummyPWOA, dummyDark]
        # Note: the atomimage here is not a gaussian profile. Fitting result is not sigmaX, sigmaY
        self.atomImage = -np.log((dummyPWA - dummyDark) / (dummyPWOA - dummyDark))

    def initializeAOI(self):
        if (self.isAOI_PrimaryOutside() and self.isAOI_SecondaryOutside()):
            print("AOI_Primary initializing....")
            self.AOI1_Primary.SetValue(str(self.primaryAOI.position[0]))
            self.AOI2_Primary.SetValue(str(self.primaryAOI.position[1]))
            self.AOI3_Primary.SetValue(str(self.primaryAOI.position[2]))
            self.AOI4_Primary.SetValue(str(self.primaryAOI.position[3]))

            print("AOI_Secondary initializing....")
            self.AOI1_Secondary.SetValue(str(self.secondaryAOI.position[0]))
            self.AOI2_Secondary.SetValue(str(self.secondaryAOI.position[1]))
            self.AOI3_Secondary.SetValue(str(self.secondaryAOI.position[2]))
            self.AOI4_Secondary.SetValue(str(self.secondaryAOI.position[3]))
            
            for activeAOI in self.AOIList:
                self.drawAOIPatch(activeAOI)
                if hasattr(activeAOI, "secondaryAOI"):
                    self.drawAOIPatch(activeAOI.secondaryAOI)

            self.canvas.draw()
            
            self.setAtomNumber()
    
        else:   # This whole thing should be simplified by looking at isAOI_PrimaryOutside and rationalize things
            print("REUSE THE PREVIOUS AOI")
            print("AOI_Primary initializing....")
            self.AOI1_Primary.SetValue(str(self.primaryAOI.position[0]))
            self.AOI2_Primary.SetValue(str(self.primaryAOI.position[1]))
            self.AOI3_Primary.SetValue(str(self.primaryAOI.position[2]))
            self.AOI4_Primary.SetValue(str(self.primaryAOI.position[3]))
           
            print("AOI_Secondary initializing....")
            self.AOI1_Secondary.SetValue(str(self.secondaryAOI.position[0]))
            self.AOI2_Secondary.SetValue(str(self.secondaryAOI.position[1]))
            self.AOI3_Secondary.SetValue(str(self.secondaryAOI.position[2]))
            self.AOI4_Secondary.SetValue(str(self.secondaryAOI.position[3]))

            for activeAOI in self.AOIList:
                self.drawAOIPatch(activeAOI)
                if hasattr(activeAOI, "secondaryAOI"):
                    self.drawAOIPatch(activeAOI.secondaryAOI)
            
            self.canvas.draw()
            self.setAtomNumber()

##############################################################
#######################UpdateInfo#############################
    def updateFileInfoBox(self):
        self.fileInfoImageIDBox.SetValue(str(self.imageID))
        self.updateFileInfoFromDB()
        self.fileInfoTimestampBox.SetValue(self.imageTimestamp)
        self.fileInfoNCountBox.SetValue(np.format_float_scientific(getNCount(self.imageID), precision = 2))
        
    def updateFileInfoFromDB(self):
        self.imageTimestamp = getTimestamp(self.imageID)

    def setSnippetPath(self, e):
        snippetPath = e.GetEventObject()
        self.snippetPath = snippetPath.GetValue()
        print(self.snippetPath)

###############################################################################################
######################Technical stuff, needless to get changed#################################
    def checkIfFileSizeChanged(self):
        hasFileSizeChanged = False
        return hasFileSizeChanged

    def setFileSize(self, e):
        try:
            fileSize = float(self.fileSizeValue.GetValue())
            self.expectedFileSize = fileSize
        except:
            print("Invalue File Size")
            print(self.expectedFileSize)

    def checkTimeChange(self):
        current = datetime.date.today()
        
        if (current != self.today):
            self.timeChanged = True
            self.today = current
        else:
            self.timeChanged = False

################################################################################################
##################Set some numbers/choices in the GUI###########################################
##################Other settings might be changed within _InitUIstuff.py########################
    def displayNormalization(self, e):
        self.isNormalizationOn = self.checkNormalization.GetValue()
        self.setTransformedData()
        self.CountnFitAOI()

    def dowingsfit(self,e):
        self.isWingsfit = self.checkwings.GetValue()
        self.update1DProfilesAndFit()

    def applyFilter(self):
        ''' The 'Median filter' button in the UI '''
        self.isMedianFilterOn = self.checkMedianFilter.GetValue()
        self.setTransformedData()
        self.CountnFitAOI()

    def setPixelSize(self, e):
        tx = e.GetEventObject()
        self.pixelSize = float(tx.GetValue())
        
        self.pixelToDistance = self.pixelSize / self.magnification * 10**-6
        self.setAtomNumber()
        
        print("PIXEL SIZE:")
        print(self.pixelSize)

    def setvmax(self,e):
        mg = e.GetEventObject()
        self.vmax = float(mg.GetValue())

        print("VMAX:")
        print(self.vmax)
        
    def setMagnification(self, e):
        mg = e.GetEventObject()
        self.magnification = float(mg.GetValue())

        self.pixelToDistance = self.pixelSize / self.magnification * 10**-6
        
        self.setAtomNumber()
        
        print("MAGNIFICATION:")
        print(self.magnification)
    
    def setClebschGordan(self, e):
        mg = e.GetEventObject()
        self.clebschGordan = float(mg.GetValue())
        
        self.setConstants()
        self.setAtomNumber()
        
        print("CLEBSCH GORDAN:")
        print(self.clebschGordan)
    
    def setConstants(self):
        self.pixelToDistance = self.pixelSize / self.magnification * 10**-6
        
        massUnit = 1.6605E-27
        wavelength = 421E-9
        self.mass = 162*massUnit
        self.crossSection = 6. * np.pi * (wavelength/(2*np.pi))**2 * self.clebschGordan

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

#########################################################################################################################
######################Read the image data when new files go into andor/images and do transform###########################

    def setRawDataFromCamera(self, imagePathList):   # called when received images from camera
        defringing = self.checkApplyDefringing.GetValue()
        defringing = False # This need to be changed and debugged

        self.imageData = readFileData(imagePathList, self.camera)
        self.setAtomImageAsDivision(defringing)
        self.isDummyImage = False
        print("Here image data after readout. (Jiahao deleted the printout)")

    def setAtomImageAsDivision(self, defringing = False):
        if len(self.imageData) != 3:
            raise Exception("~~~~~~ Given image does not have three layers ~~~~~~~")
        if defringing is True:
            correctedNoAtom = self.betterRef
        else: # Contrary to prior version, Jiahao chooses not to correct NoAtom. This only has to do with the canvas show. Different from final atom count.
            correctedNoAtom = self.imageData[1]*1 - self.imageData[2]
    
        absorbImg = np.maximum(self.imageData[0]-self.imageData[2], .1)/(np.maximum(correctedNoAtom, .1))
        self.absImage = np.maximum(absorbImg, np.exp(-9))   #The OD Image before doing np.log

    def setTransformedData(self, pca = False, gaussianFilter = False, histogramEqualization = False, rotation  = True):
        '''
        If do nothing, everything is false, it does np.log() to the data matrix
        '''
        try:
            absorbImg = self.absImage # is that necessary?
            if not self.isDummyImage:
                if pca is True:
                    try:
                        pca = sklearnPCA('mle')
                        temp = pca.fit_transform(-np.log(absorbImg))
                    except Exception:
                        raise Exception("======= PCA ERROR ========")
                    
                if gaussianFilter is True:
                    try:
                        tempp = -np.log(absorbImg)
                        signal = tempp[self.primaryAOI.position[1]:self.primaryAOI.position[3], self.primaryAOI.position[0]:self.primaryAOI.position[2]]
                        filtered = gaussian_filter(tempp, 2, order = 0, truncate = 2)
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

    def rotateImage(self, img, angle, pivot):
        '''Never used currently, but might be useful in future'''
        padX = [int(img.shape[1] - pivot[0]), int(pivot[0])]
        padY = [int(img.shape[0] - pivot[1]), int(pivot[1])]
        imgP = np.pad(img, [padY, padX], 'constant', constant_values=[(0,0), (0,0)])
        imgR = ndimage.rotate(imgP, angle, reshape = False)
        return imgR[padY[0] : -padY[1], padX[0] : -padX[1]]

    def histogramEq(self, image, number_bins = 1000):
        '''Never used currently, but might be useful in future'''
        # from http://www.janeriksolem.net/2009/06/histogram-equalization-with-python-and.html
        image_histogram, bins = np.histogram(image.flatten(), number_bins, normed=True)
        cdf = image_histogram.cumsum() # cumulative distribution function
        cdf =  cdf/cdf[-1] # normalize
        # use linear interpolation of cdf to find new pixel values
        image_equalized = np.interp(image.flatten(), bins[:-1], cdf)
        return image_equalized.reshape(image.shape)


####################################################################################################################### 
#Show Img on the main canvas axe1, another main function of this part is AOI selection, SEPARATE coded in _AOIstuff.py#

    def setCurrentImg(self, data, hasFileSizeChanged):
        if hasFileSizeChanged or self.currentImg is None:
            print("showing image")
            self.axes1.cla()
            self.currentImg = self.axes1.imshow(data, cmap=self.cmap, aspect='equal', vmin=-0.1, vmax=self.vmax) #self.cmap defined in _InitUIstuff.py
            self.setZoomImage(data)
        else:
            print("reshowing that image")
            self.axes1.cla()
            self.currentImg = self.axes1.imshow(data, cmap=self.cmap, aspect='equal', vmin=-0.1, vmax=self.vmax)
            self.setZoomImage(data)
        self.initializeAOI()

    def updateImageOnUI(self, layerNumber, hasFileSizeChanged):
        self.chosenLayerNumber = layerNumber
        if self.isDummyImage:
            self.setCurrentImg(self.imageData[0], hasFileSizeChanged)
            self.currentImg.autoscale()
        else:
            if self.imageData:
                if layerNumber == 4:
                    self.setCurrentImg(self.atomImage, hasFileSizeChanged)
                    self.currentImg.set_clim(vmin=-0.1, vmax=self.vmax)
                else:
                    self.setCurrentImg(self.imageData[layerNumber - 1], hasFileSizeChanged)
                    self.currentImg.autoscale()
                self.canvas.draw()
                self.canvasZoom.draw()
                self.backgrounds = [self.canvas.copy_from_bbox(ax.bbox) for ax in [self.axes1, self.axes2, self.axes3]]

    def showImg(self):
        self.setAtomNumber()    # seemed to be done just beofre in readImage
        if (self.chosenLayerNumber == 4):
            imageToShow = self.atomImage
        else:
            imageToShow = self.imageData[self.chosenLayerNumber - 1]
        if not self.checkLocalFiles:
            hasFileSizeChanged = False

        self.setCurrentImg(imageToShow, hasFileSizeChanged)
        print("Success ---- ShowImg()")
        self.canvas.draw()
        self.canvasZoom.draw()
        self.Update()
            
        self.benchmark_endTime=time.time()
        print("This shot took " + str(abs(self.benchmark_startTime-self.benchmark_endTime)) + " seconds")
        gc.collect()


    def showImgValue(self, e):
        if e.xdata and e.ydata:
            x = int(e.xdata)
            y = int(e.ydata)
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

 ###########################################################################################################
 #######After AOI selected, count atom number and do fitting for your AOI, show 1D fit on axe2,3############
 
    def setAtomNumber(self):
        self.setConstants()
        try:
            for aoi in self.AOIList:
                aoi.rawAtomNumber = np.sum( (aoi.ODImg > -10) * aoi.ODImg )
            self.rawAtomNumber = self.primaryAOI.rawAtomNumber
        except:
            self.rawAtomNumber = np.nan

        for aoi in self.AOIList:
            aoi.atomNumber = aoi.rawAtomNumber * (self.pixelToDistance**2)/self.crossSection
        self.atomNumber = self.rawAtomNumber *  (self.pixelToDistance**2)/self.crossSection

        self.bigNcount2.SetValue(str('%1.2e'%(self.rawAtomNumber)))
        self.bigNcount3.SetValue(str('%1.2e'%(self.primaryAOI.atomNumber)))
        if self.doubleAOIs:
            self.bigNcount4.SetValue(str("%1.2e" % (self.primaryAOI_2.atomNumber)))

    def update1DProfilesAndFit(self, i = 0):
        ''' All in one code about axe2,3 1D profile and its fit'''
        #Calculate the 1D profiles
        for activeAOI in self.AOIList:
            y_size, x_size = activeAOI.ODImg.shape
            activeAOI.x_summed = np.sum(activeAOI.ODImg, axis = 0)
            activeAOI.x_basis = np.linspace(activeAOI.position[0], activeAOI.position[2], x_size)
            activeAOI.y_summed = np.sum(activeAOI.ODImg, axis = 1)
            activeAOI.y_basis = np.linspace(activeAOI.position[1], activeAOI.position[3], y_size)
        #After calculating the 1D profile, do the fit and update the profile
        self.calc1DAvgAndRefit()
        self.Fit2D()
        self.update1DProfiles()
        self.updateFittingResult()

    def Fit2D(self):
        try:
            if self.fitMethodFermion.GetValue() is True:
                self.Fit2DFermion()
            if self.fitMethodBoson.GetValue() is True:
                self.Fit2DBoson()
            else:
                self.Fit2DGaussian()
        except IndentationError as err:
            print("------ Fitting Failed -------")

    def Fit2DGaussian(self):
        for AAOI in self.AOIList:
            Initialparams = [AAOI.x_width,AAOI.y_width,AAOI.x_center,AAOI.y_center,AAOI.position[0],AAOI.position[1],AAOI.isXFitSuccessful,AAOI.isYFitSuccessful]
            AAOI.xc2D, AAOI.yc2D, AAOI.x_width2D, AAOI.y_width2D, AAOI.modifiedrawAtomNumber, AAOI.isFit2DSuc=gaussianFit2D(AAOI.ODImg,Initialparams)
            AAOI.modifiedAtomNumber = AAOI.modifiedrawAtomNumber * (self.pixelToDistance**2)/self.crossSection

    def Fit2DBoson(self):
        for AAOI in self.AOIList:
            Initialparams = [AAOI.x_width,AAOI.y_width,AAOI.x_center,AAOI.y_center,AAOI.position[0],AAOI.position[1],AAOI.isXFitSuccessful,AAOI.isYFitSuccessful]
            AAOI.xc2D, AAOI.yc2D, AAOI.x_width2D, AAOI.tfx_width2D, AAOI.tfy_width2D, AAOI.modifiedrawAtomNumber, AAOI.BECfraction, AAOI.isFit2DSuc,AAOI.x_fitted,AAOI.y_fitted,self.Zfit=BosonFit2D(AAOI.ODImg,Initialparams)
            AAOI.modifiedAtomNumber = AAOI.modifiedrawAtomNumber * (self.pixelToDistance**2)/self.crossSection
            AAOI.y_width2D = AAOI.x_width2D


    def Fit2DFermion(self):
        for AAOI in self.AOIList:
            Initialparams = [AAOI.x_width,AAOI.y_width,AAOI.x_center,AAOI.y_center,AAOI.position[0],AAOI.position[1],AAOI.isXFitSuccessful,AAOI.isYFitSuccessful]
            AAOI.xc2D, AAOI.yc2D, AAOI.x_width2D, AAOI.fermionzeta, AAOI.modifiedrawAtomNumber, AAOI.isFit2DSuc,AAOI.x_fitted,AAOI.y_fitted,self.Zfit=FermionFit2D(AAOI.ODImg,Initialparams)
            AAOI.modifiedAtomNumber = AAOI.modifiedrawAtomNumber * (self.pixelToDistance**2)/self.crossSection
            AAOI.y_width2D = AAOI.x_width2D

    def calc1DAvgAndRefit(self):
        '''Choose either 1D fit or radial fit'''
        if self.checkDisplayRadialAvg.GetValue() is False: # Regular summation and fit
            self.doGaussianFit('xy')
        
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
            self.doGaussianFit('x')        

    def doGaussianFit(self, axis = 'xy'):
        if axis == 'xy': # Regular fit on 2 axis
            for activeAOI in self.AOIList:
                activeAOI.x_center, activeAOI.x_width, activeAOI.x_offset, activeAOI.x_peakHeight, activeAOI.x_fitted, activeAOI.isXFitSuccessful, activeAOI.x_slope, err_x = gaussianFit(activeAOI.x_basis, activeAOI.x_summed, activeAOI, axis = 'x')
                activeAOI.atomNumFromGaussianX = activeAOI.x_peakHeight *np.sqrt(2 * np.pi) * activeAOI.x_width * (self.pixelToDistance**2)/self.crossSection
                activeAOI.x_width_std = err_x[2]
                activeAOI.y_center, activeAOI.y_width, activeAOI.y_offset, activeAOI.y_peakHeight, activeAOI.y_fitted, activeAOI.isYFitSuccessful, activeAOI.y_slope , err_y= gaussianFit(activeAOI.y_basis, activeAOI.y_summed, activeAOI, axis = 'y')
                activeAOI.atomNumFromGaussianY = activeAOI.y_peakHeight *np.sqrt(2 * np.pi) * activeAOI.y_width * (self.pixelToDistance**2)/self.crossSection
                activeAOI.y_width_std = err_y[2]
            
        elif axis == 'x': # regular fit on only one of the axis, radial averaged
            self.x_center, self.x_width, self.x_offset, self.x_peakHeight, self.x_fitted, self.isXFitSuccessful, self.x_slope, err_x = gaussianFit(self.x_basis, self.x_summed, self.AOI_Primary, axis = 'x')
            self.atomNumFromGaussianX = self.x_peakHeight *np.sqrt(2 * np.pi) * self.x_width * (self.pixelToDistance**2)/self.crossSection
            self.x_width_std = err_x[2]
        else:
            self.y_center, self.y_width, self.y_offset, self.y_peakHeight, self.y_fitted, self.isYFitSuccessful, self.y_slope, err_y = gaussianFit(self.y_basis, self.y_summed, self.AOI_Primary, axis = 'y')
            self.atomNumFromGaussianY = self.y_peakHeight *np.sqrt(2 * np.pi) * self.y_width * (self.pixelToDistance**2)/self.crossSection
            self.y_width_std = err_y[2]

    def update1DProfiles(self):
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

            xsize, ysize = self.atomImage.shape
            ## x profile
            self.currentXProfile, = self.axes2.plot(activeAOI.x_basis, activeAOI.x_summed, c = activeAOI.color)

            self.currentXProfileFit, = self.axes2.plot(activeAOI.x_basis, activeAOI.x_fitted, c = 'gray')
            lx = self.axes2.legend(loc = "upper right")
            if activeAOI.isXFitSuccessful is False:
                for text in lx.get_texts():
                    text.set_color("red")
            try:                           
                xMax = np.maximum(activeAOI.x_summed.max(), activeAOI.x_fitted.max())
                xMin = np.minimum(activeAOI.x_summed.min(), activeAOI.x_fitted.min())
            except: 
                xMax = 2
                xMin = 1
            self.axes2.set_xlim([self.primaryAOI.x_center-200, self.primaryAOI.x_center+200])
            self.axes2.set_ylim([xMin, xMax])
            self.axes2.set_yticks(np.linspace(xMin, xMax, 4))

            ## y profile
            self.currentYProfile, = self.axes3.plot(activeAOI.y_summed, activeAOI.y_basis, c = activeAOI.color)
            self.currentYProfileFit, = self.axes3.plot(activeAOI.y_fitted, activeAOI.y_basis, c = 'gray')
            ly = self.axes3.legend(loc = "upper right")
            if activeAOI.isYFitSuccessful is False:
                for text in ly.get_texts():
                    text.set_color("red")
            try:                           
                yMax = np.maximum(activeAOI.y_summed.max(), activeAOI.y_fitted.max())
                yMin = np.minimum(activeAOI.y_summed.min(), activeAOI.y_fitted.min())
            except: 
                yMax = 2
                yMin = 1

            self.axes3.set_xlim([yMin, yMax])
            self.axes3.set_ylim([self.primaryAOI.y_center+200, self.primaryAOI.y_center-200])
            self.axes3.set_xticks(np.linspace(yMin, yMax, 3))
            self.axes3.xaxis.set_ticks_position('top')

        print("TIME BEFORE DRAW UPDATE1D " + str(time.time()))
        temp = time.time()
        self.canvas.draw()
        print("TIME TAKEN DRAW UPDATE1D " + str(time.time()-temp))
    
    def CountnFitAOI(self):
        '''All in one function to update main tab'''
        ## initializeAOI and generate AOI rect. only at the beginning
        self.initializeAOI()
        [aoi.update_image(self.imageData) for aoi in self.AOIList]

        ## set self.AOIImage, which is the image array confined in the AOI
        self.updatePrimaryImage()
        self.setAtomNumber()
        self.update1DProfilesAndFit()
        print("Done with Fitting and setting atom number")
    
    def displayRadialAvg(self, e):
        self.calc1DAvgAndRefit()
        self.update1DProfiles()
            
######################################################################################################
########################################Run the loop##################################################

    def startAutoRun(self, e):
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

                if self.monitor:
                    self.monitor.stop()
                    self.monitor.join()
                    
#                    self.monitor.observer.join()
                else:
                    print("------------There's NO monitor pointer-----------")
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

        self.CountnFitAOI()  # AOI and atom number
        deleteFiles(imageFilesToLoad)
        self.monitor.handlerToCall.listOfValidImagesWaiting = []
        # add here the tranfer of the image to the database
        print("########################## Found new image #########################")
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
        
    
    def dictionnaryAnalysisResults(self):
        analysisResults = {
            "nCount" : int(self.atomNumber),  ##Jiahao modified on 10/25, now we save 2D fit number and width
            #"nCount" : int(self.primaryAOI.modifiedAtomNumber),
            "xWidth" : self.primaryAOI.x_width,
            "yWidth" : self.primaryAOI.y_width,
            "xPos" : self.primaryAOI.x_center,
            "yPos" : self.primaryAOI.y_center,
            "PSD" : self.primaryAOI.BECfraction
            }
            # Jiahao modified on 11/17 to see difference
        if self.doubleAOIs:
            analysisResults["nCount2"] = int(self.primaryAOI_2.atomNumber)
            analysisResults["xWidth2"] = self.primaryAOI_2.x_width
            analysisResults["yWidth2"] = self.primaryAOI.y_width
            analysisResults["xPos2"] = self.primaryAOI_2.x_center
            analysisResults["yPos2"] = self.primaryAOI_2.y_center
        # "INSERT INTO nCounts (nCount,xWidth,yWidth,xPos,yPos,runID_fk,PSD) VALUES (@nC,@widthX,@widthY,@xPos,@yPos,@runID,@PSD)"
        return analysisResults
    
    def updateAnalysisDB(self, event): # event is the button click
        self.analysisResults = self.dictionnaryAnalysisResults()
        updateAnalysisOnDB(self.analysisResults, self.imageID)
        self.updateFileInfoBox()

###########################################################################################
##############Read old pictures from DATABASE (not used for a long time)###################

    def setImageIDText(self):
        self.imageIDText.SetValue('In the database')
    def getLastIDinDB(self, n = 20):
        return getLastImageIDs(n)
    def updateImageIDList(self):
        self.imageIDList = self.getLastIDinDB()

    def updateLatestImageID(self):
        self.updateImageIDList()
        self.imageID = self.imageIDList[-1] #this is the filename
        self.setImageIDText()

    def updateImageListBox(self):
        self.imageListBox.Clear()
        self.updateImageIDList()
        for imageID in self.imageIDList:
                 self.imageListBox.Append(str(imageID))


    def chooseImgfromDB(self, e):
        '''Choose Img to reload from lower left Image list area, only 20 options'''
        oldImagesNumber = len(self.imageIDList)
        ind = self.imageListBox.GetSelection()
        self.imageIDIndex = ind
        self.updateImageIDList()
        newImagesNumber = len(self.imageIDList)
                
        if (oldImagesNumber != newImagesNumber):
            msg = wx.MessageDialog(self, 'Such image file may not exist in the file directory','Index Error', wx.OK)
            if msg.ShowModal() == wx.ID_OK:
                msg.Destroy()
                self.updateImageListBox()

        self.imageID = self.imageIDList[ind] #this is the selected imageID
        print("----the imageID----")
        print(self.imageID)
        print("CHOOSED!!!!!")
        self.setImageIDText()
        self.updateFileInfoBox()

        if self.checkApplyDefringing.GetValue() is True:
            self.defringing()
        self.setRawDataFromDB()
        hasFileSizeChanged = self.checkIfFileSizeChanged()
        # draw the newly set data
        self.updateImageOnUI(self.chosenLayerNumber, hasFileSizeChanged)
        self.setAtomNumber()

    def setRawDataFromDB(self, pca = False, gaussianFilter = False, histogramEqualization = False, rotation  = True):
        '''Choose Img to reload from lower left Image list area, only 20 options'''
        try:
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
            self.setTransformedData(pca, gaussianFilter, histogramEqualization, rotation)
            self.CountnFitAOI()
            
        except Exception as e:
            msg = wx.MessageDialog(self, str(e),'Setting Data failed', wx.OK)
            print("self.imageID is " + str(self.imageID))
            if msg.ShowModal() == wx.ID_OK:
                msg.Destroy()
            print("====== setDataNewImageSelection error =======")

    def choosePath(self, e):
        '''at UI upper right, get photo from whereever you want'''
        myStyle = wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST
        dialog = wx.DirDialog(None,  "Choose a directory:", defaultPath = self.path, style = wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            if platform.system() == 'Darwin': # MAC OS
                self.path = dialog.GetPath() + '/'
            if platform.system() == 'Linux':
                self.path = dialog.GetPath() + '\\' # maybe not the correct one for linux
            if platform.system() == 'Windows':
                self.path = dialog.GetPath() + '\\'
            self.imageFolderPath.SetValue(self.path)        
        self.updateImageListBox()
        dialog.Destroy()

    def chooseImgfromFile(self, e):
        '''at UI upper right, get photo from whereever you want'''
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        dialog = wx.FileDialog(self, 'Open', '', style=style)
        dialog.SetDirectory(self.path)
        if dialog.ShowModal() == wx.ID_OK:
            self.imageID = dialog.GetFilename()
            print(self.imageID + "---chooseFile")
            self.setImageIDText()
        else:
            self.imageID = None

        imagePathList=[self.path+self.imageID]
        self.setRawDataFromCamera(imagePathList)
        self.setTransformedData()
        self.CountnFitAOI()  # AOI and atom number
        print("########################## Found new image #########################")
        self.showImg()

        dialog.Destroy()

#######################################
    
    def convertImagesToList(self):
        return self.imageData[0].astype(np.int16).ravel().tolist(), self.imageData[1].astype(np.int16).ravel().tolist(), self.imageData[2].astype(np.int16).ravel().tolist()
    
    def convertCropImagesToList(self):
        return self.imageData[0].astype(np.int16)[self.cropYStart-1:self.cropYEnd, self.cropXStart-1:self.cropXEnd].ravel().tolist(), self.imageData[1].astype(np.int16)[self.cropYStart-1:self.cropYEnd, self.cropXStart-1:self.cropXEnd].ravel().tolist(), self.imageData[2][self.cropYStart-1:self.cropYEnd, self.cropXStart-1:self.cropXEnd].astype(np.int16).ravel().tolist()
    
'''
class dbCommunicator():
    def __init__():
        self.serverIP = "192.168.1.133"
        self.password = "w0lfg4ng"
'''
########################################################
################## Execute the UI#######################

if __name__ == '__main__':
    app = wx.App()
    ui = ImageUI(None, title='Atom Image Analysis Dy v1.6')
    app.MainLoop()