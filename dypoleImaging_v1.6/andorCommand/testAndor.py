# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 14:40:52 2021

@author: Dypole_Imaging
"""

lib = atmcd("C:\Program Files\Andor SDK3")
#lib.Initialize("C:\\Users\\Dypole_Imaging\\Desktop\\dypole-imaging\\andorCommand\\image")
lib.Initialize("C:\\Program Files\\Andor SDK3")
lib.GetAvailableCameras()

lib = atmcd("C:\Program Files\Andor SOLIS")
lib.Initialize("C:\Program Files\Andor SOLIS")
lib.GetAvailableCameras()
lib.GetHeadModel()
lib.GetCameraHandle(2)
handle = lib.GetCameraHandle(1)[1]
lib.SetCurrentCamera(handle)
lib.GetHeadModel()
lib.GetCurrentCamera()
lib.SetTemperature(-5)


lib.GetDetector()
lib.GetGateMode()