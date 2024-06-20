from PIL import Image
import sys
import time
import numpy as np

path = 'Trigger-19287377-0.tif'
im = Image.open(path)
image16 = np.array(im, dtype = np.int16) # np.int8 should be adapted from a variable in the DB telling the pixel depth of the camera.
image8 = np.array(im, dtype = np.int8)
imageFloat = np.array(im, dtype = np.float)
image = np.array(im)
im.close()


#imageFile = open('Trigger-19287377-0', 'rb')
