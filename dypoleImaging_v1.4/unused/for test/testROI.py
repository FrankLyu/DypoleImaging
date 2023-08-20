from pylab import *
from skimage import data
from skimage.viewer.canvastools import RectangleTool
from skimage.viewer import ImageViewer

im = data.camera()

def get_rect_coord(extents):
    global viewer,coord_list
    coord_list.append(extents)

def get_ROI(im):
    global viewer,coord_list

    selecting=True
    while selecting:
        viewer = ImageViewer(im)
        coord_list = []
        rect_tool = RectangleTool(viewer, on_enter=get_rect_coord) 
        print("Draw your selections, press ENTER to validate one and close the window when you are finished")
        viewer.show()
        finished=raw_input('Is the selection correct? [y]/n: ')
        if finished!='n':
            selecting=False
    return coord_list

a=get_ROI(im)
print(a)