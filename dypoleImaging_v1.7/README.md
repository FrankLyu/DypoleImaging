# Update 1.7 (2024-06) 
Add back the ability to rotate the whole picture and primary ROI.

# install dypoleimagingv1.7 on new PC. Something to notice when you first run the software on your PC:

1. Some packages like skimage has another real library name. follow the instruction in cmd.
2. Package clr is not called clr. Don't install it. If you already installed it, uninstall. Install pythonnet instead.
3. Pyspin is a package from flir company. Google FLIR pyspin, log in their system and download python .whl file. Download the .whl file into your python. In the new PC, we are using python3.12. So there is not available pyspin yet. We commented all the FLIR sentences.
4. In InitUI_.py file, there is a rcs box. Don't use rcs.column box, which may give errors. Instead, I went back to normal static box.
5. In the imagezoombox section, three wx.flag are not working well. They show do not panic. So I just changed the 3 flags to be 0.

If you follow the instructions here, you should be able to download the required packages and run the software on a new PC in 20 minutes. The next step, is to establish a database and start communicate. Saving the files in a local address is also fine though.

# Update 1.6 (2024-05)
Add fermionic fit, fit2Dshow and Gaussian Tail fit

Fixed some small problems (of course)

# ImageAnalyze
ImageAnalyze software (since Oct. 2016)

Requirements:
- Python 3.6(.12)
- wxPython (4.0.4)
- pySpin (FLIR Spinnaker wrapper for Python)

On Ubuntu:
- Install the Python clr wrapper by doing `pip install -U git+https://github.com/pythonnet/pythonnet`
