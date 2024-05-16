
import matplotlib
gui_env = ['TKAgg','Agg','GTKAgg','Qt4Agg','WXAgg']
for gui in gui_env:
    try:
        print ("RSR Testing", gui)
        matplotlib.use(gui)
        from matplotlib import pyplot as pl
        from matplotlib import mlab as mlab
        print ("RSR Using:", matplotlib.get_backend())
        break
    except Exception as e:
        print (e)
        continue

import matplotlib.mlab as mlab
from dreampy3.redshift.netcdf import RedshiftNetCDFFile
import sys
import numpy
import os.path
from genericFileSearch import genericFileSearch, genericFileSearchRecursive
import traceback

windows = {}
windows[0] = [(72.5,79.5)]
windows[1] = [(86.1,92.5)]
windows[2] = [(79., 84.9)]
windows[3] = [(91.,99)]
windows[4] = [(104.6, 109.7)]
windows[5] = [(98.,106.)]

source_line_info = {
    'I23365': (40, 108.282),
    'VIIZw31': (110, 109.345),
    'I05189': (55, 110.532),
    'I10565': (110, 110.501),
    'I12112': (40, 107.438),
    'I17208': (110, 110.563),
}


class RSRRunLineCheck():
    def utdate(self):
        """Returns python datetime equivalent for TimePlace.UTDate"""
        import datetime
        utd = self.get_scalar('TimePlace.UTDate')
        year = int(utd)
        if year % 4 == 0:
            days_in_year = 366.
        else:
            days_in_year = 365.
        secs = 24.*3600.*days_in_year*(utd-year)
        dt = datetime.datetime(year,1,1)+datetime.timedelta(seconds=secs)
        return dt

    def decode_chassis_string(self,chassis_arg):
        """Decodes the argument provided with the -c flag."""
        if chassis_arg[0] == 'a' or chassis_arg[0] == 'n':
            self.chassis_list = [0,1,2,3]
        elif chassis_arg[0] == '[':
            self.chassis_list = eval(chassis_arg)
        else:
            p = chassis_arg.partition(':')
            if p[1] == ':':
                self.chassis_list = list(range(int(p[0]),int(p[2])+1))
            else:
                self.chassis_list = list(range(int(p[0]),int(p[0])+1))
    

    def plot_one(self, ax, freq, spec, chassis, msg, line_info, source_name):
        #ax.plot(freq, 1000*spec) #, linestyle='steps-mid')
        ax.step(freq, 1000*spec, where='mid')
        ax.set_xlim(72.5, 111.5)
        if chassis == self.chassis_list[-1]:
            ax.set_xlabel('Frequency (GHz)')
        else:
            ax.xaxis.set_visible(False)
        ax.set_ylabel('TA* (mK)')
        ax.set_title(msg)
        if line_info is not None:
            ax.plot([72.5, 111.5], [line_info[0], line_info[0]], c='r')
            ax.annotate(source_name +' line strength', (90, line_info[0]*1.02))# , c='r')
            ax.set_ylim(-10., line_info[0]*1.2)
            if line_info[1] != 0:
                l = [line_info[1]-.25, line_info[1]+.25]
                ax.axvspan(l[0], l[1], alpha=0.1, color='b')

    def run(self, argv, obsList):

      results_dict = {'status': -1}
      try:

        self.chassis_list = [0, 1, 2, 3]

        for i,arg in enumerate(argv):
            if arg in ("-c","--chassis"):
                self.decode_chassis_string(argv[i+1])

        all_tint = 0.0
        all_hdulist = []
        all_num_chassis = 0
        all_results_dict = {}
        num_plots = len(self.chassis_list)+1

        fig, axs = pl.subplots(num_plots, 1, gridspec_kw={'height_ratios': [3]+[1]*(num_plots-1)})
        #fig.tight_layout()#h_pad=0.5)
        fig.set_figheight(2*fig.get_figheight())        

        for i,chassis in enumerate(self.chassis_list):
            print('process chassis %d'%chassis)
            ax = axs[i+1]
            ax.clear()
            chassis_ncs = []
            chassis_hdulist = []
            chassis_tint = 0.0
            chassis_results_dict = {}
            chassis_results_dict['t_int'] = 0
            chassis_results_dict['ta_star'] = 0
            chassis_results_dict['freq'] = 0
            for obsNum in obsList:
                print('  look for obsnum %d'%obsNum)
                filename = genericFileSearch ('RedshiftChassis%d'%chassis, obsNum)
                print('    filename %s'%filename)
                try:
                    nc = RedshiftNetCDFFile(filename)
                    chassis_ncs.append(nc)
                except:
                    break

            if len(chassis_ncs) == 0:
                print('  chassis %d has no files'%chassis)
                ax.annotate("File not found for Chassis %d"%(chassis), [0.2,0.5], fontsize=13, fontweight='bold', stretch='250', horizontalalignment='left', verticalalignment='top')
                all_results_dict[chassis] = chassis_results_dict
                continue

            for nc in chassis_ncs:
                print(nc.hdu.header.get('Dcs.ObsNum'), nc.hdu.header.get('Dcs.ObsGoal'), nc.hdu.header.get('Dcs.ObsPgm'))
                if not (nc.hdu.header.get('Dcs.ObsGoal') == 'LineCheck' and nc.hdu.header.get('Dcs.ObsPgm') == 'Bs'):
                    continue

                if False:
                    nc.hdu.process_scan(corr_linear=False) 
                    nc.hdu.baseline(order = 0, subtract=False)
                else:
                    nc.hdu.process_scan()
                    nc.hdu.baseline(order=1, windows=windows, subtract=True)
                if nc.hdu.header['Dcs']['ObsNum'].getValue() > 101107  and chassis == 2:
                    nc.hdu.blank_frequencies({4: [(104,111)]})
                nc.hdu.average_all_repeats(weight='sigma')
                chassis_tint += (nc.hdu.data.AccSamples/48124.).mean(axis=1).sum()
                if nc == chassis_ncs[0]:
                    az = nc.hdu.header.get('Telescope.AzDesPos')
                    el = nc.hdu.header.get('Telescope.ElDesPos')
                    utdate = nc.hdu.header.utdate()
                    uttime = str(utdate).split(' ')[1].split('.')[0]
                    utdate = str(utdate).split(' ')[0]
                    try:
                        bs_beams = nc.hdu.header.get('Bs.Beam').tolist()
                    except:
                        bs_beams = [0, 1]
                    print(utdate, uttime)
                    print(bs_beams)
                chassis_hdulist.append(nc.hdu)
                all_hdulist.append(nc.hdu)
                nc.nc.sync()
                nc.nc.close()

            all_num_chassis += 1
            all_tint += chassis_tint
            hdu = chassis_hdulist[0]  # get the first observation
            hdu.average_scans(chassis_hdulist[1:])#, threshold_sigma=0.1)
            hdu.average_all_repeats()

            #hdu.blank_frequencies({0:[(72, 81),]})
            hdu.make_composite_scan()
            hdu.compspectrum[0,:] = numpy.where((hdu.compspectrum[0,:] >= -1.0) & (hdu.compspectrum[0,:] < 1.0), hdu.compspectrum[0,:], 0.0)
            line_info = source_line_info.get(hdu.header.SourceName)
            if line_info is not None and line_info[1] != 0:
                l = [line_info[1]-.25, line_info[1]+.25]
                spec = numpy.where((hdu.compfreq >= l[0]) & (hdu.compfreq <= l[1]), hdu.compspectrum[0,:], 0.0)
            else:
                spec = hdu.compspectrum[0,:]
            chassis_compspectrum = max(spec)*1000
            idx = numpy.where(spec == max(spec))
            chassis_freq = hdu.compfreq[idx][0]
            msg = "Chassis %d: %.2f mK, %.2f GHz, %.0f secs" %(chassis, chassis_compspectrum, chassis_freq, chassis_tint)
            print(msg)
            chassis_results_dict['t_int'] = chassis_tint
            chassis_results_dict['ta_star'] = chassis_compspectrum
            chassis_results_dict['freq'] = chassis_freq
            all_results_dict[chassis] = chassis_results_dict

            self.plot_one(ax, hdu.compfreq, hdu.compspectrum[0,:], chassis, msg, line_info, hdu.header.SourceName)

        hdu = all_hdulist[0]  # get the first observation
        hdu.average_scans(all_hdulist[1:])#, threshold_sigma=0.1)
        hdu.average_all_repeats()

        #hdu.blank_frequencies({0:[(72, 81),]})
        hdu.make_composite_scan()
        hdu.compspectrum[0,:] = numpy.where((hdu.compspectrum[0,:] >= -1.0) & (hdu.compspectrum[0,:] < 1.0), hdu.compspectrum[0,:], 0.0)
        line_info = source_line_info.get(hdu.header.SourceName)
        if line_info is not None and line_info[1] != 0:
            l = [line_info[1]-.25, line_info[1]+.25]
            spec = numpy.where((hdu.compfreq >= l[0]) & (hdu.compfreq <= l[1]), hdu.compspectrum[0,:], 0.0)
        else:
            spec = hdu.compspectrum[0,:]
        result_compspectrum = max(spec)*1000
        idx = numpy.where(spec == max(spec))
        result_freq = hdu.compfreq[idx][0]
        result_tint = all_tint/all_num_chassis

        msg = "Average: %.2f mK, %.2f GHz, %.0f secs" %(result_compspectrum, result_freq, result_tint)
        print(msg)

        ax = axs[0]
        self.plot_one(ax, hdu.compfreq, hdu.compspectrum[0,:], -1, msg, line_info, hdu.header.SourceName)
        
        msg = "%s %s %s" %(utdate, uttime, hdu.header.SourceName)
        msg += "\n"
        msg += "ObsNums %s, Beams %s" %(str(obsList), str(bs_beams))
        print(msg)
        pl.suptitle(msg)
        #pl.subplots_adjust(top=0.85)
        pl.savefig('rsr_summary.png', bbox_inches='tight')

        results_dict['status'] = 0
        results_dict['t_int'] = result_tint
        results_dict['ta_star'] = result_compspectrum
        results_dict['freq'] = result_freq
        results_dict['source_name'] = hdu.header.SourceName
        results_dict['obsnum'] = obsList[0]
        results_dict['obsnum_list'] = obsList
        results_dict['num'] = len(obsList)
        results_dict['chassis'] = all_results_dict
        results_dict['az'] = az
        results_dict['el'] = el
        results_dict['date'] = utdate
        results_dict['time'] = uttime
        results_dict['bs_beams'] = bs_beams
        print(results_dict)

        # make it interactive
        #pl.show()
      except:
          traceback.print_exc()

      return results_dict


if __name__ == '__main__':
    obsNumList = [65971,65972]
    obsNumList = [95186, 95187]
    obsNumList = [105232, 105233]
    obsNumList = [105380, 105381, 105382, 105383, 105384]
    obsNumList = [112315, 112316]
    obsNumList = [112316]
    obsNumList = [int(x) for x in sys.argv[1:]]
    rsr = RSRRunLineCheck()
    results_dict = rsr.run(sys.argv,obsNumList)

