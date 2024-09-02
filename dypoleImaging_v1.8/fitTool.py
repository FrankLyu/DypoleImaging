## This file defines some image fitting tool functions
import numpy as np
from scipy.optimize import curve_fit
import operator
from polylog import *
import time
from mpmath import *
import matplotlib.pyplot as plt

#########################################################
#########################################################
#########################################################
### degenerate functions ###
### from Aug 27th 2018 ###

def condensate1DDist(data, x0, thermal_sigma, thermal_amp, TF_radius, BEC_amp, offset, slope):
    thermal = thermal_amp * np.exp(-(data - x0)**2/(2. * thermal_sigma**2)) 
    condensate = BEC_amp * np.maximum((1 -  ((data - x0)/TF_radius)**2), 0)
    return thermal + condensate + offset + data * slope
    
def pureCondensate1D(data, x0, TF_radius, BEC_amp, offset, slope):
    return BEC_amp * np.maximum((1 - ((data-x0)/TF_radius)**2), 0)

#########################################################

def single_G(x, A, center, sigma, offset):
    return A*np.exp(-1*((x-center)**2)/(2*sigma**2)) + offset 

def single_G_plus_slope(x, A, center, sigma, offset, slope):
    return A*np.exp(-1*((x-center)**2)/(2*sigma**2)) + offset + slope * x

def gaussian_2d(xy, A, x0, y0, sigma_x, sigma_y, offset):
    x,y=xy
    exponent = -((x - x0)**2 / (2 * sigma_x**2) + (y - y0)**2 / (2 * sigma_y**2))
    g = A * np.exp(exponent) + offset
    return g.ravel()

def gaussianFit2D(data,Initialparams):
    Guessx_width = Initialparams[0]
    Guessy_width = Initialparams[1]
    Guessx_center = Initialparams[2]
    Guessy_center = Initialparams[3]
    x_start = Initialparams[4]
    y_start = Initialparams[5]
    IsXSuc = Initialparams[6]
    IsYSuc = Initialparams[7]
    isFitSuccessful = False
    if not IsXSuc:
        Guessx_center = x_start + data.shape[1]//2
        Guessx_width = data.shape[1]//4
    if not IsYSuc:
        Guessy_center = y_start + data.shape[0]//2
        Guessy_width = data.shape[0]//4
    # Assuming data is your 2D data
    # x_fit and y_fit are the coordinates of the point you want to fit
    x = np.arange(data.shape[1])+x_start
    y = np.arange(data.shape[0])+y_start
    # Find the coordinates of the maximum value in the data

    X, Y = np.meshgrid(x, y)
    Z = data  # Your 2D data
    # Initial guess for the parameters
    # initial guess ODmax = 1
    initial_guess = (1, Guessx_center, Guessy_center, Guessx_width, Guessy_width, 0.0)
    # Perform the fit
    if data.shape[0]*data.shape[1]>500*500:
        A, xc, yc, sigma_x, sigma_y, offset = 0,0,0,0,0,0
        isFitSuccessful = False
        modifiedrawAtomNumber = -9527
        print("------ 2D Fit Failed ------")
    else:    
        try:
            params, covariance = curve_fit(gaussian_2d, (X, Y), Z.ravel(), p0=initial_guess)
            # Unpack the parameters
            A, xc, yc, sigma_x, sigma_y, offset = params
            isFitSuccessful = True
            modifiedrawAtomNumber = np.sum(data)-offset*np.size(data)
        except Exception:
            A, xc, yc, sigma_x, sigma_y, offset = 0,0,0,0,0,0
            modifiedrawAtomNumber = -9527
            isFitSuccessful = False
            print("------ 2D Fit Failed ------")
    
    return xc, yc, sigma_x, sigma_y, modifiedrawAtomNumber, isFitSuccessful


def gaussianFit(xBasis, x_summed, aoi, isWingsfit, axis = 'x', fitBounds = None):
    isFitSuccessful = False

    ## smoothing
    N_smoothing = np.minimum(np.size(xBasis)//10+1,10)
    x_summed_smooth = np.convolve(x_summed, np.ones((N_smoothing,))/N_smoothing, mode='valid')
    
    def funcToMin(data, amp): return abs(data - amp/2.)
    def widthFinder(amp, center, data): 
        temp=np.minimum(10,np.size(xBasis))
        try:
            result = min(abs(center * np.ones(len(data)) - np.argsort(funcToMin(data, amp)))[-temp:-3])/np.sqrt(2*np.log(2))
        except:
            result = 1
            print("Error in gaussianFit - widthFinder JL doesn't understand yet")
        if result <= 0:
            result = 1. ## minimum wdith guess for the fit
        return result
    
###############################################################################
    x_max_index = np.argmax(x_summed_smooth)
    x_max = x_summed_smooth[x_max_index]
    xWidth =  widthFinder(x_max, x_max_index, x_summed_smooth)

    if axis == 'x':
        index_offset = int(aoi.position[0])
    else:
        index_offset = int(aoi.position[1])     

    x_max_index = x_max_index + index_offset

    num = len(x_summed_smooth)
    num /= 10
    num = int(np.maximum(np.minimum(num, 5), 1))
    mean1 = np.mean(x_summed_smooth[:num])
    mean2 = np.mean(x_summed_smooth[-num:])  
    slope = mean2 - mean1
    xOffset = (mean1 + mean2)/2. 

    b = ([0., 0., 1e-3, -np.inf, -np.inf], [25*x_max, np.inf, np.inf, np.inf, np.inf])
    if fitBounds is not None:
        b[0][1] = fitBounds[0][0]
        b[0][2] = fitBounds[0][1]
        b[1][1] = fitBounds[1][0]
        b[1][2] = fitBounds[1][1]
    
    initialGuess = (x_max, x_max_index, xWidth, xOffset, slope)
    
    num_trial = 0
    max_num_trial = 3
    isFitSuccessful = False
    while (num_trial <= max_num_trial and isFitSuccessful is False):
        try:
            poptx, pcovx  = curve_fit(single_G_plus_slope, xBasis, x_summed, p0 = initialGuess, bounds = b)
    
            x_center = float(poptx[1]) 
            x_width = float(poptx[2])
            x_offset = float(poptx[3])
            x_peakHeight = float(poptx[0])
            x_slope = float(poptx[4])
            
            x_fitted = single_G_plus_slope(xBasis, x_peakHeight, x_center, x_width, x_offset, x_slope)
            isFitSuccessful = True
            print("")
            print("------- fit result --------" )
            print(poptx)
            err = np.sqrt(np.diag(pcovx))
            print("------ Gaussian fitting SUCCEEDED ------")
        except Exception:
            print("------ Gaussian fitting failed ------")
            
            if (num_trial == max_num_trial):
                x_center = 0.
                x_width = 0.
                x_offset = xOffset
                x_peakHeight = 0
                x_fitted = []
                x_slope = 0.
                err = np.array([0., 0., 0., 0., 0.])
                isFitSuccessful = False
            else:
                if (num_trial % 2 == 0):
                    x_width = xWidth/2**(1 + num_trial)
                else:
                    x_width = xWidth * 2**(num_trial)
                
            initialGuess = (x_max, x_max_index, xWidth, xOffset, slope)

        print("")
        print(" ================ FIT TRIAL " + str(num_trial+1) + " ===============")
        print("")
        print("")
            
        num_trial += 1

    if isWingsfit is True:
        num_trial = 0
        max_num_trial = 2
        isFitSuccessful = False
        exclude_range = (x_center-x_width*1, x_center+x_width*1)
        wing_indices = (xBasis < exclude_range[0]) | (xBasis > exclude_range[1])

        # Create subsets for the wings
        x_wings = xBasis[wing_indices]
        y_wings = x_summed[wing_indices]

        while (num_trial <= max_num_trial and isFitSuccessful is False):
            try:
                poptx, pcovx  = curve_fit(single_G_plus_slope, x_wings, y_wings, p0 = initialGuess, bounds = b)
        
                x_center = float(poptx[1]) 
                x_width = float(poptx[2])
                x_offset = float(poptx[3])
                x_peakHeight = float(poptx[0])
                x_slope = float(poptx[4])
                
                x_fitted = single_G_plus_slope(xBasis, x_peakHeight, x_center, x_width, x_offset, x_slope)
                isFitSuccessful = True
                print("")
                print("------- fit result --------" )
                print(poptx)
                err = np.sqrt(np.diag(pcovx))
                print("------ Gaussian wing (+-1sigma) fitting SUCCEEDED ------")
            except Exception:
                print("------ Gaussian wing (+-1sigma) fitting failed ------")
                
                if (num_trial == max_num_trial):
                    x_center = 0.
                    x_width = 0.
                    x_offset = xOffset
                    x_peakHeight = 0
                    x_fitted = []
                    x_slope = 0.
                    err = np.array([0., 0., 0., 0., 0.])
                    isFitSuccessful = False
                else:
                    if (num_trial % 2 == 0):
                        x_width = xWidth/2**(1 + num_trial)
                    else:
                        x_width = xWidth * 2**(num_trial)
                    
                initialGuess = (x_max, x_max_index, xWidth, xOffset, slope)

            print("")
            print(" ================ WING FIT TRIAL " + str(num_trial+1) + " ===============")
            print("")
            print("")
            
            num_trial += 1

    return x_center, x_width, x_offset, x_peakHeight, x_fitted, isFitSuccessful, x_slope, err

def radialAverage(data, center, boundary):
#    nbins = int(np.round(r.max() / binsize)+1)
#    maxbin = nbins * binsize
#    bins = np.linspace(0,maxbin,nbins+1)
#    # but we're probably more interested in the bin centers than their left or right sides...
#    bin_centers = (bins[1:]+bins[:-1])/2.0
##########################
#    print "***********************************************************************"

    r_max = int(min(abs(center[0]-boundary[0]), abs(center[0]-boundary[2]), abs(center[1]-boundary[1]), abs(center[1]-boundary[3])))
    center = [int(center[0] - boundary[0]), int(center[1] - boundary[1])]
    y,x = np.indices((data.shape)) # first determine radii of all pixels
        
    r = np.sqrt((x-center[0])**2+(y-center[1])**2)
    ind = np.argsort(r.flat) # get sorted indices
    sr = r.flat[ind] # sorted radii
    
    sim = data.flat[ind] # image values sorted by radii
#    ri = sr.astype(np.int32) # integer part of radii (bin size = 1)
    ri = np.round(sr)
#    print ri
    # determining distance between changes
    deltar = ri[1:] - ri[:-1] # assume all radii represented
    rind = np.where(deltar)[0] # location of changed radius
    
    nr = rind[2:] - rind[:-2] # number in radius bin
    csim = np.cumsum(sim, dtype=np.float64) # cumulative sum to figure out sums for each radii bin
    tbin = csim[rind[2:]] - csim[rind[:-2]] # sum for image values in radius bins
    radialprofile = tbin/nr # the ansSwer
#    print "***********************************************************************"
#    return ri[rind][:r_max], radialprofile[:r_max]
    return radialprofile[:r_max]
    


def azimuthalAverage(image, center=None, stddev=False, returnradii=False, return_nr=False, 
        binsize = 0.2, weights=None, steps=False, interpnan=False, left=None, right=None,
        mask=None ):
    """
    Calculate the azimuthally averaged radial profile.
    image - The 2D image
    center - The [x,y] pixel coordinates used as the center. The default is 
             None, which then uses the center of the image (including 
             fractional pixels).
    stddev - if specified, return the azimuthal standard deviation instead of the average
    returnradii - if specified, return (radii_array,radial_profile)
    return_nr   - if specified, return number of pixels per radius *and* radius
    binsize - size of the averaging bin.  Can lead to strange results if
        non-binsize factors are used to specify the center and the binsize is
        too large
    weights - can do a weighted average instead of a simple average if this keyword parameter
        is set.  weights.shape must = image.shape.  weighted stddev is undefined, so don't
        set weights and stddev.
    steps - if specified, will return a double-length bin array and radial
        profile so you can plot a step-form radial profile (which more accurately
        represents what's going on)
    interpnan - Interpolate over NAN values, i.e. bins where there is no data?
        left,right - passed to interpnan; they set the extrapolated values
    mask - can supply a mask (boolean array same size as image with True for OK and False for not)
        to average over only select data.
    If a bin contains NO DATA, it will have a NAN value because of the
    divide-by-sum-of-weights component.  I think this is a useful way to denote
    lack of data, but users let me know if an alternative is prefered...
    
    """
    # Calculate the indices from the image
    y, x = np.indices(image.shape)

    if center is None:
        center = np.array([(x.max()-x.min())/2.0, (y.max()-y.min())/2.0])

    r = np.hypot(x - center[0], y - center[1])

    if weights is None:
        weights = np.ones(image.shape)
    elif stddev:
        raise ValueError("Weighted standard deviation is not defined.")

    if mask is None:
        mask = np.ones(image.shape,dtype='bool')
    # obsolete elif len(mask.shape) > 1:
    # obsolete     mask = mask.ravel()

    # the 'bins' as initially defined are lower/upper bounds for each bin
    # so that values will be in [lower,upper)  
    nbins = int(np.round(r.max() / binsize)+1)
    maxbin = nbins * binsize
    bins = np.linspace(0,maxbin,nbins+1)
    # but we're probably more interested in the bin centers than their left or right sides...
    bin_centers = (bins[1:]+bins[:-1])/2.0

    # how many per bin (i.e., histogram)?
    # there are never any in bin 0, because the lowest index returned by digitize is 1
    #nr = np.bincount(whichbin)[1:]
    nr = np.histogram(r, bins, weights=mask.astype('int'))[0]

    # recall that bins are from 1 to nbins (which is expressed in array terms by arange(nbins)+1 or xrange(1,nbins+1) )
    # radial_prof.shape = bin_centers.shape
    if stddev:
        # Find out which radial bin each point in the map belongs to
        whichbin = np.digitize(r.flat,bins)
        # This method is still very slow; is there a trick to do this with histograms? 
        radial_prof = np.array([image.flat[mask.flat*(whichbin==b)].std() for b in xrange(1,nbins+1)])
    else: 
        radial_prof = np.histogram(r, bins, weights=(image*weights*mask))[0] / np.histogram(r, bins, weights=(mask*weights))[0]
#        radial_prof = np.histogram(r, bins, weights=(image*weights*mask))[0]

    if interpnan:
        radial_prof = np.interp(bin_centers,bin_centers[radial_prof==radial_prof],radial_prof[radial_prof==radial_prof],left=left,right=right)

    if steps:
        xarr = np.array(zip(bins[:-1],bins[1:])).ravel() 
        yarr = np.array(zip(radial_prof,radial_prof)).ravel() 
        
#        idx = np.ceil(len(xarr)/2.) - 1
#        xnew = xarr[idx:-1]
#        ynew = yarr[idx:-1]
#        return xnew, ynew
        return xarr, yarr
    elif returnradii: 
        return bin_centers,radial_prof
    elif return_nr:
        return nr,bin_centers,radial_prof
    else:
        return bins[1:], radial_prof

def initialGauss(data):
	size = np.shape(data)

	xSlice = np.sum(data,0)    
	ySlice = np.sum(data,1)
	x0 = np.argmax(xSlice)
	y0 = np.argmax(ySlice)
	offset = np.nanmin(data)
	peak = np.nanmax(data)
	amplitude = peak - offset

	a = 0
	xOff = np.nanmin(xSlice)
	maxX = np.nanmax(xSlice)-xOff
	for i in range(len(xSlice)):
		if xSlice[i] - xOff > 0.5 * maxX:
			a += 1
	b = 0
	yOff = np.nanmin(ySlice)
	maxY = np.nanmax(ySlice)-yOff
	for i in range(len(ySlice)):
		if ySlice[i] - yOff > 0.5 * maxY:
			b += 1  

	return [x0, y0, max(a, 0.1), max(b,0.1), amplitude, offset]

def qguess(tof, a, b):
	vx = a/tof
	vy = b/tof
	
	m = mLi
	T = m/kB * (vx**2+vy**2)/2
	beta = 1/(kB*T)
	
	n = 10**(13) * 10**6
	mu = hbar**2/(2*m) * (3 * np.pi**2)**(2./3.) * n** (2./3.)
	
	q = beta * mu
	
	return q


def gaussionDistribution(coordinates, x0, y0, a, b, amplitude, offset):
	"""gaussionParams = ((x0, y0, a, b, amplitude, offset)) """
	dist = offset + amplitude * np.exp(- (coordinates[0] - x0) **2/a**2 - (coordinates[1] - y0)**2/b**2)
	return dist.ravel()


def fermionDistribution(xy, x0, y0, sigmax, sigmay, A, zeta, offset):
    """FermionParams = ?"""
    x,y=xy
    denom = fermi_poly2( np.log(zeta) - (x - x0) **2/(2*sigmax**2) - (y - y0)**2/(2*sigmay**2) )
    numer = fermi_poly2( np.log(zeta) )
    thermalPart = A * denom / numer  #Mingwu Lu thesis about first Dy dFg
    dist = thermalPart + offset
    return dist.ravel()

def bosonDistribution(xy, x0, y0, a, amplitudeC, offset, amplitudeT, Ca, Cb):
    """BosonParams = ?"""
    x,y=xy
    expo = np.exp(- (x - x0) **2/(2*a**2) - (y - y0)**2/(2*a**2))
    thermalPart = amplitudeT * g_two(expo)/g_two(1) 
    #thermalPart = amplitudeT * expo
    condensatePart = amplitudeC * np.maximum((1-(x-x0)**2/Ca**2-(y-y0)**2/Cb**2),0)
    dist = thermalPart + condensatePart + offset
    return dist.ravel()

def bosonDistributionSumThermal(xy, x0, y0, a, amplitudeT):
    x, y = xy
    expo = np.exp(- (x - x0) **2/(2*a**2) - (y - y0)**2/(2*a**2))
    thermalPart = amplitudeT * g_two(expo)/g_two(1) 
    #thermalPart = amplitudeT * expo
    return np.sum(thermalPart)
    
def BosonFit2D(data, Initialparams):
    Guessx_width = Initialparams[0]
    Guessy_width = Initialparams[1]
    Guessx_center = Initialparams[2]
    Guessy_center = Initialparams[3]
    x_start = Initialparams[4]
    y_start = Initialparams[5]
    IsXSuc = Initialparams[6]
    IsYSuc = Initialparams[7]
    isFitSuccessful = False
    if not IsXSuc:
        Guessx_center = x_start + data.shape[1]//2
        Guessx_width = data.shape[1]//2.5
    if not IsYSuc:
        Guessy_center = y_start + data.shape[0]//2
        Guessy_width = data.shape[0]//2.5
    # Assuming data is your 2D data
    # x_fit and y_fit are the coordinates of the point you want to fit
    x = np.arange(data.shape[1])+x_start
    y = np.arange(data.shape[0])+y_start
    # Find the coordinates of the maximum value in the data

    X, Y = np.meshgrid(x, y)
    Z = data  # Your 2D data
    # Initial guess for the parameters
    initial_guess = (Guessx_center, Guessy_center, np.sqrt(Guessx_width*Guessy_width),0.5, 0.0, 0.5, Guessx_width, Guessy_width)
    lower_bounds = [-np.inf, -np.inf, 0, 0, -0.2, 0, 0 ,0]  # Lower bounds for each parameter
    #lower_bounds = [-np.inf, -np.inf, -np.inf, -np.inf, -np.inf, -np.inf, -np.inf ,-np.inf]  # Lower bounds for each parameter
    upper_bounds = [np.inf, np.inf, np.inf, np.inf, 0.2, np.inf, np.inf, np.inf]  # Upper bounds for each parameter
    # Define specific bounds for each parameter as needed
    param_bounds = (lower_bounds, upper_bounds)
    # Perform the fit
    if data.shape[0]*data.shape[1]>400*400:
        xc, yc, sigma_x, sigma_y, Ac, offset, At, TF_x, TF_y= 0,0,0,0,0,0,0,0,0
        isFitSuccessful = False
        modifiedrawAtomNumber = -9527
        print("------ 2D Fit Failed ------")

    else:
        params, covariance = curve_fit(bosonDistribution, (X, Y), Z.ravel(), p0=initial_guess, bounds=param_bounds)

        try:
            print("jl, initial guess and fit result")
            print(initial_guess)
            print(params)
            # Unpack the parameters
            xc, yc, sigma_x, Ac, offset, At, TF_x, TF_y = params #TF refers to Thomas Fermi
            isFitSuccessful = True
            Zfit = bosonDistribution((X, Y), xc, yc, sigma_x, Ac, offset, At, TF_x, TF_y).reshape(X.shape)
            modifiedrawAtomNumber = np.sum(data)-offset*np.size(data)
            thermal_sum = bosonDistributionSumThermal((X, Y), x0=xc, y0=yc, a=sigma_x, amplitudeT=At)
            BECfrac = 1-thermal_sum/modifiedrawAtomNumber
            Bosonfit_xsum = np.sum(Zfit, axis = 0)
            Bosonfit_ysum = np.sum(Zfit, axis = 1)
            
        except Exception:
            xc, yc, sigma_x, Ac, offset, At, TF_x, TF_y= 0,0,0,0,0,0,0,0
            modifiedrawAtomNumber = 0
            isFitSuccessful = False
            BECfrac = 0
            Zfit = np.ones_like(Z)
            Bosonfit_xsum = np.zeros_like(x)
            Bosonfit_ysum = np.zeros_like(y)
            print("------ BosonFit2D Failed ------")

    
            
    return xc, yc, sigma_x, TF_x, TF_y, modifiedrawAtomNumber, BECfrac, isFitSuccessful, Bosonfit_xsum, Bosonfit_ysum, Zfit

def FermionFit2D(data, Initialparams):
    Guessx_width = Initialparams[0]
    Guessy_width = Initialparams[1]
    Guessx_center = Initialparams[2]
    Guessy_center = Initialparams[3]
    x_start = Initialparams[4]
    y_start = Initialparams[5]
    IsXSuc = Initialparams[6]
    IsYSuc = Initialparams[7]
    isFitSuccessful = False
    if not IsXSuc:
        Guessx_center = x_start + data.shape[1]//2
        Guessx_width = data.shape[1]//2.5
    if not IsYSuc:
        Guessy_center = y_start + data.shape[0]//2
        Guessy_width = data.shape[0]//2.5
    # Assuming data is your 2D data
    # x_fit and y_fit are the coordinates of the point you want to fit
    x = np.arange(data.shape[1])+x_start
    y = np.arange(data.shape[0])+y_start
    # Find the coordinates of the maximum value in the data

    X, Y = np.meshgrid(x, y)
    Z = data  # Your 2D data
    # Initial guess for the parameters
    initial_guess = (Guessx_center, Guessy_center, Guessx_width, Guessy_width,1, 5, 0)
    lower_bounds = [-np.inf, -np.inf, 0, 0, 0.2, 0, -0.2]  # Lower bounds for each parameter
    upper_bounds = [np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, 0.2]  # Upper bounds for each parameter
    # Define specific bounds for each parameter as needed
    param_bounds = (lower_bounds, upper_bounds)
    # Perform the fit
    if data.shape[0]*data.shape[1]>400*400:
        xc, yc, sigmax, sigmay, zeta, modifiedrawAtomNumber, isFitSuccessful= 0,0,0,0,0,0,0
        Fermionfit_xsum = np.zeros_like(x)
        Fermionfit_ysum = np.zeros_like(y)
        Zfit = np.ones_like(Z)
        isFitSuccessful = False
        modifiedrawAtomNumber = -9527
        print("------ 2D Fit Failed ------")

    else:
        params, covariance = curve_fit(fermionDistribution, (X, Y), Z.ravel(), p0=initial_guess, bounds=param_bounds)

        try:
            #print("jl, initial guess and fit result")
            #print(initial_guess)
            #print(params)
            # Unpack the parameters
            xc, yc, sigmax, sigmay, A, zeta, offset = params #TF refers to Thomas Fermi
            isFitSuccessful = True
            Zfit = fermionDistribution((X, Y), xc, yc, sigmax, sigmay, A, zeta, offset).reshape(X.shape)
            modifiedrawAtomNumber = np.sum(data)-offset*np.size(data)
            Fermionfit_xsum = np.sum(Zfit, axis = 0)
            Fermionfit_ysum = np.sum(Zfit, axis = 1)
            
        except Exception:
            xc, yc, sigmax, sigmay, A, zeta, offset = 0, 0, 0, 0, 0, 0, 0
            modifiedrawAtomNumber = 0
            isFitSuccessful = False
            Zfit = np.ones_like(Z)
            Fermionfit_xsum = np.zeros_like(x)
            Fermionfit_ysum = np.zeros_like(y)
            print("------ FermionFit2D Failed ------")

    return xc, yc, sigmax, sigmay, zeta, modifiedrawAtomNumber, isFitSuccessful, Fermionfit_xsum, Fermionfit_ysum, Zfit
            

def fitData(data, distribution, option):

    tmp0 =time.time()
    size = np.shape(data)
    
    tmp1 =time.time()
    if distribution == gaussionDistribution:
    	guess = initialGauss(data)
    	distribution2 = gaussionDistribution
    	
    coordinates = np.meshgrid(range(size[1]), range(size[0]))

    if distribution == fermionDistribution:
    	print(option)
    	x0, y0, a, b, amplitude0, offset0, q0 = option
    	guess = [a*1.2, b*1.2, amplitude0, offset0, q0]
    	distribution2 = lambda coordinate, fa, fb, amplitude, offset,  q: fermionDistribution(coordinate, x0, y0, fa, fb, amplitude, offset, q)
    print(guess)
    # elif distribution == bosonDistribution:
    #    	guess.append(1)
    #    	guess.append(0.1)
    #    	guess.append(0.1)


    tmp2 =time.time()
    params, Cover = curve_fit(distribution2, coordinates, data.ravel(), p0=guess, maxfev=1000)
    tmp3 =time.time()

    return params



def radioDistribution(data, center, sigma):

	size = np.shape(data)
	
	x1 = min(center[0], size[0]-center[0])/float(sigma[0])
	y1 = min(center[1], size[1]-center[1])/float(sigma[1])
	r0 = min(x1, y1)

	lr = int(0.95*r0)
	od_list = []

	for r in np.arange(0, lr, 0.01):
		od = 0
		for theta in range(0, 360, 5):
			x = center[0] + int(r*np.cos(theta) * sigma[0])
			y = center[1] + int(r*np.sin(theta) * sigma[1])
			od += data[y, x]
		od=od/360
		# print od
		od_list.append(od)

	return od_list
