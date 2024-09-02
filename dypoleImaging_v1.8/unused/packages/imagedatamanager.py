# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 16:15:58 2020

@author: Dypole
"""

import numpy as np
from config import imagingWavelength
from imgFunc_v6 import gaussianFit
from fitTool import radialAverage

class ImageDataManager():
    def __init__(self, imageData = None):
        ### Image data definition
        self.imageData = imageData
        self.atomImage = None
        # self.betterRef = None   # unused for now, will be eventually for PCA and other transformations
        
        ### Maybe should go away?
        # self.pixelDepth = np.uint8
        
        ### Primary AOI
        self.xLeft_Primary = 0
        self.xRight_Primary = 0
        self.yTop_Primary = 0
        self.yBottom_Primary = 0
                
        ### Secondary AOI
        self.xLeft_Secondary = 0
        self.xRight_Secondary = 0
        self.yTop_Secondary = 0
        self.yBottom_Secondary = 0
        
        self.AOI_PrimaryImage = None
        
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

    def setPixelSize(self, pixelSize):
        self.pixelSize = pixelSize*10**(-6)   # It take the value in micrometers from the UI
    
    def setMagnification(self, magnification):
        self.magnification = magnification
    
    def setPixelToDistance(self):
        self.pixelToDistance = self.pixelSize / self.magnification
    
    def setImageData(self, imageData):
        self.imageData = imageData

    def setPrimaryAOI(self, xLeft, xRight, yTop, yBottom):
        self.xLeft_Primary = xLeft
        self.xRight_Primary = xRight
        self.yTop_Primary = yTop
        self.yBottom_Primary = yBottom
     
    def setSecondaryAOI(self, xLeft, xRight, yTop, yBottom):
        self.xLeft_Secondary = xLeft
        self.xRight_Secondary = xRight
        self.yTop_Secondary = yTop
        self.yBottom_Secondary = yBottom
    
    ### main encapsulating functions ###
    
    def setAtomImageAndFit(self, defringing = False, pca = False, gaussianFilter = False, histogramEqualization = False, rotation  = True):
        self.setLightDifferencePerPixel()
        self.setAtomImage(self, defringing = False, pca = False, gaussianFilter = False, histogramEqualization = False, rotation  = True)
        self.setFit()
    
    def setLightDifferencePerPixel(self):  # Computes the ligth level difference in the secondary AOI between the atom and light shot
        atomLight = np.mean(self.imageData[0][self.yTop_Secondary:self.yBottom_Secondary, self.xLeft_Secondary:self.xRight_Secondary])
        lightLight = np.mean(self.imageData[1][self.yTop_Secondary:self.yBottom_Secondary, self.xLeft_Secondary:self.xRight_Secondary])
        self.lightDifferencePerPixel = atomLight/lightLight
    
    def setAtomImage(self, defringing = False, pca = False, gaussianFilter = False, histogramEqualization = False, rotation  = True):
        self.setDividedImage(self, defringing)
        #self.setTransformedData(self, pca, gaussianFilter, histogramEqualization, rotation)
        # For the moment I do not do any image transformation. When we want to do histogram equalization for instance, it would be better to 
        # not take the log here and use the setTransformedData function bellow.
    
    def setFit(self):
        self.setAOI_PrimaryImage()
        self.set1DProfiles()
        self.setAtomNumber

    ###### subfunction ###
    
    ######### setAtomImage subfunction ###
        
    def setDividedImage(self, defringing = False):
        if len(self.imageData) != 3:
            raise Exception("~~~~~~ Given image does not have three layers ~~~~~~~")
        if defringing is True:
            correctedNoAtom = self.betterRef
            if (correctedNoAtom is None) or (correctedNoAtom.shape != self.imageData[1].shape):
                correctedNoAtom = self.imageData[1] - self.imageData[2]
        else:
            correctedNoAtom = self.imageData[1]*self.lightDifferencePerPixel - self.imageData[2]
        if correctedNoAtom is None:
            correctedNoAtom = self.imageData[1] - self.imageData[2]
    
        self.atomImage = np.maximum(self.imageData[0]-self.imageData[2], 1)/(np.maximum(correctedNoAtom, 1))  
        # if atom - dark is smaller than 0 it should  be set to 1
        
        # For the moment I do not do any image transformation. When we want to do histogram equalization for instance, it would be better to 
        # not take the log here and use the setTransformedData function bellow.
        self.atomImage = -np.log(self.atomImage)
    
    ######### setFit subfunction ###
    
    def setAOI_PrimaryImage(self):
        self.AOI_PrimaryImage = self.atomImage[self.yTop_Primary:self.yBottom_Primary, self.xLeft_Primary:self.xRight_Primary]
    
    ######### sub-subfunction ###
    
    ############ set1DProfile subfunctions


    # def setTransformedData(self, pca = False, gaussianFilter = False, histogramEqualization = False, rotation  = True):
    #     try:
    #         absorbImg = self.atomImage # is that necessary?
    #         if not self.isDummyImage:
    #             if pca is True:
    #                 try:
    #                     print("----------------1=================")
    #                     pca = sklearnPCA('mle')
    #                     print("----------------2=================")
    #                     temp = pca.fit_transform(-np.log(absorbImg))
    #                     print("----------------3=================")
    #                 except Exception:
    #                     raise Exception("======= PCA ERROR ========")
                    
    #             if gaussianFilter is True:
    #                 try:
    #                     print("1111111111")
    #                     tempp = -np.log(absorbImg)
    #                     print("22222222222")
    #                     signal = tempp[self.yTop_Primary:self.yBottom_Primary, self.xLeft_Primary:self.xRight_Primary]
    #                     print(signal)
    #                     print("33333333333")
    #                     filtered = gaussian_filter(tempp, 2, order = 0, truncate = 2)
    #                     print("44444444444")
    #                     print("55555555555")
    #                     temp = filtered
                        
    #                     print('====== Gaussian filter success ======')
    #                 except Exception:
    #                     raise Exception("========= Gaussian Filter ERROR =======")
                        
    #             if histogramEqualization is True:
    #                 try:
    #                     temp = self.histogramEq(temp)
    #                     print('====== histogram equalization success ======')
    #                 except Exception:
    #                     raise Exception("========= Histogram Equalization ERROR =======")
                        
    #             if (histogramEqualization is False) and (gaussianFilter is False) and (pca is False):
    #                 print('====== no filters IN ======')
    #                 temp = -np.log(absorbImg)
    #                 print('====== no filters OUT ======')
                    
    #             if self.isNormalizationOn is True:
    #                 print('tried to normalize')
    #                 temp = -np.log(createNormalizedAbsorbImg(self.imageData, self.AOI_Primary))
        
    #             if self.isMedianFilterOn is True:
    #                 try:
    #                     temp = medfilt(temp)
    #                 except Exception:
    #                     raise Exception("======= Median Filter ERROR ========")
                        
    #             if rotation is True:
    #                 try:
    #                     if self.isRotationNeeded is True:
    #                         temp = self.rotateImage(temp, self.imageAngle, [self.imagePivotX, self.imagePivotY])
    #                         print("======= rotation executed =======")
    #                     else:
    #                         print("======= No Rotation required for 0 deg. =======")
    #                 except Exception:
    #                     raise Exception("========= rotation ERROR =======")
                
    #             self.atomImage = temp
    #         del absorbImg
    #     except:
    #         print("Fail to postprocess the image")
    #     try:
    #         absorbImg = self.atomImage # is that necessary?
    #         if not self.isDummyImage:
    #             # sklearnPCA doesn't seem available, need to rebuild something else?
    #             if pca is True:
    #                 try:
    #                     print("----------------1=================")
    #                     pca = sklearnPCA('mle')
    #                     print("----------------2=================")
    #                     temp = pca.fit_transform(-np.log(absorbImg))
    #                     print("----------------3=================")
    # #                    temp = pca.explained_varaince_
    # #                    print temp.shape
    # #                    print temp[0].type
    #                 except Exception:
    #                     raise Exception("======= PCA ERROR ========")
                    
    #             if gaussianFilter is True:
    #                 try:
    #                     print("1111111111")
    #                     tempp = -np.log(absorbImg)
    #                     print("22222222222")
    #                     signal = tempp[self.yTop_Primary:self.yBottom_Primary, self.xLeft_Primary:self.xRight_Primary]
    #                     print(signal)
    #                     print("33333333333")
    #                     filtered = gaussian_filter(tempp, 2, order = 0, truncate = 2)
    #                     print("44444444444")
    # #                    filtered[self.yTop:self.yBottom, self.xLeft:self.xRight] = signal
    #                     print("55555555555")
    #                     temp = filtered
                        
    #                     print('====== Gaussian filter success ======')
    # #                    temp2 = temp
    #                 except Exception:
    #                     raise Exception("========= Gaussian Filter ERROR =======")
                        
    #             if histogramEqualization is True:
    #                 try:
    #                     temp = self.histogramEq(temp)
    #                     print('====== histogram equalization success ======')
    #                 except Exception:
    #                     raise Exception("========= Histogram Equalization ERROR =======")
                        
    #             if (histogramEqualization is False) and (gaussianFilter is False) and (pca is False):
    #                 print('====== no filters IN ======')
    #                 temp = -np.log(absorbImg)
    #                 print('====== no filters OUT ======')
                    
    #             if self.isNormalizationOn is True:
    #                 print('tried to normalize')
    #                 temp = -np.log(createNormalizedAbsorbImg(self.imageData, self.AOI_Primary))
        
    #             if self.isMedianFilterOn is True:
    #                 try:
    #                     temp = medfilt(temp)
    #                 except Exception:
    #                     raise Exception("======= Median Filter ERROR ========")
    
    #             if rotation is True:
    #                 try:
    #                     if self.isRotationNeeded is True:
    #                         temp = self.rotateImage(temp, self.imageAngle, [self.imagePivotX, self.imagePivotY])
    #                         print("======= rotation executed =======")
    #                     else:
    #                         print("======= No Rotation required for 0 deg. =======")
    #                 except Exception:
    #                     raise Exception("========= rotation ERROR =======")
                
    #             self.atomImage = temp
    #         del absorbImg
    #     except:
    #         print("Fail to postprocess the image")
    
    
    
    
    # def rotateImage(self, img, angle, pivot):
    #     padX = [int(img.shape[1] - pivot[0]), int(pivot[0])]
    #     padY = [int(img.shape[0] - pivot[1]), int(pivot[1])]
    #     imgP = np.pad(img, [padY, padX], 'constant', constant_values=[(0,0), (0,0)])
    #     imgR = ndimage.rotate(imgP, angle, reshape = False)
    #     return imgR[padY[0] : -padY[1], padX[0] : -padX[1]]
    
    