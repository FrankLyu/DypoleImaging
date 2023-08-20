# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 12:31:04 2017

@author: Jim Hyungmok Son
"""

import os, sys, glob, gc
from os import listdir
from os.path import isfile, join
from matplotlib import gridspec
from matplotlib import rc

#1mport wx, numpy
import numpy as np
import matplotlib
import datetime
#from datetime import datetime as now
import time
#import winsound
#matplotlib.use('WXAgg')

from sklearn.decomposition import PCA as sklearnPCA
from astropy.io import fits
from matplotlib.mlab import PCA

from scipy import linalg as LA
from scipy import ndimage

#from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
#from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from scipy.ndimage.filters import convolve
from scipy.ndimage.filters import gaussian_filter
from scipy.optimize import curve_fit

from PIL import Image

from shutil import copyfile

from imagePlot import *
from imgFunc_v6 import *
from watchforchange import *
from localPath import *
from exp_params import *
from fitTool import *
from Monitor import*

#from canvasPanel import *
#from figurePanel import *
#from canvasFrame import *
class defringer():
    def __init__(self):
        self.backgroundPath = "D:\\Dropbox (MIT)\\BEC3-CODE\\imageAnalyze\\working branch\\side images_EMCCD\\pca_test\\background\\"
        self.imagePath = "D:\\Dropbox (MIT)\\BEC3-CODE\\imageAnalyze\\working branch\\side images_EMCCD\\pca_test\\atoms\\"
#        self.backgroundPath = "/Users/hyungmokson/Dropbox (MIT)/BEC3-CODE/imageAnalyze/working branch/side images_EMCCD/pca_test/background/"
#        self.imagePath = "/Users/hyungmokson/Dropbox (MIT)/BEC3-CODE/imageAnalyze/working branch/side images_EMCCD/pca_test/atoms/"
        self.yTop = 0
        self.yBottom = 1        
        self.xLeft = 0
        self.xRight = 1
        self.roiIndex = []
        self.betterRef = []                 
                                                     
#    def readThreeLayers(self, filename):
#        imageData=[]
#        print "Opening fits image: " + filename
#        try:
#            fitsHDUlist=fits.open(filename)
#        except Exception, e:
#            print str(e)
#       
#            print "Opened fits file"
#        fits_data = fitsHDUlist[0].data
#        print "read fits image"
#        for i in [0,1,2]:
#    			#temp = np.sum(np.array(fits_data[i]).astype('float'), axis=2)
#            imageData.append((fits_data[i]).astype(float))
#        return imageData
#    
#    def readNoAtomImage(self, filename):
#        imageData = self.readThreeLayers(filename)
#        temp= np.asarray(imageData[1] - imageData[2])
#        return np.maximum(temp, .1)
#    
#    def readNoAtomImageFlattened(self, fileNameList):
#        temp = []
#        for fileName in fileNameList:
#            temp.append(self.readNoAtomImage(fileName).flatten())
#        return np.array(temp)
#        
#    def readAtomImage(self, filename):
#        imageData = self.readThreeLayers(filename)
#        temp = np.asarray(imageData[0] - imageData[2])
#        return np.maximum(temp, .1)
    
#    def readFits(self, filename):
#        imageData=[]
#        print "Opening fits image: " + filename
#        try:
#            fitsHDUlist = fits.open(filename)
#        except Exception, e:
#            print str(e)
#       
#            print "Opened fits file"
#        fits_data = fitsHDUlist[0].data
#        print "read fits image"
#        for i in [0,1,2]:
#    			#temp = np.sum(np.array(fits_data[i]).astype('float'), axis=2)
#            imageData.append((fits_data[i]).astype(float))
#            
#        rowTotal,colTotal = np.shape(imageData[0])
#    
#        
#    ###  Construct the transmittance map, with an np.maximum statement to avoid dividing by zero.
#        absorbImg=np.maximum(imageData[0]-imageData[2], .1)/np.maximum(imageData[1]-imageData[2], .1)
#        #print absorbImg
#    ###  Replace extremely low transmission pixels with a minimum meaningful transmission. 
#        minT = np.exp(-5)
#        
#        temp = np.empty((rowTotal,colTotal))	
#        temp.fill(minT)
#        
#        absorbImg = np.maximum(absorbImg, temp)
#    
#        temp2 = np.where(np.array(imageData[0]) <= np.array(imageData[2]))
#        absorbImg = np.array(absorbImg)
#        absorbImg[temp2] = 1
#    
#        return absorbImg
    
    def images(self, fileNameList):
        temp = []
        for fileName in fileNameList:
            temp.append(-np.log(self.readFits(fileName)))
        return temp
        
    def imagesFlattened(self, fileNameList):
        temp = []
        for fileName in fileNameList:
            temp.append(-np.log(self.readFits(fileName).flatten()))
        return np.array(temp)
    
    def avgImages(self, fileNameList):
        temp = np.asarray(self.images(fileNameList))    
        return np.mean(temp, axis = 0)
        
    def setNoAtomFilePath(self, path):
        self.backgroundPath = path
    
    def defringedRef(self, absImgFileName, setRoiIndex = False):
        pathForBackGround = self.backgroundPath
        os.chdir(pathForBackGround)   
        noAtomFileNameList =  glob.glob(pathForBackGround + '*.' + 'fits')
        
        noAtomList = readNoAtomImageFlattened(noAtomFileNameList)
        atomImage = readAtomImage(absImgFileName)
        #        roiIndex = np.ones(atomImage.shape).flatten()
        if setRoiIndex is False:
#            print atomImage.shape
            self.roiIndex = np.ones(atomImage.shape).flatten()
#            print self.roiIndex.shape
        else:
#            np.set_printoptions(threshold = np.inf)
            temp = np.ones(atomImage.shape)      
#            temp[max(0, self.yTop-3):min(temp.shape[0], self.yBottom+4), max(0, self.xLeft-3):min(self.xRight+4, temp.shape[1])] = 0
            temp[self.yTop-3:self.yBottom+4, self.xLeft-3:self.xRight+4] = 0
            self.roiIndex = temp.flatten()
            
        betterNoAtom = self.createBetterRef(self.roiIndex, noAtomList, atomImage.flatten()).reshape(atomImage.shape)
        self.betterRef = betterNoAtom
        
        return betterNoAtom

    def defringedImage(self, absImgFileName, setRoiIndex = False):
        atomImage = readAtomImage(absImgFileName)
        betterRef = self.defringedRef(absImgFileName, setRoiIndex)        
        absorbImg = -np.log(atomImage/betterRef)
        
        minT = np.exp(-5)
        temp = np.empty(atomImage.shape)	
        temp.fill(minT)
        absorbImg = np.maximum(absorbImg, temp)
        return absorbImg
        
    def BMatrix(self, roiIndex, noAtomImageList):
        numOfRef = noAtomImageList.shape[0]
        BMatrix = np.zeros((numOfRef, numOfRef))
        for i in range(numOfRef):
            for j in range(numOfRef):
                BMatrix[i,j] = np.sum(np.dot(np.dot(noAtomImageList[i], noAtomImageList[j]), roiIndex))
                
        return BMatrix
    
    def DVector(self, roiIndex, noAtomImageList, atomImage):
        numOfRef = noAtomImageList.shape[0]
        DVector = np.zeros(numOfRef)
        for i in range(numOfRef):
            DVector[i] = np.sum(np.dot(np.dot(atomImage, noAtomImageList[i]), roiIndex))
            
        return DVector
    
    def createBetterRef(self, roiIndex, noAtomList, absImage):
        B = self.BMatrix(roiIndex, noAtomList)
        DVec = self.DVector(roiIndex, noAtomList, absImage)
#        print "This is B ---------------------"        
#        print B
#        print "This is B ---------------------"        
#        print "This is DVec ---------------------"
#        print DVec        
#        print "This is DVec ---------------------"        
        CVec = LA.solve(B, DVec)
        
        ref = np.zeros(absImage.shape)
        for i in range(len(CVec)):
            ref += CVec[i] * noAtomList[i]                    
#        print ref
        return ref
    
    def setRoiIndex(self, roiIndex):
        self.yTop = roiIndex[1]
        self.yBottom = roiIndex[3]
        self.xLeft = roiIndex[0]
        self.xRight = roiIndex[2]

    def meanSquaredDeviation(self, NoAtomImage, atomImage):
        print self.roiIndex.shape
        return np.sum(np.dot((NoAtomImage - atomImage)**2, self.roiIndex))
         
if __name__ == '__main__':
#    tester = PCA_test()
#    pathForBackGround = tester.backgroundPath
#    os.chdir(pathForBackGround)   
#    fileList =  glob.glob(pathForBackGround + '*.' + 'fits')
##    print fileList  
##    background = tester.avgAbsorbImages(fileList)
#    backgroundList = tester.imagesFlattened(fileList)
##    backgroundAvg = backgroundList - backgroundList.mean(axis = 0)
#    print backgroundList.shape
#    
#    tester.myPCA(backgroundList)
#    ## perform the PCA
#    n = len(fileList)
##    pca = sklearnPCA(8).fit(background)
##    print pca.components_.shape
#    
    
#    pca.fit(backgrounud)
#    transBacground = pca.transform(background)

    tester = defringer()

    pathForBackGround = tester.backgroundPath
    os.chdir(pathForBackGround)   
    noAtomList =  glob.glob(pathForBackGround + '*.' + 'fits')
    
#    print noAtomList
    
    pathForAtomImage = tester.imagePath
    os.chdir(pathForAtomImage)
    atomImage = glob.glob(pathForAtomImage + '*.' + 'fits')[0]    
    original = -np.log(readData(atomImage, "fits")[1])

#    print noAtomList   
    tester.setRoiIndex([88, 70, 115, 93])
    corrected = tester.defringedImage(atomImage, setRoiIndex = True)
#    corrected = original

    msdOriginal = tester.meanSquaredDeviation(readNoAtomImage(atomImage).flatten(), readAtomImage(atomImage).flatten())
    msdCorrected = tester.meanSquaredDeviation(tester.betterRef.flatten(), readAtomImage(atomImage).flatten())
    
    print msdOriginal
    print msdCorrected
    print (msdOriginal - msdCorrected)*100./msdOriginal
    
    ## plot the image
    f, (axes1, axes2) = plt.subplots(1, 2, sharex=True)
    axes1.imshow(original, cmap='gray_r', aspect='auto', vmin=-1, vmax=1)
    axes2.imshow(corrected, cmap='gray_r', aspect='auto', vmin=-1, vmax=1)
    plt.show()
    
    

#if __name__ == '__main__':
#    path = "C:\\shared_data\\AndorTransfer\\2017\\3\\30\\Li\\"
#    filePathNoDiss = path + str("kinetics_2017-3-30_ 3_52_50.fits")
#    filePathDiss = path + str("kinetics_2017-3-30_ 3_54_04.fits")
#    noDissImage = -np.log(readFits(filePathNoDiss))
#    dissImage = -np.log(readFits(filePathDiss))
#    
#    vIndexRange = [300, 400]
#    vStart = vIndexRange[0]
#    vNum = vStart + vIndexRange[-1] -1
#    noDissImage = noDissImage[vStart:vNum,:-1]
#    dissImage = dissImage[vStart:vNum,:-1]
#    diffImage = np.subtract(dissImage, noDissImage)
#    
#    f, (axes1, axes2, axes3) = plt.subplots(3, 1, sharex=True)
#
##    figure = Figure()
###        figure.tight_layout(h_pad=1.0) 
##    gs = gridspec.GridSpec(1, 3)
##    gs.update(wspace = 2, hspace = 2)
##    axes1 = figure.add_subplot(gs[0, 0])
#    axes1.imshow(noDissImage, cmap='gray_r', aspect='auto', vmin=-1, vmax=1)
#    
##    axes2 = figure.add_subplot(gs[0, 1])
#    axes2.imshow(dissImage, cmap='gray_r', aspect='auto', vmin=-1, vmax=1)
#    
##    axes3 = figure.add_subplot(gs[0, 2])
#    axes3.imshow(diffImage, cmap='gray_r', aspect='auto', vmin=-1, vmax=1)
#    
#    f.subplots_adjust(hspace=0)
#    plt.show()
##    panel = wx.Panel()
##    canvas =  FigureCanvas(panel, -1, figure)
##    canvas.draw()
#
#
