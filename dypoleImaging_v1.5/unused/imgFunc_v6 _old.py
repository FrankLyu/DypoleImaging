from constant_v6 import *
import wx
import numpy as np
from scipy import stats
import os, sys, struct
from math import sqrt, log, atan
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from mpmath import mp
from PIL import Image
from polylog import *
import copy
import time
import matplotlib.image as mpimg
from astropy.io import fits
from skimage import io
from scipy.ndimage.filters import gaussian_filter

from DatabaseCommunication.dbFunctions import getCameraDimensions, getImageDatabase

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])
# list square, for fitting
def square(list):
    return map(lambda x: x ** 2, list)

# read data, changed to absorption image
def readAIA(path):
    b = bytearray(2*3*1024*1024+100)
    f = open(path, "rb")
    try:
    	numBytesRead = f.readinto(b) 
#    print "Read ", numBytesRead, " bytes."
    finally:
    	f.close()

    tmp0 = time.time()

#print "Filetype:" + chr(b[0])+chr(b[1])+chr(b[2])
    numBytesPerValue = struct.unpack('h',chr(b[3])+chr(b[4]))[0]
    rowTotal = struct.unpack('h',chr(b[5])+chr(b[6]))[0]
    colTotal = struct.unpack('h',chr(b[7])+chr(b[8]))[0]
    layerTotal = struct.unpack('h',chr(b[9])+chr(b[10]))[0]

    imageData = np.zeros((layerTotal,rowTotal,colTotal))
    byteIndex = 11
    for layer in range(layerTotal):
        for row in range(rowTotal):
            for col in range(colTotal):
                imageData[layer][row][col]= struct.unpack('h',chr(b[byteIndex])+chr(b[byteIndex+1]))[0]  
                byteIndex+=2    
    tmp1 = time.time()
    return imageData
    
#def readTIF2(path):
#    start = time.time()
#    print "..................TIF reading.............."
#    print "Opening tif image: " + path
#    im = io.imread(path)
#    print im.shape
#    imageData = []
#    for i in range(3):
##        im.seek(i)
#        print '====in for loop ===='
###        print im.shape
##        temp = np.sum(np.array(im).astype(float), axis=2)
##        print temp.shape
#        imageData.append(im[:,:,i])
##    #print imageData
#    end = time.time()
#    print str(end - start) + " seconds taken for TIF reading...."
#    print len(imageData)
#    #    imageData = np.asarray(imageData)
##    print imageData.shape
#    print ".................. E  N  D.............."
#    return imageData

def readTIF(path):
    start = time.time()
#    print "..................TIF reading.............."
    imageData = []
    print("Opening tif image: " + path)
    im = Image.open(path)
#    print im
#    print np.array(im).shape
    for i in range(3):
        im.seek(i)
#        print '====in for loop ===='
#        print im.shape
        temp = np.sum(np.array(im).astype(float), axis=2)
#        temp = np.asarray(temp)
#        print temp.shape
        imageData.append(temp)
#        print "---- i -----" + str(i) 
    #print imageData
    end = time.time()
    print(str(end - start) + " seconds taken for TIF reading....")
#    print ".................. E  N  D.............."
    return imageData
    
def readFITS(path):
    start = time.time()
    imageData=[]
#    print "Opening fits image: " + path
    try:
        fitsHDUlist = fits.open(path)
    except Exception as e:
        print(str(e))
        
#    print "Opened fits file"
    fits_data = fitsHDUlist[0].data
#    print "read fits image"
    for i in [0,1,2]:
    			#temp = np.sum(np.array(fits_data[i]).astype('float'), axis=2)
        imageData.append((fits_data[i]).astype(float))
#    imageData = np.asarray(imageData)
#    print "size --------------------------"
#    print imageData.shape
#    print "size --------------------------"
    end = time.time()
    print(str(end - start) + " seconds taken for FITS reading....")
    return imageData

def readDatabaseFile(path): # path is the imageID in the db, not the filepath
    start = time.time()
    cameraHeight, cameraWidth = getCameraDimensions(path) # look at the config file to make sure there is no conflict zith height and width
    if (cameraHeight == 1 and cameraWidth == 1):
        imageData = [np.zeros(1, dtype = np.uint16).reshape(1,1)]*3
    try:
        byteArrayTuple = getImageDatabase(path)
        imageData = [np.frombuffer(byteArrayTuple[0], dtype=np.uint16).reshape(cameraHeight, cameraWidth),
                     np.frombuffer(byteArrayTuple[1], dtype=np.uint16).reshape(cameraHeight, cameraWidth),
                     np.frombuffer(byteArrayTuple[2], dtype=np.uint16).reshape(cameraHeight, cameraWidth)]
    except Exception as e:
        print(str(e))
    end = time.time()
    print(str(end - start) + " seconds taken for Database reading....")
    return imageData

def createAbsorbImg(imageData, correctedNoAtom = None):
    if len(imageData) is not 3:
        raise Exception("~~~~~~ Given image does not have three layers ~~~~~~~")
    
    if correctedNoAtom is None:
        correctedNoAtom = imageData[1] - imageData[2]

    absorbImg = np.maximum(imageData[0]-imageData[2], .1)/(np.maximum(correctedNoAtom, .1))  
    #print absorbImg
    ###  Replace extremely low transmission pixels with a minimum meaningful transmission. 
    minT = np.exp(-5)
    temp = np.empty(imageData[0].shape)	
    temp.fill(minT)
        
    absorbImg = np.maximum(absorbImg, temp)

#    temp2 = np.where(np.array(imageData[0]) <= np.array(imageData[2]))
#    absorbImg = np.array(absorbImg)
#    absorbImg[temp2] = 1
    return absorbImg
    
def createNormalizedAbsorbImg(imageData, aoi):
    #        print "break pt 0-------------------------------------------------"
    y, x = imageData[0].shape
    xLeft = aoi[0][0]
    yTop = aoi[0][1]
    xRight = aoi[1][0]
    yBottom = aoi[1][1]

    tempAtom = np.copy(imageData[0])
    meanAtom = (np.mean(tempAtom[0:y, 0:xLeft + 1]) + np.mean(tempAtom[0:y, xRight:x]) + np.mean(tempAtom[0:yTop+1, xLeft:xRight+1]) + np.mean(tempAtom[yBottom:y, xLeft:xRight+1]))/4
    stdAtom = np.sqrt((np.std(tempAtom[0:y, 0:xLeft + 1])**2 + np.std(tempAtom[0:y, xRight:x])**2 + np.std(tempAtom[0:yTop+1, xLeft:xRight+1])**2 + np.std(tempAtom[yBottom:y, xLeft:xRight+1])**2)/4)
    
    tempNoAtom = np.copy(imageData[1])
    meanNoAtom = (np.mean(tempNoAtom[0:y, 0:xLeft + 1]) + np.mean(tempNoAtom[0:y, xRight:x]) + np.mean(tempNoAtom[0:yTop+1, xLeft:xRight+1]) + np.mean(tempNoAtom[yBottom:y, xLeft:xRight+1]))/4
    stdNoAtom = np.sqrt((np.std(tempNoAtom[0:y, 0:xLeft + 1])**2 + np.std(tempNoAtom[0:y, xRight:x])**2 + np.std(tempNoAtom[0:yTop+1, xLeft:xRight+1])**2 + np.std(tempNoAtom[yBottom:y, xLeft:xRight+1])**2)/4)
    
#    print meanNoAtom
#    print stdNoAtom
#    print meanAtom
#    print stdAtom
#    print "------------------------------------------------"        
    
    #        tempAtom[self.yTop:self.yBottom+1, self.xLeft:self.xRight+1] = 0.
    #        tempNoAtom[self.yTop:self.yBottom+1, self.xLeft:self.xRight+1] = 0.
    #        meanAtom = np.mean(tempAtom)        
    #        meanNoAtom = np.mean(tempNoAtom)
    #        stdAtom = np.std(tempAtom)
    #        stdNoAtom = np.std(tempNoAtom)
    #        
    #        print meanNoAtom
    #        print stdNoAtom
    #        print meanAtom
    #        print stdAtom
    
    #        print "==========================================="
#    print "---- before scaling.... ----"
#    print "Yes-Atom mean: " + str(np.mean(imageData[0]))
#    print "Yes-Atom std: " + str(np.std(imageData[0]))
#    print "No-Atom mean: " + str(np.mean(imageData[1]))
#    print "No-Atom std: " + str(np.std(imageData[1]))
    imageData[1] = meanAtom + (stdAtom/stdNoAtom)*(imageData[1] - meanNoAtom)
#    print "---- after scaling.... ----"
#    print "No-Atom mean: " + str(np.mean(imageData[1]))
#    print "No-Atom std: " + str(np.std(imageData[1]))
    
    correctedNoAtom = imageData[1] - imageData[2]
    return createAbsorbImg(imageData, correctedNoAtom)
    
def readData(path, filetype, betterRefOpt = [False, None]):
    num_trial = 0
    max_num_trial = 3
    while (num_trial < max_num_trial):
        try:
            if filetype == "aia":
                imageData = readAIA(path)
            elif filetype == "tif":
    #            time.sleep(0.1)
                imageData = readTIF(path)
            elif filetype == "fits":
                imageData = readFITS(path)
            elif filetype == "dbFile":
                imageData = readDatabaseFile(path) # path is here the imageID
            else:
                raise Exception('---------Unknown file type-------')
        ###  Construct the transmittance map, with an np.maximum statement to avoid dividing by zero.
            if betterRefOpt[0] is True:
                correctedNoAtom = betterRefOpt[1]
                if (correctedNoAtom is None) or (correctedNoAtom.shape != imageData[1].shape):
                    correctedNoAtom = imageData[1] - imageData[2]
            else:
    #            meanAtom = np.mean(imageData[0])
    #            meanNoAtom = np.mean(imageData[1])
    #            stdAtom = np.std(imageData[0])
    #            stdNoAtom = np.std(imageData[1])
    #
    #            correctedNoAtom = (meanAtom + stdAtom/stdNoAtom *(imageData[1] - meanNoAtom)) - imageData[2]
                correctedNoAtom = imageData[1] - imageData[2]
            
            absorbImg = createAbsorbImg(imageData, correctedNoAtom)
            #    filtered = gaussian_filter(absorbImg, 1, order = 0, truncate = 2)
            #    temp2 = np.where(np.array(filtered[0]) <= np.array(filtered[2]))
            #    absorbImg = np.array(filtered)
            #    absorbImg[temp2] = 1
            
            #    temp2 = np.where((np.array(imageData[0]) >= np.array(imageData[2])) * (np.array(imageData[1]) <= np.array(imageData[2])))
            
            tmp2 = time.time()
            num_trial = max_num_trial
            return absorbImg, imageData
    #    print absorbImg.shape
        except Exception:
            num_trial += 1
            print("")
            print(" ===== READING IMAGE TRIAL ----> " + str(num_trial) + " ====== ")
            print("")
            time.sleep(0.2)
            if (num_trial == max_num_trial):
                raise Exception("Imaging reading failed at imgFunc_v6.py after " + str(num_trial) + " trials...")
            

    #        msg = wx.MessageDialog(selfinstance, selfinstance, str(msg.message), wx.OK)
#        if msg.ShowModal() == wx.ID_OK:
#            msg.Destroy()    



#######################################################
###### FITS specific functions for defringing #########

#def readThreeLayers(filename):
#    imageData=[]
#    print "Opening fits image: " + filename
#    try:
#        fitsHDUlist = fits.open(filename)
#    except Exception, e:
#        print "--------failed ------------"
#        print str(e)
#    
#    print "Opened fits file"
#    fits_data = fitsHDUlist[0].data
#    print "read fits image"
#    for i in [0,1,2]:
#    			#temp = np.sum(np.array(fits_data[i]).astype('float'), axis=2)
#        imageData.append((fits_data[i]).astype(float))
#    return imageData

def readNoAtomImage(filename):
#    print filename + "000000000000"
    imageData = readFITS(filename)
    temp= np.asarray(imageData[1] - imageData[2])
    return np.maximum(temp, .1)

def readNoAtomImageFlattened(fileNameList):
    temp = []
    for fileName in fileNameList:
        temp.append(readNoAtomImage(fileName).flatten())
        
    return np.array(temp)
    
def readAtomImage(filename):
    imageData = readFITS(filename)
    temp = np.asarray(imageData[0] - imageData[2])
    return np.maximum(temp, .1)
########################################

### atom number #######
def atomNumber(Img, offset):
    #ImgCopy = copy.deepcopy(Img)
    ##return np.sum(np.sum(ImgCopy))
    #ImgCopy[:] = [x - offset for x in ImgCopy]
    #return np.sum(np.sum(ImgCopy))  * (pixelToDistance**2)/crossSection

    imgsize = np.shape(Img)
    simplicio = np.sum(np.sum(Img)) 

#    print "Ncount = " + str(simplicio)
    sim2 = simplicio - offset * imgsize[0]*imgsize[1] 
    
#    sim2 = simplicio - offset
#    print "NormNcount = " + str(sim2)
#    return sim2* (pixelToDistance**2)/crossSection
    return sim2
    
def aoiEdge(Img, leftright, updown):
    imgsize = np.shape(Img)
    #x1 = np.sum(np.sum(Img[0:3,:]))
    #x2 = np.sum(np.sum(Img[-2:,:]))
    #y1 = np.sum(np.sum(Img[::,0:3]))
    #y2 = np.sum(np.sum(Img[:,-2:]))
    if leftright and updown:
        y1 = np.sum(np.sum(Img[0:3,0:-3]))
        y2 = np.sum(np.sum(Img[-3:,3:]))
        x1 = np.sum(np.sum(Img[3:,0:3]))
        x2 = np.sum(np.sum(Img[0:-3,-3:]))
        out = x1+x2+y1+y2
#        print out
        return out/(6*(imgsize[0]+imgsize[1]) - 36)
    elif leftright and not updown:
        x1 = np.sum(np.sum(Img[3:,0:3]))
        x2 = np.sum(np.sum(Img[0:-3,-3:]))
        out = x1+x2
#        print out
        return out/(6*imgsize[0])
    elif updown and not leftright:
        y1 = np.sum(np.sum(Img[0:3,0:-3]))
        y2 = np.sum(np.sum(Img[-3:,3:]))
        out = y1+y2
#        print out
        return out/(6*imgsize[1])
    elif not leftright and not updown:
        return 0
    
#def atomNumberGaussianFit(sigmaX, sigmaY, amplitude):
#    return np.pi * sigmaX * sigmaY * amplitude * (pixelToDistance**2)/crossSection


### fit image - 1d method - not using ###
def twoDGaussianFit(data):
    """Fits a two-dimensional Gaussian, A*exp(-0.5*(((x-x0)/sigmaX)^2+((y-y0)/sigmaY)**2))+offset, to given data 
    (a numpy array) and returns the fit parameters [[x0,y0],[sigmaX,sigmaY],offset,A]. """

### Get guess values by doing 1d fits to the data integrated in the X or Y direction.
    def oneDGaussian(x, centerX,sDevX,Amp,yOffset):
        return Amp*np.exp(-0.5*((x-centerX)/sDevX)**2)+yOffset
    ### Mask out only the area of interest then integrate the data long each axis
    
    xSlice = np.sum(data,0)    
    ySlice = np.sum(data,1)
        
    ### Initial guesses for 1d fits
    xOff = np.nanmin(xSlice)
    AmpX = np.nanmax(xSlice)-xOff
    x0 = np.argmax(xSlice)
    
    yOff = np.nanmin(ySlice)
    AmpY = np.nanmax(ySlice)-yOff
    y0 = np.argmax(ySlice)
    sigmaX =40
    sigmaY =40

    ### 1d fits
    xVals, yCovar = curve_fit(oneDGaussian,range(len(xSlice)),xSlice,p0=(x0,sigmaX,AmpX,xOff))
    x0 = xVals[0]
    sigmaX = xVals[1]

    
    yVals, yCovar = curve_fit(oneDGaussian,range(len(ySlice)),ySlice,p0=(y0,sigmaY,AmpY,yOff))
    y0 = yVals[0]
    sigmaY = yVals[1]
    
    ### 2d fit
#    def twoDGaussian(xVec, centerX,sDevX,Amp,yOffset):
#        return Amp*np.exp(-0.5*((x-centerX)/sDevX)^2)+yOffset
    offset = 0.5*(xVals[3]/(np.shape(data)[1]) + yVals[3]/(np.shape(data)[0]))
    A = 0.5 * ( xVals[2]/(sqrt(2.0*np.pi)*sigmaY) + yVals[2]/(sqrt(2.0*np.pi)*sigmaX) ) 
    
    return [[x0,y0],[sigmaX,sigmaY],A,offset]
    
# condensate fit
def twoDParbolicFit(data):
    """parabolic fit the function z = Amp * max(0, 1 - a*(x-x0)^2 - b*(y-y0)^2) +offset). 
    Since we only need center and width, this function returns center, width, amplitude and offset.
    """
    def oneDParabolic(x, centerX, Amp, a, offset):
        #print  - Amp *  ((x-centerX)**2) + C
        #print offset
        #return - Amp *  ((x-centerX)**2) + C * offset
        out = Amp *  np.maximum( (1 - a * (x - centerX)**2), 0)  ** 2+ offset

        return out
    #def oneDGaussian(x, centerX,sDevX,Amp,yOffset):
    #    return Amp*np.exp(-0.5*((x-centerX)/sDevX)**2)+yOffset
    ### Mask out only the area of interest then integrate the data long each axis
    



    xSlice = np.sum(data,0)    
    ySlice = np.sum(data,1)
        
    ### Initial guesses for 1d fits
    xOff = np.nanmin(xSlice)
    maxX = np.nanmax(xSlice)-xOff
    x0 = np.argmax(xSlice)
    
    yOff = np.nanmin(ySlice)
    maxY = np.nanmax(ySlice)-yOff
    y0 = np.argmax(ySlice)

    lengthX = 0
    for i in range(len(xSlice)):
        if xSlice[i] - xOff > 0.2 * maxX:
            lengthX += 1
 
    lengthY = 0
    for i in range(len(ySlice)):
        if ySlice[i] - yOff > 0.2 * maxY:
            lengthY += 1  
    
    aX = 4./lengthX**2
    aY = 4./lengthY**2
    AmpX = 4./3. * maxX/sqrt(aY)
    AmpY = 4./3. * maxY/sqrt(aX)

            
    ### 1d fits
    xVals, yCovar = curve_fit(oneDParabolic,range(len(xSlice)),xSlice,p0=(x0, AmpX, aX, xOff))
    x0 = xVals[0]
    widthX = sqrt(1/xVals[2])
    
    yVals, yCovar = curve_fit(oneDParabolic,range(len(ySlice)),ySlice,p0=(y0, AmpY, aY, yOff))
    y0 = yVals[0]
    widthY = sqrt(1/yVals[2])

    Amp = sqrt(xVals[1] * yVals[1] * 9./16. * sqrt(xVals[2] * yVals[2]) )
    
    offset = 0.5 * (xVals[3]/(np.shape(data)[1]) + yVals[3]/(np.shape(data)[0]))
    
    return [[x0, y0], [widthX, widthY], Amp, offset]


# partly condensate fit
def partlyCondensateFit(data):

    def oneDPartlyCondensate(x, centerX, AmpP, a, sDevX, AmpG, offset):
        return np.maximum(AmpG, 0)*np.exp(-0.5*((x-centerX)/sDevX)**2) + np.maximum(AmpP, 0) *  np.maximum( (1 - a * (x - centerX)**2), 0)  ** 2.5+ offset
       

    xSlice = np.sum(data,0)    
    ySlice = np.sum(data,1)
        
    ### Initial guesses for 1d fits
    xOff = np.nanmin(xSlice)
    AmpGX = np.nanmax(xSlice)-xOff
    x0 = np.argmax(xSlice)
    
    yOff = np.nanmin(ySlice)
    AmpGY = np.nanmax(ySlice)-yOff
    y0 = np.argmax(ySlice)
    sigmaX =40
    sigmaY =40

    lengthX = 0
    for i in range(len(xSlice)):
        if xSlice[i] - xOff > 0.5 * AmpGX:
            lengthX += 1
 
    lengthY = 0
    for i in range(len(ySlice)):
        if ySlice[i] - yOff > 0.5 * AmpGY:
            lengthY += 1  


    ### Standard deviation is a bit more work to estimate.
    check = AmpGX*np.exp(-0.5)
    for index in range(x0,len(xSlice)):
        if xSlice[index] < check:
            sigmaX = index-x0
            break
    check = AmpGY*np.exp(-0.5)
    for index in range(y0,len(ySlice)):
        if ySlice[index] < check:
            sigmaY = index-y0
            break
    
    aX = 4./lengthX**2
    aY = 4./lengthY**2
    # AmpPX = 4./3. * AmpGX/sqrt(aY)
    # AmpPY = 4./3. * AmpGY/sqrt(aX)
    AmpPX = AmpGX
    AmpPY = AmpGY

            
    ### 1d fits
    xVals, yCovar = curve_fit(oneDPartlyCondensate,range(len(xSlice)),xSlice,p0=(x0, AmpPX/2, aX, sigmaX, AmpGX/2, xOff))
    x0 = xVals[0]
    widthX = sqrt(1/xVals[2])
    sigmaX = xVals[3]
    
    yVals, yCovar = curve_fit(oneDPartlyCondensate,range(len(ySlice)),ySlice,p0=(y0, AmpPY/2, aY, sigmaY, AmpGY/2, yOff))
    y0 = yVals[0]
    widthY = sqrt(1/yVals[2])
    sigmaY = yVals[3]

    # AmpP = np.maximum(3./8. * xVals[2] * xVals[1], 0) + np.maximum(3./8. * yVals[2] * yVals[1], 0)
    AmpP = sqrt(np.maximum(xVals[1], 0) * np.maximum(yVals[1], 0) * 9./16. * sqrt(xVals[2] * yVals[2]) )
    AmpG = 0.5 * ( np.maximum(xVals[4], 0)/(sqrt(2.0*np.pi)*sigmaY) + np.maximum(yVals[4], 0)/(sqrt(2.0*np.pi)*sigmaX) ) 
    offset = 0.5 * (xVals[5]/(np.shape(data)[1]) + yVals[5]/(np.shape(data)[0]))

    return [[x0,y0], [widthX, widthY], [sigmaX,sigmaY], AmpP, AmpG, offset]

# for fermionic fit


# fermionic fit
def fermionFit(data):

    def oneDPolylog(x, centerX, Rx, Amp , q, yOffset):
        print [centerX, Rx, Amp, q, yOffset]
        x = np.array(x)

        numerator = fermi_poly5half(q - (x-centerX)**2/Rx**2 * f(np.exp(q)))
        denuminator = fermi_poly5half(q)

        out = numerator/denuminator * Amp + yOffset

        return out

        
        
    ### Mask out only the area of interest then integrate the data long each axis


    xSlice = np.sum(data,0)    
    ySlice = np.sum(data,1)
        
    ### Initial guesses for 1d fits
    xOff = np.nanmin(xSlice)
    AmpX = np.nanmax(xSlice)-xOff
    x0 = np.argmax(xSlice)
    
    yOff = np.nanmin(ySlice)
    AmpY = np.nanmax(ySlice)-yOff
    y0 = np.argmax(ySlice)
    # sigmaX = sXguess
    # sigmaY = sYguess
    
    sigmaX = 0
    for i in xSlice:
        if i - xOff > 0.5 * AmpX:
            sigmaX += 1

    sigmaX/=2.
    sigmaY = 0
    for i in ySlice:
        if i - yOff > 0.5 * AmpY:
            sigmaY += 1
    sigmaY/=2.
    print [sigmaX, sigmaY]

    q0 = 1

            
    ### 1d fits
    xVals, yCovar = curve_fit(oneDPolylog,range(len(xSlice)),xSlice,p0=(x0,sigmaX,AmpX, q0 ,xOff))
    yVals, yCovar = curve_fit(oneDPolylog,range(len(ySlice)),ySlice,p0=(y0,sigmaY,AmpY, q0 ,yOff))
    
    x0 = float(xVals[0])
    RX = float(xVals[1])

    y0 = float(yVals[0])
    RY = float(yVals[1])
    
    qx=float(xVals[3])
    qy=float(yVals[3])
    offset = float(0.5*(xVals[4]/(np.shape(data)[1]) + yVals[4]/(np.shape(data)[0])))
    A = np.array(data).max()
    
   
    return [[x0,y0],[RX,RY],A,[qx, qy],offset]
    
### extract static data #####

def temperatureSingleGaussianFit(ToF, gSigmaX, gSigmaY, OmegaAxial, OmegaRadial, atom):
    if atom == 'Li':
        m = mLi
    elif atom == 'Na':
        m = mNa
    else:
        return false
    
    Tempx = (m * 2 * gSigmaX**2 * OmegaAxial ** 2)/(2*kB*(1 + OmegaAxial ** 2 * ToF ** 2))
    Tempy = (m * 2 * gSigmaY**2 * OmegaRadial ** 2)/(2*kB*(1 + OmegaRadial ** 2 * ToF ** 2))

    # averageTemp = 0.5*(Tempx + Tempy)
    # deltaTemp = 0.5*abs(Tempx - Tempy)
    return [Tempx, Tempy]

# single shot -> trap frequency radial
def trapFrequencyRadial(ToF, rho, rho0):
    freq = (sqrt((rho/rho0)**2 - 1))/ToF
    return freq

# single shot -> trap frequency Axial
def trapFrequencyAxial(ToF, z, rho0, omegaRadial):
    tau = ToF * omegaRadial
    temp = tau * atan(tau) - log(sqrt(1+ tau**2))
    a = temp
    b = - z/rho0

    e = (sqrt(b**2-4*a) - b)/(2*a)

    return e*omegaRadial
    
# single shot -> chamical potential
def chemicalPotential(ToF, omegaRadial, rho0):
    m = mLi
    mu = 0.5 * m * ((omegaRadial**2/(1+(omegaRadial**2) * (ToF**2))) * rho0**2)
    return mu

#def scatteringLength(omegaRadial, omegaAxial):
#    m = mNa
#    omegaBar = omegaRadial**(2/3) * omegaAxial ** (1/3)
#    return sqrt(hbar/(omegaBar*m))
    
# used to get atom number    
def effectiveInteraction(a):
    m = mLi
    return 4*np.pi*(hbar**2)*a/m
    
# get atom number from chemical potential
def atomNumberFit(mu, omegaRadial, omegaAxial, U0):
    m= mLi
    omegaBar = (omegaRadial**2 * omegaAxial) ** (1./3.)
    #print 'omegaBar'
    #print omegaBar
    #print '(2*mu)/(m*omegaBar**2))**(3/2)'
    #print ((2*mu)/(m*omegaBar**2))**(3/2)
    N = (8 *np.pi/15) * ((2*mu)/(m*omegaBar**2))**(3./2.) * (mu/U0)


    return N
        
def fillImageAOI(data, AOI, offset):
    out = np.zeros((1024,1024)) + offset
    out[AOI[0][0]:AOI[0][1],AOI[1][0]:AOI[1][1]] 

###### multiple shots functions ##########

#fit temperature from thermal gas
def dataFit(atom, arr1, arr2, arr3):
    if atom == "Li":
        m = mLi
    elif atom == "Na":
        m = mNa

    timeOfFlight = arr1
    RX = np.array(arr2) * 1.414
    RY = np.array(arr3) * 1.414
    # print stats.linregress(np.array(square(RX)), np.array(square(timeOfFlight)))
    slopeX, bX, rX, pX, sX = stats.linregress(np.array(square(RX)), np.array(square(timeOfFlight)))

    Tempx = m  / (2 * kB * slopeX) 
    wx = 1/np.sqrt(-bX)

    slopeY, bY, rY, pY, sY = stats.linregress(np.array(square(RY)),np.array(square(timeOfFlight)))
   
    Tempy = m / (2 * kB * slopeY)
    wy = 1/np.sqrt(-bY)


   
    return [Tempx, Tempy, wx, wy]


# temperature divided by fermionic temperature
def TOverTF(q):
    return (6*fermi_poly3(q))**(-1./3.)

