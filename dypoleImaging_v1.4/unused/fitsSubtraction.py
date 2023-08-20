# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 04:02:32 2017

@author: BEC3
"""

import os, sys, glob, gc
from os import listdir
from os.path import isfile, join
from matplotlib import gridspec
from matplotlib import rc

import wx, numpy
import matplotlib
import datetime
#from datetime import datetime as now
import time
#import winsound
matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
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

from canvasPanel import *
from figurePanel import *
from canvasFrame import *

def readFits(filename):
    imageData=[]
    print "Opening fits image: " + filename
    try:
        fitsHDUlist=fits.open(filename)
    except Exception, e:
        print str(e)
   
        print "Opened fits file"
    fits_data = fitsHDUlist[0].data
    print "read fits image"
    for i in [0,1,2]:
			#temp = np.sum(np.array(fits_data[i]).astype('float'), axis=2)
        imageData.append((fits_data[i]).astype(float))
        
    rowTotal,colTotal = np.shape(imageData[0])

    
###  Construct the transmittance map, with an np.maximum statement to avoid dividing by zero.
    absorbImg=(imageData[0]-imageData[2])/(np.maximum(imageData[1]-imageData[2],1))  
    #print absorbImg
###  Replace extremely low transmission pixels with a minimum meaningful transmission. 
    minT = np.exp(-5)
    
    temp = np.empty((rowTotal,colTotal))	
    temp.fill(minT)
    
    absorbImg = np.maximum(absorbImg, temp)

    temp2 = np.where(np.array(imageData[0]) <= np.array(imageData[2]))
    absorbImg = np.array(absorbImg)
    absorbImg[temp2] = 1

    return absorbImg

if __name__ == '__main__':
    path = "C:\\shared_data\\AndorTransfer\\2017\\3\\30\\Li\\"
    filePathNoDiss = path + str("kinetics_2017-3-30_ 3_52_50.fits")
    filePathDiss = path + str("kinetics_2017-3-30_ 3_54_04.fits")
    noDissImage = -np.log(readFits(filePathNoDiss))
    dissImage = -np.log(readFits(filePathDiss))
    
    vIndexRange = [300, 400]
    vStart = vIndexRange[0]
    vNum = vStart + vIndexRange[-1] -1
    noDissImage = noDissImage[vStart:vNum,:-1]
    dissImage = dissImage[vStart:vNum,:-1]
    diffImage = np.subtract(dissImage, noDissImage)
    
    f, (axes1, axes2, axes3) = plt.subplots(3, 1, sharex=True)

#    figure = Figure()
##        figure.tight_layout(h_pad=1.0) 
#    gs = gridspec.GridSpec(1, 3)
#    gs.update(wspace = 2, hspace = 2)
#    axes1 = figure.add_subplot(gs[0, 0])
    axes1.imshow(noDissImage, cmap='gray_r', aspect='auto', vmin=-1, vmax=1)
    
#    axes2 = figure.add_subplot(gs[0, 1])
    axes2.imshow(dissImage, cmap='gray_r', aspect='auto', vmin=-1, vmax=1)
    
#    axes3 = figure.add_subplot(gs[0, 2])
    axes3.imshow(diffImage, cmap='gray_r', aspect='auto', vmin=-1, vmax=1)
    
    f.subplots_adjust(hspace=0)
    plt.show()
#    panel = wx.Panel()
#    canvas =  FigureCanvas(panel, -1, figure)
#    canvas.draw()


