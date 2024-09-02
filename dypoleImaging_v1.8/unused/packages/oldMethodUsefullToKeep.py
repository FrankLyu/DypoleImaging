

    def saveAsRef(self):
        if self.checkSaveAsRef.GetValue() is True:
            path = self.path[:-2] + "_ref\\"
            if not os.path.exists(path):
                os.makedirs(path)
            shutil.copy2(self.imageID, path)
            self.defringingRefPath = path


    def saveResult(self, e):
        if self.fitMethodFermion.GetValue():
            self.saveFermionResult(e)
        elif self.fitMethodBoson.GetValue():
            self.saveBosonResult(e)
        elif self.fitMethodGaussian.GetValue():
            self.saveGaussianResult(e)

    def saveBosonResult(self, e):
        f = open("C:\\AndorImg\\boson_data.txt", "a")
        f.writelines(self.timeString + '\t' + self.tof.GetValue() + '\t'\
         # + self.omegaAxial.GetValue() + ' , ' + self.omegaRadial.GetValue() + ' , '\
         # + str(self.gVals[0][0]) + ' , ' + str(self.gVals[0][1]) + ' , ' \
         + self.atomNumberInt.GetValue() + '\t' \
         + str(self.bosonParams[2]) + '\t' + str(self.bosonParams[3]) + '\t' \
         + str(1/np.sqrt(self.bosonParams[7])) + '\t' + str(1/np.sqrt(self.bosonParams[8]))  \
            + '\n')
        
        f.close()

    def saveFermionResult(self, e):
        f = open("C:\\AndorImg\\fermion_data.txt", "a")
        
        f.writelines(self.timeString + '\t' + self.tof.GetValue() + '\t'\
         # + self.omegaAxial.GetValue() + ' , ' + self.omegaRadial.GetValue() + ' , '\
         + str(self.gaussionParams[0]) + '\t' + str(self.gaussionParams[1]) + '\t' \
         + self.atomNumberInt.GetValue() + '\t' \
         + str(self.fermionParams[2]) + '\t' + str(self.fermionParams[3]) + '\t' \
         + str(self.fermionParams[4]) + '\n')
        
        f.close()

    def saveGaussianResult(self, e):
        f = open("C:\\AndorImg\\gaussian_data.txt", "a")
        f.writelines(self.timeString + '\t' + self.tof.GetValue() + '\t'\
         # + self.omegaAxial.GetValue() + ' , ' + self.omegaRadial.GetValue() + ' , '\
         + str(self.gaussionParams[0]) + '\t' + str(self.gaussionParams[1]) + '\t' \
         + str(self.atomNumberInt.GetValue()) + '\t' + str(self.atomNumberIntFit.GetValue()) + '\t'\
         + str(self.gaussionParams[2]) + '\t' + str(self.gaussionParams[3]) \
         + '\n')
        
        f.close()
        
    def snippetCommunicate(self, N_intEdge):
        self.setConstants()
        try:
            f = open(self.snippetPath, "w")
        except:
            msg = wx.MessageDialog(self, 'The file path for SnippetServer is not correct','Incorrect File Path', wx.OK)
            if msg.ShowModal() == wx.ID_OK:
                msg.Destroy()
            return
            
        if not N_intEdge:
            N_intEdge = -1
            N_count = -1
        else:
#            N_count = N_intEdge/((pixelToDistance**2)/crossSection)/(16/6.45)**2
            N_count = N_intEdge * (self.pixelToDistance**2)/self.crossSection
            
        
#        f.writelines(self.timeString + '\t' + str(N_intEdge) + '\t-1' + '\t' + str(N_count) + '\t-1' + '\t' + str(N_count) + '\t-1' + '\t' + str("%.2f"%(self.true_y_width*1E6)) + '\n')
#        f.writelines(self.timeString + '\t' + str(N_intEdge) + '\t-1' + '\t' + str(N_count) + '\t-1' + '\t' + str(self.atomNumFromGaussianY) + '\t-1' + '\t' + str("%.2f"%(self.true_y_width*1E6)) + '\n')
        f.writelines(self.timeString + '\t' + str(N_intEdge) + '\t-1' + '\t' + str(N_count) + '\t-1' + '\t' + str(self.atomNumFromGaussianX) + '\t-1' + '\t' + str(self.atomNumFromGaussianY) + '\t-1' + '\t' + str("%.3f"%(self.temperature[0])) + '\t-1' + '\t' + str("%.3f"%(self.temperature[1])) + '\t-1' + '\t' + str("%.3f"%(self.tempLongTime[0])) + '\t-1' + '\t' + str("%.3f"%(self.tempLongTime[1])) + '\n')
        
#        f.writelines(self.timeString + '\t' + str(N_intEdge) + '\t-1' + '\t' + str(N_count) + '\t-1' + '\t' + str(self.y_center) + '\t-1' + '\t' + str(self.x_center) + '\n')
#        f.writelines(self.timeString + '\t' + str(N_intEdge) + '\t-1' + '\t' + str(self.x_width) + '\t-1' + '\t' + str(self.x_center) + '\t-1' + '\t' + str("%.2f"%(self.true_y_width*1E6)) + '\n')

