"""Module contains "View" classes for printouts and plots of poining data.

Classes: RSRViewer, RSRScanViewer, RSRMapViewer
Uses:    RSRCC, RSRMap, RSRMapFit, mapplotlib, math, numpy
Author:  FPS
Date:    May 5, 2014
Changes: 
"""
from RSRCC import RSRCC
from RSRMap import RSRMap
from RSRFit import RSRMapFit
import numpy
import matplotlib
from matplotlib import pyplot as pl
from matplotlib import mlab as mlab
import matplotlib.mlab as mlab
from mpl_toolkits.axes_grid1 import make_axes_locatable
#from mpl_toolkits.axes_grid import make_axes_locatable
#   The mpl_toolkits.axes_grid module was deprecated in Matplotlib 2.1 and will be removed two minor releases later.
#   Use mpl_toolkits.axes_grid1 and mpl_toolkits.axisartist, which provide the same functionality instead.

import math
import sys
import time
import traceback
import scipy.interpolate as interp

class RSRViewer():
    """Base Class of Viewer"""
    def __init__(self):
        self.bigfig=None
   
    def init(self,a):
        """Initializes Interactive pyplot; closes all open windows"""
        if False:
            if a.show_ion == 1:
                pl.ion()
                pl.close('all')
            elif a.show_ion == 0:
                pl.ioff()
        self.bigfig = None
    def init_fig(self,figno=1,figsize=(12,5)):
        """Initializes a figure"""
        #pl.figure(num=figno,figsize=figsize)
        pl.clf()
    def init_big_fig(self,figno=1,figsize=(12,8),chassis_list=[0],process_list=[[0,1,2,3,4,5]],filelist=None):
        """Initializes a figure"""
        if self.bigfig != None:
            return
        self.nrows = max(chassis_list)+1
        self.ncols = 0
        flat_list = [item for sublist in process_list for item in sublist]
        for proc_l in process_list:
            if proc_l:
                self.ncols = max(self.ncols,max(proc_l)+1)
                if self.nrows == 1 and self.ncols > 4:
                    self.nrows = int(math.ceil(float(self.ncols)/4.))
                    self.ncols = 4
        if filelist is not None:
            for f in filelist:
                if 'Redshift' in f:
                    self.ncols = 6
                    self.nrows = 4
                    break
                elif 'spec' in f:
                    self.ncols = 4
                    self.nrows = 4
                    break

        if len(flat_list) == 1:
            self.nrows = 1
            self.ncols = 1

        if True:
            print(('chassis_list', chassis_list))
            print(('process_list', process_list))
            print(('nrows', self.nrows))
            print(('ncols', self.ncols))

        #self.grid = pl.GridSpec(self.nrows, self.ncols)
        figw = 12
        figh = 1.5*self.nrows+1
        if self.nrows == 1:
            figh = figh + 1#4
        #self.bigfig = pl.figure(num=figno,figsize=(figw,figh))
        self.bigfig = True
        pl.clf()

    def show(self):
        pl.show()

    def save(self, filename):
        pl.savefig(filename, bbox_inches='tight')
                

class RSRScanViewer(RSRViewer):
    """Viewer with methods to plot basic compressed continuum scans."""
    def plot_scan(self,m,board,label_it=True,ax=None):
        """Plots an individual scan from a single board.

        m is the input RSRMap
        board specifies which board's data to plot
        the label_it logical variable tells whether to add labels
        """
        if ax is None:
            ax = pl.gca()
        ax.plot(m.data[:,board])
        # limits
        maxi = numpy.max(m.data[:,board])
        mini = numpy.min(m.data[:,board])
        xlo = 0
        xhi = len(m.data[:,board])

        if label_it:
            ax.set_xlabel('Sample')
            ax.set_ylabel('Data Number')
            #pl.title('Date %s Obsnum %d Chassis %d Board %d'%(m.date,m.obsnum,m.chassis,board))
            ax.set_title(str(m.obsnum)+' '+m.source[0:20]+' Chassis='+str(m.chassis)+' Board='+str(board))
            ax.text(xhi,mini+0.8*(maxi-mini),('%d'%(maxi)),horizontalalignment='right')
        else:
            ax.text(xhi,mini+0.8*(maxi-mini),('%d'%(maxi)),horizontalalignment='right')
            ax.text(xhi,mini+0.5*(maxi-mini),('%d'%(board)),horizontalalignment='right')
    
    def plot_all_scans(self,m,board_list,figno=1):
        """Plots a single figure with data from all boards.
        
        m is the input RSRMap
        board_list is the list of boards to be plotted in the figure
        figno specifies the figure number to receive the plot
        """
        # initialize the figure
        self.init_fig(figno)
        # specify some details about plot orders and labels
        plot_order = [1,3,5,2,4,6]
        label_y_axis = [True, True, True, False, False, False]
        label_x_axis = [False, False, True, False, False, True]
        # now plot all the boards in separate subplots
        for i in board_list:
            ax = pl.subplot(3,2,plot_order[i])
            ###ax.tick_params(axis='both',which='major',labelsize=6)
            if label_y_axis[i]:
                pl.ylabel('Data Number')
            if label_x_axis[i]:
                pl.xlabel('Sample')
            else:
                ax.set_xticklabels([])
            self.plot_scan(m,i,label_it=False)
            pl.subplots_adjust(hspace=0.1)
        # titles
        pl.subplot(3,2,1)
        pl.title('%s'%(m.source[0:20]))
        pl.subplot(3,2,2)
        pl.title('%s %d Chassis %d'%(m.date,m.obsnum,m.chassis))

    def master_scan_plot(self,m,board_list):
        """Plots a single figure with data from all chassis/boardss.
        
        m is the input RSRMap (will be one  of 4)
        
        board_list is the list of boards to be plotted in the figure 
           for this chassis
        figno specifies the figure number to receive the plot
        """
        # specify some details about plot orders and labels
        plot_order = [1,3,5,2,4,6]
        if m.chassis == 0:
            label_y_axis = [True, True, True, False, False, False]
        else:
            label_y_axis = [False, False, False, False, False, False]
            
        label_x_axis = [False, False, True, False, False, True]
        # now plot all the boards in separate subplots
        for i in board_list:
            plot_index = int(6*m.chassis+i+1)
            ax = pl.subplot(4,6,plot_index)

            if m.chassis<3:
                ax.set_xticklabels([])
            else:
                ###ax.tick_params(axis='both',which='major',labelsize=6)
                pl.xlabel('Sample')
            if i > 0:
                ax.set_yticklabels([])
            else:
                ###ax.tick_params(axis='both',which='major',labelsize=6)
                pl.ylabel('Chassis %d'%(m.chassis))
            if m.chassis == 0:
                pl.title('Board %d'%(i))
            self.plot_scan(m,i,label_it=False)
            pl.subplots_adjust(hspace=0.1)
        # titles
        pl.suptitle('%20s %s %d'% 
                    (m.source[0:20],
                     m.date,
                     m.obsnum),
                    size=16)


    
class RSRMapViewer(RSRScanViewer):
    """Viewer for Pointing Maps."""
    def plot_model_scan(self,m,board,label_it=True):
        """Plots a single board of pointing map data as a scan with model and rediduals overlayed.

        m is the input RSRMap
        board specifies the board to be plotted
        label_it logical tells whether to include labels on figure.
        """
        # limits
        maxi = numpy.max(m.data[:,board])
        mini = numpy.min(m.data[:,board])
        xlo = 0
        xhi = len(m.data[:,board])

        # create array to plot
        plot_array = numpy.zeros(m.n)
        for i in range(m.n):
            if m.flag[board,i] == 1:
                plot_array[i] = numpy.nan
            else:
                plot_array[i] = m.data[i,board]
        # now plot array, model and residuals
        pl.plot(plot_array,'k',label='data')
        pl.plot(m.model[board,:],'r',label='model')
        if m.fit_beam_single:
            plot_offset = (m.ap[board,m.set_pid[m.chassis][m.fit_beam]]+m.bias[board])
        else:
            plot_offset = (m.ap[board,1]+m.bias[board])

        pl.plot(m.peak[m.set_pid[m.chassis][m.fit_beam]]*(plot_array-m.model[board,:])+plot_offset,'g',label='residuals')
        # and label the graph if specified
        if label_it:
            pl.legend(loc=4)
            pl.xlabel('Sample')
            pl.ylabel('Data Number')
            pl.title('Date %s Obsnum %d Chassis %d Board %d'%(m.date,m.obsnum,m.chassis,board))
            pl.text(xhi,mini+0.5*(maxi-mini),('%d'%(m.ap[board,m.set_pid[m.chassis][m.fit_beam]])),horizontalalignment='right')
        else:
            pl.text(xhi,mini+0.5*(maxi-mini),('%d'%(m.ap[board,m.set_pid[m.chassis][m.fit_beam]])),horizontalalignment='right')
            #pl.text(xhi,mini+0.2*(maxi-mini),('%d'%(board)),horizontalalignment='right')
    
    def plot_map_and_model(self,m,board,figno=1,fit_window=16,label_it=True):
        """Plots data from a board as a map and a scan with model overlayed."""
        self.init_fig(figno)
        pl.subplot(2,1,1)
        self.plot_map(m,board,fit_window)
        pl.subplot(2,1,2)
        self.plot_model_scan(m,board,False)
    
    def plot_all_model_scans(self,m,board_list,figno=1,label_it=True):
        """Plots model scans from all boards in a single figure."""
        self.init_fig(figno)
        plot_order = [1,3,5,2,4,6]
        label_y_axis = [True, True, True, False, False, False]
        label_x_axis = [False, False, True, False, False, True]
        for i in board_list:
            ax = pl.subplot(3,2,plot_order[i])
            ###ax.tick_params(axis='both',which='major',labelsize=6)
            if label_y_axis[i]:
                pl.ylabel('Data Number')
            if label_x_axis[i]:
                pl.xlabel('Sample')
            else:
                ax.set_xticklabels([])
            self.plot_model_scan(m,i,label_it=False)
            pl.subplots_adjust(hspace=0.1)
        pl.subplot(3,2,1)
        pl.title('%s'%(m.source[0:20]))
        pl.subplot(3,2,2)
        pl.title('%s %d Chassis %d'%(m.date,m.obsnum,m.chassis))

    def master_model_scan_plot(self,m,board_list):
        """Plots model scans from all boards in a single figure."""
        plot_order = [1,3,5,2,4,6]
        if m.chassis == 0:
            label_y_axis = [True, True, True, False, False, False]
        else:
            label_y_axis = [False, False, False, False, False, False]            
        label_x_axis = [False, False, True, False, False, True]
        for i in board_list:
            plot_index = int(6*m.chassis+i+1)
            ax = pl.subplot(4,6,plot_index)
            if m.chassis<3:
                ax.set_xticklabels([])
            else:
                ###ax.tick_params(axis='both',which='major',labelsize=6)
                pl.xlabel('Sample')
            if i > 0:
                ax.set_yticklabels([])
            else:
                ###ax.tick_params(axis='both',which='major',labelsize=6)
                pl.ylabel('Chassis %d'%(m.chassis))
            if m.chassis == 0:
                pl.title('Board %d'%(i))
            self.plot_model_scan(m,i,label_it=False)
            pl.subplots_adjust(hspace=0.1)
        # titles
        pl.suptitle('%20s %s %d'% 
                    (m.source[0:20],
                     m.date,
                     m.obsnum),
                    size=16)




    def print_all_results(self,m,board_list):
        """Prints out results of fit to screen for boards specified in board_list"""
        az_map_offset = numpy.zeros(len(board_list))
        el_map_offset = numpy.zeros(len(board_list))
        az_model_offset = numpy.zeros(len(board_list))
        el_model_offset = numpy.zeros(len(board_list))
        hpbws = numpy.zeros(len(board_list))
        print('----- --------  ----- -----    ----- -----   -----    ----- -----')
        print('                                 Offset')
        print(('Board    I      Map Offset     wrt Model %d    HPBW     SEP   ANG'%(m.modrev)))
        print('                 dAz   dEl      dAz   dEl ')           
        print('----- --------  ----- -----    ----- -----   -----    ----- -----')
        for idx,i in enumerate(board_list):
            az_map_offset[idx] = m.azoff[i]+m.az_receiver
            el_map_offset[idx] = m.eloff[i]+m.el_receiver
            az_model_offset[idx] = m.azoff[i]+m.az_user+m.az_paddle+m.az_receiver
            el_model_offset[idx] = m.eloff[i]+m.el_user+m.el_paddle+m.el_receiver
            hpbws[idx] = (math.sqrt(m.hpx[i][0]*m.hpy[i][0])+math.sqrt(m.hpx[i][1]*m.hpy[i][1]))/2.
            print(('  %d   %8.1f %5.1f %5.1f    %5.1f %5.1f    %5.1f    %5.1f %5.1f' %
                   (i,
                    m.I[i],
                    az_map_offset[idx],
                    el_map_offset[idx],
                    az_model_offset[idx],
                    el_model_offset[idx],
                    hpbws[idx],
                    m.beamsep[i],
                    m.beamang[i])
                   ))
        print('----- --------  ----- -----    ----- -----   -----    ----- -----')
        print(('Averages       %5.1f %5.1f    %5.1f %5.1f             %5.1f %5.1f' %
               (numpy.mean(az_map_offset),
                numpy.mean(el_map_offset),
                numpy.mean(az_model_offset),
                numpy.mean(el_model_offset),
                numpy.mean(m.beamsep[:]),
                numpy.mean(m.beamang[:]))
               ))
        print(('Errors         %5.1f %5.1f    %5.1f %5.1f             %5.1f %5.1f' %
               (numpy.std(az_map_offset),
                numpy.std(el_map_offset),
                numpy.std(az_model_offset),
                numpy.std(el_model_offset),
                numpy.std(m.beamsep[:]),
                numpy.std(m.beamang[:]))
               ))
    
    def print_result(self,m,board=0):
        """Prints results from a model fit to a single board."""
        az_map_offset = m.azoff[board]+m.az_receiver
        el_map_offset = m.eloff[board]+m.el_receiver
        az_model_offset = m.azoff[board]+m.az_user+m.az_paddle+m.az_receiver
        el_model_offset = m.eloff[board]+m.el_user+m.el_paddle+m.el_receiver
        hpbws = (math.sqrt(m.hpx[board][0]*m.hpy[board][0])+math.sqrt(m.hpx[board][1]*m.hpy[board][1]))/2.
        print('----- --------  ----- -----    ----- -----   -----    ----- -----')
        print('                                 Offset')
        print(('Board    I      Map Offset     wrt Model %d    HPBW     SEP   ANG'%(m.modrev)))
        print('                 dAz   dEl      dAz   dEl ')           
        print('----- --------  ----- -----    ----- -----   -----    ----- -----')
        print(('  %d   %8.1f %5.1f %5.1f    %5.1f %5.1f    %5.1f    %5.1f %5.1f' %
               (board,
                m.I[board],
                az_map_offset,
                el_map_offset,
                az_model_offset,
                el_model_offset,
                hpbws,
                m.beamsep[board],
                m.beamang[board])
               ))
        print('----- --------  ----- -----    ----- -----   -----    ----- -----')
    
    def plot_all(self,m,board_list=(0,1,2,3,4,5),figno=1,fit_window=16,show_samples=False):
        """Plots all maps together in a single figure."""
        self.init_fig(figno)
        plot_order = [1,3,5,2,4,6]
        label_y_axis = [True, True, True, False, False, False]
        label_x_axis = [False, False, True, False, False, True]
        for i in board_list:
            ax = pl.subplot(3,2,plot_order[i])
            ###ax.tick_params(axis='both',which='major',labelsize=6)
            if label_y_axis[i]:
                pl.ylabel('Elevation (arcsec)')
            else:
                ax.set_yticklabels([])
            if label_x_axis[i]:
                pl.xlabel('Azimuth (arcsec)')
            else:
                ax.set_xticklabels([])
            self.plot_map(m,i,fit_window,label_it=False,show_samples=show_samples)
            pl.subplots_adjust(hspace=0.001,wspace=0.001)
        pl.subplot(3,2,1)
        pl.title('%s'%(m.source[0:20]))
        pl.subplot(3,2,2)
        pl.title('%s %d Chassis %d'%(m.date,m.obsnum,m.chassis))

    
    def master_map_plot(self,m,chassis,chassis_list=(0,1,2,3),board_list=(0,1,2,3,4,5),figno=1,fit_window=16,show_samples=False):
        """Plots all maps together in a single figure."""
        row = chassis
        need_y_label = True
        if m.receiver == "Sequoia":
            index_list = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]
            b_list = [i for i in range(16)]
            board_label = 'Pixel'
            single_chassis = (m.num_pixels == 16)
            single_board = (len(board_list) == 1)
        elif m.receiver == "RedshiftReceiver":
            index_list = [i for i in range(24)]
            b_list = [i for i in range(6)]
            board_label = 'Board'
            single_chassis = False
            single_board = False
            single_chassis = (len(board_list) == 1)
            single_board = (len(board_list) == 1)
        else:
            index_list = board_list
            b_list = board_list
            board_label = 'Pixel'
            single_chassis = True
            single_board = False

        col = 0

        for i in range(len(b_list)):
            if i in board_list or True:
                # create plot
                index = row*self.ncols+col
                if single_chassis:
                    index = i
                if single_board:
                    index = 0
                #print 'coord', row, col, index, i, index_list[index]+1
                print('subplot',self.nrows, self.ncols, index_list[index]+1) 
                ax = pl.subplot(self.nrows, self.ncols, index_list[index]+1)

                # plot
                if i not in board_list:
                    valid = False
                else:
                    valid = True
                self.plot_map(m,i,fit_window,label_it=False,show_samples=show_samples,valid=valid)

                #title the first row
                if row == 0 and False:
                    ax.set_title('%s %d'%(board_label, i))

                #x label the last row
                if single_board or (index_list[index]>=(self.nrows-1)*self.ncols):
                    for tick in ax.get_xticklabels():
                        tick.set_rotation(60)
                    ax.set_xlabel('Azimuth\n(arcsec)')
                else:
                    ax.set_xticklabels([])

                #y label the first col
                if single_board or (index_list[index]%self.ncols) == 0:
                    if m.receiver == 'RedshiftReceiver':
                        ax.set_ylabel('Chassis %d\nElevation\n(arcsec)'%chassis)
                    else:
                        ax.set_ylabel('Elevation\n(arcsec)')
                else:
                    ax.set_yticklabels([])

            #now can step
            col = col + 1
            if col == self.ncols:
                col = 0
                row = row + 1
            
        # titles
        #pl.suptitle('%20s %s %d'% (m.source[0:20], m.date, m.obsnum), size=16)
        pl.savefig('rsr_pointing_maps.png', bbox_inches='tight')
        #pl.gcf().subplots_adjust(hspace=0.001,wspace=0.1)
        pl.gcf().subplots_adjust(hspace=0.5,wspace=0.5)

    def plot_pointing_result(self,m,figno=1):
        """Plots the pointing results together in a single figure."""
        self.init_fig(figno=figno)
        pl.subplot(1,2,1)
        pl.plot(m.azoff[:]+m.az_receiver,m.eloff[:]+m.el_receiver,'o')
        pl.plot(numpy.mean(m.azoff[:])+m.az_receiver,numpy.mean(m.eloff[:])+m.el_receiver,'r+',markersize=20)
        pl.axis('equal')
        pl.axis([-36,36,-36,36])
        pl.grid()
        pl.xlabel('Az Map Offset (arcsec)')
        pl.ylabel('El Map Offset (arcsec)')
        pl.title('Map Offset')
        pl.subplot(1,2,2)
        pl.plot(m.azoff[:]+m.az_user+m.az_paddle+m.az_receiver,m.eloff[:]+m.el_user+m.el_paddle+m.el_receiver,'o')
        pl.plot(numpy.mean(m.azoff[:])+m.az_user+m.az_paddle+m.az_receiver,numpy.mean(m.eloff[:])+m.el_user+m.el_paddle+m.el_receiver,'r+',markersize=20)
        pl.axis('equal')
        pl.axis([-36,36,-36,36])
        pl.grid()
        pl.xlabel('Az Model Offset (arcsec)')
        pl.ylabel('El Model Offset (arcsec)')
        pl.title('Offset wrt Model %d'%(m.modrev))
    

    def plot_map(self,m,board=0,fit_window=16,label_it=True,show_samples=False,valid=True,ax=None,fig=None):
        """Plots a single pointing map."""
        if ax is None:
            ax = pl.gca()
        
        if m.fit_beam_single and m.fit_beam_is_tracking_beam:
            maplimits = [-50, 50, -50, 50]
        else:
            if m.beamthrow > 100:
                maplimits = [-200, 200, -200, 200]
            else:
                maplimits = [-100, 100, -100, 100]
        mapgrid = 4
        if m.xpos.ndim == 2:
            xpos = m.xpos[:,board]
            ypos = m.ypos[:,board]
        else:
            xpos = m.xpos
            ypos = m.ypos

        if True or m.beamthrow == 0:
            maplimits = [min(xpos), max(xpos), min(ypos), max(ypos)]
        nx = int((maplimits[1]-maplimits[0])/mapgrid+1)
        ny = int((maplimits[3]-maplimits[2])/mapgrid+1)
        nx = ny = min(nx, ny)
        xi = numpy.linspace(maplimits[0],maplimits[1],nx)
        yi = numpy.linspace(maplimits[2],maplimits[3],ny)
        plot_array = numpy.zeros(m.n)
        for i in range(m.n):
            if m.flag[board,i] == 1:
                plot_array[i] = 0.#numpy.nan
            else:
                plot_array[i] = m.flip[board]*(m.data[i,board]-m.bias[board]) # sign flip to match dreampy??

        xpos = xpos + numpy.random.random(xpos.size)*1e-6
        ypos = ypos + numpy.random.random(ypos.size)*1e-6
        #print 'griddata', len(xpos), len(xi), mapgrid, maplimits
        t0 = time.time()
        try:
            print('try scipy griddata linear')
            grid_x, grid_y = numpy.mgrid[maplimits[0]:maplimits[1]:complex(nx), maplimits[2]:maplimits[3]:complex(ny)]
            zi = interp.griddata((xpos,ypos),plot_array,(grid_x,grid_y),method='linear').T
        except Exception as e:
            try:
                print('try mlab griddata linear')
                zi = mlab.griddata(xpos,ypos,plot_array,xi,yi,interp='linear')
                print('griddata linear ok')
            except Exception as e:
                print('use mlab griddata default')
                zi = mlab.griddata(xpos,ypos,plot_array,xi,yi)
            print('griddata default ok')
        #print 'griddata time',time.time()-t0

        x0,y0,x1,y1 = m.beam_offsets(board)
        x0 = m.xmax
        y0 = m.ymax
        x1 = m.xmax
        y1 = m.ymax
        plot_circle0 = numpy.zeros((100,2))
        plot_circle1 = numpy.zeros((100,2))
        for i in range(100):
            plot_circle0[i,0] = x0+fit_window*math.cos(i/100.*2.*math.pi)
            plot_circle0[i,1] = y0+fit_window*math.sin(i/100.*2.*math.pi)
            plot_circle1[i,0] = x1+fit_window*math.cos(i/100.*2.*math.pi)
            plot_circle1[i,1] = y1+fit_window*math.sin(i/100.*2.*math.pi)

        
        if m.I[board]>0:
            if m.receiver == 'RedshiftReceiver':
                imagemax = m.I[board]/2.
                levels = [-0.95*imagemax,-0.75*imagemax,-0.5*imagemax,-0.25*imagemax,-0.1*imagemax,-0.05*imagemax,0.05*imagemax,0.1*imagemax,0.25*imagemax,0.5*imagemax,0.75*imagemax,0.95*imagemax]
            else:
                imagemax = m.I[board]
                levels = [0.05*imagemax,0.1*imagemax,0.25*imagemax,0.5*imagemax,0.75*imagemax,0.95*imagemax, 0.99*imagemax]
        else:
            if m.receiver == 'RedshiftReceiver':
                imagemax = numpy.max(plot_array)
                levels = [-0.95*imagemax,-0.75*imagemax,-0.5*imagemax,-0.25*imagemax,-0.1*imagemax,-0.05*imagemax,0.05*imagemax,0.1*imagemax,0.25*imagemax,0.5*imagemax,0.75*imagemax,0.95*imagemax, 0.99*imagemax]
            else:
                imagemax = numpy.max(plot_array)
                levels = [0.05*imagemax,0.1*imagemax,0.25*imagemax,0.5*imagemax,0.75*imagemax,0.95*imagemax, 0.99*imagemax]
        #print 'contour'
        try:
            ax.contour(xi,yi,zi,levels)
        except Exception as e:
            print(e)
            pass
        #print 'image'
        im = ax.imshow(zi,interpolation='bicubic',cmap=pl.cm.gray,origin='lower',extent=maplimits)
        if m.fit_beam_is_tracking_beam and m.fit_beam_single:
            if m.fit_beam == 0:
                ax.plot(plot_circle0[:,0],plot_circle0[:,1],'k')
            else:
                ax.plot(plot_circle1[:,0],plot_circle1[:,1],'w')
        else:
                ax.plot(plot_circle0[:,0],plot_circle0[:,1],'k')
                ax.plot(plot_circle1[:,0],plot_circle1[:,1],'k')
        if show_samples:
            ax.plot(xpos,ypos,'.')
        if not valid:
            x = [maplimits[0], maplimits[1]]
            y = [maplimits[2], maplimits[3]]
            ax.plot(x,y,'-r',linewidth=2)
            x = [maplimits[0], maplimits[1]]
            y = [maplimits[3], maplimits[2]]
            ax.plot(x,y,'-r',linewidth=2)
        ax.axis('equal')
        #ax = pl.gca()
        if fig is None:
            fig = pl.gcf()
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='5%', pad=0.05)
        cbar=fig.colorbar(im, cax=cax, orientation='vertical')
        #cbar=ax.colorbar()
        if label_it:
            ax.set_xlabel('Azimuth (arcsec)')
            ax.set_ylabel('Elevation (arcsec)')
            ax.set_title(str(m.obsnum)+' '+m.source[0:20]+' Chassis='+str(m.chassis)+' Board='+str(board))
        if m.isGood[board] or not valid:
            pltext = '%d.%d'%(m.chassis,m.board_id(board))
        else:
            pltext = '%d.%d Bad Fit'%(m.chassis,m.board_id(board))
        ax.text(maplimits[0]+0.0*(maplimits[1]-maplimits[0]),
                maplimits[3]+0.0*(maplimits[3]-maplimits[2]),
                pltext,horizontalalignment='left', color='red', fontsize=6,
                bbox=dict(facecolor='white', alpha=0.5))

class RSRFitViewer(RSRViewer):
    """Viewer class to handle Fit results."""
    def print_hpbw_result(self,F):
        """Printed summary table with HPBW fit results."""
        if F.hpbw_result == False:
            F.find_hpbw_result()
        print('---- ------ ----- -----  ------')
        print('Band  Freq   HPBW Error    L/D')
        print('---- ------ ----- -----  ------')
        for band in range(6):
            if F.mean_hpbw[band] == 0:
                print(('  %d  %6.2f No Data' %
                       (band,
                        F.band_freq[band])
                   ))
            else:
                print(('  %d  %6.2f %5.1f %5.1f  %6.3f' %
                       (band,
                        F.band_freq[band],
                        F.mean_hpbw[band],
                        F.std_hpbw[band],
                        F.band_freq[band]*1.0e9/3.0e8*32.5*F.mean_hpbw[band]/206265.)
                       ))
        print('---- ------ ----- -----  ------')

    def print_result(self,F):
        """Prints the result of a pointing fit."""
        if F.fit_beam_single:
            self.print_single_beam_result(F)
        else:
            self.print_dual_beam_result(F)

    def print_dual_beam_result(self,F):
        """Prints result of dual beam pointing fit."""
        print('------- ----- --------  ----- -----    ----- -----   -----    ----- -----')
        print('                                         Offset')
        print(('Chassis Board    I       Map Offset    wrt Model %d    HPBW     SEP   ANG'%(F.modrev)))
        print('                         dAz   dEl      dAz   dEl ')           
        print('------- ----- --------  ----- -----    ----- -----   -----    ----- -----')
        for i in range(F.nresults):
            print(('  %d       %d   %8.1f  %5.1f %5.1f    %5.1f %5.1f   %5.1f    %5.1f %5.1f' %
                   (F.chassis_id_numbers[i],
                    F.board_id_numbers[i],
                    F.Intensity[i],
                    F.az_map_offset[i],
                    F.el_map_offset[i],
                    F.az_model_offset[i],
                    F.el_model_offset[i],
                    F.hpbw[i],
                    F.sep[i],
                    F.ang[i])
                       ))
        print('------- ----- --------  ----- -----    ----- -----   -----    ----- -----')
    
    def print_single_beam_result(self,F):
        """Prints result of single beam pointing fit."""
        print(('Single Beam Fit to Beam %d'%(F.fit_beam))) 
        print('------- ----- --------  ----- -----    ----- -----   -----')
        print('                                         Offset')
        print(('Chassis Board    I       Map Offset    wrt Model %d    HPBW'%(F.modrev)))
        print('                         dAz   dEl      dAz   dEl ')           
        print('------- ----- --------  ----- -----    ----- -----   -----')
        for i in range(F.nresults):
            print(('  %d       %d   %8.1f  %5.1f %5.1f    %5.1f %5.1f   %5.1f' %
                   (F.chassis_id_numbers[i],
                    F.board_id_numbers[i],
                    F.Intensity[i],
                    F.az_map_offset[i],
                    F.el_map_offset[i],
                    F.az_model_offset[i],
                    F.el_model_offset[i],
                    F.hpbw[i])
                       ))
        print('------- ----- --------  ----- -----    ----- -----   -----')
    
    def print_header(self,F):
        """Prints header information pertaining to this fit."""
        print(('%20s utd=%s uth=%4.1f obs=%d az=%6.1f el=%5.1f  maptime=%5.1f  m2z=%5.1f'%(F.source[0:20],F.date,numpy.mean(F.ut1_h),F.obsnum,numpy.mean(F.azim),numpy.mean(F.elev),numpy.mean(F.duration),numpy.mean(F.m2z))))

    def print_summary_pointing(self,F):
        """Prints summary of pointing results."""
        if F.fit_beam_single:
            self.print_single_beam_summary_pointing(F)
        else:
            self.print_dual_beam_summary_pointing(F)

    def print_dual_beam_summary_pointing(self,F):
        """Prints summary of pointing results for dual beam fits."""
        if F.pointing_result == False:
            F.find_pointing_result()
        print(('Avergage Pointing:      %5.1f %5.1f    %5.1f %5.1f            %5.1f %5.1f' % 
               (F.mean_az_map_offset,
                F.mean_el_map_offset,
                F.mean_az_model_offset,
                F.mean_el_model_offset,
                F.mean_sep,
                F.mean_ang)
               ))
        print(('Pointing RMS     :      %5.1f %5.1f    %5.1f %5.1f            %5.1f %5.1f' %
               (F.std_az_map_offset,
                F.std_el_map_offset,
                F.std_az_model_offset,
                F.std_el_model_offset,
                F.std_sep,
                F.std_ang)
               ))

    def print_single_beam_summary_pointing(self,F):
        """Prints summary of pointing results for single beam fits."""
        if F.pointing_result == False:
            F.find_pointing_result()
        print(('Avergage Pointing:      %5.1f %5.1f    %5.1f %5.1f' % 
               (F.mean_az_map_offset,
                F.mean_el_map_offset,
                F.mean_az_model_offset,
                F.mean_el_model_offset)
               ))
        print(('Pointing RMS     :      %5.1f %5.1f    %5.1f %5.1f' %
               (F.std_az_map_offset,
                F.std_el_map_offset,
                F.std_az_model_offset,
                F.std_el_model_offset)
               ))

    def plot_pointing_summary(self,F,figno=1,axis=[-36,36,-36,36]):
        """Plots the pointing offsets determined by the fit."""
        self.init_fig(figno)
        pl.subplot(1,2,1)
        pl.plot(F.az_map_offset[numpy.nonzero(F.isGood)],F.el_map_offset[numpy.nonzero(F.isGood)],'o')
        pl.xlabel('Az Offset (arcsec)')
        pl.ylabel('El Offset (arcsec)')
        #pl.title('%s %s'%(F.receiver.strip(), F.source.strip()))
        #pl.axis('equal')
        axis = [x * 2 for x in axis] 
        pl.axis(axis)
        pl.grid()
        if F.n == 0:
            textstr = 'File has no data'          
        else:
            textstr =           'Az Map Offset:   %6.4f'%(F.mean_az_map_offset) + '\n' 
            textstr = textstr + 'El Map Offset:   %6.4f'%(F.mean_el_map_offset) + '\n' 
            #textstr = textstr + 'HPBW:   %6.4f'%(F.mean_hpbw_map) + '\n'
            textstr = textstr + 'Az HPBW:   %6.4f'%(F.mean_hpbw_az_map) + '\n'
            textstr = textstr + 'El HPBW:   %6.4f'%(F.mean_hpbw_el_map)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        pl.text(0, axis[3]*0.9, textstr, horizontalalignment='center', verticalalignment='top', bbox=props, color='red')
        pl.subplot(1,2,2)
        pl.plot(F.az_model_offset[numpy.nonzero(F.isGood)],F.el_model_offset[numpy.nonzero(F.isGood)],'o')
        pl.xlabel('Az Offset (arcsec)')
        #pl.title('%s %d'%(F.date,F.obsnum))
        #pl.axis('equal')
        axis2 = [x for x in axis] 
        pl.axis(axis2)
        #print axis2
        pl.grid()
        if F.n == 0:
            textstr = 'File has no data'          
        else:
            textstr =           'Az Model %d Offset:   %6.4f'%(F.modrev, F.mean_az_model_offset) + '\n' 
            textstr = textstr + 'El Model %d Offset:   %6.4f'%(F.modrev, F.mean_el_model_offset)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        pl.text(0, axis2[3]*0.9, textstr, horizontalalignment='center', verticalalignment='top', bbox=props, color='red')
        pl.suptitle('%s %s %s %d'%(F.receiver.strip(), F.source.strip(), F.date,F.obsnum))
        pl.savefig('rsr_summary.png', bbox_inches='tight')

    def write_temperature_log_entry(self,F,tfile):
        """Writes a log entry with temperature data for this fit to a file."""
        tfile.write('1 ')
        tfile.write('{0:d} '
                    .format(F.obsnum)
                    )
        tarray = F.get_TemperatureSensors()
        for i in range(64):
            tfile.write('{0:5.1f} '
                        .format(tarray[i])
                        )
        tfile.write('\n')

    def write_pointing_log_header(self,ofile):
        # Col 1 Flag
        ofile.write('Flag,')
        # Col 2 Date
        ofile.write('Date,')
        # Col 3 UTDate
        ofile.write('UTDate,')
        # Col 4 UT1 - hours
        ofile.write('UT1,')
        # Col 5 Obsnum
        ofile.write('ObsNum,')
        # Col 6 Source Name
        ofile.write('Source,')
        # Col 7,8 Az, El
        ofile.write('Az,El,')
        # Col 9,10,11 M2Z, M2Y, EL_M2
        ofile.write('M2Z,M2Y,EL_M2,')
        # Col 12,13,14,15 X and Y tilts and errors
        ofile.write('TxPar,TxStd,TyPar,TyStd,')
        # Col 16,17,18,19 Az, El Map offsets and Errors
        ofile.write('AzMapOff,AzMapErr,ElMapOff,ElMapErr,')
        # Col 20,21 HPBW ratio and error
        ofile.write('HpbwRatio,HpbwRatioErr,')
        # Col 22,23,24,25 sep, sep error, ang, ang_error
        ofile.write('Sep,SepErr,Ang,AngErr,')
        # Col 26 27 total azoff, eloff
        ofile.write('AzTotalOff,ElTotalOff,')
        # Col 28 29 model
        ofile.write('AzPointModelCor,ElPointModelCor,')
        # Col 30 ambient temp
        ofile.write('AmbientTemp\n')

    def write_pointing_log_entry(self,F,ofile):
        """Writes a log entry with pointing data for this fit to a file."""
        # Col 1 Flag
        ofile.write('1,')
        # Col 2 Date
        ofile.write('{:s},'
                    .format(F.date_ymd))
        # Col 3 UTDate
        ofile.write('{:.5f},'
                    .format(numpy.mean(F.utdate))
                    )
        # Col 4 UT1 - hours
        ofile.write('{:.1f},'
                    .format(numpy.mean(F.ut1_h))
                    )
        # Col 5 Obsnum
        ofile.write('{:d},'
                    .format(F.obsnum)
                    )
        # Col 6 Source Name
        ofile.write('{:s},'
                    .format(F.source[0:12])
                    )
        # Col 7,8 Az, El
        ofile.write('{:.1f},{:.1f},'
                    .format(F.get_azim()[0],
                            F.get_elev()[0])
                    )
        # Col 9,10,11 M2Z, M2Y, EL_M2
        ofile.write('{:.2f},{:.2f},{:.1f},'
                    .format(F.get_m2z()[0],
                            F.get_m2y()[0],
                            F.get_el_m2()[0])
                    )              
        # Col 12,13,14,15 X and Y tilts and errors
        txpar,txstd = F.get_tilt_x()
        typar,tystd = F.get_tilt_y()
        ofile.write('{:.1f},{:.1f},{:.1f},{:.1f},'
                    .format(txpar,txstd,typar,tystd)
                    )
        # Col 16,17,18,19 Az, El Map offsets and Errors
        ofile.write('{:.1f},{:.1f},{:.1f},{:.1f},'
                    .format(F.mean_az_map_offset,
                            F.std_az_map_offset,
                            F.mean_el_map_offset,
                            F.std_el_map_offset)
                    )
        # Col 20,21 HPBW ratio and error
        ofile.write('{:.3f},{:.3f},'
                    .format(F.mean_hpbw_ratio,
                            F.std_hpbw_ratio)
                    )
        # Col 22,23,24,25 sep, sep error, ang, ang_error
        ofile.write('{:.1f},{:.1f},{:.1f},{:.1f},'
                    .format(F.mean_sep,
                            F.std_sep,
                            F.mean_ang,
                            F.std_ang)
                    )
        # Col 26 27 total azoff, eloff
        ofile.write('{:.1f},{:.1f},'
                    .format(F.mean_az_total_offset,
                            F.mean_el_total_offset)
                    )
        # Col 28 29 model
        ofile.write('{:.1f},{:.1f},'
                    .format(F.mean_az_point_model_cor,
                            F.mean_el_point_model_cor)
                    )
        # Col Ambient Temp
        ofile.write('{:.2f}\n'
                    .format(F.weather_temperature)
                   )

class RSRM2FitViewer(RSRViewer):
    """Viewer for M2 Fitting."""
    def print_results(self,M):
        """Prints M2 fit results.
        
        M is the input RSRM2Fit instance with the results.
        """
        for index in range(M.n):
            if(math.isnan(M.result_relative[index])):
                continue
            result_max = (M.parameters[index,0] 
                          + M.parameters[index,1]*M.result_relative[index]
                          + M.parameters[index,2]*M.result_relative[index]*M.result_relative[index]
                          )
            print(('%d %d %5.1f   %6.2f %6.2f  %8.3f, %8.3f' %
                   (M.chassis_id[index],
                    M.board_id[index],
                    numpy.mean(M.elev),
                    M.result_relative[index],
                    M.result_absolute[index],
                    result_max,
                    M.parameters[index,2]/result_max if result_max != 0 else 0)
                   ))
    
    def print_summary_fit(self,M):
        print('--------------------------------------------------')
        print(('Summary: Rel %6.2f (%6.2f)   Abs %6.2f (%6.2f)' % (numpy.mean(M.result_relative),numpy.std(M.result_relative),numpy.mean(M.result_absolute),numpy.std(M.result_absolute))))
        print(' ')
    
    def plot_fits(self,M,figno=1):
        """Plots graphs of all data and fits.

        M is the input RSRM2Fit instance with the results.
        figno specifies the figure to receive the plot.
        """
        if M.receiver == "Sequoia":
            board_label = 'Pixel'
        else:
            board_label = 'Board'
        if M.m2pos == 0:
            self.xlabel = 'Z Offset'
            self.ylabel = 'Z offset (mm)'
            prange = numpy.arange(-7,7.1,.1)
        elif M.m2pos == 1:
            self.xlabel = 'Y Offset'
            self.ylabel = 'Y offset (mm)'
            prange = numpy.arange(-36,36.1,.1)
        elif M.m2pos == 2:
            self.xlabel = 'X Offset'
            self.ylabel = 'X offset (mm)'
            prange = numpy.arange(-36,36.1,.1)
        elif M.m2pos == 3:
            self.xlabel = 'ZernikeC0'
            self.ylabel = 'ZernikeC0 (um)'
            prange = numpy.arange(-1000,1000,10)
        else:
            self.xlabel = 'Offset'
            self.ylabel = 'Offset (mm)'
            prange = numpy.arange(-36,36.1,.1)
        prange = numpy.arange(min(M.m2_position)-.1,max(M.m2_position)+.1,.1)
        prange = numpy.arange(min(M.scans_xpos)-.1,max(M.scans_xpos)+.1,.1)
        didylabel = numpy.full(4, False)

        for index in range(M.n):
            if(math.isnan(M.result_relative[index])):
                continue
            mdata = M.data[:,index]
            model = (M.parameters[index,0]
                     + M.parameters[index,1]*prange
                     + M.parameters[index,2]*prange*prange
                     )
            mdata_max = numpy.max(mdata)
            if mdata_max >= 0:
                mdata = mdata/mdata_max
                model = model/mdata_max
            if self.nrows == 1 and self.ncols == 1:
                plot_index = 1
            else:
                plot_index = int(self.ncols*M.chassis_id[index]+M.board_id[index]+1)
            ax = pl.subplot(self.nrows,self.ncols,plot_index)
            pl.plot(M.m2_position,mdata,'o')
            pl.plot(prange,model,'r')
            pl.axhline(y=.5*numpy.max(mdata), color='b')
            pl.ylim(0., 1.1)
            ax.annotate("max\n%0.0f"%mdata_max, [prange[0]+0.1,0.8], fontsize=6)
            pl.subplots_adjust(hspace=0.001, wspace=0.001)
            if (self.nrows == 1 and self.ncols == 1):
                pl.xlabel(self.xlabel)
            elif M.chassis_id[index]<3:
                ax.set_xticklabels([])
            else:
                ###ax.tick_params(axis='both',which='major',labelsize=6)
                pl.xlabel(self.xlabel)

            if not didylabel[int((plot_index-1)/6)] or (self.nrows == 1 and self.ncols == 1):
                didylabel[int((plot_index-1)/6)] = True
                pl.ylabel('')
                #ax.tick_params(axis="y",direction="in", pad=-30)
            elif M.board_id[index] > 0:
                ax.set_yticklabels([])
            else:
                ###ax.tick_params(axis='both',which='major',labelsize=6)
                pl.ylabel('Chassis %d'%(M.chassis_id[index]))
            if M.chassis_id[index] == 0 or (self.nrows == 1 and self.ncols == 1):
                pl.title('%s %d'%(board_label, M.board_id[index]))
            #pl.suptitle('%20s %s %d'% (M.source[0:20], M.date, M.obsnum), size=16)
            pl.savefig('rsr_focus_fits.png', bbox_inches='tight')
        
    def print_focus_model_fit(self,M):
        """Prints result of focus model fit."""
        print(('%s %d %6.2f %6.2f %6.3f %6.2f %5.2f %6.2f %6.2f %6.2f' %
               (M.date,
                M.obsnum,
                M.relative_focus_fit,
                M.focus_error,
                M.focus_slope,
                M.absolute_focus_fit,
                M.fit_rms,
                M.M2zfocus,
                M.M2yfocus,
                M.M2xfocus)
              ))

    def plot_focus_model_fit(self,M,figno,obsNumArg):
        """Plots data and focus model fit."""
        ##pl.figure(figno)
        pl.clf()
        
        if M.receiver == 'RedshiftReceiver':
            band_order = [0,2,1,3,5,4]
            freq = [75.703906,82.003906,89.396094,94.599906,100.899906,108.292094]
            band_freq = []
            result_relative = []
            for index in range(M.n):
                if(math.isnan(M.result_relative[index])):
                    continue
                band_freq.append(freq[band_order[int(M.board_id[index])]])
                result_relative.append(M.result_relative[index])
            band_freq = numpy.array(band_freq)
            result_relative = numpy.array(result_relative)
            pl.plot(band_freq,result_relative,'o')
            freq_0 = (freq[0]+freq[5])/2.
            d_freq = (freq[5]-freq_0)
            brange = numpy.arange(-1.2,1.3,.1)
            f = freq_0+brange*d_freq
            the_model = M.relative_focus_fit+M.focus_slope*brange
            pl.plot(f,the_model,'r')
            pl.xlabel('Frequency (GHz)')
            xpos = 93
            ypos = result_relative.max()-0.3*(result_relative.max()-result_relative.min())
        else:
            result_relative = M.result_relative
            brange = numpy.arange(-0.5*(M.n-1),0.5*(M.n-1)+1,1)
            the_model = M.relative_focus_fit+(M.focus_slope)*brange
            pl.plot(brange,result_relative,'o')
            pl.plot(brange,the_model,'r')
            try:
                #pl.margins(1,1)
                #xpos = 3*brange[0]+.5
                #ypos = result_relative.max()+0.2*(result_relative.max()-result_relative.min())
                if len(brange) == 1:
                    xpos = brange[0]
                    ypos = result_relative*1.01
                else:
                    xpos = brange[0]+.5
                    ypos = result_relative.max()-0.2*(result_relative.max()-result_relative.min())
            except:
                if len(brange) == 1:
                    xpos = brange[0]
                    ypos = result_relative*1.01
                else:
                    xpos = brange[0]+.5
                    ypos = result_relative.max()-0.2*(result_relative.max()-result_relative.min())
        if M.m2pos == 0:
            self.xlabel = 'Z Offset'
            self.ylabel = 'Z offset (mm)'
            prange = numpy.arange(-7,7.1,.1)
        elif M.m2pos == 1:
            self.xlabel = 'Y Offset'
            self.ylabel = 'Y offset (mm)'
            prange = numpy.arange(-36,36.1,.1)
        elif M.m2pos == 2:
            self.xlabel = 'X Offset'
            self.ylabel = 'X offset (mm)'
            prange = numpy.arange(-36,36.1,.1)
        else:
            self.xlabel = 'Offset'
            self.ylabel = 'Offset (mm)'
            prange = numpy.arange(-36,36.1,.1)
        pl.ylabel(self.ylabel)
        if obsNumArg == False:
            titleObsNum = M.obsnum
        else:
            titleObsNum = obsNumArg
        pl.suptitle('%s %s %s %s' %
                 (M.receiver.strip(),
                  M.source.strip(),
                  M.date,
                  titleObsNum)
                 )
        if M.m2pos == 2:
            fitype = 'M2.X'
        if M.m2pos == 1:
            fitype = 'M2.Y'
        if M.m2pos == 0:
            fitype = 'M2.Z'
        if M.m2pos == 3:
            fitype = 'M1.ZernikeC0'
        textstr =           'Relative '+fitype+':   ' +str(round(M.relative_focus_fit,4)) + '\n' 
        textstr = textstr + fitype+' Error:         ' +str(round(M.focus_error,4)) + '\n' 
        textstr = textstr + fitype+' Slope:       ' +str(round(M.focus_slope,4)) + '\n' 
        textstr = textstr + 'Absolute '+fitype+':  ' +str(round(M.absolute_focus_fit,4)) + '\n' 
        textstr = textstr + 'Fit RMS:                ' +str(round(M.fit_rms,4))
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        pl.text(xpos, ypos, textstr, bbox=props, color='red')
        pl.savefig('rsr_summary.png', bbox_inches='tight')

