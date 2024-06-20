# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 13:28:25 2021

@author: Dypole_Imaging
"""

import os
import time
from astropy.io import fits

def readFITS(path):
    start = time.time()
    imageData=[]
    try:
        fitsHDUlist = fits.open(path)
    except Exception as e:
        print(str(e))
        
    fits_data = fitsHDUlist[0].data
    for i in [0,1,2]:
        imageData.append((fits_data[i]).astype(float))

    end = time.time()
    print(str(end - start) + " seconds taken for FITS reading....")
    return imageData

path = os.getcwd() + "\\image\\combinedShots.fits"
fitsHDUlist = fits.open(path)
fits_data = fitsHDUlist[0].data
print(fitsHDUlist.info())
print(fits_data)