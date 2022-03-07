"""Module with definition of classes of containers for fit results.

Classes: RSRMapFit, RSRM2Fit
Uses:    RSRMap, m2_model, TempSens, numpy, math
Author:  FPS
Date:    May 5, 2014
Changes:
"""
from RSRMap import RSRMap
from RSRUtilities import m2_model, TempSens
import numpy
import math

class RSRMapFit():
    """RSRMapFit holds and analyzes variables from pointing fits."""
    def __init__(self,process_list):
        """__init__ creates useful variables and prepares to load data from a fit."""
        self.band_order = [0,2,1,3,5,4]
        self.band_freq = [75.703906,82.003906,89.396094,94.599906,100.899906,108.292094]

        self.nchassis = len(process_list)
        nresults = 0
        for i in range(self.nchassis):
            nresults = nresults + len(process_list[i])
        self.nresults = nresults
        self.chassis_id_numbers = numpy.zeros(nresults)
        self.board_id_numbers = numpy.zeros(nresults)
        self.isGood = numpy.zeros(nresults)
        self.az_map_offset = numpy.zeros(nresults)
        self.el_map_offset = numpy.zeros(nresults)
        self.az_model_offset = numpy.zeros(nresults)
        self.el_model_offset = numpy.zeros(nresults)
        self.az_total_offset = numpy.zeros(nresults)
        self.el_total_offset = numpy.zeros(nresults)
        self.tracking_beam_position = True
        self.Intensity = numpy.zeros(nresults)
        self.hpbw = numpy.zeros(nresults)
        self.hpbw_x = numpy.zeros(nresults)
        self.hpbw_y = numpy.zeros(nresults)
        self.sep = numpy.zeros(nresults)
        self.ang = numpy.zeros(nresults)
        self.modrev = -1
        self.pointing_result = False
        self.hpbw_result = False
        # header variables we average 
        self.utdate = []
        self.ut1_h = []
        self.azim = []
        self.elev = []
        self.duration = []
        # m1 params
        self.m1ZernikeC0 = []
        # subreflector parameters
        self.m2x = []
        self.m2y = []
        self.m2z = []
        self.m2xPcor = []
        self.m2yPcor = []
        self.m2zPcor = []
        self.az_m2 = []
        self.el_m2 = []
        # tiltmeter parameters
        self.tilt_x = []
        self.tilt_y = []
        # temperature sensor parameters
        self.TemperatureSensors = []
                              
    def load_average_parameters(self,m):
        """Takes header data from RSRMap and adds it to the lists maintained by this object.

        Fits of data in multiple chassis have slightly different header variables.
        This procedure allows us to take averages later on.
        input m is an instance of an RSRMap..
        """
        # header variables
        self.utdate.append(m.utdate)
        self.ut1_h.append(m.ut1_h)
        self.azim.append(m.azim)
        self.elev.append(m.elev)
        self.m1ZernikeC0.append(m.m1ZernikeC0)
        self.m2z.append(m.m2z)
        self.m2y.append(m.m2y)
        self.m2x.append(m.m2x)
        self.m2zPcor.append(m.m2zPcor)
        self.m2yPcor.append(m.m2yPcor)
        self.m2xPcor.append(m.m2xPcor)
        self.az_m2.append(m.az_m2)
        self.el_m2.append(m.el_m2)
        self.duration.append(m.duration)
        # tiltmeters
        self.tilt_x.append(m.tilt0_x)
        self.tilt_y.append(m.tilt0_y)
        # Temperatures
        self.TemperatureSensors.append(m.T.tempsens)
        # load these too in case the fit fails
        self.receiver = m.receiver
        self.source = m.source
        self.date = m.date
        self.obsnum = m.obsnum
        self.n = m.n
    
    def get_duration(self):
        return (numpy.mean(self.duration),numpy.std(self.duration))

    def get_az_m2(self):
        return (numpy.mean(self.az_m2),numpy.std(self.az_m2))

    def get_el_m2(self):
        return (numpy.mean(self.el_m2),numpy.std(self.el_m2))

    def get_tilt_x(self):
        return (numpy.mean(self.tilt_x),numpy.std(self.tilt_x))

    def get_tilt_y(self):
        return (numpy.mean(self.tilt_y),numpy.std(self.tilt_y))

    def get_m1zer(self):
        return (numpy.mean(self.m1ZernikeC0),numpy.std(self.m1ZernikeC0))
    
    def get_m2z(self):
        return (numpy.mean(self.m2z),numpy.std(self.m2z))
    
    def get_m2y(self):
        return (numpy.mean(self.m2y),numpy.std(self.m2y))
    
    def get_m2x(self):
        return (numpy.mean(self.m2x),numpy.std(self.m2x))
    
    def get_m2zPcor(self):
        return (numpy.mean(self.m2zPcor),numpy.std(self.m2zPcor))
    
    def get_m2yPcor(self):
        return (numpy.mean(self.m2yPcor),numpy.std(self.m2yPcor))
    
    def get_m2xPcor(self):
        return (numpy.mean(self.m2xPcor),numpy.std(self.m2xPcor))
    
    def get_azim(self):
        return (numpy.mean(self.azim),numpy.std(self.azim))

    def get_elev(self):
        return (numpy.mean(self.elev),numpy.std(self.elev))

    def get_TemperatureSensors(self):
        """Returns an array of temperature data for this observation."""
        array = numpy.zeros(64)
        n = len(self.TemperatureSensors)
        for i in range(64):
            x = 0.
            for j in range(n):
                array[i] = array[i] + self.TemperatureSensors[j][i]
            array[i] = array[i]/n
        return array

    def load_chassis_board_result(self,m,index,chassis_id,board,board_id):
        """Loads all resuts and relevant parameters for a particular chassis and board."""
        if index == 0:
            # for the first one loaded, we set things that don't change
            self.modrev = m.modrev
            self.receiver = m.receiver
            self.source = m.source
            self.date = m.date
            self.obsnum = m.obsnum
            self.tracking_beam = m.tracking_beam
            self.fit_beam_is_tracking_beam = m.fit_beam_is_tracking_beam
            self.fit_beam_single = m.fit_beam_single
            self.fit_beam = m.fit_beam

        # now load things that change from one board/chassis to the next
        self.chassis_id_numbers[index] = m.chassis
        self.board_id_numbers[index] = board
        # compute pointing results based on whether we are doing a single beam or two.
        self.isGood[index] = m.isGood[board]
        if self.fit_beam_single:
            if self.fit_beam_is_tracking_beam == True:
                # if doing a single beam fit and tracking the beam, we can analyze easily
                self.az_map_offset[index] = m.azoff[board]
                self.el_map_offset[index] = m.eloff[board]
                self.az_model_offset[index] = m.azoff[board]+m.az_user+m.az_paddle
                self.el_model_offset[index] = m.eloff[board]+m.el_user+m.el_paddle
                self.az_total_offset[index] = m.azoff[board]+m.az_total-m.az_receiver-m.az_m2
                self.el_total_offset[index] = m.eloff[board]+m.el_total-m.el_receiver-m.el_m2
            else:
                # on the other hand, if we are doing single beam and tracking the other: be careful
                x0,y0,x1,y1 = m.beam_offsets(board)
                if self.fit_beam == 0:
                    yoffset = x0
                    xoffset = y0
                else:
                    yoffset = x1
                    xoffset = y1
                self.el_map_offset[index] = m.eloff[board] - yoffset
                self.az_map_offset[index] = m.azoff[board] - xoffset
                self.az_model_offset[index] = m.azoff[board] - xoffset +m.az_user+m.az_paddle
                self.el_model_offset[index] = m.eloff[board] - yoffset +m.el_user+m.el_paddle
                self.az_total_offset[index] = m.azoff[board] - xoffset +m.az_total-m.az_receiver-m.az_m2
                self.el_total_offset[index] = m.eloff[board] - yoffset +m.el_total-m.el_receiver-m.el_m2
        else:
            # this is analysis of traditional two-beam map
            self.az_map_offset[index] = m.azoff[board]+m.az_receiver
            self.el_map_offset[index] = m.eloff[board]+m.el_receiver
            self.az_model_offset[index] = m.azoff[board]+m.az_user+m.az_paddle+m.az_receiver
            self.el_model_offset[index] = m.eloff[board]+m.el_user+m.el_paddle+m.el_receiver
            self.az_total_offset[index] = m.azoff[board]+m.az_total-m.az_m2
            self.el_total_offset[index] = m.eloff[board]+m.el_total-m.el_m2
        
        self.Intensity[index] = m.I[board]
        self.hpbw[index] = m.hpbw[board]
        self.hpbw_x[index] = m.hpbw_x[board]
        self.hpbw_y[index] = m.hpbw_y[board]
        self.sep[index] = m.beamsep[board]
        if self.sep[index] == 0:
            self.ang[index] = 0
        else:
            if m.beamang[board]<0:
                self.ang[index] = -m.beamang[board]-m.elev
            else:
                self.ang[index] = 180.0-m.beamang[board]-m.elev


    def find_pointing_result(self):
        """Finds the final results and standard deviation after all results are loaded."""
        print(('az_map_offset',self.az_map_offset))
        print(('el_map_offset',self.el_map_offset))
        print(('isGood',self.isGood, self.isGood.any()))
        print(('az_map_offset[isGood]',self.az_map_offset[numpy.nonzero(self.isGood)]))
        print(('el_map_offset[isGood]',self.el_map_offset[numpy.nonzero(self.isGood)]))

        self.pointing_result = self.isGood.any()
        if self.pointing_result:
            self.mean_az_map_offset = numpy.mean(self.az_map_offset[numpy.nonzero(self.isGood)])
            self.std_az_map_offset = numpy.std(self.az_map_offset[numpy.nonzero(self.isGood)])
            self.mean_el_map_offset = numpy.mean(self.el_map_offset[numpy.nonzero(self.isGood)])
            self.std_el_map_offset = numpy.std(self.el_map_offset[numpy.nonzero(self.isGood)])

            self.mean_hpbw_az_map = numpy.mean(self.hpbw_x[numpy.nonzero(self.isGood)])
            self.mean_hpbw_el_map = numpy.mean(self.hpbw_y[numpy.nonzero(self.isGood)])
            self.mean_hpbw_map = numpy.mean(self.hpbw[numpy.nonzero(self.isGood)])
            
            self.mean_az_model_offset = numpy.mean(self.az_model_offset[numpy.nonzero(self.isGood)])
            self.std_az_model_offset = numpy.std(self.az_model_offset[numpy.nonzero(self.isGood)])
            self.mean_el_model_offset = numpy.mean(self.el_model_offset[numpy.nonzero(self.isGood)])
            self.std_el_model_offset = numpy.std(self.el_model_offset[numpy.nonzero(self.isGood)])

            self.mean_az_total_offset = numpy.mean(self.az_total_offset[numpy.nonzero(self.isGood)])
            self.std_az_total_offset = numpy.std(self.az_total_offset[numpy.nonzero(self.isGood)])
            self.mean_el_total_offset = numpy.mean(self.el_total_offset[numpy.nonzero(self.isGood)])
            self.std_el_total_offset = numpy.std(self.el_total_offset[numpy.nonzero(self.isGood)])

            self.mean_sep = numpy.mean(self.sep)
            self.std_sep = numpy.std(self.sep)

            self.mean_ang = numpy.mean(self.ang)
            self.std_ang = numpy.std(self.ang)

            
        else:
            self.mean_az_map_offset = 0
            self.std_az_map_offset = 0
            self.mean_el_map_offset = 0
            self.std_el_map_offset = 0

            self.mean_hpbw_map = 0

            self.mean_az_model_offset = 0
            self.std_az_model_offset = 0
            self.mean_el_model_offset = 0
            self.std_el_model_offset = 0

            self.mean_az_total_offset = 0
            self.std_az_total_offset = 0
            self.mean_el_total_offset = 0
            self.std_el_total_offset = 0

            self.mean_sep = 0
            self.std_sep = 0

            self.mean_ang = 0
            self.std_ang = 0
            

    def find_hpbw_result(self):
        """Derives the Half Power Beam Widths of fits."""
        self.mean_hpbw = numpy.zeros(32)
        self.std_hpbw = numpy.zeros(32)
        self.ratio_hpbw = []
        for band in range(32):
            band_list = []
            for i in range(self.nresults):
                if self.board_id_numbers[i] == self.band_order[band%6]:
                    band_list.append(self.hpbw[i])
            if len(band_list)>0:
                self.mean_hpbw[band] = numpy.mean(band_list)
                self.std_hpbw[band] = numpy.std(band_list)
                self.ratio_hpbw.append((self.band_freq[band%6] * 1.0e9
                                        / 3.0e8 
                                        * 32.5
                                        * self.mean_hpbw[band]
                                        / 206265.)
                                       )
        # the "ratio" HPBW is ratio of HPBW to Lambda/D for each board
        # in this way we can combine results for different frequencies
        self.mean_hpbw_ratio = numpy.mean(self.ratio_hpbw)
        self.std_hpbw_ratio = numpy.std(self.ratio_hpbw)
        self.hpbw_result = True
    
class RSRM2Fit():
    """RSRM2Fit holds and analyzes variables for fitting pointing maps to derive M2 parameters.

    ONLY DOING Z RIGHT NOW>>>>
    """
    def __init__(self,F,m2pos=0):
        """__init__ sets up parameters to hold data from pointing maps for focus fit.

        
        input F is an array of RSRMapFit instances with data from pointing maps to be fit.
        """
        # get common information from first instance of RSRMapFit array
        self.receiver = F[0].receiver
        self.source = F[0].source
        self.date = F[0].date
        self.obsnum = F[0].obsnum
        self.n = F[0].nresults
        self.nscans = len(F)
        self.result_relative = numpy.zeros(self.n)
        self.result_absolute = numpy.zeros(self.n)
        self.data = numpy.zeros((self.nscans,self.n))
        self.board_id = numpy.zeros(self.n)
        self.chassis_id = numpy.zeros(self.n)
        for index in range(self.n):
            self.board_id[index] = F[0].board_id_numbers[index]
            self.chassis_id[index] = F[0].chassis_id_numbers[index]

        # now we load the data for each of the scans
        for scan_id in range(self.nscans):
            for index in range(self.n):
                self.data[scan_id,index] = F[scan_id].Intensity[index]
        # determine x,y,z or zernike
        M2zReq = []
        M2yReq = []
        M2xReq = []
        M1zer0 = []
        for scan_id in range(self.nscans):
            M2zReq.append(F[scan_id].m2z)
            M2yReq.append(F[scan_id].m2y)
            M2xReq.append(F[scan_id].m2x)
            M1zer0.append(F[scan_id].m1ZernikeC0)
        M2z = [item for sublist in M2zReq for item in sublist]
        M2y = [item for sublist in M2yReq for item in sublist]
        M2x = [item for sublist in M2xReq for item in sublist]
        M1zer0 = [item for sublist in M1zer0 for item in sublist]
        dx=max(M2x)-min(M2x)
        dy=max(M2y)-min(M2y)
        dz=max(M2z)-min(M2z)
        dzer=max(M1zer0)-min(M1zer0)
        if (dx == dy and dx == dz and dx == 0 and dzer == 0):
            #nothing's changing, an error should be thrown
            self.msg = "M2 or Zernike offsets are not changing in these files."
            m2pos = -1
        elif (dx != 0):
            if (dy != 0 or dz != 0 or dzer != 0):
                #more than one offset changing, throw an error
                self.msg = "More than one M2 offset is changing in these files."
                m2pos = -1
            else:
                self.M2zfocus = max(M2z)
                self.M2yfocus = max(M2y)
                m2pos = 2
        elif (dy != 0):
            if (dx != 0 or dz != 0 or dzer != 0):
                #more than one offset changing, throw an error
                self.msg = "More than one M2 or Zernike offset is changing in these files."
                m2pos = -1
            else:
                self.M2zfocus = max(M2z)
                self.M2xfocus = max(M2x)
                m2pos = 1
        elif (dz != 0):
            if (dx != 0 or dy != 0 or dzer != 0):
                #more than one offset changing, throw an error
                self.msg = "More than one M2 or Zernike offset is changing in these files."
                m2pos = -1
            else:
                self.M2yfocus = max(M2y)
                self.M2xfocus = max(M2x)
                m2pos = 0
        elif (dzer != 0):
            if (dx != 0 or dy != 0 or dz != 0):
                #more than one offset changing, throw an error
                self.msg = "More than one M2 or Zernike offset is changing in these files."
                m2pos = -1
            else:
                self.M2xfocus = max(M2x)
                self.M2yfocus = max(M2y)
                self.M2zfocus = max(M2z)
                m2pos = 3

        self.m2_position = numpy.zeros(self.nscans)
        self.m2_pcor = numpy.zeros(self.nscans)
        self.elev = numpy.zeros(self.nscans)
        self.m2pos = m2pos
        m2posLabel = {-1: 'Error', 0: 'Z', 1: 'Y', 2: 'X', 3: 'A'}
        print(("m2pos = ", m2pos, m2posLabel[m2pos]))
        if (m2pos == -1):
            print((self.msg))
        else:
            for scan_id in range(self.nscans):
                self.elev[scan_id],sig = F[scan_id].get_elev()
                if self.m2pos == 0:
                    ave,sig = F[scan_id].get_m2z()
                    pcor,pcorsig = F[scan_id].get_m2zPcor()
                elif self.m2pos == 1:
                    ave,sig = F[scan_id].get_m2y()
                    pcor,pcorsig = F[scan_id].get_m2yPcor()
                elif self.m2pos == 2:
                    ave,sig = F[scan_id].get_m2x()
                    pcor,pcorsig = F[scan_id].get_m2xPcor()
                else:
                    ave,sig = F[scan_id].get_m1zer()
                    pcor,pcorsig = [0,0]

                self.m2_position[scan_id] = ave
                self.m2_pcor[scan_id] = pcor
            self.parameters = numpy.zeros((self.n,3))
    
    def find_focus(self):
        """Uses data loaded in during creation of this instance to fit focus."""
        for index in range(self.n):
            ptp = numpy.zeros((3,3))
            ptr = numpy.zeros(3)
            f = numpy.zeros(3)
            ee = []
            I = []
            par = []
            pcor = []
            for scan_id in range(self.nscans):
                I.append(self.data[scan_id,index])
                par.append(self.m2_position[scan_id])
                pcor.append(self.m2_pcor[scan_id])
                f[0] = 1.
                f[1] = par[scan_id]
                f[2] = par[scan_id]*par[scan_id]
                for ii in range(3):
                    for jj in range(3):
                        ptp[ii][jj] = ptp[ii][jj] + f[ii]*f[jj]
                    ptr[ii] = ptr[ii] + f[ii]*I[scan_id]
            ptpinv = numpy.linalg.inv(ptp)
            self.parameters[index,:] = numpy.dot(ptpinv,ptr)
            if self.parameters[index,2] != 0:
                self.result_relative[index] = -self.parameters[index,1]/self.parameters[index,2]/2.
                self.result_absolute[index] = self.result_relative[index] + numpy.mean(pcor)
            else:
                self.result_relative[index] = None
                self.result_absolute[index] = None


    def fit_focus_model(self):
        """Uses best fit focus (Z) for each chassis/board result to fit linear focus model."""
        if self.n > 1:
            if self.receiver == 'RedshiftReceiver':
                xband = [-1,-.2,-.6,.2,1.,.6]
            else:
                xband = [index-0.5*(self.n-1) for index in range(self.n)]
            print(xband)
            ptp = numpy.zeros((2,2))
            ptr = numpy.zeros(2)
            pta = numpy.zeros(2)
            f = numpy.zeros(2)
            for index in range(self.n):
                if(math.isnan(self.result_relative[index])):
                    continue
                f[0] = 1.
                f[1] = xband[int(self.board_id[index])]
                for ii in range(2):
                    for jj in range(2):
                        ptp[ii][jj] = ptp[ii][jj] + f[ii]*f[jj]
                    ptr[ii] = ptr[ii] + f[ii]*self.result_relative[index]
                    pta[ii] = pta[ii] + f[ii]*self.result_absolute[index]
            ptpinv = numpy.linalg.inv(ptp)
            relative_focus_fit = numpy.dot(ptpinv,ptr)
            absolute_focus_fit = numpy.dot(ptpinv,pta)
            self.resids = numpy.zeros(self.n)
            resids_squared = 0.
            actual_n = 0
            for index in range(self.n):
                if(math.isnan(self.result_relative[index])):
                    continue
                self.resids[index] = self.result_relative[index] - relative_focus_fit[0] - relative_focus_fit[1]*xband[int(self.board_id[index])]
                resids_squared = resids_squared + self.resids[index]*self.resids[index]
                actual_n = actual_n + 1
            rms = math.sqrt(resids_squared/actual_n)
            focus_error = math.sqrt(ptpinv[0][0])*rms

            self.relative_focus_fit = relative_focus_fit[0]
            self.focus_error = focus_error
            self.absolute_focus_fit = absolute_focus_fit[0]
            self.focus_slope = relative_focus_fit[1]
            self.fit_rms = rms
        else:
            self.relative_focus_fit = self.result_relative[0]
            self.focus_error = 0
            self.absolute_focus_fit = self.result_absolute[0]
            self.focus_slope = 0
            self.fit_rms = 0
        if self.m2pos == 0:
            self.M2zfocus = self.relative_focus_fit
        elif self.m2pos == 1:
            self.M2yfocus = self.relative_focus_fit
        elif self.m2pos == 2:
            self.M2xfocus = self.relative_focus_fit
        elif self.m2pos == 3:
            self.M1ZernikeC0 = self.relative_focus_fit

