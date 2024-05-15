from dreampy3.redshift.netcdf import RedshiftNetCDFFile
try:
    from dreampy3.redshift.plots import RedshiftPlotChart
    #from dreampy3.redshift.utils.correlate_lines import CrossCorrelation    # does not exist
    dreampy_plot = True
except Exception as e:
    dreampy_plot = False
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
    

    def run(self, argv, obsList):

      results_dict = {'status': -1}
      try:
        hdulist = []

        tint = 0.0
        real_tint = 0.0

        actual_chassis_list = {}
        self.chassis_list = [0, 1, 2, 3]

        for i,arg in enumerate(argv):
            if arg in ("-c","--chassis"):
                self.decode_chassis_string(argv[i+1])
        for obsNum in obsList:
            obsnum_chassis_list = []
            for chassis in self.chassis_list:

                filename = genericFileSearch ('RedshiftChassis%d'%chassis, obsNum)
                if filename == "":
                    continue

                nc = RedshiftNetCDFFile(filename)
                print(nc.hdu.header.get('Dcs.ObsNum'), nc.hdu.header.get('Dcs.ObsGoal'), nc.hdu.header.get('Dcs.ObsPgm'))
                if not (nc.hdu.header.get('Dcs.ObsGoal') == 'LineCheck' and nc.hdu.header.get('Dcs.ObsPgm') == 'Bs'):
                    continue

                obsnum_chassis_list += [chassis]

                if False:
                    nc.hdu.process_scan(corr_linear=False) 
                    nc.hdu.baseline(order = 0, subtract=False)
                else:
                    nc.hdu.process_scan()
                    nc.hdu.baseline(order=1, windows=windows, subtract=True)
                if nc.hdu.header['Dcs']['ObsNum'].getValue() > 101107  and chassis == 2:
                    nc.hdu.blank_frequencies({4: [(104,111)]})
                nc.hdu.average_all_repeats(weight='sigma')
                try:
                    integ = 2*int(nc.hdu.header.get('Bs.NumRepeats'))*int(nc.hdu.header.get('Bs.TSamp'))
                except:
                    integ = 0
                tint += integ
                real_tint += (nc.hdu.data.AccSamples/48124.).mean(axis=1).sum()
                if obsNum == obsList[0]:
                    az = nc.hdu.header.get('Telescope.AzDesPos')
                    el = nc.hdu.header.get('Telescope.ElDesPos')
                    utdate = nc.hdu.header.utdate()
                    uttime = str(utdate).split(' ')[1].split('.')[0]
                    utdate = str(utdate).split(' ')[0]
                    print(utdate, uttime)
                hdulist.append(nc.hdu)
                nc.nc.sync()
                nc.nc.close()

            if len(obsnum_chassis_list) > 0:
                actual_chassis_list[int(obsNum)] = obsnum_chassis_list

        
        hdu = hdulist[0]  # get the first observation
        hdu.average_scans(hdulist[1:])#, threshold_sigma=0.1)
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
        result_tint = real_tint/4.0
        msg = "%s %s %s\n%s: %.2f mK, %.2f GHz, %.0f secs" %(utdate, uttime, str(actual_chassis_list), hdu.header.SourceName, result_compspectrum, result_freq, result_tint)
        print(msg)
        
        if False and dreampy_plot:
            print('using dreampy_plot')
            pl = RedshiftPlotChart()
            pl.clear()
            pl.plot(hdu.compfreq, 1000*hdu.compspectrum[0,:]) #, linestyle='steps-mid')
            pl.set_xlim(72.5, 111.5)
            pl.set_xlabel('Frequency (GHz)')
            pl.set_ylabel('TA* (mK)')
            pl.set_subplot_title(msg)
        else:
            print('using matplotlib_plot')
            import matplotlib.pyplot as pl
            #pl.plot(hdu.compfreq, 1000*hdu.compspectrum[0,:]) #, linestyle='steps-mid')
            pl.clf()
            pl.step(hdu.compfreq, 1000*hdu.compspectrum[0,:], where='mid')
            pl.xlim(72.5, 111.5)
            pl.xlabel('Frequency (GHz)')
            pl.ylabel('TA* (mK)')
            pl.title(msg)
        if line_info is not None:
            pl.plot([72.5, 111.5], [line_info[0], line_info[0]], c='r')
            pl.annotate(hdu.header.SourceName +' line strength', (90, line_info[0]*1.02))# , c='r')
            pl.ylim(-10., line_info[0]*1.2)
            if line_info[1] != 0:
                l = [line_info[1]-.25, line_info[1]+.25]
                pl.axvspan(l[0], l[1], alpha=0.1, color='b')
            
        pl.savefig('rsr_summary.png', bbox_inches='tight')
        # make it interactive
        # pl.show()

        results_dict['status'] = 0
        results_dict['t_int'] = result_tint
        results_dict['ta_star'] = result_compspectrum
        results_dict['freq'] = result_freq
        results_dict['source_name'] = hdu.header.SourceName
        results_dict['obsnum'] = obsList[0]
        results_dict['obsnum_list'] = obsList
        results_dict['num'] = len(obsList)
        results_dict['chassis'] = actual_chassis_list
        results_dict['az'] = az
        results_dict['el'] = el
        results_dict['date'] = utdate
        results_dict['time'] = uttime
        print(results_dict)
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
    obsNumList = [int(sys.argv[1])]
    flist = genericFileSearchRecursive(obsNumList[0], None, full = True)
    print(flist)
    rsr = RSRRunLineCheck()
    results_dict = rsr.run(sys.argv,obsNumList)
    print(results_dict)

