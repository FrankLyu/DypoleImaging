def setZoomedCoordinates(self):
    self.xMinZoom = self.xZoomCenter - self.zoomWidth//2
    self.xMaxZoom = self.xZoomCenter + self.zoomWidth//2
    self.yMinZoom = self.yZoomCenter - self.zoomWidth//2
    self.yMaxZoom = self.yZoomCenter + self.zoomWidth//2
    
def setZoomImage(self, data):
    self.setZoomedCoordinates()
    dataZoom = data[self.yMinZoom:self.yMaxZoom, self.xMinZoom:self.xMaxZoom]
    self.axesZoom.cla()
    self.currentZoomImage = self.axesZoom.imshow(dataZoom, cmap=self.cmap, aspect='equal', vmin=-0.1, vmax=0.3, extent=[self.xMinZoom, self.xMaxZoom, self.yMaxZoom, self.yMinZoom])
    self.canvasZoom.draw()
    
def setZoomCenterX(self, e):
    try:
        value = int(e.GetEventObject().GetValue())
        if value > 0:
            self.xZoomCenter = value
            self.setZoomImage(self.atomImage)
    except:
        pass
            
def setZoomCenterY(self, e):
    try:
        value = int(e.GetEventObject().GetValue())
        if value > 0:
            self.yZoomCenter = value
            self.setZoomImage(self.atomImage)
    except:
        pass
    
def setZoomWidth(self, e):
    try:
        value = int(e.GetEventObject().GetValue())
        if value > 0:
            self.zoomWidth = value
            self.setZoomImage(self.atomImage)
    except:
        pass

def showImgValueZoom(self, e):
    if e.xdata and e.ydata:
        x = int(e.xdata)
        y = int(e.ydata)
        if self.imageData and (x >= 0  and x < self.imageData[0].shape[1]) and (y >= 0 and y < self.imageData[0].shape[0]):
            self.cursorX_Zoom.SetValue(str(x))
            self.cursorY_Zoom.SetValue(str(y))
            self.cursorZ_Zoom.SetValue('%0.4f'%self.atomImage[y][x])