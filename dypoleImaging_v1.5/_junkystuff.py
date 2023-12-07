import datetime
import time

def copy3Layer(self):
    pass

def saveAbsorbImg(self, atomImage):
    pass

def snap(self, event):
    return

def showTOFFit(self, e):
    pass

def setXTrapFreq(self, e):
    pass

def setYTrapFreq(self, e):
    pass

def setTOF(self, e):
    pass

def snippetCommunicate(self, N_intEdge):
    self.setConstants()
    try:
        f = open(self.snippetPath, "w")
    except:
        msg = wx.MessageDialog(self, 'The file path for SnippetServer is not correct','Incorrect File Path', wx.OK)
        if msg.ShowModal() == wx.ID_OK:
            msg.Destroy()
        return
        
    if not N_intEdge:
        N_intEdge = -1
        N_count = -1
    else:
#            N_count = N_intEdge/((pixelToDistance**2)/crossSection)/(16/6.45)**2
        N_count = N_intEdge * (self.pixelToDistance**2)/self.crossSection
        
    
    f.writelines(self.timeString + '\t' + str(N_intEdge) + '\t-1' + '\t' + str(N_count) + '\t-1' + '\t' + str(self.atomNumFromGaussianX) + '\t-1' + '\t' + str(self.atomNumFromGaussianY) + '\t-1' + '\t' + str("%.3f"%(self.temperature[0])) + '\t-1' + '\t' + str("%.3f"%(self.temperature[1])) + '\t-1' + '\t' + str("%.3f"%(self.tempLongTime[0])) + '\t-1' + '\t' + str("%.3f"%(self.tempLongTime[1])) + '\n')
    
def autoFluorescenceRun(self, event):
    if self.isFluorescenceOn:
        print("I stop the camera")
        self.endCamera_fluorescence()
        self.isFluorescenceOn = False
        self.fluorescenceButton.SetLabel("Turn On")
    else:
        print("I start the camera")
        self.startCamera_fluorescence()
        self.isFluorescenceOn = True
        self.fluorescenceButton.SetLabel("Turn Off")
    return

def startCamera_fluorescence(self):
    self.camera.cameraDevice.shouldCameraRun_fluorescence = True
    self.cameraThread_fluorescence = threading.Thread(target = self.camera.cameraDevice.main_fluorescence, args = [self.axes1, self.canvas, self.fluorescenceNumberBox, self.axes_fluorescence, self.canvas_fluorescence]) #, args=[i])
    self.cameraThread_fluorescence.start()

def endCamera_fluorescence(self):
    print("Called the end camera")
    self.camera.cameraDevice.shouldCameraRun_fluorescence = False # that will change the value of the loop to acquire images
                                                    # and eventually end the acquisition process in a few seconds depending on the wait time for trigger
    time.sleep(0.5)
    self.cameraThread_fluorescence.join()    # this waits for the acquisition process to end
    print("UI ready to be used again")
    
def turnFluorescenceOn(self):
    acquire.main(self.axes1, self.canvas)

def setImageAngle(self, e):
    tx = e.GetEventObject()
    rotation = tx.GetValue()
    self.imageAngle = float(rotation)
    
def setImagePivotX(self, e):
    tx = e.GetEventObject()
    temp = int(tx.GetValue())
    
    x = self.atomImage.shape[0]
    if (x < temp) or (temp <= 0):
        temp = x/2
    
    self.imagePivotX = temp
    self.pivotXBox.SetValue(str(self.imagePivotX))
            
def setImagePivotY(self, e):
    tx = e.GetEventObject()
    temp = int(tx.GetValue())
    
    y = self.atomImage.shape[1]
    if (y < temp) or (temp <= 0):
        temp = y/2
    
    self.imagePivotY = temp
    self.pivotYBox.SetValue(str(self.imagePivotY))
    
def setImageRotationParams(self, e):
    if self.imageAngle == 0.  and self.imageAngle == self.prevImageAngle:
        self.isRotationNeeded = False
    else:
        self.isRotationNeeded = True

    self.setDataAndUpdate

def saveAsRef(self):
    if self.checkSaveAsRef.GetValue() is True:
        path = self.path[:-2] + "_ref\\"
        if not os.path.exists(path):
            os.makedirs(path)
        shutil.copy2(self.imageID, path)
        self.defringingRefPath = path

def fitImage(self):
    self.timeString = datetime.datetime.today().strftime("%a-%b-%d-%H_%M_%S-%Y")
    self.benchmark_startTime=time.time()
    try:
        if self.autoRunning == False:
            if not self.path:
                print("------------Wrong Folder!--------")
                return None
            self.updateLatestImageID()
            fileText = self.imageIDText.GetValue()     # This one is simply "In the database" if not checkLocalFiles
            if (len(fileText) == 0):    # ilf the file name has no length you just pick up the one on top of the list
                latestImageID = max(self.imageIDList)
                self.imageID = latestImageID[-1]
            self.setImageIDText()

        elif self.autoRunning == True:      
            self.updateLatestImageID()

        self.updateImageListBox()
        self.setDataNewIncomingFile()
        print("Successfully read Image")
        return True
    except Exception as err:
        print("Failed to read this image.")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

        self.showImg()

def setDataNewIncomingFile(self, pca = False, gaussianFilter = False, histogramEqualization = False, rotation  = True):
    # setDataNewIncomingFile is used after having loaded a new file from the camera
    try:
        self.setTransformedData(pca, gaussianFilter, histogramEqualization, rotation)
        self.setFitting()
        
    except Exception as e:
        msg = wx.MessageDialog(self, str(e),'Setting Data failed', wx.OK)
        print("self.imageID is " + str(self.imageID))
        if msg.ShowModal() == wx.ID_OK:
            msg.Destroy()
        print("====== setDataNewIncomingFile error =======")

def updateFittingResults(self):  # the two functions are defined in  _InitUIstuff
    self.updateTrueWidths()
    self.updatePeakValues()

def setDataAndUpdate(self):
    if self.checkApplyDefringing.GetValue() is True:
        self.defringing()
    self.setRawDataFromDB()
    hasFileSizeChanged = self.checkIfFileSizeChanged()
    # draw the newly set data
    self.updateImageOnUI(self.chosenLayerNumber, hasFileSizeChanged)
    self.setAtomNumber()

def updatePeakValues(self):
    activeAOI = self.primaryAOI
    temp = str(int(activeAOI.x_peakHeight)) + ",  " + str(int(activeAOI.y_peakHeight))
    self.peakBox.SetValue(temp)
    
def updateTrueWidths(self):
    activeAOI = self.primaryAOI
    activeAOI.true_x_width = activeAOI.x_width * self.pixelToDistance
    activeAOI.true_y_width = activeAOI.y_width * self.pixelToDistance
    
    activeAOI.true_x_width_std = activeAOI.x_width_std * self.pixelToDistance
    activeAOI.true_y_width_std = activeAOI.y_width_std * self.pixelToDistance
    try:
        std_avg = (activeAOI.true_x_width_std/activeAOI.true_x_width + activeAOI.true_y_width_std/activeAOI.true_y_width)/2
    except Exception as ex:
        print(ex)
        std_avg = 0
    temp = str("%.1f"%(activeAOI.true_x_width*1E6)) +",   " + str("%.1f"%(activeAOI.true_y_width*1E6))
    temp = "spotted"
    self.widthBox.SetValue(temp)
          