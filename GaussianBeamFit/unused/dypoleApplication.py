#!/usr/bin/python
# -*- coding: utf-8 -*-

#####WX IMPORTS#####
#wx- GUI toolkit for the Python programming language. wxPython can be used to create graphical user interfaces (GUI).
import wx
import packages.core as core
import packages.userinterface as userinterface
import packages.imagedatamanager as imagedata
import packages.fitmanager as fit
import packages.monitor as monitor
#import packages.devicemanager as devicemanager
#import packages.dbmanager as dbmanager

class ImageViewer():
    def __init__(self):
        self.core = core.Core()
        self.userInterface = userinterface.UserInterface()
        self.imageDataManager = imagedata.ImageDataManager(None)
        self.fitManager = fit.FitManager()
        self.monitor = monitor.Monitor()
        #self.devicemanager = devicemanager.DeviceManager()
        #self.dbManager = dbmanager.DBManager()


if __name__ == '__main__':
    print("here1")
    app = wx.App()
    print("here2")
    dypoleImageViewer = ImageViewer()
    #ui = ImageUI(None, title='Atom Image Analysis Dy v')
    print("here3")
    #ui.fitImage()
    #print("here4")
    app.MainLoop()
    print("here5")

