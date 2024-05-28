import numpy as np
import wx

class CalculatorFrame(wx.Frame):
    def __init__(self, parent, title):
        super(CalculatorFrame, self).__init__(parent, title=title, size=(300, 200))

        panel = wx.Panel(self)
        button = wx.Button(panel, label="Open Calculator", pos=(100, 50))

        button.Bind(wx.EVT_BUTTON, self.on_button_click)

    def on_button_click(self, event):
        calculator_frame = AreaCalculatorFrame(None, "Area Calculator")
        calculator_frame.Show()

class AreaCalculatorFrame(wx.Frame):
    def __init__(self, parent, title):
        super(AreaCalculatorFrame, self).__init__(parent, title=title, size=(300, 200))

        # Add your area calculator widgets and logic here

if __name__ == "__main__":
    app = wx.App(False)
    frame = CalculatorFrame(None, "GUI with Area Calculator Button")
    frame.Show()
    app.MainLoop()
