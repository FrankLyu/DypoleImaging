import wx
from matplotlib.figure import Figure
import numpy as np
from matplotlib import gridspec
from cmapManager import todayscmap
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import wx.lib.rcsizer  as rcs
import datetime
from DatabaseCommunication.dbFunctions import getLastImageID, getLastImageIDs, getTimestamp, getLastID, updateNewImage, writeAnalysisToDB, updateAnalysisOnDB, getNCount
from DatabaseCommunication.dbFunctionsC import writeImageToCacheC

def InitUI(self):
    #        self.panel = wx.Panel(self)
    self.panel = wx.lib.scrolledpanel.ScrolledPanel(self, id = -1, size = (1,1)) # does the size even matter?
    self.panel.SetupScrolling()
    
    font1 = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)

    hbox = wx.BoxSizer(wx.HORIZONTAL)  # this is the general box: its left part are the setting, 
                                        # and its right part the image/Ncounts

    vbox0 = wx.BoxSizer(wx.VERTICAL)    # this is the setting vertical box

    settingBox = wx.StaticBox(self.panel, label = 'Setting')
    settingBoxSizer = wx.StaticBoxSizer(settingBox, wx.VERTICAL)

    
    ## camera configuration
    cameraConfigBox = wx.StaticBox(self.panel, label = 'Camera Configuration')
    cameraConfigBoxSizer = wx.StaticBoxSizer(cameraConfigBox, wx.VERTICAL)
    
    # Camera Type
    cameraTypeBox = wx.StaticBox(self.panel, label = 'Camera Type')
    cameraTypeBoxSizer = wx.StaticBoxSizer(cameraTypeBox, wx.HORIZONTAL)
    self.FLIRCamera = wx.RadioButton(self.panel, label="FLIR", style = wx.RB_GROUP)
    self.AndorCamera = wx.RadioButton(self.panel, label="Andor")
    self.AndorCamera.SetValue(True)
    cameraTypeBoxSizer.Add(self.FLIRCamera, flag=wx.ALL, border=5)
    cameraTypeBoxSizer.Add(self.AndorCamera, flag=wx.ALL, border=5)
    self.Bind(wx.EVT_RADIOBUTTON, self.setCameraType, id = self.FLIRCamera.GetId())
    self.Bind(wx.EVT_RADIOBUTTON, self.setCameraType, id = self.AndorCamera.GetId())
    
    # camera position (for FLIR camera)
    cameraPositionBox = wx.StaticBox(self.panel, label = 'Camera Position')
    cameraPositionBoxSizer = wx.StaticBoxSizer(cameraPositionBox, wx.HORIZONTAL)
    self.verticalCamera = wx.RadioButton(self.panel, label="Vertical", style = wx.RB_GROUP)
    self.horizontalCamera = wx.RadioButton(self.panel, label="Horizontal")
    self.TestCamera = wx.RadioButton(self.panel, label="Test")
    self.TestCamera.SetValue(True)
    
    cameraPositionBoxSizer.Add(self.verticalCamera, flag=wx.ALL, border=5)
    cameraPositionBoxSizer.Add(self.horizontalCamera, flag=wx.ALL, border=5)
    cameraPositionBoxSizer.Add(self.TestCamera, flag=wx.ALL, border=5)
    
    self.Bind(wx.EVT_RADIOBUTTON, self.setCameraPosition, id = self.verticalCamera.GetId())
    self.Bind(wx.EVT_RADIOBUTTON, self.setCameraPosition, id = self.horizontalCamera.GetId())
    self.Bind(wx.EVT_RADIOBUTTON, self.setCameraPosition, id = self.TestCamera.GetId())
    
    imageCroppedOrNot = wx.BoxSizer(wx.HORIZONTAL)
    self.buttonSaveFull = wx.RadioButton(self.panel, label="Save full image", style = wx.RB_GROUP )
    self.buttonSaveCropped = wx.RadioButton(self.panel, label="Save crop")
    self.buttonSaveDummy = wx.RadioButton(self.panel, label="Save dummy")

    imageCroppedOrNot.Add(self.buttonSaveFull, flag=wx.ALL, border=5)
    imageCroppedOrNot.Add(self.buttonSaveCropped, flag=wx.ALL, border=5)
    imageCroppedOrNot.Add(self.buttonSaveDummy, flag=wx.ALL, border=5)
    self.buttonSaveDummy.SetValue(True)
    

    self.startCameraButton = wx.Button(self.panel, label = 'Start FLIR camera')
    self.startCameraButton.Bind(wx.EVT_BUTTON, self.startCamera_trigger)
    self.endCameraButton = wx.Button(self.panel, label = 'End FLIR camera')
    self.endCameraButton.Bind(wx.EVT_BUTTON, self.endCamera_trigger)
    hbox155 = wx.BoxSizer(wx.HORIZONTAL)
    hbox155.Add(self.startCameraButton, flag = wx.ALL, border = 5)
    hbox155.Add(self.endCameraButton, flag = wx.ALL, border = 5)
    
    
    cameraConfigBoxSizer.Add(cameraTypeBoxSizer, flag=wx.ALL| wx.EXPAND, border = 5)
    cameraConfigBoxSizer.Add(cameraPositionBoxSizer, flag=wx.ALL| wx.EXPAND, border = 5)
    #cameraConfigBoxSizer.Add(self.checkBoxSaveDummy, border=5)
    cameraConfigBoxSizer.Add(imageCroppedOrNot, border=5)
    cameraConfigBoxSizer.Add(hbox155, wx.ALL|wx.EXPAND, 5)
    
    settingBoxSizer.Add(cameraConfigBoxSizer, flag=wx.ALL| wx.EXPAND, border = 5)
    '''
    fermionOrBosonBox = wx.StaticBox(self.panel, label = 'Fermion/Boson/Gaussian')
    fermionOrBosonBoxSizer = wx.StaticBoxSizer(fermionOrBosonBox, wx.HORIZONTAL)
    '''
    ######################
    ## TEXT BUTTON ##
    self.fitMethodFermion = wx.RadioButton(self.panel, label="Fermion", style = wx.RB_GROUP )
    self.fitMethodBoson = wx.RadioButton(self.panel, label="Boson")
    self.fitMethodGaussian = wx.RadioButton(self.panel, label="Gaussian")
    self.fitMethodGaussian.Hide()
    self.fitMethodBoson.Hide()
    self.fitMethodFermion.Hide()
    self.checkDisplayRadialAvg = wx.CheckBox(self.panel, label="Display radially averaged profile")
    self.Bind(wx.EVT_CHECKBOX, self.displayRadialAvg, id = self.checkDisplayRadialAvg.GetId())
    
    self.checkNormalization = wx.CheckBox(self.panel, label="Normalization (matching " + u"\u03BC" + " , " + u"\u03C3"+ " of atom shot && ref.)")
    self.Bind(wx.EVT_CHECKBOX, self.displayNormalization, id = self.checkNormalization.GetId())

    ######################
    '''
    self.fitMethodFermion.Disable()
#        self.fitMethodBoson.Disable()
    
    self.Bind(wx.EVT_RADIOBUTTON, self.update1DProfilesAndFit, id = self.fitMethodFermion.GetId())
    self.Bind(wx.EVT_RADIOBUTTON, self.update1DProfilesAndFit, id = self.fitMethodBoson.GetId())
    self.Bind(wx.EVT_RADIOBUTTON, self.update1DProfilesAndFit, id = self.fitMethodGaussian.GetId())
    
    fermionOrBosonBoxSizer.Add(self.fitMethodFermion, flag=wx.ALL, border=5)
    fermionOrBosonBoxSizer.Add(self.fitMethodBoson, flag=wx.ALL, border=5)
    fermionOrBosonBoxSizer.Add(self.fitMethodGaussian, flag=wx.ALL, border=5)
    settingBoxSizer.Add(fermionOrBosonBoxSizer, flag=wx.ALL| wx.EXPAND, border = 5)
    settingBoxSizer.Add(self.show2DContourButton, flag=wx.ALL| wx.EXPAND, border = 5)
    '''
    settingBoxSizer.Add(self.checkNormalization, flag = wx.ALL | wx.EXPAND, border = 5)
    settingBoxSizer.Add(self.checkDisplayRadialAvg, flag = wx.ALL | wx.EXPAND, border = 5)
    

    vbox0.Add(settingBoxSizer, 0, wx.ALL|wx.EXPAND,  5)

    ### Fluorescence monitor
    '''
    fluorescenceBox = wx.StaticBox(self.panel, label = 'Fluorescence monitor')
    fluorescenceBoxSizer = wx.StaticBoxSizer(fluorescenceBox,  wx.VERTICAL)
    
    self.snapButton = wx.Button(self.panel, label = 'Snap')
    self.snapButton.Bind(wx.EVT_BUTTON, self.snap)
    self.fluorescenceButton = wx.Button(self.panel, label = 'Turn On')
    
    self.fluorescenceButton.Bind(wx.EVT_BUTTON, self.autoFluorescenceRun)
    fluorescenceBoxSizer.Add(self.snapButton, flag=wx.ALL|wx.EXPAND, border= 5)
    fluorescenceBoxSizer.Add(self.fluorescenceButton, flag=wx.ALL|wx.EXPAND, border= 5)
    
    self.isFluorescence = False
    bigfont_fluorescence = wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
    fluorescenceNumberText = wx.StaticText(self.panel, label='Total nCount: ')
    self.fluorescenceNumberBox = wx.TextCtrl(self.panel,  style=wx.TE_READONLY|wx.TE_CENTRE, size=(100,34))
    self.fluorescenceNumberBox.SetFont(bigfont_fluorescence)
    fluorescenceBoxSizer.Add(fluorescenceNumberText, flag=wx.ALL, border=5)
    fluorescenceBoxSizer.Add(self.fluorescenceNumberBox, flag=wx.ALL, border=5)
    
    
    self.figure_fluorescence = Figure(figsize = (2,2))
    self.axes_fluorescence = self.figure_fluorescence.add_subplot(111)
    self.axes_fluorescence.set_title('Fluorescence count', fontsize=12)
    for label in (self.axes_fluorescence.get_xticklabels() + self.axes_fluorescence.get_yticklabels()):
        label.set_fontsize(10)
    self.linePlot_fluorescence, = self.axes_fluorescence.plot(np.zeros(20))
    '''
    #Don't show the fluo count for now
    #self.canvas_fluorescence = FigureCanvas(self.panel, -1, self.figure_fluorescence)
    #fluorescenceBoxSizer.Add(self.canvas_fluorescence, flag=wx.ALL|wx.EXPAND, border=5)
    #vbox0.Add(fluorescenceBoxSizer, 0, wx.ALL|wx.EXPAND, 5)


    ###############################
    fittingBox = wx.StaticBox(self.panel, label = 'Reading')
#        fittingBox.SetMaxSize((250, 400))
    fittingBoxSizer = wx.StaticBoxSizer(fittingBox,  wx.VERTICAL)


    
    self.autoButton = wx.Button(self.panel, label = 'Auto Read')
    self.autoButton.Bind(wx.EVT_BUTTON, self.startAutoRun)
    self.TOFcalcbutton = wx.Button(self.panel, label="TOF Calculator")
    self.TOFcalcbutton.Bind(wx.EVT_BUTTON, self.TOFcalc)

    fittingBoxSizer.Add(self.autoButton, flag=wx.ALL|wx.EXPAND, border= 5)
    fittingBoxSizer.Add(self.TOFcalcbutton, flag=wx.ALL|wx.EXPAND, border= 5)

    self.snippetPath = "~\Dropbox (MIT)\Documents\MIT\dypole-imaging\Andor\snippet.txt"
    snippetText = wx.StaticText(self.panel, label='Text file path for Snippet Server:')
    self.snippetTextBox = wx.TextCtrl(self.panel, value = self.snippetPath)
    self.snippetTextBox.Bind(wx.EVT_TEXT, self.setSnippetPath)
    fittingBoxSizer.Add(snippetText, flag=wx.ALL | wx.EXPAND, border=5)
    fittingBoxSizer.Add(self.snippetTextBox, flag=wx.ALL | wx.EXPAND, border=5)

    listText = wx.StaticText(self.panel, label='Image List')
    self.imageListBox = wx.ListBox(self.panel, size = (265, 100))
    self.Bind(wx.EVT_LISTBOX, self.chooseImgfromDB, self.imageListBox)
    fittingBoxSizer.Add(listText, flag=wx.ALL, border=5)
    fittingBoxSizer.Add(self.imageListBox, 1, wx.ALL | wx.EXPAND, border=5)
    self.updateImageListBox()
    vbox0.Add(fittingBoxSizer, 0, wx.ALL|wx.EXPAND, 5)
    

    hbox.Add(vbox0, 2, wx.ALL|wx.EXPAND, 5)  # 2 here means that the relative width of the box will be 2

######### images ##################
    
#        self.initImageUI()
    imagesBox = wx.StaticBox(self.panel, label='Images')
    imagesBoxSizer = wx.StaticBoxSizer(imagesBox, wx.VERTICAL)
   
    self.figure = Figure(figsize = (8,8))
#        figure.tight_layout(h_pad=1.0)
    #gs = gridspec.GridSpec(5, 5)
    gs = gridspec.GridSpec(2, 2, width_ratios=(7, 2), height_ratios=(7, 2), wspace = 0.05, hspace = 0.08)
    #gs.update(wspace = 0.05, hspace = 0.05)
    #self.axes1 = figure.add_subplot(gs[:-1, :-1])
    self.axes1 = self.figure.add_subplot(gs[0, 0])
    self.axes1.set_title('Original Image', fontsize=12)
    self.cmap = todayscmap()

    for label in (self.axes1.get_xticklabels() + self.axes1.get_yticklabels()):
        label.set_fontsize(10)
        
    #self.axes2 = figure.add_subplot(gs[-1, 0:-1])
    self.axes2 = self.figure.add_subplot(gs[1, 0])
    self.axes2.grid(True)
    for label in (self.axes2.get_xticklabels() + self.axes2.get_yticklabels()):
        label.set_fontsize(10)

    #self.axes3 = figure.add_subplot(gs[:-1, -1])
    self.axes3 = self.figure.add_subplot(gs[0, 1])
    self.axes3.grid(True)
    for label in (self.axes3.get_xticklabels()):
        label.set_fontsize(10)
    
    for label in (self.axes3.get_yticklabels()):
        label.set_visible(False)
        
    self.canvas = FigureCanvas(self.panel, -1, self.figure)
    self.canvas.mpl_connect('button_press_event', self.on_press)
    self.canvas.mpl_connect('button_release_event', self.on_release)
    self.canvas.mpl_connect('motion_notify_event', self.on_motion)
    self.canvas.mpl_connect('motion_notify_event', self.showImgValue)
    imagesBoxSizer.Add(self.canvas, flag=wx.ALL|wx.EXPAND, border=5)
    self.press= None


# 4 layer radio buttons

    hbox41 = wx.BoxSizer(wx.HORIZONTAL)
    self.layer1Button = wx.RadioButton(self.panel, label="Probe With Atoms", style = wx.RB_GROUP )
    self.layer2Button = wx.RadioButton(self.panel, label="Probe Without Atoms")
    self.layer3Button = wx.RadioButton(self.panel, label="Dark Field")
    self.layer4Button = wx.RadioButton(self.panel, label="Absorption Image")
    hasFileSizeChanged = False
    self.Bind(wx.EVT_RADIOBUTTON, lambda e: self.updateImageOnUI(1, hasFileSizeChanged), id=self.layer1Button.GetId())
    self.Bind(wx.EVT_RADIOBUTTON, lambda e: self.updateImageOnUI(2, hasFileSizeChanged), id=self.layer2Button.GetId())
    self.Bind(wx.EVT_RADIOBUTTON, lambda e: self.updateImageOnUI(3, hasFileSizeChanged), id=self.layer3Button.GetId())
    self.Bind(wx.EVT_RADIOBUTTON, lambda e: self.updateImageOnUI(4, hasFileSizeChanged), id=self.layer4Button.GetId())
    # default setting
    self.layer4Button.SetValue(True)
    self.chosenLayerNumber = 4

    hbox41.Add(self.layer1Button, flag=wx.ALL, border=5)
    hbox41.Add(self.layer2Button, flag=wx.ALL, border=5)
    hbox41.Add(self.layer3Button, flag=wx.ALL, border=5)
    hbox41.Add(self.layer4Button, flag=wx.ALL, border=5)

    imagesBoxSizer.Add(hbox41,flag= wx.CENTER, border=5)

# 4 layer radio buttons

    hbox421 = rcs.RowColSizer()
    hbox42 = wx.BoxSizer(wx.HORIZONTAL)
    boldFont = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
    st17 = wx.StaticText(self.panel, label='X:')
    self.cursorX = wx.TextCtrl(self.panel,  style=wx.TE_READONLY|wx.TE_CENTRE, size = (50, 22))
    st18 = wx.StaticText(self.panel, label='Y:')
    self.cursorY = wx.TextCtrl(self.panel, style=wx.TE_READONLY|wx.TE_CENTRE,  size = (50, 22))
    st19 = wx.StaticText(self.panel, label='Value:')
    self.cursorZ = wx.TextCtrl(self.panel, style=wx.TE_READONLY|wx.TE_CENTRE,  size = (80, 22))
    hbox42.Add(st17, flag=wx.ALL, border=5)
    hbox42.Add(self.cursorX, flag=wx.ALL, border=5)
    hbox42.Add(st18, flag=wx.ALL, border=5)
    hbox42.Add(self.cursorY, flag=wx.ALL, border=5)
    hbox42.Add(st19, flag=wx.ALL, border=5)
    hbox42.Add(self.cursorZ, flag=wx.ALL, border=5)
    
    self.cursorX.SetFont(boldFont)
    self.cursorY.SetFont(boldFont)
    self.cursorZ.SetFont(boldFont)
    
    #########
    ## defringing option ##
    hbox43 = wx.BoxSizer(wx.HORIZONTAL)
    defringingBox = wx.StaticBox(self.panel)
    defringingBoxSizer = wx.StaticBoxSizer(defringingBox, wx.HORIZONTAL)
    
    self.checkApplyDefringing = wx.CheckBox(self.panel, label = "Apply defringing")
    self.checkResetAOI = wx.CheckBox(self.panel, label = "Reset AOI")
    self.checkMedianFilter = wx.CheckBox(self.panel, label = "Median filter")
#        self.checkSaveAsRef = wx.CheckBox(self.panel, label = "Save as ref")
    
    self.Bind(wx.EVT_CHECKBOX, lambda e: self.applyDefringing(), id = self.checkApplyDefringing.GetId())
    self.checkResetAOI.Enable(False)
    self.Bind(wx.EVT_CHECKBOX, lambda e: self.applyFilter(), id = self.checkMedianFilter.GetId())

    defringingBoxSizer.Add(self.checkApplyDefringing, flag = wx.ALL, border = 5)
    defringingBoxSizer.Add(self.checkResetAOI, flag = wx.ALL, border = 5)
    defringingBoxSizer.Add(self.checkMedianFilter, flag = wx.ALL, border = 5)
    
    hbox421.Add(hbox42,  flag= wx.ALL, border = 8, row=0, col=0)
    hbox421.Add(defringingBoxSizer, flag = wx.ALL, row = 0 , col = 1)

#        defringingBoxSizer.Add(self.checkSaveAsRef, flag = wx.ALL, border = 5)

  
    imagesBoxSizer.Add(hbox421,flag= wx.CENTER, border=5)
   ##
    atomNum = wx.StaticBox(self.panel, label='# of Atoms')
    atomNumBoxSizer = wx.StaticBoxSizer(atomNum, wx.VERTICAL)
    
    ##
    hbox43 = wx.BoxSizer(wx.HORIZONTAL)
#        atomNumParam = wx.StaticBox(self.panel)
#        atomNumParamBoxSizer = wx.StaticBoxSizer(atomNumParam, wx.HORIZONTAL)
#
    magnif = wx.StaticText(self.panel, label = 'Mag:')
    self.magnif = wx.TextCtrl(self.panel, value= str(self.magnification), size=(30,22))
    self.magnif.Bind(wx.EVT_TEXT, self.setMagnification)
    
    pixelSize= wx.StaticText(self.panel, label = u"\u00B5"+"m/pix:")
    self.pxSize = wx.TextCtrl(self.panel, value= str(self.pixelSize), size=(35,22))
    self.pxSize.Bind(wx.EVT_TEXT, self.setPixelSize)
    
    clebschGordan = wx.StaticText(self.panel, label = "Clebsch")
    self.clebschGordanText = wx.TextCtrl(self.panel, value= str(self.clebschGordan), size=(35,22))
    self.clebschGordanText.Bind(wx.EVT_TEXT, self.setClebschGordan)
    
    atomKind = ['Dy']       # Old thing from BEC 3, we could delete this selection, it used to be ['Na, 'Li']
    self.atomRadioBox = wx.RadioBox(self.panel, choices = atomKind, majorDimension = 1)
    self.atomRadioBox.Bind(wx.EVT_RADIOBOX, self.onAtomRadioClicked)
    
    hbox43.Add(self.atomRadioBox, flag = wx.ALL, border = 5)
    hbox43.Add(magnif, flag = wx.ALL, border = 5)
    hbox43.Add(self.magnif, flag = wx.ALL, border = 5)
    hbox43.Add(pixelSize, flag = wx.ALL, border = 5)
    hbox43.Add(self.pxSize, flag = wx.ALL, border = 5)
    hbox43.Add(clebschGordan, flag = wx.ALL, border = 5)
    hbox43.Add(self.clebschGordanText, flag = wx.ALL, border = 5)  
    
    atomNumBoxSizer.Add(hbox43, flag=wx.ALL|wx.EXPAND)

    ##
    hbox44 = wx.BoxSizer(wx.HORIZONTAL)
    atomNumDisplay = wx.StaticBox(self.panel)
    atomNumDisplayBoxSizer = wx.StaticBoxSizer(atomNumDisplay, wx.HORIZONTAL)

#        bigNcountText = wx.StaticText(self.panel, label='NormNcount:')
#        self.bigNcount = wx.TextCtrl(self.panel,  style=wx.TE_READONLY)
    bigfont = wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
    bigNcountText2 = wx.StaticText(self.panel, label='Norm Ncount: \n (pure integral)')
    self.bigNcount2 = wx.TextCtrl(self.panel,  style=wx.TE_READONLY|wx.TE_CENTRE, size=(100,34))
    bigNcountText3 = wx.StaticText(self.panel, label='Atom #:')
    self.bigNcount3 = wx.TextCtrl(self.panel, style=wx.TE_READONLY|wx.TE_CENTRE, size=(115,34))
    bigNcountText4 = wx.StaticText(self.panel, label = 'Atom #2:')
    self.bigNcount4 = wx.TextCtrl(self.panel, style = wx.TE_READONLY|wx.TE_CENTRE, size = (114, 34))
    self.bigNcount4.Enable(False)
    for (txt, ctrl) in zip([bigNcountText2, bigNcountText3, bigNcountText4], [self.bigNcount2, self.bigNcount3, self.bigNcount4]):
        ctrl.SetFont(bigfont)
        hbox43.Add(txt, flag=wx.ALL, border=5)
        hbox43.Add(ctrl, flag=wx.ALL, border=5)

    imagesBoxSizer.Add(atomNumBoxSizer, flag=wx.ALL| wx.EXPAND, border=5)


    ### DIALS FOR SELECTING AOI SETS
    self.aoiDialBox = wx.StaticBox(self.panel, label = "AOI Controls")
    aoiDialBoxSizer = wx.StaticBoxSizer(self.aoiDialBox, wx.HORIZONTAL)
    hbox15_Primary = wx.BoxSizer(wx.HORIZONTAL)

    # self.toggleAOIButton = wx.Button(self.panel, label = "Moving N1 ROI")
    # self.toggleAOIButton.Bind(wx.EVT_BUTTON, self.toggleActiveAOI)
    # hbox15_Primary.Add(self.toggleAOIButton)

    activateDoubleAOICheck = wx.CheckBox(self.panel, label = "Use two AOI's?")
    activateDoubleAOICheck.Bind(wx.EVT_CHECKBOX, self.activateDoubleAOI)
    hbox15_Primary.Add(activateDoubleAOICheck)

    self.AOIRadioBox = wx.RadioBox(self.panel, choices = ['1', '2'], majorDimension = 0)
    # self.AOIRadioBox.Bind(wx.EVT_RADIOBOX, lambda e: self.toggleAOISelection())
    self.AOIRadioBox.Enable(False)
    hbox15_Primary.Add(self.AOIRadioBox)

    self.panel.Bind(wx.EVT_MIDDLE_DOWN, lambda e: self.toggleAOISelection())

    aoiDialBoxSizer.Add(hbox15_Primary, flag = wx.EXPAND|wx.ALL, border = 5)
    imagesBoxSizer.Add(aoiDialBoxSizer, flag = wx.ALL|wx.EXPAND, border = 5)

    ### PRIMARY AOI
    aoi_Box = wx.StaticBox(self.panel, label = "Manual AOI")
    hbox14_Primary = wx.BoxSizer(wx.HORIZONTAL)
    aoi_BoxSizer = wx.StaticBoxSizer(aoi_Box, wx.HORIZONTAL)
    aoi_PrimaryText = wx.StaticText(self.panel, label = 'Primary AOI: (x,y)->(x,y)')

    hbox14_Primary.Add(aoi_PrimaryText, flag=wx.ALL, border=5)
    self.AOI1_Primary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
    self.AOI2_Primary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
    self.AOI3_Primary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
    self.AOI4_Primary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
    hbox14_Primary.Add(self.AOI1_Primary, flag=wx.ALL, border=2)
    hbox14_Primary.Add(self.AOI2_Primary, flag=wx.ALL, border=2)
    hbox14_Primary.Add(self.AOI3_Primary, flag=wx.ALL, border=2)
    hbox14_Primary.Add(self.AOI4_Primary, flag=wx.ALL, border=2)
    self.AOI1_Primary.Bind(wx.EVT_TEXT, self.settempAOI1)
    self.AOI2_Primary.Bind(wx.EVT_TEXT, self.settempAOI2)
    self.AOI3_Primary.Bind(wx.EVT_TEXT, self.settempAOI3)
    self.AOI4_Primary.Bind(wx.EVT_TEXT, self.settempAOI4)
    aoi_BoxSizer.Add(hbox14_Primary, flag=wx.EXPAND|wx.ALL, border=5)
    
    ### SECONDARY AOI
    #aoi_SecondaryBox = wx.StaticBox(self.panel)
    hbox14_Secondary = wx.BoxSizer(wx.HORIZONTAL)
    #aoi_SecondaryBoxSizer = wx.StaticBoxSizer(aoi_Box, wx.HORIZONTAL)
    aoi_SecondaryText = wx.StaticText(self.panel, label = 'Secondary AOI: (x,y)->(x,y)')
    hbox14_Secondary.Add(aoi_SecondaryText, flag=wx.ALL, border=5)

    self.AOI1_Secondary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
    self.AOI2_Secondary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
    self.AOI3_Secondary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
    self.AOI4_Secondary = wx.TextCtrl(self.panel, value='-1', size=(40,22))
    hbox14_Secondary.Add(self.AOI1_Secondary, flag=wx.ALL, border=2)
    hbox14_Secondary.Add(self.AOI2_Secondary, flag=wx.ALL, border=2)
    hbox14_Secondary.Add(self.AOI3_Secondary, flag=wx.ALL, border=2)
    hbox14_Secondary.Add(self.AOI4_Secondary, flag=wx.ALL, border=2)
    aoi_BoxSizer.Add(hbox14_Secondary, flag=wx.EXPAND|wx.ALL, border=5)
    
    self.checkBoxAutoAOI = wx.CheckBox(self.panel, label=" Auto AOI?")
    self.checkBoxAutoAOI.SetValue(False)
    self.checkBoxAutoAOI.Hide()
    ''' We never know what this is so JL cancelled this function
    aoi_BoxSizer.Add(self.checkBoxAutoAOI, flag=wx.EXPAND|wx.ALL, border=5)
    '''

    self.updateButton = wx.Button(self.panel, label = 'Update pAOI')
    self.updateButton.Bind(wx.EVT_BUTTON, self.typedAOI)
    aoi_BoxSizer.Add(self.updateButton, flag=wx.ALL|wx.EXPAND, border= 5)

    hbox43_Secondary = wx.BoxSizer(wx.HORIZONTAL)
    aoi_BoxSizer.Add(hbox43_Secondary,flag=wx.ALL|wx.EXPAND)

    imagesBoxSizer.Add(aoi_BoxSizer, flag=wx.ALL| wx.EXPAND, border= 5)

            
    #####################
    #### fiting part ####
    #####################
    fittingResultDisplay = wx.StaticBox(self.panel, label = "Fitting results")
    fittingResultDisplaySizer = wx.StaticBoxSizer(fittingResultDisplay, wx.VERTICAL)
    
#        widthPeakStaticBox = wx.StaticBox(self.panel)
#        widthPeakSizer = wx.StaticBoxSizer(widthPeakStaticBox, wx.HORIZONTAL)
#
#        paramStaticBox = wx.StaticBox(self.panel)
#        parameterSettingSizer = wx.StaticBoxSizer(paramStaticBox, wx.HORIZONTAL)
#        tempStaticBox = wx.StaticBox(self.panel)
#        tempSizer = wx.StaticBoxSizer(tempStaticBox, wx.HORIZONTAL)
    '''        
    TOFText = wx.StaticText(self.panel, label = 'TOF (ms): ' )
    self.TOFBox = wx.TextCtrl(self.panel, value = str(self.TOF), size=(40,22))
    self.TOFBox.Bind(wx.EVT_TEXT, self.setTOF)
    
    xTrapFreqText = wx.StaticText(self.panel, label = 'X trap freq.(Hz): ')
    self.xTrapFreqBox = wx.TextCtrl(self.panel, value = str(self.xTrapFreq), size=(40,22))
    self.xTrapFreqBox.Bind(wx.EVT_TEXT, self.setXTrapFreq)
    
    yTrapFreqText = wx.StaticText(self.panel, label = 'Y trap freq.(Hz): ')
    self.yTrapFreqBox = wx.TextCtrl(self.panel, value = str(self.yTrapFreq), size=(40,22))
    self.yTrapFreqBox.Bind(wx.EVT_TEXT, self.setYTrapFreq)

    widthText = wx.StaticText(self.panel, label = "Width (" + u"\u00B5"+ "m):")
    self.widthBox = wx.TextCtrl(self.panel,value = str(1)+",  " + str(1) , style=wx.TE_READONLY|wx.TE_CENTRE, size = (90, 22))
    peakText = wx.StaticText(self.panel, label = 'Peak (arb.): ')
    self.peakBox = wx.TextCtrl(self.panel,value = str(1)+",  " +str(1), style=wx.TE_READONLY|wx.TE_CENTRE, size = (85, 22))
    
    TcText = wx.StaticText(self.panel, label = "(T/Tc, Nc/N) :")
    self.TcBox = wx.TextCtrl(self.panel,value = str(1)+",  " +str(1), style=wx.TE_READONLY|wx.TE_CENTRE, size = (90, 22))
    self.TcBox = wx.TextCtrl(self.panel,value = str(1)+",  " +str(0), style=wx.TE_READONLY|wx.TE_CENTRE, size = (75, 22))
    TFRadiusText = wx.StaticText(self.panel, label = "TF rad. (" + u"\u00B5"+ "m):")
    self.TFRadiusBox = wx.TextCtrl(self.panel,value = str(1)+",  " +str(1), style=wx.TE_READONLY|wx.TE_CENTRE, size = (90, 22))
    self.TFRadiusBox = wx.TextCtrl(self.panel,value = str(1), style=wx.TE_READONLY|wx.TE_CENTRE, size = (55, 22))
    
    TempText = wx.StaticText(self.panel, label = "Temperature (" + u"\u00B5"+"K): ")
    TempText2 = wx.StaticText(self.panel, label = "long time limit (" +u"\u00B5" + "K): ")
    self.tempBox = wx.TextCtrl(self.panel, value = "(" + str(self.temperature[0])+", " +str(self.temperature[1]) + ")", style=wx.TE_READONLY|wx.TE_CENTRE, size = (160, 35))
    self.tempBox2 = wx.TextCtrl(self.panel, value = "(" + str(self.temperature[0])+", " +str(self.temperature[1]) + ")", style=wx.TE_READONLY|wx.TE_CENTRE, size = (160, 35))
    bigfont2 = wx.Font(14, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
    self.tempBox.SetFont(bigfont2)
    self.tempBox2.SetFont(bigfont2)

    # CHANGE THIS LINE TO ADD BACK THE FITTING RESULT DISPLAYER
    #imagesBoxSizer.Add(fittingResultDisplaySizer, flag=wx.ALL| wx.EXPAND, border=5)
    '''

    # final step to add the middle column
    hbox.Add(imagesBoxSizer, 4, wx.ALL|wx.EXPAND)


    vbox2 = wx.BoxSizer(wx.VERTICAL)    # this is the file vertical box
    
    fileBox = wx.StaticBox(self.panel, label = "File")
    fileBoxSizer = wx.StaticBoxSizer(fileBox, wx.VERTICAL)
    self.fileSizeValue = wx.TextCtrl(self.panel, value= "31.6")
    self.fileSizeValue.Hide()
    '''
    ## file Size
    fileSizeUnit = wx.StaticText(self.panel, label = 'MB')
    fileSize = wx.StaticText(self.panel, label = 'File Size')

    #fileSizeBox = wx.StaticBox(self.panel)
    fileSizeBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
    fileSizeBoxSizer.Add(fileSizeUnit, flag=wx.ALL, border=5)
    self.fileSizeValue.Bind(wx.EVT_TEXT, self.setFileSize)
    fileSizeBoxSizer.Add(self.fileSizeValue, flag=wx.ALL, border=5)
    '''
    #fileBoxSizer.Add(fileSizeBoxSizer,  flag=wx.ALL| wx.EXPAND, border = 5)
    
    '''
    ## Database file info
    fileInfoDisplayText = wx.StaticText(self.panel,label='Currently displayed file informations')
    #fileBoxSizer.Add(fileInfoDisplayText, flag=wx.ALL|wx.EXPAND, border=5)
    
    fileInfoImageIDText = wx.StaticText(self.panel, label = "imageID:")
    self.fileInfoImageIDBox = wx.TextCtrl(self.panel, value = "  ", style=wx.TE_READONLY|wx.TE_CENTRE, size = (50, 22))
    fileInfoTimestampText = wx.StaticText(self.panel, label = 'Timestamp:')
    self.fileInfoTimestampBox = wx.TextCtrl(self.panel,value = "  ", style=wx.TE_READONLY|wx.TE_CENTRE, size = (140, 22))
    fileInfoNCountText = wx.StaticText(self.panel, label = 'nCount:')
    self.fileInfoNCountBox = wx.TextCtrl(self.panel,value = "  ", style=wx.TE_READONLY|wx.TE_CENTRE, size = (140, 22))
    vbox11 = wx.BoxSizer(wx.VERTICAL)
    hbox151 = wx.BoxSizer(wx.HORIZONTAL)
    hbox151.Add(fileInfoImageIDText, flag = wx.ALL, border = 5)
    hbox151.Add(self.fileInfoImageIDBox, flag = wx.ALL, border = 5)
    hbox152 = wx.BoxSizer(wx.HORIZONTAL)
    hbox152.Add(fileInfoTimestampText, flag = wx.ALL, border = 5)
    hbox152.Add(self.fileInfoTimestampBox, flag = wx.ALL, border = 5)
    hbox153 = wx.BoxSizer(wx.HORIZONTAL)
    hbox153.Add(fileInfoNCountText, flag = wx.ALL, border = 5)
    hbox153.Add(self.fileInfoNCountBox, flag = wx.ALL, border = 5)
    vbox11.Add(hbox151, 0, wx.ALL|wx.EXPAND, 5)
    vbox11.Add(hbox152, 0, wx.ALL|wx.EXPAND, 5)
    vbox11.Add(hbox153, 0, wx.ALL|wx.EXPAND, 5)
    

    
    SpeciesTableSizer = wx.BoxSizer(wx.HORIZONTAL)
    infoDBGrid = wx.grid.Grid(self.panel, -1, size=(300,150))
    infoDBGrid.CreateGrid(5,2)
    infoDBGrid.SetColLabelValue(0, 'Variable')
    infoDBGrid.SetColLabelValue(1, 'DB Value')
    for i in range(5):
        infoDBGrid.SetReadOnly(i,0,True)
        infoDBGrid.SetReadOnly(i,1,True)
    infoDBGrid.SetCellValue(0,0,"imageID")
    infoDBGrid.SetCellValue(1,0,"runID")
    infoDBGrid.SetCellValue(2,0,"sequenceID")
    infoDBGrid.SetCellValue(3,0,"Timestamp")
    infoDBGrid.SetCellValue(4,0,"nCount")

    infoDBGrid.SetRowLabelSize(0)
    vbox11.Add(infoDBGrid, wx.ALIGN_CENTER | wx.ALL,0 )
    '''
    #fileBoxSizer.Add(vbox11, flag=wx.ALL| wx.EXPAND, border=0)

    
    hbox154 = wx.BoxSizer(wx.HORIZONTAL)
    '''
    self.updateAnalysisButton = wx.Button(self.panel, label = 'Update analysis')
    self.updateAnalysisButton.Bind(wx.EVT_BUTTON, self.updateAnalysisDB)
    hbox154.Add(self.updateAnalysisButton, flag=wx.ALL, border=5)
    '''
    #fileBoxSizer.Add(hbox154, flag=wx.ALL| wx.EXPAND, border=0)
    
    ## image file path
    pathText = wx.StaticText(self.panel,label='Image Folder Path')
    fileBoxSizer.Add(pathText, flag=wx.ALL|wx.EXPAND, border=5)
    
    if not self.checkLocalFiles:
        self.today = datetime.date.today()
        self.path = str(getLastImageID())
#        self.setDefringingRefPath()
                    
    self.imageFolderPath = wx.TextCtrl(self.panel, value = self.path)
      
    hbox13 = wx.BoxSizer(wx.HORIZONTAL)
    hbox13.Add(self.imageFolderPath, 1, flag=wx.ALL| wx.EXPAND , border=5)
    self.choosePathButton = wx.Button(self.panel, label = 'Choose Path')
    self.choosePathButton.Bind(wx.EVT_BUTTON, self.choosePath)
    hbox13.Add(self.choosePathButton, flag=wx.ALL, border=5)
    fileBoxSizer.Add(hbox13, flag=wx.ALL| wx.EXPAND, border=0)

    nameText = wx.StaticText(self.panel, label='Image File Name')
    fileBoxSizer.Add(nameText, flag=wx.ALL, border=5)

    hbox12 = wx.BoxSizer(wx.HORIZONTAL)
    self.imageIDText = wx.TextCtrl(self.panel)
    hbox12.Add(self.imageIDText, 1, flag=wx.ALL| wx.EXPAND , border=5)
    self.chooseFileButton = wx.Button(self.panel, label = 'Choose File')
    self.chooseFileButton.Bind(wx.EVT_BUTTON, self.chooseImgfromFile)
    hbox12.Add(self.chooseFileButton, flag=wx.ALL, border=5)
    fileBoxSizer.Add(hbox12,flag=wx.ALL| wx.EXPAND, border=0)

    vbox2.Add(fileBoxSizer,flag=wx.ALL| wx.EXPAND, border = 5)
    

    FitUpdateBox = wx.StaticBox(self.panel, label = "Fit Result")
    FitUpdateBoxSizer = wx.StaticBoxSizer(FitUpdateBox, wx.VERTICAL)

    self.FitResultText = wx.TextCtrl(self.panel, value = "REMEMBER to set mag,pixel\n , camera and \n click Auto Read!", style=wx.TE_MULTILINE | wx.TE_READONLY, size = (420, 300))

    FitUpdateBoxSizer.Add(self.FitResultText,flag=wx.ALL, border=5)
    vbox2.Add(FitUpdateBoxSizer,flag=wx.ALL| wx.EXPAND, border = 5)

    # image zoom
    
    imageZoomBox = wx.StaticBox(self.panel, label = "Image zoom")
    imageZoomBoxSizer = wx.StaticBoxSizer(imageZoomBox, wx.VERTICAL)
    
    self.figureZoom = Figure(figsize = (4,4))
    self.axesZoom = self.figureZoom.add_subplot()
    self.axesZoom.set_title('Zoomed Image', fontsize=12)
    for label in (self.axesZoom.get_xticklabels() + self.axesZoom.get_yticklabels()):
        label.set_fontsize(10)
    
    self.canvasZoom = FigureCanvas(self.panel, -1, self.figureZoom)
    imageZoomBoxSizer.Add(self.canvasZoom, flag=wx.ALL|wx.EXPAND, border=5)
    self.canvasZoom.mpl_connect('motion_notify_event', self.showImgValueZoom)
    hboxZoomInput = wx.BoxSizer(wx.HORIZONTAL)
    xZoomCenterText = wx.StaticText(self.panel, label='X center:')
    self.xZoomCenterBox = wx.TextCtrl(self.panel, value = str(self.xZoomCenter), style=wx.TE_CENTRE, size = (50, 22))
    self.xZoomCenterBox.Bind(wx.EVT_TEXT, self.setZoomCenterX)
    yZoomCenterText = wx.StaticText(self.panel, label='Y center:')
    self.yZoomCenterBox = wx.TextCtrl(self.panel, value = str(self.yZoomCenter), style=wx.TE_CENTRE, size = (50, 22))
    self.yZoomCenterBox.Bind(wx.EVT_TEXT, self.setZoomCenterY)
    zoomWidthText = wx.StaticText(self.panel, label='Width:')
    self.zoomWidthBox = wx.TextCtrl(self.panel, value = str(self.zoomWidth), style=wx.TE_CENTRE, size = (50, 22))
    self.zoomWidthBox.Bind(wx.EVT_TEXT, self.setZoomWidth)
    
    hboxZoomInput.Add(xZoomCenterText, flag=wx.ALL, border=5)
    hboxZoomInput.Add(self.xZoomCenterBox, flag=wx.ALL, border=5)
    hboxZoomInput.Add(yZoomCenterText, flag=wx.ALL, border=5)
    hboxZoomInput.Add(self.yZoomCenterBox, flag=wx.ALL, border=5)
    hboxZoomInput.Add(zoomWidthText, flag=wx.ALL, border=5)
    hboxZoomInput.Add(self.zoomWidthBox, flag=wx.ALL, border=5)
    
    imageZoomBoxSizer.Add(hboxZoomInput, flag=wx.TE_CENTRE| wx.EXPAND)

    
    hboxZoomOutput = wx.BoxSizer(wx.HORIZONTAL)
    stX_Zoom = wx.StaticText(self.panel, label='X:')
    self.cursorX_Zoom = wx.TextCtrl(self.panel,  style=wx.TE_READONLY|wx.TE_CENTRE, size = (50, 22))
    stY_Zoom = wx.StaticText(self.panel, label='Y:')
    self.cursorY_Zoom = wx.TextCtrl(self.panel, style=wx.TE_READONLY|wx.TE_CENTRE,  size = (50, 22))
    stZ_Zoom = wx.StaticText(self.panel, label='Value:')
    self.cursorZ_Zoom = wx.TextCtrl(self.panel, style=wx.TE_READONLY|wx.TE_CENTRE,  size = (80, 22))
    self.cursorX_Zoom.SetFont(boldFont)
    self.cursorY_Zoom.SetFont(boldFont)
    self.cursorZ_Zoom.SetFont(boldFont)
    hboxZoomOutput.Add(stX_Zoom, flag=wx.ALL, border=5)
    hboxZoomOutput.Add(self.cursorX_Zoom, flag=wx.ALL, border=5)
    hboxZoomOutput.Add(stY_Zoom, flag=wx.ALL, border=5)
    hboxZoomOutput.Add(self.cursorY_Zoom, flag=wx.ALL, border=5)
    hboxZoomOutput.Add(stZ_Zoom, flag=wx.ALL, border=5)
    hboxZoomOutput.Add(self.cursorZ_Zoom, flag=wx.ALL, border=5)
    
    imageZoomBoxSizer.Add(hboxZoomOutput, flag=wx.TE_CENTRE| wx.EXPAND)
    vbox2.Add(imageZoomBoxSizer,flag=wx.ALL|wx.TE_CENTRE| wx.EXPAND, border = 5)
    
    
    hbox.Add(vbox2, 2, wx.ALL|wx.EXPAND, 5)  # 2 here means that the relative width of the box will be 2


    self.panel.SetSizer(hbox)

def startCamera_trigger(self, event):
    self.camera.cameraDevice.shouldCameraRun = True
    self.cameraThread = threading.Thread(target = self.camera.cameraDevice.run_single_camera_trigger) #, args=[i])
    self.cameraThread.start()

def endCamera_trigger(self, event):
    self.camera.cameraDevice.shouldCameraRun = False # that will change the value of the loop to acquire images
                                                    # and eventually end the acquisition process in a few seconds depending on the wait time for trigger
    self.cameraThread.join()    # this waits for the acquisition process to end

def onAtomRadioClicked(self,e):
    self.atom = self.atomRadioBox.GetStringSelection()
    print(self.atom)
    self.setAtomNumber()
    self.updateFittingResults()
    
    snippetPath = "C:\\shared_data\\AndorImg\\SnippetLookHere"  + self.atom + ".txt"
    self.snippetTextBox.SetLabel(snippetPath)
    
    print("new snippet path -----> " + self.snippetPath)

def updateFittingResult(self):
    self.resultstring =  f"In-situ true pixel size ={self.pixelToDistance*1e6:.2f} um \n\n"
    for AAOI in self.AOIList:
        if AAOI==self.primaryAOI:
            self.resultstring += "AOI1 Fitted parameters: \n"
        else:
            self.resultstring += "AOI2 Fitted parameters: \n"
        self.resultstring += "1D X-fit Success? "+str(AAOI.isXFitSuccessful)
        self.resultstring += ". 1D Y-fit Success? "+str(AAOI.isYFitSuccessful)
        self.resultstring += ". 2D Fit Success? " + str(AAOI.isFit2DSuc) +"\n"
        self.resultstring += f"Atom number old method: {AAOI.atomNumber:.3e} \n"
        self.resultstring += f"Atom number new method: {AAOI.modifiedAtomNumber:.3e} \n"
        self.resultstring += f"1D fit x_width: {AAOI.x_width:.1f} pixels"
        self.resultstring += f". y_width: {AAOI.y_width:.1f} pixels\n"
        self.resultstring += f"2D fit width: {AAOI.x_width2D:.1f} pixels, {AAOI.y_width2D:.1f} pixels\n\n" 
    self.FitResultText.SetValue(self.resultstring)

def TOFcalc(self, event):
    calculator_frame = TOFCalculatorFrame(None, "TOF Calculator",self.mass,self.pixelToDistance)
    calculator_frame.Show()

class TOFCalculatorFrame(wx.Frame):
    def __init__(self, parent, title,mass,pixelToDistance):
        super(TOFCalculatorFrame, self).__init__(parent, title=title, size=(300, 200))
        self.mass = mass
        self.pixelToDistance =pixelToDistance

        self.panel = wx.Panel(self)
        self.value1_label = wx.StaticText(self.panel, label="TOF time/ms:", pos=(10, 10))
        self.value1_text = wx.TextCtrl(self.panel, pos=(140, 10))
        
        self.value2_label = wx.StaticText(self.panel, label="Fitted RMS size/pxls:", pos=(10, 40))
        self.value2_text = wx.TextCtrl(self.panel, pos=(140, 40))

        # Create a button to perform the calculation
        self.calculate_button = wx.Button(self.panel, label="Calculate", pos=(100, 70))
        self.calculate_button.Bind(wx.EVT_BUTTON, self.calculate_area)

        # Create a result text control
        self.result_label = wx.StaticText(self.panel, label="Result in uK:", pos=(10, 100))
        self.result_text = wx.TextCtrl(self.panel, pos=(80, 100), size=(150, -1), style=wx.TE_READONLY)

    def calculate_area(self, event):
        try:
            t = float(self.value1_text.GetValue())
            sigma = float(self.value2_text.GetValue())*self.pixelToDistance
            kB = 1.38065e-23
            result = round(sigma**2/(t*1e-3)**2*self.mass/kB *1e6,3)  # Perform the calculation
            self.result_text.SetValue(str(result))
        except ValueError:
            wx.MessageBox("Invalid input. Please enter valid numeric values.", "Error", wx.OK | wx.ICON_ERROR)
