# -*- coding: utf-8 -*-

import time
import sys, os
from watchdog.observers import Observer
from watchforchange import MyHandler
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff
from watchdog.events import PatternMatchingEventHandler
from watchdog.events import DirCreatedEvent, DirDeletedEvent, DirModifiedEvent, DirMovedEvent


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
        #self.observer.schedule(self.handlerToCall, self.filePath)
        self.observer.schedule(self.handlerToCall, os.getcwd())
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
