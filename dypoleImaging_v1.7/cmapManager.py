# "In Dypole, any change has to be incremental" - Michael
import numpy as np
import matplotlib.pyplot as plt
import datetime
from matplotlib import cm
from matplotlib.colors import ListedColormap

def dayssince():
    return (datetime.date.today() - datetime.date(2022, 5, 4)).days

def todayscmap():
    days = dayssince()
    k = np.min((days, 30))
    c1 = cm.get_cmap("Greens")
    c2 = cm.get_cmap("magma_r")
    newc = [(np.array(c1(i))*(30-k) + k*np.array(c2(i)))/30 for i in range(256)]
    return ListedColormap(np.vstack(newc))