import wx
from matplotlib.figure import Figure
import numpy as np
import threading
from matplotlib import gridspec
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import matplotlib.pyplot as plt
import datetime
from scipy.special import jv

class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MainFrame, self).__init__(*args, **kw)

        # Set up the main panel and sizer
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Create buttons
        btn_fermitemp = wx.Button(panel, label="Fermi Temp Calculator")
        btn_KD = wx.Button(panel, label="KD Calculator")

        # Bind buttons to events
        btn_fermitemp.Bind(wx.EVT_BUTTON, self.on_open_FermiTemp_calculator)
        btn_KD.Bind(wx.EVT_BUTTON, self.on_open_KD_calculator)

        # Add buttons to the sizer
        sizer.Add(btn_fermitemp, 0, wx.ALL | wx.CENTER, 5)
        sizer.Add(btn_KD, 0, wx.ALL | wx.CENTER, 5)

        panel.SetSizer(sizer)

        # Set frame properties
        self.SetTitle("Dypole Help Function v1.8")
        self.SetSize((400, 300))  # Set the size of the main window
        self.Centre()

    def on_open_FermiTemp_calculator(self, event):
        area_calculator = FermiTempCalculatorFrame(None, title="Fermi Temp Calculator")
        area_calculator.Show()

    def on_open_KD_calculator(self, event):
        volume_calculator = KaDiCalculatorFrame(None, title="KD Calculator")
        volume_calculator.Show()

class FermiTempCalculatorFrame(wx.Frame):
    def __init__(self, parent, title):
        super(FermiTempCalculatorFrame, self).__init__(parent, title=title, size=(350, 250))

        self.panel = wx.Panel(self)
        self.value1_label = wx.StaticText(self.panel, label="Mean trap frequency/Hz: 2pi*", pos=(10, 10))
        self.value1_text = wx.TextCtrl(self.panel, pos=(180, 10))
        
        self.value2_label = wx.StaticText(self.panel, label="Atom number/10^4:", pos=(10, 40))
        self.value2_text = wx.TextCtrl(self.panel, pos=(140, 40))

        # Create a button to perform the calculation
        self.calculate_button = wx.Button(self.panel, label="Calculate", pos=(100, 70))
        self.calculate_button.Bind(wx.EVT_BUTTON, self.calculate_tf)

        # Create a result text control
        self.result1_label = wx.StaticText(self.panel, label="T_Fermi in uK:", pos=(10, 100))
        self.result1_text = wx.TextCtrl(self.panel, pos=(100, 100), size=(150, -1), style=wx.TE_READONLY)
        self.result2_label = wx.StaticText(self.panel, label="n_peak (/um^3):", pos=(10, 130))
        self.result2_text = wx.TextCtrl(self.panel, pos=(100, 130), size=(150, -1), style=wx.TE_READONLY)
        self.result3_label = wx.StaticText(self.panel, label="n_ave (/um^3):", pos=(10, 160))
        self.result3_text = wx.TextCtrl(self.panel, pos=(100, 160), size=(150, -1), style=wx.TE_READONLY)

    def calculate_tf(self, event):
        try:
            nu = float(self.value1_text.GetValue())
            N = float(self.value2_text.GetValue())*1e4
            kB = 1.38065e-23
            h = 6.62607e-34
            m = 160.93 * 1.67262192e-27
            EF = h*nu*(6*N)**(1/3)
            radius_fermi = np.sqrt(2*EF/m/(2*np.pi*nu)**2)
            result1 = round(h*nu*(6*N)**(1/3)/kB *1e6,3)  # Perform the calculation
            result2 = round(N*8/np.pi**2/radius_fermi**3*1e-18, 3)
            result3 = round(N*4096/np.pi**3/315/radius_fermi**3*1e-18, 3)
            self.result1_text.SetValue(str(result1))
            self.result2_text.SetValue(str(result2))
            self.result3_text.SetValue(str(result3))
        except ValueError:
            wx.MessageBox("Invalid input. Please enter valid numeric values.", "Error", wx.OK | wx.ICON_ERROR)


class KaDiCalculatorFrame(wx.Frame):
    def __init__(self, parent, title):
        super(KaDiCalculatorFrame, self).__init__(parent, title=title, size=(350, 350))

        self.panel = wx.Panel(self)

        self.info_label = wx.StaticText(self.panel, label=" Calculate +1 or -1 order fraction. \n Ref: Bryce Gadway et, al. 2009 OE. Need: "+u"\u03B1"+u"\u03B2"+" <<1", pos=(10, 10))

        self.value1_label = wx.StaticText(self.panel, label="lattice wavelength / nm: ", pos=(10, 50))
        self.value1_text = wx.TextCtrl(self.panel, pos=(180, 50))
        self.value1_text.SetValue(str(1064))
        
        self.value2_label = wx.StaticText(self.panel, label="lattice depth / Er:", pos=(10, 90))
        self.value2_text = wx.TextCtrl(self.panel, pos=(140, 90))

        self.value3_label = wx.StaticText(self.panel, label="pulse duration / us:", pos=(10, 120))
        self.value3_text = wx.TextCtrl(self.panel, pos=(140, 120))

        # Create a button to perform the calculation
        self.calculate_button = wx.Button(self.panel, label="Calculate", pos=(100, 150))
        self.calculate_button.Bind(wx.EVT_BUTTON, self.calculate_KD)

        # Create a result text control
        self.result1_label = wx.StaticText(self.panel, label="Lattice Er:", pos=(10, 180))
        self.result1_text = wx.TextCtrl(self.panel, pos=(110, 180), size=(150, -1), style=wx.TE_READONLY)
        self.result2_label = wx.StaticText(self.panel, label=u"\u03B1", pos=(10, 220))
        self.result2_text = wx.TextCtrl(self.panel, pos=(110, 220), size=(150, -1), style=wx.TE_READONLY)
        self.result3_label = wx.StaticText(self.panel, label=u"\u03B2", pos=(10, 250))
        self.result3_text = wx.TextCtrl(self.panel, pos=(110, 250), size=(150, -1), style=wx.TE_READONLY)
        self.result4_label = wx.StaticText(self.panel, label="P1=J_1(beta/2)^2=", pos=(10, 280))
        self.result4_text = wx.TextCtrl(self.panel, pos=(110, 280), size=(150, -1), style=wx.TE_READONLY)

    def calculate_KD(self, event):
        try:
            wavelength = float(self.value1_text.GetValue())*1e-9;
            V0 = float(self.value2_text.GetValue());
            tau = float(self.value3_text.GetValue())*1e-6;
            kB = 1.38065e-23
            h = 6.62607e-34
            hbar = h/(2*np.pi)
            m = 160.93 * 1.67262192e-27

            Er = h**2/(2*m*wavelength**2);
            alpha = 4* Er * tau / hbar
            beta = V0 * Er * tau / hbar
            P1 = jv(1, beta/2)**2

            result1 = round(Er/h, -1)  # Perform the calculation
            result2 = round(alpha, 2)
            result3 = round(beta, 2)
            result4 = round(P1, 3)
            self.result1_text.SetValue(str(result1))
            self.result2_text.SetValue(str(result2))
            self.result3_text.SetValue(str(result3))
            self.result4_text.SetValue(str(result4))
        except ValueError:
            wx.MessageBox("Invalid input. Please enter valid numeric values.", "Error", wx.OK | wx.ICON_ERROR)


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame(None, wx.ID_ANY, "")
    frame.Show()
    app.MainLoop()