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
import platform
import csv
#import memcache

from config import minimumFileSize, waitTimeStep, MYSQLserverIP, username, password, databaseName
#from config import memcachedServerIP
#from localPath import SPACER

if platform.system() == 'Darwin': # MAC OS
    SPACER = '/'

if platform.system() == 'Linux':
    SPACER = '/'

if platform.system() == 'Windows':
    SPACER = '\\'

#### Used functions ####


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
    return mydb

def setDistantConnection():
    # Open database connection
    mydb = mysql.connector.connect(host = MYSQLserverIP,
                        user = username,
                        password = password,
                        database = databaseName)
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

def getRunIDFromImageID(imageID):
    sql_query = "SELECT runID_fk FROM images WHERE imageID = {} ;".format(imageID)
    runID_fk = executeGetQuery(sql_query)[0][0]
    return runID_fk


def executeGetQuery(sql_query): # works when you don't need to use db.commit, so for read only functions
    db = setConnection()
    cursor = db.cursor()
    cursor.execute(sql_query)
    cursorResult = cursor.fetchall()
    cursor.close()
    db.close()
    return cursorResult

def updatePSDOnDB(PSD, runID_fk):
    try:
        db = setConnection()
        cursor = db.cursor()
        sql_query = "UPDATE nCounts SET PSD = {} WHERE runID_fk = {};".format(PSD, runID_fk)
        cursor.execute(sql_query)
        db.commit()
        cursor.close()
        db.close()
    except:
        print("Failed JH")
        
# Path to your CSV file
file_path = 'local_data.csv'

db = setConnection()
cursor = db.cursor()

with open(file_path, mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        runID = int(row['runID'])
        nCount = int(row['nCount'])
        sql_query = "UPDATE nCounts SET PSD = {} WHERE runID_fk = {};".format(nCount, runID)
        cursor.execute(sql_query)
        db.commit()

cursor.close()

db.close()