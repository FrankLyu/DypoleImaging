import time
import sys, os
from watchdog.observers import Observer
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff
from watchdog.events import PatternMatchingEventHandler
from watchdog.events import DirCreatedEvent, DirDeletedEvent, DirModifiedEvent, DirMovedEvent
# import AnalyzeAIA


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
        if len(self.listOfValidImagesWaiting) < 1:
            if self.checkValidImage(event.src_path):
                self.listOfValidImagesWaiting += [event.src_path]
            else:
                print("Invalid image")
        if len(self.listOfValidImagesWaiting) == 1:
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
                print("actual file size " + str(filesize) + "expected file size " + str(self.expectedFileSize))
                if (filesize >= self.expectedFileSize):
                    break
            time.sleep(0.2)
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