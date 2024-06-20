# -*- coding: utf-8 -*-
"""
Created on Fri Dec 02 18:08:44 2016

@author: Jim Hyungmok Son
"""

import time
import sys, os
from watchdog.observers import Observer
#from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff
from watchdog.events import PatternMatchingEventHandler
#from watchdog.events import DirCreatedEvent, DirDeletedEvent, DirModifiedEvent, DirMovedEvent


class Monitor():
    def __init__(self, path, func, fileSize, Camera):
#        super(Monitor, self).__init__()
        self.filePath = path
        self.camera = Camera
#        self.timeChanged = False
        self.fileSize = fileSize
        self.handlerToCall = MyHandler(func, self.fileSize, self.camera)
        self.oldObserver = None
        
        # create the instance of the observer and set schedule
#        self.createObserverAndStart()

    def oldObserver(self):
        return self.oldObserver
        
    def createObserverAndStart(self):
#        try:        
#            if self.observer.isAlive():
#                print "--------Previous observer is alive------- Monitor"
#                self.observer.join()
#        except:
#            print "Failed at killing the previous observer --------- Monitor"
            
        self.observer = Observer()
        self.observer.schedule(self.handlerToCall, self.filePath)
        self.observer.start()

    def join(self):
        self.observer.join()
            
    def stop(self):
        self.observer.stop()
        
        
        # wait 5 secs until the thread dies
#        t = 0
#        while self.observer.isAlive() and t  <= 10:       
##            self.observer.join(0.5)
#            t = t + 1
#            print t
#            
#        if self.observer.isAlive():
#            print "Observer sill alive --- Monitor"           
#            return False
#        else:
#            print "Observer died --- Monitor"           
#            return True
        
    def changeFilePath(self, newFilePath):
#        if self.stopAndWait():
#            self.filePath = newFilePath
#            self.observer = None
#            self.createObserverAndStart()
#            print "========NEW OBSERVER FOR NEW FILE PATH CREATED============"
#        else:
##            self.filePath = newFilePath
##            self.observer = None
##            self.createObserverAndStart()
#            print "====FAILED====NO NEW OBSERVER============"

#        if not os.path.exists(newFilePath):
#            os.mkdir(newFilePath)
        self.stop()
        self.filePath = newFilePath
        self.oldObserver = self.observer
        self.observer = None
        self.createObserverAndStart()


class MyHandler(PatternMatchingEventHandler):
    def __init__(self, autoRunToCall, expectedFileSizeMB, Camera):
         super(MyHandler, self ).__init__()
         self.autoRunToCall = autoRunToCall      # autoRunToCall will be a function comming from the UI
         self.expectedFileSize = expectedFileSizeMB * 1024**2
         self.lastModTime=-1
         self.camera = Camera
         self.listOfValidImagesWaiting = []
         self.imageData = None

    def process(self, event):
        print(event.src_path, event.event_type)  # print now only for debug
        if len(self.listOfValidImagesWaiting) < self.camera.expectedImageWaiting:
            if self.checkValidImage(event.src_path):
                self.listOfValidImagesWaiting += [event.src_path]
            else:
                print("Invalid image")
        if len(self.listOfValidImagesWaiting) == self.camera.expectedImageWaiting:
            self.autoRunToCall()
            
            
    #     if self.cameraType == "Andor":      # gives a combined file
    #         self.processFLIR(event.src_path)
    #     if self.cameraType == "FLIR":       # gives 3 different files
    #         self.processAndor(event.src_path)
    
    # def processFLIR(self, newImagePath):
    #     if self.checkValidImage(newImagePath):
    #         print("One combined image ready to be read")
    #         self.listOfValidImagesWaiting += [newImagePath]
    #         self.autoRunToCall()
    #     else:
    #         print("Invalid combined image")

    # def processAndor(self, newImagePath):
    #     if len(self.listOfValidImagesWaiting) < 3:
    #         if self.checkValidImage(newImagePath):
    #             self.listOfValidImagesWaiting += [newImagePath]
    #             print("Found image number " + str(len(self.listOfValidImagesWaiting)))
    #         else:
    #             print("Invalid image")
    #     else:
    #         self.autoRunToCall()

    def getFileSize(self, imagePath):
        return int(os.stat(imagePath).st_size)
    
    def checkValidImage(self, newImagePath):
        print("Waiting for camera to write")
        nIteration = 10
        for i in range(nIteration):
            if self.checkImageNotFillingUp(newImagePath, nIteration): # True means the image file has a stable size
                filesize = self.getFileSize(newImagePath)
                print("ici")
                print("actual file size " + str(filesize) + "expected file size " + str(self.expectedFileSize))
                print("la")
                if (filesize >= self.expectedFileSize):
                    break
            time.sleep(0.05)
        if i == nIteration - 1:
            print("The image file is too small")
            return False
        return True
    
    def checkImageNotFillingUp(self, newImagePath, nIteration): # returns True if the file has finished to fill up
        previousFilesize = 1    # one byte, to prevent 0 size image
        for j in range(nIteration):
            filesize = self.getFileSize(newImagePath)
            if previousFilesize == filesize:
                break
            previousFilesize = filesize
            time.sleep(0.01)
        if j == nIteration - 1:
            print("The image file didn't fill up properly")
            return False
        return True

    def on_created(self, event):
        self.process(event)

if __name__ == '__main__':
    args = sys.argv[1:]
    observer = Observer()
    observer.schedule(MyHandler(), path = args[0] if args else '.')
    observer.start()

    try:
        while True:
            time.sleep(1)
            print("tick tock------")
    except KeyboardInterrupt:
        observer.stop()
        observer.join()