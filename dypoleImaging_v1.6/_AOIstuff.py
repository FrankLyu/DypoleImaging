import time
from selectionRectangle import *

def settempAOI1(self,e):
    try:
        value = int(e.GetEventObject().GetValue())
        if value > 0:
            self.tempAOI1 = value
    except:
        pass

def settempAOI2(self,e):
    try:
        value = int(e.GetEventObject().GetValue())
        if value > 0:
            self.tempAOI2 = value
    except:
        pass

def settempAOI3(self,e):
    try:
        value = int(e.GetEventObject().GetValue())
        if value > 0:
            self.tempAOI3 = value
    except:
        pass

def settempAOI4(self,e):
    try:
        value = int(e.GetEventObject().GetValue())
        if value > 0:
            self.tempAOI4 = value
    except:
        pass

def isAOI_PrimaryOutside(self):
    shape = self.atomImage.shape
    flag = self.primaryAOI.isOutside(shape)
    return flag
   
def isAOI_SecondaryOutside(self):
    flag = False
    shape = self.atomImage.shape
    if int(self.AOI1_Secondary.GetValue()) >= shape[1] or int(self.AOI1_Secondary.GetValue()) < 0:
        print("case 1")
        self.secondaryAOI.position[0] = 10
        flag = True
    
    if int(self.AOI2_Secondary.GetValue()) >= shape[0] or int(self.AOI2_Secondary.GetValue()) < 0:
        print("case 2")
        self.secondaryAOI.position[1] = 10
        flag = True
            
    if int(self.AOI3_Secondary.GetValue()) >= shape[1] or int(self.AOI3_Secondary.GetValue()) < 0 :
        print("case 3")
        self.secondaryAOI.position[2] = shape[1] - 10
        flag = True
        
    if int(self.AOI4_Secondary.GetValue()) >= shape[0] or int(self.AOI4_Secondary.GetValue()) < 0:
        print("case 4")
        self.secondaryAOI.position[3] = shape[0] - 10
        flag = True
    return flag
            

def on_press(self, event):
    if (event.xdata is None) or (event.ydata is None):
        return
    print("Clicked xpos =")
    print(event.xdata)
    print("Clicked ypos =")
    print(event.ydata)
    if event.button == 1: # 1 corresponds to MouseButton.LEFT
        print("PRESSING PRIMARY")
        if self.doubleAOIs and (self.AOIRadioBox.GetSelection() == 1):
            activeAOI = self.primaryAOI_2
        else:
            activeAOI = self.primaryAOI
    elif event.button == 3: # 3 corresponds to MouseButton.RIGHT
        print("PRESSING SECONDARY")
        if self.doubleAOIs and (self.AOIRadioBox.GetSelection() == 1):
            activeAOI = self.secondaryAOI_2
        else:
            activeAOI = self.secondaryAOI
    elif event.button == 2: # 2 corresponds to scroll wheel click
        self.toggleAOISelection()
    x0 = activeAOI.position[0] = int(event.xdata)
    y0 = activeAOI.position[1] = int(event.ydata)
    self.press = x0, y0, event.xdata, event.ydata

def on_motion(self, event):
    #'on motion we will move the rect if the mouse is over us'
    if (self.press is None) or (event.inaxes != self.axes1):
        return

    if event.button == 1: # 1 corresponds to MouseButton.LEFT
        if self.doubleAOIs and (self.AOIRadioBox.GetSelection() == 1):
            activeAOI = self.primaryAOI_2
        else:
            activeAOI = self.primaryAOI
    elif event.button == 3: # 3 corresponds to MouseButton.RIGHT
        if self.doubleAOIs and (self.AOIRadioBox.GetSelection() == 1):
            activeAOI = self.secondaryAOI_2
        else:
            activeAOI = self.secondaryAOI

    x0, y0, xpress, ypress = self.press
    self.x1 = event.xdata
    self.y1 = event.ydata
    activeAOI.position[2] = int(self.x1)
    activeAOI.position[3] = int(self.y1)
    activeAOI.update_patch()
    self.canvas.draw()

def on_release(self, event):
    if (event.xdata is None) or (event.ydata is None):
        return
    self.press = None

    if event.button == 1: # 1 corresponds to MouseButton.LEFT
        if self.doubleAOIs and (self.AOIRadioBox.GetSelection() == 1):
            activeAOI = self.primaryAOI_2
        else:
            activeAOI = self.primaryAOI
    elif event.button == 3: # 3 corresponds to MouseButton.RIGHT
        if self.doubleAOIs and (self.AOIRadioBox.GetSelection() == 1):
            activeAOI = self.secondaryAOI_2
        else:
            activeAOI = self.secondaryAOI

    self.x1 = event.xdata
    self.y1 = event.ydata
    activeAOI.position[2] = int(self.x1)
    activeAOI.position[3] = int(self.y1)
    if activeAOI.position[2] < activeAOI.position[0]:
        activeAOI.position[2], activeAOI.position[0] = activeAOI.position[0], activeAOI.position[2]
    if activeAOI.position[3] < activeAOI.position[1]:
        activeAOI.position[3], activeAOI.position[1] = activeAOI.position[1], activeAOI.position[3]

    if activeAOI.position[0] < 1: activeAOI.position[0] = 1
    if activeAOI.position[1] < 1: activeAOI.position[1] = 1
    if activeAOI.position[2] + 1 >= self.imageData[0].shape[1]: activeAOI.position[2] = self.imageData[0].shape[1] - 2
    if activeAOI.position[3] + 1 >= self.imageData[0].shape[0]: activeAOI.position[3] = self.imageData[0].shape[0] - 2

    activeAOI.update_patch()
    print("TIME BEFORE DRAW RELEASE " + str(time.time()))
    temp = time.time()
    self.canvas.draw()
    print("TIME TAKEN DRAW RELEASE " + str(time.time()-temp))
    self.canvas.flush_events()

    if event.button == 1:
        self.AOI1_Primary.SetValue(str(self.primaryAOI.position[0]))
        self.AOI2_Primary.SetValue(str(self.primaryAOI.position[1]))
        self.AOI3_Primary.SetValue(str(self.primaryAOI.position[2]))
        self.AOI4_Primary.SetValue(str(self.primaryAOI.position[3]))
        self.AOI_Primary = [[self.primaryAOI.position[0], self.primaryAOI.position[1]],[self.primaryAOI.position[2], self.primaryAOI.position[3]]]
    elif event.button == 3:
        self.AOI1_Secondary.SetValue(str(self.secondaryAOI.position[0]))
        self.AOI2_Secondary.SetValue(str(self.secondaryAOI.position[1]))
        self.AOI3_Secondary.SetValue(str(self.secondaryAOI.position[2]))
        self.AOI4_Secondary.SetValue(str(self.secondaryAOI.position[3]))
        self.AOI_Secondary = [[self.secondaryAOI.position[0], self.secondaryAOI.position[1]],[self.secondaryAOI.position[2], self.secondaryAOI.position[3]]]
    
    self.updatePrimaryImage()
    activeAOI.update_image(self.imageData)
    [aoi.update_image(self.imageData) for aoi in self.AOIList]

    self.setAtomNumber()
    self.update1DProfilesAndFit()

def typedAOI(self, event):
    activeAOI = self.primaryAOI  # Now this new function is only available for one spin, primary patch 08/16/2023

    activeAOI.position[0]=self.tempAOI1
    activeAOI.position[1]=self.tempAOI2
    activeAOI.position[2]=self.tempAOI3
    activeAOI.position[3]=self.tempAOI4

    if activeAOI.position[2] < activeAOI.position[0]:
        activeAOI.position[2], activeAOI.position[0] = activeAOI.position[0], activeAOI.position[2]
    if activeAOI.position[3] < activeAOI.position[1]:
        activeAOI.position[3], activeAOI.position[1] = activeAOI.position[1], activeAOI.position[3]

    if activeAOI.position[0] < 1: activeAOI.position[0] = 1
    if activeAOI.position[1] < 1: activeAOI.position[1] = 1
    if activeAOI.position[2] + 1 >= self.imageData[0].shape[1]: activeAOI.position[2] = self.imageData[0].shape[1] - 2
    if activeAOI.position[3] + 1 >= self.imageData[0].shape[0]: activeAOI.position[3] = self.imageData[0].shape[0] - 2

    activeAOI.update_patch()
    activeAOI.update_image(self.imageData)
    self.canvas.draw()
    self.canvas.flush_events()

    self.AOI1_Primary.SetValue(str(self.primaryAOI.position[0]))
    self.AOI2_Primary.SetValue(str(self.primaryAOI.position[1]))
    self.AOI3_Primary.SetValue(str(self.primaryAOI.position[2]))
    self.AOI4_Primary.SetValue(str(self.primaryAOI.position[3]))
    self.AOI_Primary = [[self.primaryAOI.position[0], self.primaryAOI.position[1]],[self.primaryAOI.position[2], self.primaryAOI.position[3]]]
    self.updatePrimaryImage()

    self.setAtomNumber()
    self.update1DProfilesAndFit()


def updatePrimaryImage(self):
    self.AOI_PrimaryImage = self.atomImage[self.primaryAOI.position[1]:self.primaryAOI.position[3], self.primaryAOI.position[0]:self.primaryAOI.position[2]]
    for activeAOI in self.AOIList:
        activeAOI.PrimaryImage = self.atomImage[activeAOI.position[1]:activeAOI.position[3], activeAOI.position[0]:activeAOI.position[2]]

def activateDoubleAOI(self, e):
    if e.IsChecked():
        self.doubleAOIs = e.IsChecked()
        self.primaryAOI_2 = selectionRectangle(color = "#d9294f", id_num = 2)
        self.secondaryAOI_2 = selectionRectangle(color = "#d9294f", dashed = True)
        self.secondaryAOI_2.issecondaryAOI = True
        self.primaryAOI_2.attachSecondaryAOI(self.secondaryAOI_2)
        self.AOIList.append( self.primaryAOI_2 )
        [self.drawAOIPatch(sR) for sR in [self.primaryAOI_2, self.secondaryAOI_2]]
        self.bigNcount4.Enable(True)
        self.canvas.draw()
        self.toggleAOISelection()
    else:
        if self.AOIRadioBox.GetSelection() == 1:
            self.toggleAOISelection()
        self.AOIList.pop()
        self.primaryAOI_2.patch.remove()
        self.secondaryAOI_2.patch.remove()
        self.primaryAOI_2.labelText.remove()
        self.primaryAOI_2 = None
        self.secondaryAOI_2 = None
        self.bigNcount4.Enable(False)
        self.bigNcount4.SetValue("")
        self.canvas.draw()
        self.doubleAOIs = e.IsChecked()


def toggleAOISelection(self):
    if self.doubleAOIs:
        newAOI_id = self.AOIRadioBox.GetSelection()
        if newAOI_id == 0:
            aoi0 = self.AOIList[1]
            aoi1 = self.AOIList[0]
        else:
            aoi0 = self.AOIList[0]
            aoi1 = self.AOIList[1]
        aoi0.labelText.set_bbox(dict(facecolor = aoi0.color, edgecolor = "none", pad = aoi0.labelTextPadding, alpha = 1.0))
        aoi0.patch.set_alpha(1.0)
        aoi0.secondaryAOI.patch.set_alpha(1.0)
        aoi1.labelText.set_bbox(dict(facecolor = aoi1.color, edgecolor = "none", pad = aoi1.labelTextPadding, alpha = 0.5))
        aoi1.patch.set_alpha(0.5)
        aoi1.secondaryAOI.patch.set_alpha(0.5)
        aoi0.update_patch()
        aoi1.update_patch()
        self.canvas.draw()
        self.AOIRadioBox.SetSelection((self.AOIRadioBox.GetSelection() + 1) % 2)            

def drawAOIPatch(self, aoi):
    self.axes1.add_patch(aoi.patch)
    if not aoi.id_num == 0:
        aoi.labelText = self.axes1.text(aoi.position[0] + 2*aoi.labelTextPadding,
                        aoi.position[1] + 2*aoi.labelTextPadding,
                        str(aoi.id_num),
                        color = "white",
                        horizontalalignment = "left",
                        verticalalignment = "top",
                        bbox = dict(facecolor = aoi.color, edgecolor = "none", pad = aoi.labelTextPadding))
    aoi.update_patch()