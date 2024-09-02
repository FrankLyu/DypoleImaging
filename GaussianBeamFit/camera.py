# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 16:15:58 2020

@author: Dypole
"""
import time
#from FLIRCommand.runHardwareTriggerContinuousTwoCam import mainRunHardwareTrigger
#from FLIRCommand.runHardwareTriggerContinuousTwoCam import FLIRCamera
from config import LOCAL_CAMERA_PATH_FLIR, LOCAL_CAMERA_PATH_ANDOR

class Camera():
    def __init__(self, cameraType, cameraPosition):
        self.cameraType = cameraType
        if self.cameraType == "Andor":
            self.expectedImageWaiting = 1
            self.height = 2160
            self.width = 2560
            self.cameraID = 4
            self.pathWrittenImages = LOCAL_CAMERA_PATH_ANDOR
            print("It s an Andor")
        elif self.cameraType == "FLIR":
            self.expectedImageWaiting = 3
            self.height = 1536
            self.width = 2048
            self.cameraID = 5
            self.cameraDevice = FLIRCamera(cameraPosition)
            self.pathWrittenImages = LOCAL_CAMERA_PATH_FLIR
        elif self.cameraType == "dummy": # Maybe replace by the camera nb in the db
            self.expectedImageWaiting = None
            self.height = 1
            self.width = 1
            self.cameraID = 2
            self.pathWrittenImages = None
        else:
            self.expectedImageWaiting = None
            self.pathWrittenImages = None
    
    def runFLIRCamera(self):
        self.cameraDevice.mainRunHardwareTrigger()
        #mainRunHardwareTrigger()
    

def mimicRunning():
    while True:
        print("Camera Started")
        time.sleep(5)
    #print("Camera Ended")