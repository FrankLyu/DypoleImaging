# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 10:51:32 2020

@author: Dypole_Imaging
"""
 
import mysql.connector
from astropy.io import fits
import os
import time
import numpy as np
#import memcache

from config import minimumFileSize, waitTimeStep, MYSQLserverIP, username, password, databaseName
#from config import memcachedServerIP
from localPath import SPACER

#### Used functions ####

def setVariablesNewRun(pathImageFolder):
    runID, sequenceID = getLastID()
    print('runID = ' + str(runID))
    # Check updates in the local directory
    previousSet = set(os.listdir(pathImageFolder))  # set of all the files in the directory
    return runID, sequenceID, previousSet

def waitForNewImage(pathImageFolder, previousSet):     # wait until a new image is added to the folder where the path
                                            # points at and returns the path name of this new image
    while set(os.listdir(pathImageFolder)) == previousSet:
        time.sleep(waitTimeStep)    # wait 100ms
    # if new fits file, check that it's a full 3-image file with correct size
    print('Found new image')
    newFile = set(os.listdir(pathImageFolder)) - previousSet
    pathFile = pathImageFolder + SPACER + newFile.pop()
    while os.stat(pathFile).st_size < minimumFileSize:
        time.sleep(.50)
        print('I waited for the file to fill up')
    return pathFile

def dataToArray(pathFile):
    # Convert camera fits data to binary format
    with open(pathFile, 'rb') as file:
        image = fits.getdata(file)
    return image[0].ravel().tolist(), image[1].ravel().tolist(), image[2].ravel().tolist()   # atoms, noAtoms, dark

def updateNewImage():
    db = setConnection()
    cursor = db.cursor()
    sql_query = """UPDATE updates SET newImage = 1 WHERE idUpdates = 0;"""
    cursor.execute(sql_query)
    db.commit()
    cursor.close()
    db.close()

def getLastID():
    sql_query = """SELECT runID FROM ciceroOut ORDER BY runID DESC LIMIT 1;"""
    lastRunID = executeGetQuery(sql_query)[0][0]
    sql_query = """SELECT sequenceID FROM sequence ORDER BY sequenceID DESC LIMIT 1;"""
    lastSequenceID = executeGetQuery(sql_query)[0][0]
    return lastRunID, lastSequenceID

def getLastImageID():
    sql_query = """SELECT imageID FROM images ORDER BY imageID DESC LIMIT 1;"""
    lastImageID = executeGetQuery(sql_query)[0][0]
    return lastImageID

def getTimestamp(imageID):
    sql_query = "SELECT timestamp FROM images WHERE imageID = " + str(imageID) + ";"
    timestamp = executeGetQuery(sql_query)[0][0]
    return timestamp

def getLastImageIDs(n):
    sql_query = """SELECT imageID FROM images ORDER BY imageID DESC LIMIT """ + str(n) + """;"""
    lastImageIDsTupleList = executeGetQuery(sql_query)
    lastImageIDs = listTupleToList(lastImageIDsTupleList)
    return lastImageIDs

def listTupleToList(List):
    outputList = []
    for oneTuple in List:
        outputList += [oneTuple[0]]
    return outputList

def setConnection(typeOfConnection = 'global'):
    if typeOfConnection == 'local':
        return setLocalConnection()
    elif typeOfConnection == 'global':
        return setDistantConnection()
    else:
        print('Set what type of connection you want')

def setLocalConnection():
    # Open database connection
    mydb = mysql.connector.connect(host = "localhost",
                        user = "student",
                        password = "w0lfg4ng",
                        database = "imagesdypoledatabase")
    #print('Local connection established')
    return mydb

def setDistantConnection():
    # Open database connection
    mydb = mysql.connector.connect(host = MYSQLserverIP,
                        user = username,
                        password = password,
                        database = databaseName)
    #print('Distant connection established')
    return mydb

def getImageIDfromRunID(runID):
    sql_query = """SELECT imageID FROM images WHERE runID_fk = """ + str(runID) + """;"""
    imageID = executeGetQuery(sql_query)[0][0]
    return imageID

def getImageDatabase(imageID):
    sql_query = """SELECT atoms, noAtoms, dark FROM images WHERE imageID = """ + str(imageID) + """;"""
    byteArrayList = list(executeGetQuery(sql_query)[0])
    i = 0
    for i in range(len(byteArrayList)):
        if type(byteArrayList[i]) == str:
            byteArrayList[i] = bytearray(byteArrayList[i], 'utf-8')
    return byteArrayList  # returns a list of 3 bytearrays

def executeGetQuery(sql_query): # works when you don't need to use db.commit, so for read only functions
    db = setConnection()
    cursor = db.cursor()
    cursor.execute(sql_query)
    cursorResult = cursor.fetchall()
    cursor.close()
    db.close()
    return cursorResult

def getCameraDimensions(imageID):
    sql_query = "SELECT cameraID_fk FROM images WHERE imageID = " + str(imageID) + ";"
    cameraID = executeGetQuery(sql_query)[0][0]
    sql_query = "SELECT cameraHeight, cameraWidth FROM cameras WHERE cameraID = " + str(cameraID) + ";"
    height, width = executeGetQuery(sql_query)[0]
    return height, width

def writeAnalysisToDB(dictionnary, runID_fk):
    db = setConnection()
    cursor = db.cursor()
    if "nCount2" in dictionnary:
        sql_query = "INSERT INTO nCounts (nCount,xWidth,yWidth,xPos,yPos,runID_fk,PSD,nCount2,xWidth2,yWidth2,xPos2,yPos2) VALUES ({},{},{},{},{},{},{},{},{},{},{},{});" \
                .format(dictionnary["nCount"],dictionnary["xWidth"],dictionnary["yWidth"],dictionnary["xPos"],dictionnary["yPos"],runID_fk,dictionnary["PSD"],dictionnary["nCount2"],dictionnary["xWidth2"],dictionnary["yWidth2"],dictionnary["xPos2"],dictionnary["yPos2"])
    else:
        sql_query = "INSERT INTO nCounts (nCount,xWidth,yWidth,xPos,yPos,runID_fk,PSD) VALUES ({},{},{},{},{},{},{});".format(dictionnary["nCount"],dictionnary["xWidth"],dictionnary["yWidth"],dictionnary["xPos"],dictionnary["yPos"],runID_fk,dictionnary["PSD"])
    cursor.execute(sql_query)
    db.commit()
    cursor.close()
    db.close()

def getRunIDFromImageID(imageID):
    sql_query = "SELECT runID_fk FROM images WHERE imageID = {} ;".format(imageID)
    runID_fk = executeGetQuery(sql_query)[0][0]
    return runID_fk

def getNCount(imageID):
    try:
        runID_fk = getRunIDFromImageID(imageID)
        sql_query = "SELECT nCount FROM nCounts WHERE runID_fk = {} ;".format(runID_fk)
        nCount = executeGetQuery(sql_query)[0][0]
    except:
        nCount = 0.0
    return nCount

def updateAnalysisOnDB(dictionnary, imageID):
    if doesAnalysisExists(imageID):
        runID_fk = getRunIDFromImageID(imageID)
        db = setConnection()
        cursor = db.cursor()
        sql_query = "UPDATE nCounts SET nCount = {}, xWidth = {}, yWidth = {}, xPos = {}, yPos = {}, PSD = {} WHERE runID_fk = {};".format(dictionnary["nCount"],dictionnary["xWidth"],dictionnary["yWidth"],dictionnary["xPos"],dictionnary["yPos"],dictionnary["PSD"], runID_fk)
        cursor.execute(sql_query)
        db.commit()
        cursor.close()
        db.close()
    else:
        runID_fk = getRunIDFromImageID(imageID)
        writeAnalysisToDB(dictionnary, runID_fk)
        
        
def doesAnalysisExists(imageID):
    runID_fk = getRunIDFromImageID(imageID)
    sql_query = "SELECT nCountID FROM nCounts WHERE runID_fk = {} ;".format(runID_fk)
    result = executeGetQuery(sql_query)
    if result == []:
        return False
    else:
        return True

#### Unused functions ####

# def getLastImageID():
#     db = setConnection()
#     cursor = db.cursor()
#     sql_query = """SELECT MAX(imageID) FROM images;"""
#     cursor.execute(sql_query)
#     lastImageID = cursor.fetchall()[0][0]
#     cursor.close()
#     db.close()
#     return lastImageID

# def isNewRun():   # returns True if the value of newRun is set to 1 in the database
#     db = setConnection()
#     cursor = db.cursor()
#     sql_query = """SELECT newRun FROM updates;"""
#     cursor.execute(sql_query)
#     isNewRun = bool(cursor.fetchall()[0][0])
#     cursor.close()
#     db.close()
#     return isNewRun

# def getForeignKeys(imageID):
#     db = setConnection()
#     cursor = db.cursor()
#     sql_query = """SELECT runID_fk, sequenceID_fk FROM images WHERE images.imageID = %s;"""%(imageID)
#     cursor.execute(sql_query)
#     runID_fk, sequenceID_fk = cursor.fetchall()[0]
#     cursor.close()
#     db.close()
#     return runID_fk, sequenceID_fk


# def dataToBytes(pathFile):
#     # Convert camera fits data to binary format
#     with open(pathFile, 'rb') as file:
#         image = fits.getdata(file)
#     return image[0].tobytes('C'), image[1].tobytes('C'), image[2].tobytes('C')    # atoms, noAtoms, dark


# # one can get the header detailing the andorcamera parameters: fits.getheader(path)

# def insertNewImageLine(pathFile, parameters):
#     db = setConnection()
#     cursor = db.cursor()
#     sql_query = """INSERT INTO images (imageID, runID_fk, sequenceID_fk, cameraID_fk, timestamp) VALUES (%s, %s, %s, %s, '%s');"""%parameters
#     cursor.execute(sql_query)
#     db.commit()
#     print('New line set')
#     cursor.close()
#     db.close()

# def insertNewImage(bytesArray, imageType, imageID):
#     sql_query_imagaType = """UPDATE images SET %s = """%(imageType,)
#     sql_query_imageID = """ WHERE imageID = %s;"""%(imageID,)
#     sql_query = sql_query_imagaType + """%s""" + sql_query_imageID
#     db = setConnection()
#     cursor = db.cursor()
#     cursor.execute(sql_query, (bytesArray,))
#     db.commit()
#     print('uploaded image' + imageType)
#     cursor.close()
#     db.close()

# def importImagesToDatabase(pathFile, parameters):
#     imageID = parameters[0]
#     insertNewImageLine(pathFile, parameters)
#     atoms, noAtoms, dark = dataToBytes(pathFile)
#     insertNewImage(atoms, 'atoms', imageID)
#     insertNewImage(atoms, 'noAtoms', imageID)
#     insertNewImage(atoms, 'dark', imageID)

# def writeImageDataToCache(bytesAtoms, bytesNoAtoms, bytesDark, cameraID, runID, seqID):
#     dictImage = {"atoms": bytesAtoms,
#                  "noAtoms": bytesNoAtoms,
#                  "dark": bytesDark,
#                  "camID": cameraID,
#                  "runID": runID,
#                  "seqID": seqID}
#     client = memcache.Client([(memcachedServerIP, 11211)])
#     client.set_multi(dictImage, time=30)



