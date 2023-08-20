import matplotlib
import numpy as np

class selectionRectangle():
    def __init__(self, color = "#14a7fc", dashed = False, id_num = 0):
        self.position = np.array([1, 1, 3, 3]) # left, top, right, bottom
        if dashed:
            lstl = "--"
        else:
            lstl = "-"
        self.patch = matplotlib.patches.Rectangle((0,0), 1, 1, facecolor="none",linewidth=2, edgecolor = color, ls = lstl)
        self.id_num = id_num
        self.color = color
        self.labelTextPadding = 1.5
        self.absImg = np.zeros((100, 100))
        self.ODImg = np.zeros((100, 100))
        self.rawAtomNumber = 0
        self.temperature = [0, 0]
        self.tempLongTime = [0, 0]

    def update_patch(self):
        width = self.position[2] - self.position[0]
        self.patch.set_width(width)
        height = self.position[3] - self.position[1]
        self.patch.set_height(height)
        self.patch.set_xy((self.position[0], self.position[1]))
        if hasattr(self, "labelText"):
            xpos = np.min(self.position[[0, 2]])
            ypos = np.min(self.position[[1, 3]])
            self.labelText.set(x = xpos + 2*self.labelTextPadding,
                               y = ypos + 2*self.labelTextPadding)

    def update_image(self, imageData):
        imageData = np.array(imageData)
        self.imageCrop = imageData[:, self.position[1]:self.position[3], self.position[0]:self.position[2]]
        if hasattr(self, "secondaryAOI"):
            # A second AOI has been linked, and we use that to normalize the background
            self.secondaryAOI.update_image(imageData)
            lightDiff = self.secondaryAOI.getLightDiff()
            noAtom = self.imageCrop[1]*lightDiff - self.imageCrop[2]
        else:
            noAtom = self.imageCrop[1] - self.imageCrop[2]
        self.absImg = np.maximum(self.imageCrop[0] - self.imageCrop[2], 0.1) / np.maximum(noAtom, 0.1)
        self.ODImg = -np.log(self.absImg)

    def getLightDiff(self):
        return np.mean(self.imageCrop[0])/np.mean(self.imageCrop[1])

    def attachPrimaryAOI(self, primaryAOI):
        self.primaryAOI = primaryAOI

    def attachSecondaryAOI(self, secondaryAOI):
        self.secondaryAOI = secondaryAOI

    def isOutside(self, shape):
        flag = False
        if int(self.position[0]) >= shape[1] or int(self.position[0]) < 0:
            self.position[0] = 10
            flag = True

        if int(self.position[1]) >= shape[0] or int(self.position[1]) < 0:
            self.position[1] = 10
            flag = True

        if int(self.position[2]) >= shape[1] or int(self.position[2]) < 0:
            self.position[2] = shape[1] - 10
            flag = True

        if int(self.position[3]) >= shape[0] or int(self.position[3]) < 0:
            self.position[3] = shape[0] - 10
            flag = True

        return flag
