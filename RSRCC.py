"""Module with definition of the RSRCC base class for compressed continuum data.

Classes: RSRCC
Uses:    netCDF4, os, numpy, math, Tempsens
Author:  FPS
Date:    May 5, 2014
Changes:
"""
import netCDF4
import os
import numpy as np
import math
from RSRUtilities import TempSens

class RSRCC():
    """RSRCC is the base class for compressed continuum data scans"""
    def __init__(self,filelist,date,scan,chassis,groupscan=0,subscan=1,path='/data_lmt'):
        """__init__ reads the netcdf file and fills in parameters and arrays""" 
        self.path = path
        self.date = date
        self.scan = scan
        self.groupscan = groupscan
        self.subscan = subscan
        self.chassis = chassis
        self.filename = self.make_filename(filelist)
        print 'process file ',self.filename
        if os.path.isfile(self.filename):
            # open file as a dataset
            self.nc = netCDF4.Dataset(self.filename)

            # load useful header variables
            self.source = ''.join(self.nc.variables['Header.Source.SourceName'][:])
            self.obsnum = self.nc.variables['Header.Dcs.ObsNum'][:][0]
            self.utdate = self.nc.variables['Header.TimePlace.UTDate'][:][0]
            self.ut1_h = self.nc.variables['Header.TimePlace.UT1'][:][0]/2./math.pi*24.
            self.azim = self.nc.variables['Header.Sky.AzReq'][:][0]*180./math.pi
            self.elev = self.nc.variables['Header.Sky.ElReq'][:][0]*180./math.pi
            self.m1ZernikeC0 = self.nc.variables['Header.M1.ZernikeC'][:][0]
            self.m2x = self.nc.variables['Header.M2.XReq'][:][0]
            self.m2y = self.nc.variables['Header.M2.YReq'][:][0]
            self.m2z = self.nc.variables['Header.M2.ZReq'][:][0]
            self.m2xPcor = self.nc.variables['Header.M2.XPcor'][:][0]
            self.m2yPcor = self.nc.variables['Header.M2.YPcor'][:][0]
            self.m2zPcor = self.nc.variables['Header.M2.ZPcor'][:][0]
            self.m2tip = self.nc.variables['Header.M2.TipCmd'][:][0] #rotation about X
            self.m2tilt = self.nc.variables['Header.M2.TiltCmd'][:][0] #rotation about Y

            # sometimes the Receiver designation is wrong; check and warn but don't stop
            self.beam_throw = -1
            self.beam_throw2 = -1
            rx = ''.join(self.nc.variables['Header.Dcs.Receiver'][:])
            if rx[0] == 'R':
                self.tracking_beam = self.nc.variables['Header.RedshiftReceiver.BeamSelected'][:][0]
                #self.azPointOff = self.nc.variables['Header.RedshiftReceiver.AzPointOff'][:][0]
                #self.elPointOff = self.nc.variables['Header.RedshiftReceiver.ElPointOff'][:][0]
                #self.skyElReq = self.nc.variables['Header.Sky.ElReq'][:][0]
                #self.beam_throw = np.abs(np.round(self.azPointOff/np.cos(self.skyElReq)*3600*180/np.pi))
                #self.beam_throw2 = np.abs(np.round(self.elPointOff/np.sin(self.skyElReq)*3600*180/np.pi))
                self.beam_throw = np.abs(self.nc.variables['Header.RedshiftReceiver.Dx'][:][0])*3600*180/np.pi
                self.beam_throw2 = np.abs(self.nc.variables['Header.RedshiftReceiver.Dx'][:][1])*3600*180/np.pi
                if(self.beam_throw != self.beam_throw2):
                    self.beam_throw = self.beam_throw2 = -1
                #print 'AzPointOff ',self.azPointOff
                #print 'ElPointOff ',self.elPointOff
                #print 'SkyElReq ',self.skyElReq
                print 'beam throw ', self.beam_throw,self.beam_throw2
                if self.tracking_beam != -1:
                    print 'TRACKING BEAM ',self.tracking_beam
            elif rx[0] == 'V':
                self.tracking_beam = 0
                self.azPointOff = self.nc.variables['Header.Vlbi1mmReceiver.AzPointOff'][:][0]
                self.elPointOff = self.nc.variables['Header.Vlbi1mmReceiver.ElPointOff'][:][0]
                self.skyElReq = self.nc.variables['Header.Sky.ElReq'][:][0]
                print 'AzPointOff ',self.azPointOff
                print 'ElPointOff ',self.elPointOff
                print 'SkyElReq ',self.skyElReq
            else:
                print 'WARNING: NOT AN RSR FILE'
                self.tracking_beam = -1

            # Pointing Variables
            self.modrev = self.nc.variables['Header.PointModel.ModRev'][:][0]
            self.az_user = self.nc.variables['Header.PointModel.AzUserOff'][:][0]*206264.8 
            self.el_user = self.nc.variables['Header.PointModel.ElUserOff'][:][0]*206264.8 
            self.az_paddle = self.nc.variables['Header.PointModel.AzPaddleOff'][:][0]*206264.8 
            self.el_paddle = self.nc.variables['Header.PointModel.ElPaddleOff'][:][0]*206264.8 
            self.az_total = self.nc.variables['Header.PointModel.AzTotalCor'][:][0]*206264.8 
            self.el_total = self.nc.variables['Header.PointModel.ElTotalCor'][:][0]*206264.8 
            self.az_receiver = self.nc.variables['Header.PointModel.AzReceiverOff'][:][0]*206264.8
            self.el_receiver = self.nc.variables['Header.PointModel.ElReceiverOff'][:][0]*206264.8
            try:
                self.el_m2 = self.nc.variables['Header.PointModel.ElM2Cor'][:][0]*206264.8
            except:
                self.el_m2 = 0.0

            # TILTMETER Information
            self.tilt0_x = self.nc.variables['Header.Tiltmeter_0_.TiltX'][:][0]*206264.8
            self.tilt0_y = self.nc.variables['Header.Tiltmeter_0_.TiltY'][:][0]*206264.8
            self.tilt1_x = self.nc.variables['Header.Tiltmeter_1_.TiltX'][:][0]*206264.8
            self.tilt1_y = self.nc.variables['Header.Tiltmeter_1_.TiltY'][:][0]*206264.8

            # TEMPERATURE SENSOR Information
            self.T = TempSens(self.nc.variables['Header.TempSens.TempSens'][:]/100.)

            # Data Block - sometimes this isn't written, so check it and handle exception
            try:
                self.xpos = self.nc.variables['Data.Sky.XPos'][:]*206264.8
                self.ypos = self.nc.variables['Data.Sky.YPos'][:]*206264.8
                self.time = self.nc.variables['Data.Sky.Time'][:]
                self.duration = self.time[len(self.time)-1]-self.time[0]
                if rx[0] == 'R':
                    self.bufpos = self.nc.variables['Data.Dcs.BufPos'][:]
                    self.data = self.nc.variables['Data.RedshiftChassis_'+str(self.chassis)+'_.AccAverage'][:]
                    if 'Data.RedshiftChassis_'+str(self.chassis)+'_.AccSamples' in self.nc.variables.keys():
                        self.samples = self.nc.variables['Data.RedshiftChassis_'+str(self.chassis)+'_.AccSamples'][:]
                        self.samples_exist = True
                    else:
                        self.samples_exist = False
                    self.n =  np.shape(self.data)[0]
                    self.bias = np.zeros(6)
                    self.flag = np.zeros((6,self.n))
                    for board in range(6):
                        self.bias[board] = np.median(self.data[:,board])
                elif rx[0] == 'V':
                    try:
                        print 'get bufpos from dcs'
                        self.bufpos = self.nc.variables['Data.Dcs.BufPos'][:]
                    except:
                        print 'get bufpos from sky'
                        self.bufpos = self.nc.variables['Data.Sky.BufPos'][:]
                    self.apower = self.nc.variables['Data.Vlbi1mmTpm.APower'][:]
                    self.bpower = self.nc.variables['Data.Vlbi1mmTpm.BPower'][:]
                    self.samples_exist = True
                    na = len(self.apower)
                    nb = len(self.bpower)
                    self.data = [[]]
                    self.samples = [[]]
                    self.data = np.zeros((na,2))
                    self.samples = np.zeros((na,2))
                    for j in range(na):
                        self.data[j][0] = self.apower[j]
                        self.samples[j][0] = 3936
                    for j in range(nb):
                        self.data[j][1] = self.apower[j]
                        self.samples[j][1] = 3936
                    self.n = np.shape(self.data)[0]
                    self.bias = np.zeros(2)
                    self.flag = np.zeros((2,self.n))
                    for board in range(1):
                        self.bias[board] = np.median(self.data[:,board])
            except Exception as e:
                print 'Trouble with data block for file '+self.filename
                print e
        
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
        # look for vlbi 1st since redshift has multiple chassis and one of them
        # might not have a file
        for rx in ['VLBI1mm', 'RSR']:
            filename = self.make_filename_rx(filelist,rx)
            print filename
            if os.path.isfile(filename):
                print "is ", rx
                return filename
        return ""

    def make_filename_rx(self,filelist,rx):
        filename = ""
        """Builds an LMT filename from date and obsnum."""
        if filelist != False:
            print "Get filename from filelist"
            for filel in filelist:
                if rx[0] == 'R':
                    chassis_str = ('RedshiftChassis%d' % self.chassis)
                elif rx[0] == 'V':
                    chassis_str = ('vlbi1mm')
                if chassis_str in filel and str(self.scan) in filel:
                    filename = filel
                    break
        else:
            print "Get filename from date and obsnum"
            if rx[0] == 'R':
                filename = ('%s/RedshiftChassis%d/RedshiftChassis%d_%s_%06d_%02d_%04d.nc' % (self.path, self.chassis, self.chassis, self.date,self.scan,self.groupscan,self.subscan))
            elif rx[0] == 'V':
                filename = ('%s/vlbi1mm/vlbi1mm_%s_%06d_%02d_%04d.nc' % (self.path, self.date,self.scan,self.groupscan,self.subscan))
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
                self.flag[band,i] = 1
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
        for board in range(6):
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
                

