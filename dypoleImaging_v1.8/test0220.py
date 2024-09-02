import wx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class PlotDialog(wx.Dialog):
    def __init__(self, parent, title, data):
        wx.Dialog.__init__(self, parent, title=title)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self, -1, self.figure)

        # Create the plot
        self.ax.imshow(data)
        self.ax.set_title("Your Plot Title")
        self.figure.tight_layout()

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
        self.Fit()

class MyFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MyFrame, self).__init__(*args, **kw)

        # Initialize plot dialog reference
        self.plot_dialog = None

        # Example button to show plot
        btn = wx.Button(self, label="Show Plot")
        btn.Bind(wx.EVT_BUTTON, self.on_show_plot)

    def on_show_plot(self, event):
        # Data for plotting
        data = [[0,1],[1,2]]

        # Close previous dialog if open
        if self.plot_dialog:
            self.plot_dialog.Destroy()

        # Create new plot dialog
        self.plot_dialog = PlotDialog(self, "Plot Window", data)
        self.plot_dialog.Show()

# Run the application
app = wx.App(False)
frame = MyFrame(None, title='Your Application')
frame.Show()
app.MainLoop()