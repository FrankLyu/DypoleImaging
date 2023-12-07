# -*- coding: utf-8 -*-

import time
import os
# import variables
#from config import path, waitTimeStep, height, width, cameraID
path = os.getcwd()
waitTimeStep = 0.2
height = 2160
width = 2560
cameraID = 4

# import functions
from dbFunctions import setVariablesNewRun, waitForNewImage, dataToArray, updateNewImage

# import C# functions
from dbFunctionsC import writeImageToCacheC

# Remark: all the imageID, runID and sequenceID are in auto-increment, so we should not need to
# care about updating it correctly, just fetch the last runID and sequenceID, and add that to
# the foreign keys when we save the picture


while True:
    time.sleep(waitTimeStep)        # wait before checking of a new image showed up in the folder
    runID, seqID, previousSet = setVariablesNewRun(path)    # current runID, if a new image comes, it 
                                                            # must then be from the latest runID
    pathFile = waitForNewImage(path, previousSet)   # pathFile is the path to the image that poped in, otherwise
                                                    # it stays here forever
    arrayAtoms, arrayNoAtoms, arrayDark = dataToArray(pathFile)
    writeImageToCacheC(arrayAtoms,
                       arrayNoAtoms,
                       arrayDark,
                       width,
                       height,
                       cameraID,
                       runID,
                       seqID)
    updateNewImage()     # This is the cleared signal for Zeus
    