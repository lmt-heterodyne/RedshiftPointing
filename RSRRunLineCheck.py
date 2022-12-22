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
from genericFileSearch import genericFileSearch

windows = {}
windows[0] = [(72.5,79.5)]
windows[1] = [(86.1,92.5)]
windows[2] = [(79., 84.9)]
windows[3] = [(91.,99)]
windows[4] = [(104.6, 109.7)]
windows[5] = [(98.,106.)]


class RSRRunLineCheck():
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

                obsnum_chassis_list += [chassis]

                nc = RedshiftNetCDFFile(filename)
                if False:
                    nc.hdu.process_scan(corr_linear=False) 
                    nc.hdu.baseline(order = 0, subtract=False)
                else:
                    nc.hdu.process_scan()
                    nc.hdu.baseline(order=1, windows=windows, subtract=True)
                nc.hdu.average_all_repeats(weight='sigma')
                try:
                    integ = 2*int(nc.hdu.header.get('Bs.NumRepeats'))*int(nc.hdu.header.get('Bs.TSamp'))
                except:
                    integ = 0
                tint += integ
                real_tint += (nc.hdu.data.AccSamples/48124.).mean(axis=1).sum()        
                hdulist.append(nc.hdu)
                nc.nc.sync()
                nc.nc.close()
            actual_chassis_list[obsNum] = obsnum_chassis_list

        
        hdu = hdulist[0]  # get the first observation
        hdu.average_scans(hdulist[1:])#, threshold_sigma=0.1)
        hdu.average_all_repeats()

        hdu.blank_frequencies({0:[(72, 81),]})
        hdu.make_composite_scan()
        hdu.compspectrum[0,:] = numpy.where((hdu.compspectrum[0,:] >= -1.0) & (hdu.compspectrum[0,:] < 1.0), hdu.compspectrum[0,:], 0.0)
        msg = "%s -- %s Tint=%f mins" %(str(actual_chassis_list),hdu.header.SourceName, real_tint/4.0/60.0)
        print(msg)
        
        if dreampy_plot:
            print('using dreampy_plot')
            pl = RedshiftPlotChart()
            pl.clear()
            pl.plot(hdu.compfreq, 1000*hdu.compspectrum[0,:], linestyle='steps-mid')
            pl.set_xlim(72.5, 111.5)
            pl.set_xlabel('Frequency (GHz)')
            pl.set_ylabel('TA* (mK)')
            pl.set_subplot_title(msg)
        else:
            print('using matplotlib_plot')
            import matplotlib.pyplot as pl
            #pl.plot(hdu.compfreq, 1000*hdu.compspectrum[0,:], linestyle='steps-mid')
            pl.clf()
            pl.step(hdu.compfreq, 1000*hdu.compspectrum[0,:], where='mid')
            pl.xlim(72.5, 111.5)
            pl.xlabel('Frequency (GHz)')
            pl.ylabel('TA* (mK)')
            pl.title(msg)
        pl.savefig('rsr_summary.png', bbox_inches='tight')
        # make it interactive
        # pl.show()



if __name__ == '__main__':
    obsNumList = [65971,65972]
    rsr = RSRRunLineCheck()
    M = rsr.run(sys.argv,obsNumList)
