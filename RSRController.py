"""Module with classes for implementing the Controller.

Classes: RSRMapController
Uses:    RSRMap, RSRMapFit, RSRMapViewer, sys, getopt
Author:  FPS
Date:    May 5, 2014
Changes:
"""
import sys
import getopt

from RSRMap import RSRMap
from RSRFit import RSRMapFit
from RSRViewer import RSRMapViewer

SHOW_MAP_SAMPLING = True

class RSRMapController():
    """Controller class for managing maps and pointing fits."""
    def reduce_map(self,a,scan,plot_option,filelist=False):
        """Method to reduce an individual pointing observation.

        a is list of parameters derived from command line args to control function.
        scan is the obsnum of the data to be processed
        plot_option specifies whether to show an image of the maps and results.
        Function returns an RSRMapFit object with the fit results.
        """
        F = RSRMapFit(a.process_list)
        V = RSRMapViewer()
        if plot_option:
            V.init(a)
        index = 0
        print 'processing %s %d'%(a.date,scan)
        print '           chassis=%s'%(str(a.chassis_list))
        print '           process=%s'%(str(a.process_list))
        for chassis_id, chassis in enumerate(a.chassis_list):
            m = RSRMap(filelist,a.date,scan,chassis,a.beam_throw)
            try:
                fnc = m.nc
            except AttributeError:
                print "map doesn't have a file"
                continue
            F.load_average_parameters(m)        
            print '           chassis_id=%d, chassis=%d'%(chassis_id,chassis)
            for board_id,board in enumerate(a.process_list[chassis_id]):
                print '           board_id=%d, board=%d'%(board_id,board)
                m.process_single_board(board, 
                                       a.fit_window, 
                                       a.remove_baseline, 
                                       a.baseline_elimination_window,
                                       a.baseline_smoothing_window, 
                                       a.despike_data, 
                                       a.eliminate_bad_integrations, 
                                       a.bad_integration_checksum, 
                                       a.flag_data, 
                                       a.flag_windows,
                                       process_dual_beam=a.dual_beam_map,
                                       select_beam=a.select_beam
                                       )
                F.load_chassis_board_result(m,index,chassis_id,board,board_id)
                index = index + 1
            if plot_option == True and a.show_ion==1 or True:
                if len(a.process_list[chassis_id]) > 1:
                    if a.show_type==1:
                        if len(a.chassis_list)>0:
                            if chassis_id == 0:
                                V.init_big_fig(figno=1)
                            V.master_map_plot(m,a.process_list[chassis_id])
                        else:
                            V.plot_all(m,a.process_list[chassis_id],figno=chassis_id+1,fit_window=a.fit_window,show_samples=SHOW_MAP_SAMPLING)
                    else:
                        if len(a.chassis_list)>1:
                            if chassis_id == 0:
                                V.init_big_fig(figno=1)
                            V.master_model_scan_plot(m,a.process_list[chassis_id])
                        else:
                            V.plot_all_model_scans(m,a.process_list[chassis_id],figno=chassis_id+1)
                elif len(a.process_list[chassis_id]) == 1:
                    V.init_fig(figno=chassis_id+1)
                    if a.show_type==1:
                        V.plot_map(m,a.process_list[chassis_id][0],fit_window=a.fit_window,show_samples=SHOW_MAP_SAMPLING)
                    else:
                        V.plot_model_scan(m,a.process_list[chassis_id][0])
        m.close()
        return F

    def reduce_maps(self,a,filelist=False):
        """Reduces the set of scans specified in scan_list

        a is list of parameters that control the reduction derived from command line args.
        """
        FList = []
        for scan_id,scan in enumerate(a.scan_list):
            FList.append(self.reduce_map(a,scan,False,filelist))
        return FList


class RSRHandleArgs():
    """Maintains important parameters that control reductions and provides command line argument handling""" 
    def __init__(self,
                 path='/data_lmt',
                 date='2013-12-22',
                 scan_arg='[13631]',
                 chassis_arg='[0,1,2,3]',
                 board_arg='[0,1,2,3,4,5]',
                 process_arg='[]',
                 obstype=1,
                 beam_throw=39,
                 fit_window=16,
                 eliminate_bad_integrations=True,
                 bad_integration_checksum=3936,
                 despike_data=False,
                 remove_baseline=False,
                 baseline_elimination_window=50,
                 baseline_smoothing_window=50,
                 flag_data=False,
                 flag_windows=[],
                 show_it=False,
                 show_type=1,
                 select_beam=1
                 ):
        """Initializes parameters which control fitting functionality"""
        # basic file parameters
        self.ion = True
        self.show_ion = 1
        self.path = path
        self.date = date
        self.decode_scan_string(scan_arg)
        self.process_list = eval(process_arg)
        self.decode_chassis_string(chassis_arg)
        self.decode_board_string(board_arg)
        self.obstype = obstype
        self.obsdata = [[0,1],[1,1],[1,1],[1,2]]
        self.groupscan = self.obsdata[self.obstype][0]
        self.subscan = self.obsdata[self.obstype][1]
        self.show_it = show_it
        self.show_type = show_type
        self.select_beam = select_beam
        if self.select_beam ==-1:
            self.dual_beam_map = True
        else:
            self.dual_beam_map = False

        # scan processing parameters
        self.beam_throw = beam_throw
        self.fit_window = fit_window
        self.eliminate_bad_integrations = eliminate_bad_integrations
        self.bad_integration_checksum = bad_integration_checksum
        self.despike_data = despike_data
        self.remove_baseline = remove_baseline
        self.baseline_elimination_window = baseline_elimination_window
        self.baseline_smoothing_window = baseline_smoothing_window
        self.flag_data = flag_data
        self.flag_windows = flag_windows

    def parse_args(self,s,program,arglevel=0):
        """Parses the command line arguments for a function to allow user to specify them."""
        self.program = program
        self.arglevel = arglevel
        try:
            opts, arg = getopt.getopt(s,
                                      "hd:s:c:b:o:t:w:e:m:rxz:l:01",
                                      ["chassis=",
                                       "date=",
                                       "scan=",
                                       "board=",
                                       "list=",
                                       "obstype=",
                                       "show=",
                                       "path=",
                                       "throw=",
                                       "flag=",
                                       "beam="
                                       ]
                                      )
        except getopt.GetoptError:
            result = -1
            print 'error: argument error'
            return result
        for opt, arg in opts:
            # here is the "help" result
            if opt == '-h':
                print 'usage: '+self.program
                print '-d (date)    date in yyyy-mm-dd format'
                print '-s (scan)    OBSNUM list to process'
                print '             for map, only one argument needed'
                print '             e.g. -s 16481 will just process 16481'
                print '             for fit_m2, we specify a list of scans as follows'
                print '             e.g. -s [16481,16492, 16493] will process the scans'
                print '                  -s 16481:16485 will process 16481 to 16485'
                print '-c (chassis) list of chassis to process'
                print '             e.g. -c [0,1] will process chassis 0 and 1'
                print '                  -c 0:2   will process 0,1, and 2'
                print '                  -c a     will process all chassis (default)'
                print '                  -c 1     will process only chassis 1'
                print '-b (board)   list of boards to process; same list is used for all chassis'
                print '             e.g. -b [0,1,2,5] will process boards 0,1,2, and 5'  
                print '                  -b 2:5       will process boards 2 to 5'
                print '                  -b a         will process all boards (default)'
                print '                  -b 1         will only process board 1'
                print '-l (list)    specify a separate list of boards for each chassis in the'
                print '             chassis list'
                print '             e.g. if -c [0,1,3] then -l [[0,1,2,3,4,5],[0,1,4,5],[1]] '
                print '             will process only the requested boards for each chassis'
                print '-o (obstype) observation type (0=ON; 1=MAP; 2=XSCAN_X; 3=XSCAN_Y) default=%d'%(self.obstype)
                print '--show       display plot flag; default is to show no plots'
                print '             --show True or true will cause default plot to be displayed; '
                print '             --show Map          will cause map plot to be displayed'
                print '             --show Scan         will cause scan plot to be displayed'
                print '--path       the path to the data (default %s)'%(self.path)
                print '--beam       argument selects beam 1 or beam 0 for fitting'
                print '             -0 is shorthand to select 0; -1 is shorthand to select 1.'
                if self.arglevel > 0:
                    print '--beam       argument selects beam 1 or beam 0 for fitting '
                    print '              only a single beam beam in a map'
                    print '               -0 is shorthand to select beam 0; '
                    print '               -1 is shorthand to select beam 1.'
                    print '-t (throw)   beam throw (arcsec)'
                    print '               default narrow beam = %d arcsec'%(self.beam_throw)
                    print '               use -t 147 for the wide beam throw'
                    print '-w           window for fitting gaussian'
                    print '               default = %d arcsec'%(self.fit_window)
                    print '-r           remove a baseline - no argument'
                    print '-e           size of region around beam peak to exclude from'
                    print '              baseline fit (%d arcsec)'%(self.baseline_elimination_window)
                    print '-m           size of baseline smoothing window in samples (%d arcsec)'%(self.baseline_smoothing_window)
                    print '-x           turns on the despike algorithm - no argument'
                    print '-z           eliminates bad integrations'
                    print '             the argument is number of interrupts per sample'
                    print '             you may enter -z n to set for our nominal number of '
                    print '             interrupts per sample'
                    print '--flag       list of regions to exclude from analysis'
                    print '             e.g. --flag [[0,10],[502,535]] will eliminate samples'
                    print '                  0-10 and 502-535'
                    print '                  No whitespace is allowed in the flag list!'
                result = 1
                return result
            elif opt in ("-c","--chassis"):
                self.decode_chassis_string(arg)
            elif opt in ("-d","--date"):
                self.date = arg
            elif opt in ("-s","--scan"):
                self.decode_scan_string(arg)
            elif opt in ("-b","--board"):
                self.decode_board_string(arg)
            elif opt in ("-l","--list"):
                if(arg[0] != "a" and arg[0] != 'n'):
                    self.process_list = eval(arg)
            elif opt in ("-o","--obstype"):
                self.obstype = eval(arg)
                self.groupscan = self.obsdata[self.obstype][0]
                self.subscan = self.obsdata[self.obstype][1]
            elif opt in ("--path"):
                self.path = arg
            elif opt in ("--show"):
                self.decode_show_string(arg)
            elif opt in ("-t","--throw"):
                if(arg[0] != 'n'):
                    self.beam_throw = eval(arg)
            elif opt in ("-w"):
                self.fit_window = eval(arg)
            elif opt in ("-r"):
                self.remove_baseline = True
            elif opt in ("-e"):
                self.baseline_elimination_window = eval(arg)
            elif opt in ("-m"):
                self.baseline_smoothing_window = eval(arg)
            elif opt in ("-x"):
                self.despike_data = True
            elif opt in ("-z"):
                self.eliminate_bad_integrations = True
                if arg[0] == 'n':
                    self.bad_integration_checksum = 3936
                else:
                    self.bad_integration_checksum = eval(arg)
            elif opt in ("--flag"):
                self.flag_data = True
                self.flag_windows = eval(arg)
            elif opt in ("--beam"):
                if arg[0] == 'b' or arg[0] == 'n':
                    self.select_beam = -1
                else:
                    self.select_beam = eval(arg)
            elif opt in ("-0"):
                self.select_beam = 0
            elif opt in ("-1"):
                self.select_beam = 1
        self.make_process_list()
        if self.select_beam ==-1:
            self.dual_beam_map = True
        else:
            self.dual_beam_map = False
        result = 0
        return result
    
    def make_process_list(self):
        """Creates the list of boards to process in each chassis."""
        if self.process_list == []:
            for chassis in self.chassis_list:
                self.process_list.append(self.board_list)
        if len(self.process_list) != len(self.chassis_list):
            print 'warning: process list and chassis_list are not consistent'
    
    def decode_chassis_string(self,chassis_arg):
        """Decodes the argument provided with the -c flag."""
        if chassis_arg[0] == 'a' or chassis_arg[0] == 'n':
            self.chassis_list = [0,1,2,3]
        elif chassis_arg[0] == '[':
            self.chassis_list = eval(chassis_arg)
        else:
            p = chassis_arg.partition(':')
            if p[1] == ':':
                self.chassis_list = range(int(p[0]),int(p[2])+1)
            else:
                self.chassis_list = range(int(p[0]),int(p[0])+1)
    
    def decode_board_string(self,board_arg):
        """Decodes the argument provided with the -b flag."""
        if board_arg[0] == 'a' or board_arg[0] == 'n':
            self.board_list = [0,1,2,3,4,5]
        elif board_arg[0] == '[':
            self.board_list = eval(board_arg)
        else:
            p = board_arg.partition(':')
            if p[1] == ':':
                self.board_list = range(int(p[0]),int(p[2])+1)
            else:
                self.board_list = range(int(p[0]),int(p[0])+1)

    def decode_scan_string(self,scan_arg):
        """Decodes the argument provided with the -s flag."""
        if scan_arg[0] == '[':
            self.scan_list = eval(scan_arg)
        else:
            p = scan_arg.partition(':')
            if p[1] == ':':
                self.scan_list = range(int(p[0]),int(p[2])+1)
            else:
                self.scan_list = range(int(p[0]),int(p[0])+1)

    def decode_show_string(self,show_arg):
        """Decodes the argument provided with the --show flag."""
        self.show_ion = 1
        if show_arg[0]=='T' or show_arg[0]=='t':
            self.show_it = True
        elif show_arg[0]=='F' or show_arg[0]=='f':
            self.show_it = False
        elif show_arg[0]=='s' or show_arg[0]=='S':
            self.show_it = True
            self.show_type = 0
        elif show_arg[0]=='m' or show_arg[0]=='M':
            self.show_it = True
            self.show_type = 1
        elif show_arg[0]=='a' or show_arg[0]=='A':
            self.show_it = True
            self.show_ion = 0
        else:
            self.show_it = False
            print 'unknown argument for show keyword'

