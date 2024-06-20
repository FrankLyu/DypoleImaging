# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 16:15:58 2020

@author: Dypole
"""

import numpy as np
from config import imagingWavelength
from imgFunc_v6 import radialAverage, gaussianFit

class ImageFitManager():
    def __init__(self, AOI_PrimaryImage = None):
        ### Image data definition
        self.AOI_PrimaryImage = AOI_PrimaryImage

        ### Data for calculation
        self.pixelSize = 1*10**(-6)
        self.magnification = 1
        self.pixelToDistance = self.pixelSize / self.magnification
        self.imagingWavelength = imagingWavelength
        self.crossSection = 6 * np.pi * (self.imagingWavelength/(2*np.pi))**2

        ### Fitting variables
        self.rawAtomNumber = None
        self.atomNumber = None
        self.isXFitSuccessful = False
        self.isYFitSuccessful = False
        self.x_summed = None
        self.y_summed = None
        self.x_basis = None
        self.y_basis = None
        self.x_center = None
        self.y_center = None
        
    ### set functions ###
    def setAOI_PrimaryImage(self, AOI_PrimaryImage):
        self.AOI_PrimaryImage = AOI_PrimaryImage
    
    def setPixelSize(self, pixelSize):
        self.pixelSize = pixelSize*10**(-6)   # It take the value in micrometers from the UI
    
    def setMagnification(self, magnification):
        self.magnification = magnification
    
    def setPixelToDistance(self):
        self.pixelToDistance = self.pixelSize / self.magnification
    
    def setImageData(self, imageData):
        self.imageData = imageData

    ### main encapsulating functions ###
    
    def setFit(self):
        self.set1DProfiles()
        self.setAtomNumber

    ###### subfunction ###

    ######### setFit subfunction ###

    def set1DProfiles(self, calculateRadialAverage = False):
        self.calc1DProfiles()           # it defines the function that are the sums over each axis of the AOI Image.
        if calculateRadialAverage:   # used to be: if self.checkDisplayRadialAvg.GetValue(): # do a radial average
            self.calc1DRadialAverage()
        self.fit()
        self.update1DProfiles()
        self.updateFittingResults()
    
    def setAtomNumber(self):
        self.setConstants()
        self.setRawAtomNumber()
        self.atomNumber = self.rawAtomNumber *  (self.pixelToDistance**2)/self.crossSection

    ######### sub-subfunction ###
    
    ############ set1DProfile subfunctions
    def calc1DProfiles(self):
        # it defines the function that are the sums over each axis of the AOI Image.
        y_size, x_size = self.AOI_PrimaryImage.shape
        self.x_summed = np.sum(self.AOI_PrimaryImage,axis=0)
        self.x_basis =  np.linspace(self.xLeft_Primary, self.xRight_Primary, x_size)
        self.y_summed = np.sum(self.AOI_PrimaryImage,axis=1)
        self.y_basis = np.linspace(self.yTop_Primary, self.yBottom_Primary, y_size)
        
    def calc1DRadialAvgAndRefit(self):
        # Note: a fit on the 1D profiles has already been done, therefore we use the 
        # result to find where to start the radial average.
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




###### Those functions should go in the core / UI region

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
    
    def updateFittingResults(self):
        self.updateTrueWidths()
        self.updatePeakValues()
        self.updateTemp()
        
        if self.fitMethodBoson.GetValue() is True:
            self.updateBosonParams()
            print(" ~~~~ BEC population ratio: " + str(self.x_becPopulationRatio))
        elif self.fitMethodFermion.GetValue() is True:
            self.updateFermionParams()