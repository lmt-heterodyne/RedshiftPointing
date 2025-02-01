"""Module with definition of the RSR Map class for analyzing pointing maps.

Classes: RSRMap
Uses:    RSRCC, numpy, math, scipy.optimize.leastsq
Author:  FPS
Date:    May 5, 2014
Changes: 03/15/18: changed fit_peak to use scipy.optimize.leastsq
"""
from RSRCC import RSRCC
import numpy as np
import math
import sys
from data_lmt import data_lmt
from scipy.optimize import leastsq

def compute_model(v,xdata,ydata):
    """computes gaussian 2d model from x,y; added 3/15/18 for least squares fit to beam"""
    model = v[0]*np.exp(-4.*np.log(2.)*((xdata-v[1])**2/v[2]**2+(ydata-v[3])**2/v[4]**2))
    return(model)

def compute_the_residuals(v,xdata,ydata,data):
    """computes residuals to gaussian 2d model; added 3/15/18 for least squares fit to beam"""
    n = len(data)
    model = compute_model(v,xdata,ydata)
    residuals = data-model
    return(residuals)

class RSRMap(RSRCC):
    """RSRMap is derived from RSRCC; it provides methods for analysis of pointing maps"""
    def __init__(self,filelist,date,scan,chassis_id,chassis,beamthrow=38.9,beamthrow_angle=-0.33,groupscan=1,subscan=1,path=None):
        """__init__ loads file parameters and data which are needed for pointing analysis"""
        path = data_lmt(path)
        RSRCC.__init__(self,filelist,date,scan,chassis_id,chassis,groupscan=groupscan,subscan=subscan,path=path)
        # check to see if we have a valid instance after RSRCC loads data
        if self.n < 0:
            return
        try:
            a=self.n
            # set the beam throw parameter
            if self.beam_throw != -1:
                self.beamthrow = self.beam_throw
                self.beamthrow_angle = self.beam_throw_angle
                print(('    from file beamthrow/angle', self.beamthrow, self.beamthrow_angle))
            else:
                self.beamthrow = beamthrow
                self.beamthrow_angle = beamthrow_angle
                print(('    from arg beamthrow/angle', self.beamthrow, self.beamthrow_angle))
            if self.beamthrow == 0:
                self.beamthrow_angle = 0

            # map parameters
            try:
                self.hpbw = self.nc.variables['Header.Map.HPBW'][0]*206264.8
                self.xlength = self.nc.variables['Header.Map.XLength'][0]*204264.8
                self.ylength = self.nc.variables['Header.Map.YLength'][0]*206264.8
                self.xstep = self.nc.variables['Header.Map.XStep'][0]
                self.ystep = self.nc.variables['Header.Map.YStep'][0]
                self.rows = self.nc.variables['Header.Map.RowsPerScan'][0]
            except:
                print(('    ',self.filename+' does not have map parameters'))
    
            # define space for results of indivual beams in chassis
            self.peak = [-1.0,+1.0]
            if self.receiver == 'RedshiftReceiver':
                self.set_pid = [[1,0],[0,1],[0,1],[1,0]]
            else:
                self.set_pid = [[1,1],[1,1],[1,1],[1,1]]
            self.xp = np.zeros((32,2))
            self.yp = np.zeros((32,2))
            self.ap = np.zeros((32,2))
            self.hpx = np.zeros((32,2))
            self.hpy = np.zeros((32,2))
            self.xp_snr = np.zeros((32,2))
            self.yp_snr = np.zeros((32,2))
            self.ap_snr = np.zeros((32,2))
            self.hpx_snr = np.zeros((32,2))
            self.hpy_snr = np.zeros((32,2))
            self.goodx = np.zeros((32,2))
            self.goody = np.zeros((32,2))
            self.xmax = 0
            self.ymax = 0
        
            # circumstances of beam fitting
            self.fit_beam = -1
            self.fit_beam_single = False
            self.fit_beam_is_tracking_beam = False

            # define space for final fitted parameters
            self.I = np.zeros(32)
            self.azoff = np.zeros(32)
            self.eloff = np.zeros(32)
            self.clipped = False
            self.isGood = np.zeros(32)
            self.beamsep = np.zeros(32)
            self.beamang = np.zeros(32)
            self.hpbw = np.zeros(32)
            self.hpbw_x = np.zeros(32)
            self.hpbw_y = np.zeros(32)
            self.I_snr = np.zeros(32)
            self.azoff_snr = np.zeros(32)
            self.eloff_snr = np.zeros(32)
            self.hpbw_x_snr = np.zeros(32)
            self.hpbw_y_snr = np.zeros(32)
            # define space for model
            self.model = np.zeros((32,self.n))
        except AttributeError as e:
            print(('    ',e))
            print(('    ',self.filename+' is not valid MAP file'))

    def check(self):
        """Provides a way to check for a valid instance of an RSRMap"""
        try:
            a = self.hpbw
        except AttributeError:
            return False
        else:
            return True
    
    def remove_baseline(self, board=0, dd=50, ww=50):
        """Removes baseline from a map file, ignoring the places where the beam is located"""
        test_array = np.zeros(self.n)
        elev_r = (self.elev+self.beamthrow_angle)*math.pi/180.
        if self.fit_beam_is_tracking_beam == True:
            y0 = 0
            x0 = 0
            y1 = 0
            x1 = 0
        else:
            y0 = self.beamthrow*math.sin(elev_r) - self.el_receiver
            x0 = -self.beamthrow*math.cos(elev_r) - self.az_receiver
            y1 = -self.beamthrow*math.sin(elev_r) - self.el_receiver
            x1 = self.beamthrow*math.cos(elev_r) - self.az_receiver
        if self.xpos.ndim == 2:
            xpos = self.xpos[:,board]
            ypos = self.ypos[:,board]
        else:
            xpos = self.xpos
            ypos = self.ypos
        for i in range(self.n):
            d0 = math.sqrt((xpos[i]-x0)**2 + (ypos[i]-y0)**2)
            d1 = math.sqrt((xpos[i]-x1)**2 + (ypos[i]-y1)**2)
            if self.flag[board,i] == 1:
                test_array[i] = self.ELIM
            elif d0 < dd:
                test_array[i] = self.ELIM
            elif d1 < dd:
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
    
    

    def find_peak(self, board=0, pid=1, dd=60):
        """Locates the beam peak in a map for a given board.

        pid specifies peak (positive of negative) we are looking for
        returns maximum value of peak and its location
        """
        # require peak to be in right place
        x0,y0,x1,y1 = self.beam_offsets(board)
        # locates peak position in map
        bmax = -20000
        imax = 0
        if self.n > 100:
            w = 10 # to handle case where spike is outside of area filtered
        else:
            w = 0
        if self.xpos.ndim == 2:
            xpos = self.xpos[:,board]
            ypos = self.ypos[:,board]
        else:
            xpos = self.xpos
            ypos = self.ypos
        for i in range(w,self.n-w):
            if self.flag[board,i] == 0:
                d0 = math.sqrt((xpos[i]-x0)**2 + (ypos[i]-y0)**2)
                d1 = math.sqrt((xpos[i]-x1)**2 + (ypos[i]-y1)**2)
                #print("%4d %6.2f %6.2f   %6.1f   %6.2f %6.2f" % (i,xpos[i],ypos[i],self.data[i,board],d0,d1))
                if (d0<dd or d1<dd):
                    if self.peak[pid]*(self.data[i,board]-self.bias[board])>bmax:
                        imax = i
                        bmax = self.peak[pid]*(self.data[i,board]-self.bias[board])
        
        print(('found_peak',board,bmax,imax,xpos[imax],ypos[imax],self.data[imax,board]))
        return bmax,xpos[imax],ypos[imax]

    def fit_peak(self,board=0,pid=1,w=16):
        """Fits a simple gaussian to a peak for a given board.

        pid identifies the positive of negative peak for the fit.
        w specifies the window (arcsec) within which we will fit data.
        """
        bmax,xmax,ymax = self.find_peak(board,pid)
        if self.xpos.ndim == 2:
            xpos = self.xpos[:,board]
            ypos = self.ypos[:,board]
        else:
            xpos = self.xpos
            ypos = self.ypos

        # looks at all points in map and finds those within "w" for fit
        XPOS_LIST = []
        YPOS_LIST = []
        DATA_LIST = []
        COUNT_LIST = 0
        for i in range(self.n):
            delta = math.sqrt((xpos[i]-xmax)*(xpos[i]-xmax)+(ypos[i]-ymax)*(ypos[i]-ymax))
            if self.flag[board,i] == 0:
                if delta < w:
                    COUNT_LIST = COUNT_LIST + 1
                    XPOS_LIST.append(xpos[i])
                    YPOS_LIST.append(ypos[i])
                    DATA_LIST.append(self.peak[pid]*(self.data[i,board]-self.bias[board]))

        xdata = np.array(XPOS_LIST)
        ydata = np.array(YPOS_LIST)
        fit_data = np.array(DATA_LIST)
        v0 = np.array([bmax, xmax, 15., ymax, 15.])
        lsq_fit,lsq_cov,lsq_inf,lsq_msg,lsq_success = leastsq(compute_the_residuals,v0,args=(xdata,ydata,fit_data),full_output=1)
        residuals = compute_the_residuals(lsq_fit,xdata,ydata,fit_data)
        chisq = np.dot(residuals.transpose(),residuals)
        npts = len(fit_data)
        if lsq_cov is None:
            lsq_err = np.zeros(5)
            lsq_snr = np.zeros(5)
        else:
            lsq_err = np.sqrt(np.diag(lsq_cov)*chisq/(npts-5))
            lsq_snr = lsq_fit/lsq_err
        print('lsq_fit',lsq_fit)
        print('lsq_cov',lsq_cov)
        print('lsq_msg',lsq_msg)
        print('lsq_success',lsq_success)
        print('lsq_err',lsq_err)
        print('lsq_snr',lsq_snr)

        self.xmax = xmax
        self.ymax = ymax
        self.ap[board,pid] = self.peak[pid]*lsq_fit[0]
        self.xp[board,pid] = lsq_fit[1]
        self.yp[board,pid] = lsq_fit[3]

        self.ap_snr[board,pid] = lsq_snr[0]
        self.xp_snr[board,pid] = lsq_snr[1]
        self.yp_snr[board,pid] = lsq_snr[3]
        self.hpx_snr[board,pid] = lsq_snr[2]
        self.hpy_snr[board,pid] = lsq_snr[4]

        if lsq_fit[2] < 0:
            print(('warning: bad gaussian fit in azimuth: obsnum=',self.obsnum,' board=', board,' chassis=',self.chassis))
            self.hpx[board,pid] = np.abs(lsq_fit[2])
            self.goodx[board,pid] = 0
        else:
            self.hpx[board,pid] = lsq_fit[2]
            self.goodx[board,pid] = 1
        
        if lsq_fit[4] < 0:
            print(('warning: bad gaussian fit in elevation: obsnum=',self.obsnum,' board=', board,' chassis=',self.chassis))
            self.hpy[board,pid] = np.abs(lsq_fit[4])
            self.goody[board,pid] = 0
        else:
            self.hpy[board,pid] = lsq_fit[4]
            self.goody[board,pid] = 1
    
        if lsq_success > 4:
            print(('warning: bad fit: obsnum=',self.obsnum,' board=', board,' chassis=',self.chassis))
            self.hpx[board,pid] = np.abs(lsq_fit[2])
            self.hpy[board,pid] = np.abs(lsq_fit[4])
            self.goodx[board,pid] = 0
            self.goody[board,pid] = 0


    def find_dual_beam(self, board=0, w=16):
        """Fits each beam and then derives final results for a particular board."""
        # fit each beam in the map
        self.fit_peak(board, 1, w)
        self.fit_peak(board, 0, w)
        if self.xpos.ndim == 2:
            xpos = self.xpos[:,board]
            ypos = self.ypos[:,board]
        else:
            xpos = self.xpos
            ypos = self.ypos

        # then calculate the results
        self.I[board] = self.ap[board,1]-self.ap[board,0]
        self.I_snr[board] = (self.ap_snr[board,1]+self.ap_snr[board,0])/2.
        self.isGood[board] = (self.goodx[board,1]*self.goodx[board,0])*(self.goody[board,1]*self.goody[board,0])
        self.azoff[board] = (self.xp[board,1]+self.xp[board,0])/2.
        self.eloff[board] = (self.yp[board,1]+self.yp[board,0])/2.
        self.azoff_snr[board] = (self.xp_snr[board,1]+self.xp_snr[board,0])/2.
        self.eloff_snr[board] = (self.yp_snr[board,1]+self.yp_snr[board,0])/2.
        az_off_unclipped = self.azoff[board]
        el_off_unclipped = self.eloff[board]
        self.azoff[board] = np.clip(self.azoff[board], self.xpos.min(), self.xpos.max())
        self.eloff[board] = np.clip(self.eloff[board], self.ypos.min(), self.ypos.max())
        if az_off_unclipped != self.azoff[board] or el_off_unclipped != self.eloff[board]:
            self.clipped = True
        self.hpbw[board] = (math.sqrt(self.hpx[board,1]*self.hpx[board,1]) +
                            math.sqrt(self.hpx[board,0]*self.hpy[board,0]))/2.
        self.hpbw_x[board] = (self.hpx[board,1]+self.hpx[board,0])/2.
        self.hpbw_y[board] = (self.hpy[board,1]+self.hpy[board,0])/2.
        self.hpbw_x_snr[board] = (self.hpx_snr[board,1]+self.hpx_snr[board,0])/2.
        self.hpbw_y_snr[board] = (self.hpy_snr[board,1]+self.hpy_snr[board,0])/2.
        self.beamsep[board] = math.sqrt((self.xp[board,1]-self.xp[board,0])*(self.xp[board,1]-self.xp[board,0]) + (self.yp[board,1]-self.yp[board,0])*(self.yp[board,1]-self.yp[board,0]))/2.
        self.beamang[board] = math.atan2((self.yp[board,1]-self.yp[board,0]),(self.xp[board,1]-self.xp[board,0]))/math.pi*180.0
        # now calculate the model for this board and save it for later display.
        for i in range(self.n):
            self.model[board,i] = self.ap[board,1]*math.exp(-4.*math.log(2.)*(((xpos[i]-self.xp[board,1])/self.hpx[board,1])**2+((ypos[i]-self.yp[board,1])/self.hpy[board,1])**2)) + self.ap[board,0]*math.exp(-4.*math.log(2.)*(((xpos[i]-self.xp[board,0])/self.hpx[board,0])**2+((ypos[i]-self.yp[board,0])/self.hpy[board,0])**2)) + self.bias[board]

    def select_pid(self,select_beam):
        """Specifies whether we want the positive or negative beam.

        input select_beam requests beam 0 or beam 1 for the receiver.
        function has to figure out whether this is positive or negative peak.
        also we have to see wether user wants to fit only one beam.
        returns the pid of the requested beam and sets flags used in fitting data.
        """
        self.fit_beam = select_beam
        self.fit_beam_single = True
        # check to see whether we are tracking beam "none"
        if self.tracking_beam == -1:
            self.fit_beam_is_tracking_beam = False
            # if tracking "none" then we can select beam 0 or 1
            # however, we will have to correct pointing for beam offset
            if select_beam == 0 or select_beam == 1:
                pid = self.set_pid[self.chassis][select_beam]
            # but if select_beam is not 0 or 1 we go get 1 by default
            else:
                pid = self.set_pid[self.chassis][1]
        # now if we are tracking a beam, check to see if we are fitting it
        else:
            pid = self.set_pid[self.chassis][select_beam]
            if self.tracking_beam == select_beam:
                self.fit_beam_is_tracking_beam = True
            # if we are NOT fitting the tracked beam, so be careful
            else:
                self.fit_beam_is_tracking_beam = False
            
        return pid

    def find_selected_beam(self, board=0, w=16, select_beam=1):
        """Performs fit for individual beam and sets final results."""
        # first define which beam
        pid = self.select_pid(select_beam)
        #print(self.beam_selected,self.chassis_index,pid)
        self.fit_peak(board, pid, w)
        if self.xpos.ndim == 2:
            xpos = self.xpos[:,board]
            ypos = self.ypos[:,board]
        else:
            xpos = self.xpos
            ypos = self.ypos
        self.I[board] = self.peak[pid]*self.ap[board,pid]
        self.I_snr[board] = self.ap_snr[board,pid]
        self.isGood[board] = self.goodx[board,pid]*self.goody[board,pid]
        if self.beam_selected == -1:
            x0,y0,x1,y1 = self.beam_offsets(board)
            self.azoff[board] = self.xp[board,pid]# - x1
            self.eloff[board] = self.yp[board,pid]# - y1
        else:
            self.azoff[board] = self.xp[board,pid]
            self.eloff[board] = self.yp[board,pid]
        self.azoff_snr[board] = self.xp_snr[board,pid]
        self.eloff_snr[board] = self.yp_snr[board,pid]
        az_off_unclipped = self.azoff[board]
        el_off_unclipped = self.eloff[board]
        self.azoff[board] = np.clip(self.azoff[board], self.xpos.min(), self.xpos.max())
        self.eloff[board] = np.clip(self.eloff[board], self.ypos.min(), self.ypos.max())
        if az_off_unclipped != self.azoff[board] or el_off_unclipped != self.eloff[board]:
            self.clipped = True
        self.beamsep[board] = 0.0
        self.beamang[board] = 0.0
        self.hpbw[board] = math.sqrt(self.hpx[board,pid]*self.hpy[board,pid])
        self.hpbw_x[board] = self.hpx[board,pid]
        self.hpbw_y[board] = self.hpy[board,pid]
        self.hpbw_x_snr[board] = self.hpx_snr[board,pid]
        self.hpbw_y_snr[board] = self.hpy_snr[board,pid]
        # now calculate the model for this board
        for i in range(self.n):
            self.model[board,i] = self.ap[board,pid]*math.exp(-4.*math.log(2.)*(((xpos[i]-self.xp[board,pid])/self.hpx[board,pid])**2+((ypos[i]-self.yp[board,pid])/self.hpy[board,pid])**2)) + self.bias[board]
    

    def process(self, w=16, remove_baseline=False, dd=50, ww=50, despike_scan=False, elim_bad_integrations = False, checksum=3936, flag_data=False, flag_windows=(),process_dual_beam=True,select_beam=1):
        """Runs the full fitting procedure for all boards."""
        for board in range(32):
            # clean up each scan
            if(elim_bad_integrations):
                self.elim_bad_integrations(board,checksum)
            if(despike_scan):
                self.despike(board,1)
            if(flag_data):
                self.flag_windows(board, flag_windows)
            if(remove_baseline):
                self.remove_baseline(board,dd,ww)
                
            # now that scan is cleaned up, we do the fit(s)
            if process_dual_beam:
                self.find_dual_beam(board,w)
            else:
                self.find_selected_beam(board,w,select_beam)
    

    def process_single_board(self, board=0, w=16, remove_baseline=False, dd=50, ww=50, despike_scan=False, elim_bad_integrations = False, checksum=3936, flag_data=False, flag_windows=(),process_dual_beam=True,select_beam=1):
        """Runs the full fitting procedure for a single specified band."""
        # doing the cleanup
        if(elim_bad_integrations):
            if self.elim_bad_integrations(board,checksum) != 0:
                return -1
        if(despike_scan):
            self.despike(board,1)
        if(flag_data):
            self.flag_windows(board, flag_windows)
        if(remove_baseline):
            self.remove_baseline(board,dd,ww)

        # now ready to do the fit
        if process_dual_beam:
            self.find_dual_beam(board,w)
        else:
            self.find_selected_beam(board,w,select_beam)
        return 0


    def beam_offsets(self, board):
        if self.receiver == 'Sequoia':
            if self.beam_selected >=0:
                board = self.beam_selected
            else:
                board = self.board_id(board)
            #print('              find beam offsets for pixel', board)
            theta = self.beamthrow_angle*math.pi/180.
            cosTheta = math.cos(theta)
            sinTheta = math.sin(theta)
            dr = 0
            du = 0
            elDes = self.elev*math.pi/180.
            cosEl = math.cos(elDes)
            sinEl = math.sin(elDes)
            j = board%4
            i = board/4
            di = (1.5-i)*self.beamthrow
            dj = (j-1.5)*self.beamthrow
            cos_sin = cosTheta*di-sinTheta*dj;
            sin_cos = sinTheta*di+cosTheta*dj;
            b = j*4+i;
            xx = -(cosEl*cos_sin + sinEl*sin_cos)
            yy = -(-sinEl*cos_sin + cosEl*sin_cos)
            x0 = x1 = xx - self.az_receiver
            y0 = y1 = yy - self.el_receiver
            #print('board ',board,i,j,xx,yy,self.az_receiver,self.el_receiver,x1,y1)
        else:
            elev_r = (self.elev+self.beamthrow_angle)*math.pi/180.
            y0 = self.beamthrow*math.sin(elev_r) - self.el_receiver
            x0 = -self.beamthrow*math.cos(elev_r) - self.az_receiver
            y1 = -self.beamthrow*math.sin(elev_r) - self.el_receiver
            x1 = self.beamthrow*math.cos(elev_r) - self.az_receiver
            #print('beam 0 ',x0,y0)
            #print('beam 1 ',x1,y1)
        return x0, y0, x1, y1
