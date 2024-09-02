# DypoleImaging
The python imaging system in Dypole lab @MIT

The imaging system was first developed by Hyungmok Son. Then Pierre make major changes to fit it into Dypole lab @MIT.

08/2023
In order to make further changes and do quicker and more sophisticated analyze, we start to update different versions here on github. 


09/2024:

v1.8 is a relatively stable version. 
1. We changed the wxpython function for presenting "imaging process" zone under the 'images' zone. The old function is something flexible UI, but unstable.
2. Previously we do 2D fit with uncorrected pictures (with help of dashed AOI), but do 1D fit with corrected pictures. Now we fixed it.
3. We created a helpfunction to keep all the useful fast analyze function.
4. We use wxpython webview to vendor Fit2Dshow. (Does not work for py36)
5. We are able to rotate the picture.
6. Something we did long time ago, which I forgot.
7. Maybe, in order to trigger FLIR, lots of lines need to be uncommented. But now we barely use FLIR.
8. We wrote a 'save to local' function. Look into autorun function and functions therein.
