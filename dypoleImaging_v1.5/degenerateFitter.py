#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 26 17:17:42 2018

@author: hyungmokson
"""
import numpy as np
from scipy.optimize import minimize
from scipy.optimize import curve_fit
from scipy.optimize import basinhopping
import os
from os import listdir
from os.path import isfile, join       
from decimal import Decimal
from scipy import stats
import sys, struct
from math import sqrt, log, atan
import matplotlib.pyplot as plt
from mpmath import mp
from PIL import Image

from polylog import *
from imgFunc_v6 import *
from fitTool import *

import copy
import time
import matplotlib.image as mpimg
from astropy.io import fits
from skimage import io
from scipy import ndimage
from scipy.ndimage.filters import convolve
from scipy.ndimage.filters import gaussian_filter
from scipy.ndimage.filters import median_filter


#from matplotlib.pyplot import figure, show
#import matplotlib
#from matplotlib import gridspec
#from matplotlib.figure import Figure

class degenerateFitter():
    def __init__(self):
        ## initial guess for the degenerate fitting
        self.x_center = 0.
        self.x_width = 1.
        self.x_peakHeight = 1.
        self.x_offset = 0.
        self.x_slope = 0.
        
        ## data to fit ----  1D profile
        self.x_basis = np.array([])
        self.x_summed = np.array([])
                
        ## degenerate fitting result parameters
        self.x_center_degen = 0.
        self.thermal_width = 1.
        self.thermal_amp = 1.
        self.TF_radius = 1.
        self.BEC_amp = 1.
        self.offset_degen = 0.
        self.slope_degen = 0.  
        
        self.totalPopulation = 1.        
        
    def setInitialCenter(self, x0):
        self.x_center = x0
    
    def setInitialWidth(self, w0):
        self.x_width = w0
    
    def setInitialPeakHeight(self, h0):
        self.x_peakHeight = h0
    
    def setInitialOffset(self, offset):
        self.x_offset = offset
    
    def setInitialSlope(self, slope):
        self.x_slope = slope

    def setData(self, basis, data):
        self.x_basis = basis
        self.x_summed = data    
    
    def getFolded1DProfile(self):
        temp_center_x = int(round(self.x_center))
        below_center = self.x_summed[:temp_center_x]
        above_center = self.x_summed[temp_center_x:]
        profile_length = np.minimum(len(below_center), len(above_center))
        
        x_folded_profile = np.empty(profile_length)
        x_folded_profile[0] = self.x_summed[temp_center_x]
        for i in np.arange(1, profile_length-1):
            x_folded_profile[i] = (above_center[i] + below_center[-i])/2.
        
        self.x_folded_profile = x_folded_profile
        self.x_folded_basis = np.linspace(temp_center_x, above_center[profile_length-1], profile_length)
    
    def doDegenerateFit(self):
        ##############################################################################
        #        x0, thermal_sigma, thermal_amp, TF_radius, BEC_amp, offset, slope
        ##############################################################################
        try:
            if len(self.x_basis) == 0 or len(self.x_summed) == 0:
                raise Exception(" <<<<<< Can't do Degenerate fit since NO DATA >>>>>>>> ")
                        
            def letsFit(scaling_factor):
                g = [self.x_center,  10.*scaling_factor*self.x_width, self.x_peakHeight/scaling_factor/10., self.x_width/scaling_factor, scaling_factor*self.x_peakHeight, self.x_offset, self.x_slope]
                b  = ([0.8 * g[0], 0, 0, 0, 0, -np.inf, -np.inf], [1.2 *g[0], np.inf, np.inf, np.inf, np.inf, np.inf, np.inf])
                time1 = time.time()
                p, q = curve_fit(condensate1DDist, self.x_basis, self.x_summed, p0=g, bounds = b, method = 'trf', maxfev=1e10)
                time2 = time.time()
                print("-------- BEC fit took " + str(time2 - time1) + " seconds...")
                print(p)
                self.x_center_degen = p[0]
                self.thermal_width = p[1]
                self.thermal_amp = p[2]
                self.TF_radius = p[3]
                self.BEC_amp = p[4]
                self.offset_degen = p[5]
                self.slope_degen = p[6]
                
            def fitDecider():
                if self.thermal_width > self.TF_radius and self.BEC_amp >= self.thermal_amp:
                    return True
                else:
                    return False
            
            i = 0
            num_trial = 20
            sc = 1
            while i < num_trial:
                letsFit(sc)
                if fitDecider() is True:
                    print(" <<<<<< BEC FIT SUCCEEDED >>>>>> ")
                    break
                print("======= BEC fit " + str(i+1) + " trial =======")
                i += 1
                sc += .25
            
            if i == num_trial:
                g = [self.x_center,  self.x_width, self.x_peakHeight, self.x_offset, self.x_slope]
                b  = ([0.8 * g[0], 0, 0, -np.inf, -np.inf], [1.2 *g[0], np.inf, np.inf, np.inf, np.inf])
                p, q = curve_fit(pureCondensate1D, self.x_basis, self.x_summed, p0=g, bounds = b, method = 'trf', maxfev=1e10)
                
                self.x_center_degen = p[0]
                self.thermal_width = 0.
                self.thermal_amp = 0.
                self.TF_radius = p[1]
                self.BEC_amp = p[2]
                self.offset_degen = p[3]
                self.slope_degen = p[4]
            
            self.x_fitted_degen = condensate1DDist(self.x_basis, self.x_center_degen, self.thermal_width, self.thermal_amp, self.TF_radius, self.BEC_amp, self.offset_degen, self.slope_degen)
            self.calculateTemp()
        except Exception as e:
            print("")
            print("")
            print(" ~~~~~~~~ degenerate fitting failed ~~~~~~~~~")
            print(e)
            print("")
            print("")
            return e

    #    def setProfileLimits(self):
    #        y_size, x_size = self.AOIImage.shape
    #
    #        yMax = np.maximum(self.y_summed.max(), self.y_fitted.max())
    #        yMin = np.minimum(self.y_summed.min(), self.y_fitted.min())
    #        for a in [self.axes3, self.axes5]:            
    #            a.set_xlim([yMin, yMax])
    #            a.set_ylim([y_size, 0])
    #            a.set_xticks(np.linspace(yMin, yMax, 3))
    #            a.xaxis.set_ticks_position('top')
    #
    #        xMax = np.maximum(self.x_summed.max(), self.x_fitted.max())
    #        xMin = np.minimum(self.x_summed.min(), self.x_fitted.min())
    #        for a in [self.axes2, self.axes4]:            
    #            a.set_xlim([0, x_size])
    #            a.set_ylim([xMin, xMax])            
    #            a.set_yticks(np.linspace(xMin, xMax, 4))
                
    def calculateTemp(self):
        becPopulation = self.BEC_amp  * 4./3. * self.TF_radius
        thermalPopulation = self.thermal_amp *np.sqrt(2 * np.pi) * self.thermal_width
        temp = condensate1DDist(self.x_basis, self.x_center_degen, self.thermal_width, self.thermal_amp, self.TF_radius, self.BEC_amp, 0., 0.)
        totalPopulation = np.trapz(temp, self.x_basis, dx=.1)
        
        self.totalPopulation = totalPopulation
        self.becPopulationRatio = (becPopulation/totalPopulation)
        self.tOverTc = (1 - self.becPopulationRatio)**(1./3.)
        
        print("")
        print("")
        print("BEC population: " + str(becPopulation))
        
        print("")
        print("thermal population: " + str(thermalPopulation))        
        
        print("sum = " + str(becPopulation + thermalPopulation))
        print("")
        print("Total population: " + str(totalPopulation))
        
        print("")
        print("")
        print(" ~~~~~~ T/T_C = " + str(self.tOverTc))
        print("")
        print("")
    
    def getFittedProfile(self):
        return self.x_fitted_degen
    
    def getTOverTc(self):
        return self.tOverTc
    
    def getTotalPopulation(self):
        return self.totalPopulation
    
    def getBecPopulationRatio(self):
        return self.becPopulationRatio
    
    def getThomasFermiRadius(self):
        return self.TF_radius
    
    def getThermalWidth(self):
        return self.thermal_width
    
    def getThermalAmp(self):
        return self.thermal_amp
    
