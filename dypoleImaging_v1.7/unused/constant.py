import numpy as np

# transfer pixel to distance: divided by 2 because the image is magnified before the camara
pixelToDistance = 6.45E-6/2

mNuc = 1.66E-27
kB = 1.38E-23
mLi = 6 * mNuc
mNa = 23 * mNuc
hbar = 1.0545718E-34
MIN_T = np.exp(-5)

pixel2number = 1
lambdaBar = 589E-9  / (2 * np.pi)
crossSection = 6 * np.pi * lambdaBar ** 2

scatteringLength = 2.9E-9