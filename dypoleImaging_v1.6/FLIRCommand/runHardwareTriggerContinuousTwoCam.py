# coding=utf-8
# =============================================================================
# Copyright (c) 2001-2019 FLIR Systems, Inc. All Rights Reserved.
#
# This software is the confidential and proprietary information of FLIR
# Integrated Imaging Solutions, Inc. ("Confidential Information"). You
# shall not disclose such Confidential Information and shall use it only in
# accordance with the terms of the license agreement you entered into
# with FLIR Integrated Imaging Solutions, Inc. (FLIR).
#
# FLIR MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
# SOFTWARE, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT. FLIR SHALL NOT BE LIABLE FOR ANY DAMAGES
# SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
# THIS SOFTWARE OR ITS DERIVATIVES.
# =============================================================================
#
#  Trigger_QuickSpin.py shows how to capture images with the
#  trigger using the QuickSpin API. QuickSpin is a subset of the Spinnaker
#  library that allows for simpler node access and control.
#
#  This example demonstrates how to prepare, execute, and clean up the camera
#  in regards to using both software and hardware triggers. Retrieving and
#  setting node values using QuickSpin is the only portion of the example
#  that differs from Trigger.
#
#  A much wider range of topics is covered in the full Spinnaker examples than
#  in the QuickSpin ones. There are only enough QuickSpin examples to
#  demonstrate node access and to get started with the API; please see full
#  Spinnaker examples for further or specific knowledge on a topic.

import PySpin
import sys
import time

NUM_IMAGES = 3  # number of images to grab
#desired_exposure_time = 1000.0  # in micro seconds
desired_exposure_time = 10000.0  # in micro seconds

class TriggerType:
    SOFTWARE = 1
    HARDWARE = 2

class SerialNumberCameraPosition:  # this is the serial number of the horizontal and vertical camera
    VERTICAL = "18575505"
    HORIZONTAL = "19287377"
    TEST = "20397379"

#CHOSEN_TRIGGER = TriggerType.SOFTWARE
CHOSEN_TRIGGER = TriggerType.HARDWARE

# class FLIRCamera(PySpin.PySpin.CameraPtr):
#     def __init__(self, cameraPosition):
#         super(FLIRCamera, self).__init__()
class FLIRCamera():
    def __init__(self, cameraPosition):
        if cameraPosition == "VERTICAL":
            self.serialNumber = SerialNumberCameraPosition.VERTICAL
        elif cameraPosition == "HORIZONTAL":
            self.serialNumber = SerialNumberCameraPosition.HORIZONTAL
        elif cameraPosition == "TEST":
            self.serialNumber = SerialNumberCameraPosition.TEST
        else:
            raise Exception("No cameraPosition specified")
        self.cam = None
        self.system = None
        self.initiateCameraAndSystem()
        self.shouldCameraRun = True
        self.shouldCameraRun_fluorescence = False
        self.xdata = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        
    def initiateCameraAndSystem(self): # initiate the correct camera pointer
    # Retrieve singleton reference to system object
        self.system = PySpin.System.GetInstance()
    # Get current library version
        version = self.system.GetLibraryVersion()
        print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))
    # Retrieve list of cameras from the system
        cam_list = self.system.GetCameras()
        num_cameras = cam_list.GetSize()
        print('Number of cameras detected: %d' % num_cameras)
        # Finish if there are no cameras
        if num_cameras == 0:
            # Clear camera list before releasing system
            cam_list.Clear()
            # Release system instance
            self.system.ReleaseInstance()
            print('Not enough cameras!')
            #input('Done! Press Enter to exit...')
            self.cam = None
            self.system = None
            return
        for i, runningCam in enumerate(cam_list):
            device_serial_number = runningCam.TLDevice.DeviceSerialNumber.GetValue()
            if device_serial_number == self.serialNumber:
                self.cam = runningCam
                try:
                    self.cam.EndAcquisition()   # I have the impression it prevents from rising an error if an acquisition got aborted before
                except:
                    pass
        if str(type(self.cam)) != "<class 'PySpin.PySpin.CameraPtr'>":
            raise Exception("No camera found")
        del runningCam
        # Clear camera list before releasing system
        cam_list.Clear()
    
    
    def configure_trigger(self):
        """
        This function configures the camera to use a trigger. First, trigger mode is
        ensured to be off in order to select the trigger source. Trigger mode is
        then enabled, which has the camera capture only a single image upon the
        execution of the chosen trigger.
    
         :param cam: Camera to configure trigger for.
         :type cam: CameraPtr
         :return: True if successful, False otherwise.
         :rtype: bool
        """
    
        print('*** CONFIGURING TRIGGER ***\n')
    
        print('Note that if the application / user software triggers faster than frame time, the trigger may be dropped / skipped by the camera.\n')
        print('If several frames are needed per trigger, a more reliable alternative for such case, is to use the multi-frame mode.\n\n')
    
        if CHOSEN_TRIGGER == TriggerType.SOFTWARE:
            print('Software trigger chosen...')
        elif CHOSEN_TRIGGER == TriggerType.HARDWARE:
            print('Hardware trigger chose...')
    
        try:
            result = True
    
            # Ensure trigger mode off
            # The trigger must be disabled in order to configure whether the source
            # is software or hardware.
            if self.cam.TriggerMode.GetAccessMode() != PySpin.RW:
                print('Unable to disable trigger mode (node retrieval). Aborting...')
                return False
    
            self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
    
            print('Trigger mode disabled...')
            
            # Set TriggerSelector to FrameStart
            # For this example, the trigger selector should be set to frame start.
            # This is the default for most cameras.
            if self.cam.TriggerSelector.GetAccessMode() != PySpin.RW:
                print('Unable to get trigger selector (node retrieval). Aborting...')
                return False
                
            self.cam.TriggerSource.SetValue(PySpin.TriggerSelector_FrameStart)
    
            print('Trigger selector set to frame start...')
            
            # Select trigger source
            # The trigger source must be set to hardware or software while trigger
    		# mode is off.
            if self.cam.TriggerSource.GetAccessMode() != PySpin.RW:
                print('Unable to get trigger source (node retrieval). Aborting...')
                return False
    
            if CHOSEN_TRIGGER == TriggerType.SOFTWARE:
                self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Software)
                print('Trigger source set to software...')
            elif CHOSEN_TRIGGER == TriggerType.HARDWARE:
                self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Line0)
                print('Trigger source set to hardware...')
    
            # Turn trigger mode on
            # Once the appropriate trigger source has been set, turn trigger mode
            # on in order to retrieve images using the trigger.
            self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
            print('Trigger mode turned back on...')
    
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False
    
        return result
    
    
    def grab_next_image_by_trigger(self):
        """
        This function acquires an image by executing the trigger node.
    
        :param cam: Camera to acquire images from.
        :type cam: CameraPtr
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        try:
            result = True
            # Use trigger to capture image
            # The software trigger only feigns being executed by the Enter key;
            # what might not be immediately apparent is that there is not a
            # continuous stream of images being captured; in other examples that
            # acquire images, the camera captures a continuous stream of images.
            # When an image is retrieved, it is plucked from the stream.
    
            if CHOSEN_TRIGGER == TriggerType.SOFTWARE:
                # Get user input
                input('Press the Enter key to initiate software trigger.')
    
                # Execute software trigger
                if self.cam.TriggerSoftware.GetAccessMode() != PySpin.WO:
                    print('Unable to execute trigger. Aborting...')
                    return False
    
                self.cam.TriggerSoftware.Execute()
    
                # TODO: Blackfly and Flea3 GEV cameras need 2 second delay after software trigger
    
            elif CHOSEN_TRIGGER == TriggerType.HARDWARE:
                print('Use the hardware to trigger image acquisition.')
    
    
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False
    
        return result
    
    
    def acquire_images_trigger(self):
        """
        This function acquires and saves 3 images from a device.
        Please see Acquisition example for more in-depth comments on acquiring images.
    
        :param cam: Camera to acquire images from.
        :type cam: CameraPtr
        :return: True if successful, False otherwise.
        :rtype: bool
        """
    
        print('*** IMAGE ACQUISITION ***\n')
        try:
            result = True
    
            # Set acquisition mode to continuous
            if self.cam.AcquisitionMode.GetAccessMode() != PySpin.RW:
                print('Unable to set acquisition mode to continuous. Aborting...')
                return False
    
            self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
            print('Acquisition mode set to continuous...')
    
            #  Begin acquiring images
            self.cam.BeginAcquisition()
    
            print('Acquiring images...')
    
            # Get device serial number for filename
            device_serial_number = ''
            if self.cam.TLDevice.DeviceSerialNumber.GetAccessMode() == PySpin.RO:
                device_serial_number = self.cam.TLDevice.DeviceSerialNumber.GetValue()
    
                print('Device serial number retrieved as %s...' % device_serial_number)
            
            while self.shouldCameraRun:
                print("Begin new sequence acquisition")
                # Retrieve, convert, and save images
                for i in range(NUM_IMAGES):
                    try:
        
                        #  Retrieve the next image from the trigger
                        #result &= self.grab_next_image_by_trigger()
                        #time.sleep(5)
                        #  Retrieve next received image
                        
                        while self.shouldCameraRun:
                            #  Retrieve the next image from the trigger
                            result &= self.grab_next_image_by_trigger()
                            try:
                                image_result = self.cam.GetNextImage(1000) # time in millisecond it will wait for the buffer to fill (so basically when
                                                                        # at the latest can the trigger pulse arrive
                                                                        # this time will be the reaction time of the camera
                                print("image received")
                                                            #  Ensure image completion
                                if image_result.IsIncomplete():
                                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
                
                                else:
                
                                    #  Print image information
                                    width = image_result.GetWidth()
                                    height = image_result.GetHeight()
                                    print('Grabbed Image %d, width = %d, height = %d' % (i, width, height))
                
                                    #  Convert image to mono 8
                                    #image_converted = image_result.Convert(PySpin.PixelFormat_Mono16, PySpin.HQ_LINEAR)
                                    #image_converted = image_result.Convert(PySpin.PixelFormat_Mono12p, PySpin.HQ_LINEAR)
                                    #image_converted = image_result.Convert(PySpin.PixelFormat_Mono12Packed, PySpin.HQ_LINEAR)
                                    image_converted = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)
                                    print(image_converted)
                                    # Create a unique filename
                                    if device_serial_number:
                                        filename = 'FLIRCommand/Trigger-%s-%d.tif' % (device_serial_number, i)
                                    else:  # if serial number is empty
                                        filename = 'FLIRCommand/Trigger-%d.tif' % i
                
                                    # Save image
                                    image_type = PySpin.TIFFOption()
                                    image_type.compression = 1 # This set to None, otherwise it is LZW (7)
                                    image_converted.Save(filename, image_type)
                
                                    print('Image saved at %s\n' % filename)
                
                                    #  Release image
                                    image_result.Release()
            
                                break
                            except PySpin.SpinnakerException as ex:
                                print("Next in loop at " + str(time.time()))
                                if ex.errorcode == -1011: # This is the error when no triggerr pulse has been sent
                                    pass
                                else:
                                    raise ex

                    except PySpin.SpinnakerException as ex:
                        print('Error: %s' % ex)
                        return False
                    
                    except KeyboardInterrupt:
                        # End acquisition
                        self.cam.EndAcquisition()
                        print("Keyboard interruption: ending program")
                        return False
            # End acquisition
            self.cam.EndAcquisition()
    
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False
    
        return result
    
    
    def reset_trigger(self):
        """
        This function returns the camera to a normal state by turning off trigger mode.
    
        :param cam: Camera to acquire images from.
        :type cam: CameraPtr
        :returns: True if successful, False otherwise.
        :rtype: bool
        """
        try:
            result = True
            # Ensure trigger mode off
            # The trigger must be disabled in order to configure whether the source
            # is software or hardware.
            if self.cam.TriggerMode.GetAccessMode() != PySpin.RW:
                print('Unable to disable trigger mode (node retrieval). Aborting...')
                return False
    
            self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
    
            print('Trigger mode disabled...')
    
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False
    
        return result
    
    
    def print_device_info(self):
        """
        This function prints the device information of the camera from the transport
        layer; please see NodeMapInfo example for more in-depth comments on printing
        device information from the nodemap.
    
        :param nodemap: Transport layer device nodemap.
        :type nodemap: INodeMap
        :returns: True if successful, False otherwise.
        :rtype: bool
        """
    
        print('*** DEVICE INFORMATION ***\n')
        # Retrieve TL device nodemap and print device information
        nodemap = self.cam.GetTLDeviceNodeMap()
        try:
            result = True
            node_device_information = PySpin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))
    
            if PySpin.IsAvailable(node_device_information) and PySpin.IsReadable(node_device_information):
                features = node_device_information.GetFeatures()
                for feature in features:
                    node_feature = PySpin.CValuePtr(feature)
                    print('%s: %s' % (node_feature.GetName(),
                                      node_feature.ToString() if PySpin.IsReadable(node_feature) else 'Node not readable'))
    
            else:
                print('Device control information not available.')
    
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False
    
        return result
    
    
    # configure_exposure added from Exposure_QuickSpin.py
    def configure_exposure(self):
        """
         This function configures a custom exposure time. Automatic exposure is turned
         off in order to allow for the customization, and then the custom setting is
         applied.
    
         :param cam: Camera to configure exposure for.
         :type cam: CameraPtr
         :return: True if successful, False otherwise.
         :rtype: bool
        """
    
        print('*** CONFIGURING EXPOSURE ***\n')
    
        try:
            result = True
    
            # Turn off automatic exposure mode
            #
            # *** NOTES ***
            # Automatic exposure prevents the manual configuration of exposure
            # times and needs to be turned off for this example. Enumerations
            # representing entry nodes have been added to QuickSpin. This allows
            # for the much easier setting of enumeration nodes to new values.
            #
            # The naming convention of QuickSpin enums is the name of the
            # enumeration node followed by an underscore and the symbolic of
            # the entry node. Selecting "Off" on the "ExposureAuto" node is
            # thus named "ExposureAuto_Off".
            #
            # *** LATER ***
            # Exposure time can be set automatically or manually as needed. This
            # example turns automatic exposure off to set it manually and back
            # on to return the camera to its default state.
    
            if self.cam.ExposureAuto.GetAccessMode() != PySpin.RW:
                print('Unable to disable automatic exposure. Aborting...')
                return False
    
            self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
            print('Automatic exposure disabled...')
    
            # Set exposure time manually; exposure time recorded in microseconds
            #
            # *** NOTES ***
            # Notice that the node is checked for availability and writability
            # prior to the setting of the node. In QuickSpin, availability and
            # writability are ensured by checking the access mode.
            #
            # Further, it is ensured that the desired exposure time does not exceed
            # the maximum. Exposure time is counted in microseconds - this can be
            # found out either by retrieving the unit with the GetUnit() method or
            # by checking SpinView.
    
            if self.cam.ExposureTime.GetAccessMode() != PySpin.RW:
                print('Unable to set exposure time. Aborting...')
                return False
    
            # Ensure desired exposure time does not exceed the maximum
            exposure_time_to_set = min(self.cam.ExposureTime.GetMax(), desired_exposure_time)
            self.cam.ExposureTime.SetValue(exposure_time_to_set)
            print('Shutter time set to %s us...\n' % exposure_time_to_set)
    
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False
    
        return result
    
    # reset_exposure added from Exposure_QuickSpin.py
    def reset_exposure(self):
        """
        This function returns the camera to a normal state by re-enabling automatic exposure.
    
        :param cam: Camera to reset exposure on.
        :type cam: CameraPtr
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        try:
            result = True
    
            # Turn automatic exposure back on
            #
            # *** NOTES ***
            # Automatic exposure is turned on in order to return the camera to its
            # default state.
    
            if self.cam.ExposureAuto.GetAccessMode() != PySpin.RW:
                print('Unable to enable automatic exposure (node retrieval). Non-fatal error...')
                return False
    
            self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)
    
            print('Automatic exposure enabled...')
    
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False
    
        return result
    
    
    
    def run_single_camera_trigger(self):
        """
        This function acts as the body of the example; please see NodeMapInfo example
        for more in-depth comments on setting up cameras.
    
        :param cam: Camera to run on.
        :type cam: CameraPtr
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        try:
            result = True
            err = False
    
            # Retrieve TL device nodemap and print device information
            nodemap_tldevice = self.cam.GetTLDeviceNodeMap()
    
            result &= self.print_device_info()
    
            # Initialize camera
            self.cam.Init()
    
            # Retrieve GenICam nodemap
            nodemap = self.cam.GetNodeMap()
    
            # Configure trigger
            if self.configure_trigger() is False:
                return False
            
            # Configure exposure
            if not self.configure_exposure():
                return False
    
            # Acquire images
            result &= self.acquire_images_trigger()
    
            # Reset trigger
            result &= self.reset_trigger()
            
            # Reset exposure
            result &= self.reset_exposure()
    
            # Deinitialize camera
            self.cam.DeInit()
    
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False
    
        return result
    
    
    def closeCameraPtrAndSystem(self):
        self.cam.EndAcquisition()  # check if this one should be removed
        self.reset_trigger()
        self.reset_exposure()
        self.cam.DeInit()
        # Release reference to camera
        # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
        # cleaned up when going out of scope.
        # The usage of del is preferred to assigning the variable to None.
        del self.cam
        
        # Release system instance
        self.system.ReleaseInstance()
        del self.system
    
    def main_trigger(self):
        """
        Example entry point; please see Enumeration example for more in-depth
        comments on preparing and cleaning up the system.
    
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        result = True
        result &= self.run_single_camera_trigger()
        return result


    ### Run fluorescence monitor

    def acquire_and_display_images(self, axes, canvas, fluorescenceNumberBox, axes_fluorescencePlot, canvas_fluorescence):
        """
        This function continuously acquires images from a device and display them in a GUI.
    
        :param cam: Camera to acquire images from.
        :param nodemap: Device nodemap.
        :param nodemap_tldevice: Transport layer device nodemap.
        :type cam: CameraPtr
        :type nodemap: INodeMap
        :type nodemap_tldevice: INodeMap
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        
        self.nCountList = [0]*13
        
        global continue_recording
    
        sNodemap = self.cam.GetTLStreamNodeMap()
    
        # Change bufferhandling mode to NewestOnly
        node_bufferhandling_mode = PySpin.CEnumerationPtr(sNodemap.GetNode('StreamBufferHandlingMode'))
        if not PySpin.IsAvailable(node_bufferhandling_mode) or not PySpin.IsWritable(node_bufferhandling_mode):
            print('Unable to set stream buffer handling mode.. Aborting...')
            return False
    
        # Retrieve entry node from enumeration node
        node_newestonly = node_bufferhandling_mode.GetEntryByName('NewestOnly')
        if not PySpin.IsAvailable(node_newestonly) or not PySpin.IsReadable(node_newestonly):
            print('Unable to set stream buffer handling mode.. Aborting...')
            return False
    
        # Retrieve integer value from entry node
        node_newestonly_mode = node_newestonly.GetValue()
    
        # Set integer value from entry node as new value of enumeration node
        node_bufferhandling_mode.SetIntValue(node_newestonly_mode)
    
        print('*** IMAGE ACQUISITION ***\n')
        try:
            node_acquisition_mode = PySpin.CEnumerationPtr(self.nodemap.GetNode('AcquisitionMode'))
            if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
                print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
                return False
    
            # Retrieve entry node from enumeration node
            node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
            if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
                    node_acquisition_mode_continuous):
                print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
                return False
    
            # Retrieve integer value from entry node
            acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
    
            # Set integer value from entry node as new value of enumeration node
            node_acquisition_mode.SetIntValue(acquisition_mode_continuous)
    
            print('Acquisition mode set to continuous...')
    
            #  Begin acquiring images
            #
            #  *** NOTES ***
            #  What happens when the camera begins acquiring images depends on the
            #  acquisition mode. Single frame captures only a single image, multi
            #  frame catures a set number of images, and continuous captures a
            #  continuous stream of images.
            #
            #  *** LATER ***
            #  Image acquisition must be ended when no more images are needed.
            self.cam.BeginAcquisition()
    
            print('Acquiring images...')
    
            #  Retrieve device serial number for filename
            #
            #  *** NOTES ***
            #  The device serial number is retrieved in order to keep cameras from
            #  overwriting one another. Grabbing image IDs could also accomplish
            #  this.
            device_serial_number = ''
            node_device_serial_number = PySpin.CStringPtr(self.nodemap_tldevice.GetNode('DeviceSerialNumber'))
            if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
                device_serial_number = node_device_serial_number.GetValue()
                print('Device serial number retrieved as %s...' % device_serial_number)
    
            # Close program
    
            # Figure(1) is default so you can omit this line. Figure(0) will create a new window every time program hits this line
            # fig = plt.figure(1)
            # plt.figure()
    
            # Close the GUI when close event happens
            # fig.canvas.mpl_connect('close_event', handle_close)
            # plt.canvas.mpl_connect('close_event', handle_close)
    
            # Retrieve and display images
            #while(continue_recording):
            while self.shouldCameraRun_fluorescence:
            #for i in range(3):
                print("shouldCameraRun_fluorescence is ")
                print(self.shouldCameraRun_fluorescence)
                #print(i)
                try:
    
                    #  Retrieve next received image
                    #
                    #  *** NOTES ***
                    #  Capturing an image houses images on the camera buffer. Trying
                    #  to capture an image that does not exist will hang the camera.
                    #
                    #  *** LATER ***
                    #  Once an image from the buffer is saved and/or no longer
                    #  needed, the image must be released in order to keep the
                    #  buffer from filling up.
                    
                    image_result = self.cam.GetNextImage(1000)
                    
                    #  Ensure image completion
                    if image_result.IsIncomplete():
                        print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
    
                    else:                    
                        print('Here 1')
                        # Getting the image data as a numpy array
                        image_data = image_result.GetNDArray()
                        #print(image_data)
                        print(type(image_data))
                        # Draws an image on the current figure
                        axes.imshow(image_data, cmap='gray')
                        #axes.set_data(image_data)
                        canvas.draw()
                        #axes.show()
                        print("image drawn")
                        axes.clear()
                        self.updateFluorescenceCount(image_data, fluorescenceNumberBox)
                        self.updateFluorescencePlot(axes_fluorescencePlot, canvas_fluorescence)
                        #canvas.flush_events()
                        #time.sleep(0.1)
                        # Interval in plt.pause(interval) determines how fast the images are displayed in a GUI
                        # Interval is in seconds.
                        # plt.pause(0.1)
                        
                        # Clear current reference of a figure. This will improve display speed significantly
                        #plt.clf()
                        
                        # # If user presses enter, close the program
                        # if keyboard.is_pressed('ENTER'):
                        #     print('Program is closing...')
                            
                        #     # Close figure
                        #     plt.close('all')             
                        #     input('Entered pressed Done! Press Enter to exit...')
                        #     continue_recording=False                        
    
                    #  Release image
                    #
                    #  *** NOTES ***
                    #  Images retrieved directly from the camera (i.e. non-converted
                    #  images) need to be released in order to keep from filling the
                    #  buffer.
                    image_result.Release()
                    print("result released")
                except PySpin.SpinnakerException as ex:
                    print('Error: %s' % ex)
                    return False
            print("Out of the loop")
            #  End acquisition
            #
            #  *** NOTES ***
            #  Ending acquisition appropriately helps ensure that devices clean up
            #  properly and do not need to be power-cycled to maintain integrity.
            self.cam.EndAcquisition()
            print("Ended acquisition")
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False
    
        return True
    
    def updateFluorescenceCount(self, imageData, fluorescenceNumberBox):
        self.nCount = imageData.sum()
        self.nCountList.append(self.nCount)
        self.nCountList.pop(0)
        fluorescenceNumberBox.SetValue(str(self.nCount))
        
    def updateFluorescencePlot(self, axes_fluorescencePlot, canvas_fluorescence):
        axes_fluorescencePlot.clear()
        axes_fluorescencePlot.plot(self.xdata, self.nCountList)
        canvas_fluorescence.draw()
        axes_fluorescencePlot.relim()
        axes_fluorescencePlot.autoscale_view()

    def run_single_camera_fluorescence(self, axes, canvas, fluorescenceNumberBox, axes_fluorescencePlot, canvas_fluorescence):
        """
        This function acts as the body of the example; please see NodeMapInfo example
        for more in-depth comments on setting up cameras.
    
        :param cam: Camera to run on.
        :type cam: CameraPtr
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        try:
            result = True
    
            self.nodemap_tldevice = self.cam.GetTLDeviceNodeMap()
    
            # Initialize camera
            self.cam.Init()
    
            # Retrieve GenICam nodemap
            self.nodemap = self.cam.GetNodeMap()
    
            # Acquire images
            result &= self.acquire_and_display_images(axes, canvas, fluorescenceNumberBox, axes_fluorescencePlot, canvas_fluorescence)
    
            # Deinitialize camera
            self.cam.DeInit()
    
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False
    
        return result
    
    
    def main_fluorescence(self, axes, canvas, fluorescenceNumberBox, axes_fluorescencePlot, canvas_fluorescence):
        """
        Example entry point; notice the volume of data that the logging event handler
        prints out on debug despite the fact that very little really happens in this
        example. Because of this, it may be better to have the logger set to lower
        level in order to provide a more concise, focused log.
    
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        result = True
    
        # Retrieve singleton reference to system object
        system = PySpin.System.GetInstance()
    
        # Get current library version
        version = system.GetLibraryVersion()
        print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))
    
        # Retrieve list of cameras from the system
        cam_list = system.GetCameras()
    
        num_cameras = cam_list.GetSize()
    
        print('Number of cameras detected: %d' % num_cameras)
    
        # Finish if there are no cameras
        if num_cameras == 0:
    
            # Clear camera list before releasing system
            cam_list.Clear()
    
            # Release system instance
            system.ReleaseInstance()
    
            print('Not enough cameras!')
            input('Done! Press Enter to exit...')
            return False
    
        # Run example on each camera
        for i, cam in enumerate(cam_list):
    
            print('Running example for camera %d...' % i)
            self.cam = cam
            result &= self.run_single_camera_fluorescence(axes, canvas, fluorescenceNumberBox, axes_fluorescencePlot, canvas_fluorescence)
            print('Camera %d example complete... \n' % i)
    
        # Release reference to camera
        # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
        # cleaned up when going out of scope.
        # The usage of del is preferred to assigning the variable to None.
        del cam
    
        # Clear camera list before releasing system
        cam_list.Clear()
    
        # # Release system instance
        # system.ReleaseInstance()
    
        #input('Main Done!')
        print("Done with main")
        return result


if __name__ == '__main__':
    camera = FLIRCamera("VERTICAL")
    if camera.run_single_camera_trigger():
        sys.exit(0)
    else:
        sys.exit(1)
#    if main():
#        sys.exit(0)
#    else:
#        sys.exit(1)
    # try:
    #     while main():
    #         print("New successfull run from the camera")
    #         print("Starting new image acquisition")
    #     sys.exit(0)
    # except Exception:
    #     print("error occured")