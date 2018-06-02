"""Module with definition of the RSRCC base class for compressed continuum data.

Classes: RSRCC
Uses:    netCDF4, os, numpy, math, Tempsens
Author:  FPS
Date:    May 5, 2014
Changes: 05/13/2014: caught use of "band" instead of "board" in line 159.
"""
import netCDF4
import sys
import os
import numpy as np
import math
from RSRUtilities import TempSens

class RSRCC():
    """RSRCC is the base class for compressed continuum data scans"""
    def __init__(self,filelist,date,scan,chassis_id,chassis,groupscan=0,subscan=1,path='/data_lmt'):
        """__init__ reads the netcdf file and fills in parameters and arrays"""
        self.path = path
        self.date = date
        self.scan = scan
        self.groupscan = groupscan
        self.subscan = subscan
        self.chassis_id = chassis_id
        self.chassis = chassis
        self.filename = self.make_filename(filelist)
        if self.filename == '':
            print '    file not found'
            self.n = -1
            return
        print '    process file', self.filename
        if os.path.isfile(self.filename):
            # open file as a dataset
            self.nc = netCDF4.Dataset(self.filename)

            # load useful header variables
            self.source = ''.join(self.nc.variables['Header.Source.SourceName'][:])
            self.obsnum = self.nc.variables['Header.Dcs.ObsNum'][0]
            self.utdate = self.nc.variables['Header.TimePlace.UTDate'][0]
            self.ut1_h = self.nc.variables['Header.TimePlace.UT1'][0]/2./math.pi*24.
            #self.azim = self.nc.variables['Header.Sky.AzReq'][0]*180./math.pi
            #self.elev = self.nc.variables['Header.Sky.ElReq'][0]*180./math.pi
            self.azim = self.nc.variables['Header.Telescope.AzDesPos'][0]*180./math.pi
            self.elev = self.nc.variables['Header.Telescope.ElDesPos'][0]*180./math.pi
            self.m1ZernikeC0 = self.nc.variables['Header.M1.ZernikeC'][0]
            self.m2x = self.nc.variables['Header.M2.XReq'][0]
            self.m2y = self.nc.variables['Header.M2.YReq'][0]
            self.m2z = self.nc.variables['Header.M2.ZReq'][0]
            self.m2xPcor = self.nc.variables['Header.M2.XPcor'][0]
            self.m2yPcor = self.nc.variables['Header.M2.YPcor'][0]
            self.m2zPcor = self.nc.variables['Header.M2.ZPcor'][0]
            self.m2tip = self.nc.variables['Header.M2.TipCmd'][0] #rotation about X
            self.m2tilt = self.nc.variables['Header.M2.TiltCmd'][0] #rotation about Y

            # sometimes the Receiver designation is wrong; check and warn but don't stop
            self.beam_throw = -1
            self.beam_throw2 = -1
            self.beam_throw_angle = 0
            self.receiver = ''.join(self.nc.variables['Header.Dcs.Receiver'][:]).strip()
            if self.receiver == 'RedshiftReceiver':
                print '    receiver =', self.receiver
                self.beam_selected = self.nc.variables['Header.RedshiftReceiver.BeamSelected'][0]
                self.tracking_beam = self.nc.variables['Header.RedshiftReceiver.BeamSelected'][0]
                self.beam_throw = np.abs(self.nc.variables['Header.RedshiftReceiver.Dx'][0])*3600*180/np.pi
                self.beam_throw2 = np.abs(self.nc.variables['Header.RedshiftReceiver.Dx'][:][1])*3600*180/np.pi
                self.beam_throw_angle = np.abs(self.nc.variables['Header.RedshiftReceiver.Beta'][:])*180/np.pi
                if(self.beam_throw != self.beam_throw2):
                    self.beam_throw = self.beam_throw2 = -1
                print '    beam throw and theta', self.beam_throw,self.beam_throw2,self.beam_throw_angle
                if self.tracking_beam != -1:
                    print '    TRACKING BEAM ',self.tracking_beam
            elif self.receiver == 'Sequoia':
                self.beam_selected = self.nc.variables['Header.Sequoia.BeamSelected'][0]
                #self.beam_selected = -1
                self.pixel_selected = self.beam_selected
                self.tracking_beam = 1
                try:
                    self.beam_throw = self.nc.variables['Header.Sequoia.PixelDelta'][0]*3600*180/np.pi
                    self.beam_throw2 = self.beam_throw
                    self.beam_throw_angle = np.abs(self.nc.variables['Header.Sequoia.CenterTheta'][:])*180/np.pi
                except:
                    self.beam_throw = 27.9
                    self.beam_throw2 = self.beam_throw
                    self.beam_throw_angle = 46.0
                self.num_pixels = self.nc.variables['Header.Sequoia.NumPixels'][0]
            else:
                print '    receiver =', self.receiver
                self.beam_selected = 1
                self.tracking_beam = 1
                self.beam_throw = 0
                self.beam_throw2 = 0

            # Pointing Variables
            self.modrev = self.nc.variables['Header.PointModel.ModRev'][0]
            self.az_user = self.nc.variables['Header.PointModel.AzUserOff'][0]*206264.8 
            self.el_user = self.nc.variables['Header.PointModel.ElUserOff'][0]*206264.8 
            self.az_paddle = self.nc.variables['Header.PointModel.AzPaddleOff'][0]*206264.8 
            self.el_paddle = self.nc.variables['Header.PointModel.ElPaddleOff'][0]*206264.8 
            self.az_total = self.nc.variables['Header.PointModel.AzTotalCor'][0]*206264.8 
            self.el_total = self.nc.variables['Header.PointModel.ElTotalCor'][0]*206264.8 
            self.az_receiver = self.nc.variables['Header.PointModel.AzReceiverOff'][0]*206264.8
            self.el_receiver = self.nc.variables['Header.PointModel.ElReceiverOff'][0]*206264.8
            try:
                self.az_m2 = self.nc.variables['Header.PointModel.AzM2Cor'][0]*206264.8
                self.el_m2 = self.nc.variables['Header.PointModel.ElM2Cor'][0]*206264.8
            except:
                self.az_m2 = 0.0
                self.el_m2 = 0.0

            # TILTMETER Information
            self.tilt0_x = self.nc.variables['Header.Tiltmeter_0_.TiltX'][0]*206264.8
            self.tilt0_y = self.nc.variables['Header.Tiltmeter_0_.TiltY'][0]*206264.8
            self.tilt1_x = self.nc.variables['Header.Tiltmeter_1_.TiltX'][0]*206264.8
            self.tilt1_y = self.nc.variables['Header.Tiltmeter_1_.TiltY'][0]*206264.8

            # TEMPERATURE SENSOR Information
            self.T = TempSens(self.nc.variables['Header.TempSens.TempSens'][:]/100.)

            # Data Block - sometimes this isn't written, so check it and handle exception
            try:
                if self.receiver == 'RedshiftReceiver':
                    this_chassis = 'Data.RedshiftChassis_'+str(self.chassis)
                    self.xpos = self.nc.variables['Data.Sky.XPos'][:]*206264.8
                    self.ypos = self.nc.variables['Data.Sky.YPos'][:]*206264.8
                    self.time = self.nc.variables['Data.Sky.Time'][:]
                    self.duration = self.time[len(self.time)-1]-self.time[0]
                    self.bufpos = self.nc.variables['Data.Dcs.BufPos'][:]
                    self.data = self.nc.variables[this_chassis+'_.AccAverage'][:]
                    if this_chassis+'_.AccSamples' in self.nc.variables.keys():
                        self.samples = self.nc.variables[this_chassis+'_.AccSamples'][:]
                        self.samples_exist = True
                    else:
                        self.samples_exist = False
                    self.n =  np.shape(self.data)[0]
                    self.nchan = 6
                    self.bias = np.zeros(self.nchan)
                    self.flip = np.zeros(self.nchan)
                    self.flag = np.zeros((self.nchan,self.n))
                    for board in range(self.nchan):
                        self.flip[board] = -1
                        self.bias[board] = np.median(self.data[:,board])
                elif 'vlbi1mm' in self.filename:
                    self.xpos = self.nc.variables['Data.Sky.XPos'][:]*206264.8
                    self.ypos = self.nc.variables['Data.Sky.YPos'][:]*206264.8
                    self.time = self.nc.variables['Data.Sky.Time'][:]
                    self.duration = self.time[len(self.time)-1]-self.time[0]
                    try:
                        self.bufpos = self.nc.variables['Data.Dcs.BufPos'][:]
                        print '    got bufpos from dcs'
                    except:
                        self.bufpos = self.nc.variables['Data.Sky.BufPos'][:]
                        print '    got bufpos from sky'
                    self.apower = self.nc.variables['Data.Vlbi1mmTpm.APower'][:]
                    self.bpower = self.nc.variables['Data.Vlbi1mmTpm.BPower'][:]
                    self.samples_exist = True
                    na = len(self.apower)
                    nb = len(self.bpower)
                    self.data = [[]]
                    self.samples = [[]]
                    self.nchan = 2
                    self.data = np.zeros((na,self.nchan))
                    self.samples = np.zeros((na,self.nchan))
                    for b in range(0,self.nchan,2):
                        for j in range(na):
                            self.data[j][b+0] = self.apower[j]
                            self.samples[j][b+0] = 3936
                        for j in range(nb):
                            self.data[j][b+1] = self.bpower[j]
                            self.samples[j][b+1] = 3936
                            
                    self.n = np.shape(self.data)[0]
                    self.bias = np.zeros(self.nchan)
                    self.flip = np.zeros(self.nchan)
                    self.flag = np.zeros((self.nchan,self.n))
                    for board in range(self.nchan):
                        self.flip[board] = 1
                        self.bias[board] = np.median(self.data[:,board])
                elif 'lmttpm' in self.filename or 'ifproc' in self.filename:

                    self.xpos = self.nc.variables['Data.TelescopeBackend.TelAzMap'][:]*206264.8
                    self.ypos = self.nc.variables['Data.TelescopeBackend.TelElMap'][:]*206264.8
                    self.time = self.nc.variables['Data.TelescopeBackend.TelTime'][:]
                    self.duration = self.time[len(self.time)-1]-self.time[0]
                    self.bufpos = self.nc.variables['Data.TelescopeBackend.BufPos'][:]
                    if 'lmttpm' in self.filename:
                        self.signals = self.nc.variables['Data.LmtTpm.Signal']
                    elif 'ifproc' in self.filename:
                        self.signals = self.nc.variables['Data.IfProc.BasebandLevel']
                    self.samples_exist = True
                    self.data = [[]]
                    self.samples = [[]]
                    na = len(self.signals)
                    sigs = np.transpose(self.signals)
                    self.nchan = len(sigs)
                    self.data = np.zeros((na,self.nchan))
                    self.samples = np.zeros((na,self.nchan))
                    for b,sig in enumerate(sigs):
                      for j in range(na):
                          self.data[j][b] = sig[j]
                          self.samples[j][b] = 3936
                    self.n = np.shape(self.data)[0]
                    self.bias = np.zeros(self.nchan)
                    self.flip = np.zeros(self.nchan)
                    self.flag = np.zeros((self.nchan,self.n))
                    for board in range(self.nchan):
                        self.flip[board] = 1
                        self.bias[board] = np.median(self.data[:,board])
                elif 'spec' in self.filename:
                    self.pixel_list = self.nc.variables['Header.Spec.PixelList'][:]
                    if self.beam_selected == -1:
                        self.pixel_selected = self.beam_selected
                    elif self.beam_selected in self.pixel_list:
                        self.pixel_selected = int(np.where(self.pixel_list == self.beam_selected)[0])
                    else:
                        self.pixel_selected = -2
                    self.num_pixels = self.nc.variables['Header.Sequoia.NumPixels'][0]
                    self.xpos = self.nc.variables['Data.Spec.MapX'][:]*206264.8
                    self.ypos = self.nc.variables['Data.Spec.MapY'][:]*206264.8
                    self.time = self.nc.variables['Data.Spec.MapT'][:]
                    self.duration = self.time[len(self.time)-1]-self.time[0]
                    #self.bufpos = self.nc.variables['Data.Spec.BufPos'][:]
                    self.signals = self.nc.variables['Data.Spec.MapData']
                    self.samples_exist = True
                    self.data = [[]]
                    self.samples = [[]]
                    na = len(self.signals)
                    sigs = np.transpose(self.signals)
                    self.nchan = len(sigs)
                    self.data = np.zeros((na,self.nchan))
                    self.samples = np.zeros((na,self.nchan))
                    for b,sig in enumerate(sigs):
                      for j in range(na):
                          self.data[j][b] = sig[j]
                          self.samples[j][b] = 3936
                    self.n = np.shape(self.data)[0]
                    self.bias = np.zeros(self.nchan)
                    self.flip = np.zeros(self.nchan)
                    self.flag = np.zeros((self.nchan,self.n))
                    for board in range(self.nchan):
                        self.flip[board] = 1
                        self.bias[board] = np.median(self.data[:,board])
            except Exception as e:
              print 'Trouble with data block for file '+self.filename
              print e
              sys.exit(0)
        
            # define special elimination flag
            self.ELIM = -999999.

        else:
            print self.filename+' does not exist'
    
    def sync(self):
        self.nc.sync()

    def close(self):
        try:
            self.nc.close()
        except AttributeError:
            print "from close(): ncfile not open"
    
    def make_filename(self,filelist):
        filename = ""
        if filelist != False:
            print '  get filename from filelist for obsnum', self.scan, 'chassis', self.chassis
            for i,filel in enumerate(filelist):
                """Builds an LMT filename filelist and chassis."""
                if 'RedshiftChassis' in filel:
                    chassis_str = ('RedshiftChassis%d' % self.chassis)
                    if chassis_str in filel and str(self.scan) in filel:
                        filename = filel
                        break
                elif 'spec' in filel:
                    chassis_str = ('spec%d' % self.chassis)
                    if chassis_str in filel and str(self.scan) in filel:
                        filename = filel
                        break
                else:
                    chassis_str = 'other'
                    if self.chassis == i and str(self.scan) in filel:
                        filename = filel
                        break
        else:
            """Builds an LMT filename from date and obsnum."""
            print '  get filename from date and obsnum'
            filename = ('%s/RedshiftChassis%d/RedshiftChassis%d_%s_%06d_%02d_%04d.nc' % (self.path, self.chassis, self.chassis, self.date,self.scan,self.groupscan,self.subscan))
        return filename

    def check(self):
        """Provides a way to test whether this is a good instance."""
        try:
            a = self.n
        except AttributeError:
            return False
        else:
            return True
    
    def elim_bad_integrations(self,board=0,checksum=3936):
        """Routine checks for correct number of integrations in a sample and flags bad ones."""
        if self.samples_exist:
            counter = 0
            for i in range(self.n):
                if self.samples[i,board] != checksum:
                    self.flag[board,i] = 1
                    print 'Eliminate sample ',i,'  AccSamples =',self.samples[i,board]
                    counter = counter+1        
            if counter > 0:
                print 'Bad integrations: ',counter
        else:
            print 'AccSamples Array does not exist in file; cannot remove bad integrations'    

    def despike(self,board=0,cut=1):
        """Implements a despike routine which looks for outliers in a running filter."""
        w = 10
        d = 1
        r = np.zeros(self.n)
        first = w
        last = self.n-w
        x = np.arange(-w,w+1)
        for i in range(first,last):
            y = self.data[i-w:i+w+1,board]
            p = np.polyfit(x,y,2)
            r[i] = self.data[i,board]-p[2]
        
        rsig = np.std(r[first:last])
        rcut = cut*rsig

        counter2 = 0
        for i in range(d,self.n-d+1):
            if abs(r[i])>rcut:
                self.flag[board,i] = 1
                counter2 = counter2+1
        print "Bad Points: ", counter2
    
    def flag_windows(self, board=0, flag_windows=()):
        """Uses the flag_windows lists to flag bad data."""
        counter = 0
        if flag_windows == ():
            print 'No windows to flag'
        else:
            if type(flag_windows[0]) == int:
                # we are flagging one window
                for j in range(flag_windows[0],flag_windows[1]+1):
                    counter = counter + 1
                    self.flag[board,j] = 1
            else:
                nwindows = np.shape(flag_windows)[0]
                for i in range(nwindows):
                    for j in range(flag_windows[i][0],flag_windows[i][1]+1):
                        counter = counter + 1
                        self.flag[board,j] = 1
        print "Flagged ",counter," points"
    
    def remove_baseline(self, board=0, ww=50):
        """Performs a baseline removal using a running smooth to estimate baseline.

        The parameter ww is the number of samples to use in the running smooth.
        """
        test_array = np.zeros(self.n)
        for i in range(self.n):
            if self.flag[board,i] == 1:
                test_array[i] = self.ELIM
            else:
                test_array[i] = self.data[i,board]
        
        baseline = np.zeros(self.n)

        for i in range(ww,self.n-ww+1):
            nn = 0.
            for j in range(2*ww):
                k = i-ww+j
                if test_array[k] != self.ELIM:
                    baseline[i] = baseline[i]+test_array[k]
                    nn = nn+1.
        
            baseline[i] = baseline[i]/nn
    
        for i in range(ww):
            baseline[i] = baseline[ww]
            baseline[self.n-ww+i] = baseline[self.n-ww]
    
        for i in range(self.n):
            if self.flag[board,i] == 0:
                self.data[i,board] = self.data[i,board]-baseline[i]+self.bias[board]
    
    
    def process(self, remove_baseline=False, ww=50, despike_scan=False, elim_bad_integrations = True, checksum=3936, flag_data=False, flag_windows=()):
        """Runs through all the clean-up processing steps for a scan for data from all boards

        The processing steps are: (1) elimination of bad integrations; ;(2) despike;
        (3) baseline removal; (4) bad data flagging.
        """
        for board in range(self.nchan):
            if(elim_bad_integrations):
                self.elim_bad_integrations(board,checksum)
            if(despike_scan):
                self.despike(board,1)
            if(flag_data):
                self.flag_windows(board, flag_windows)
            if(remove_baseline):
                self.remove_baseline(board,dd,ww)
    

    def process_single_band(self, board=0, remove_baseline=False, ww=50, despike_scan=False, elim_bad_integrations = True, checksum=3936, flag_data=False, flag_windows=()):
        """Runs through all the clean-up processing steps for a scan for data from a single board.

        The processing steps are: (1) elimination of bad integrations; ;(2) despike;
        (3) baseline removal; (4) bad data flagging.
        """
        if(elim_bad_integrations):
            self.elim_bad_integrations(board,checksum)
        if(despike_scan):
            self.despike(board,1)
        if(flag_data):
            self.flag_windows(board, flag_windows)
        if(remove_baseline):
            self.remove_baseline(board,dd,ww)

    def board_id(self, board=0):
        if 'spec' in self.filename:
            return self.pixel_list[board]
        return board
                
def main():
    filelist = ['/data_lmt/ifproc/ifproc_2018-04-16_074753_00_0001.nc']
    r = RSRCC(filelist, '', 74753, 0)
    filelist = ['/data_lmt/lmttpm/lmttpm_2018-03-16_073677_01_0000.nc']
    r = RSRCC(filelist, '', 73677, 0)

if __name__ == '__main__':
    main()
    
