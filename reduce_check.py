from dreampy3.redshift.netcdf import RedshiftNetCDFFile
from dreampy3.redshift.plots import RedshiftPlot
from dreampy3.redshift.utils.correlate_lines import CrossCorrelation
import numpy
import os.path
from genericFileSearch import genericFileSearch


hdulist = []
windows = {}
windows[0] = [(73.5, 76.8), (76.9, 79.0) ]
windows[1] = [(86.6, 91.3)]
windows[2] = [(80, 80.95), (82.3,85.4)]
windows[3] = [(92.2, 95.5), (97.4,98.0)]
windows[4] = [(105.23, 110.0)]
windows[5] = [(100, 103.5)]


tint = 0.0
real_tint = 0.0



### CHANGE THESE ObsNum for every science spectrum ###
Obslist = [27870,27871]

for ObsNum in Obslist:
    for chassis in [0,1,2,3]:

	#filename= '/data_lmt/RedshiftChassis%d/RedshiftChassis%d_%s_%06d_00_0001.nc' % (chassis, chassis, datestg, ObsNum)
	filename = genericFileSearch ('RedshiftChassis%d'%chassis,ObsNum)
	
	if filename == "":
		raise Exception ('File not found for chassis %d ObsNumber: %s ' % (chassis,ObsNum))
		

        nc = RedshiftNetCDFFile(filename)
        nc.hdu.process_scan(corr_linear=False) 
        #nc.hdu.baseline(order = 1, subtract=True)
        nc.hdu.average_all_repeats(weight='sigma')
        integ = 2*int(nc.hdu.header.get('Bs.NumRepeats'))*int(nc.hdu.header.get('Bs.TSamp'))
        tint += integ
        real_tint += (nc.hdu.data.AccSamples/48124.).mean(axis=1).sum()        
        hdulist.append(nc.hdu)
        nc.sync()
        nc.close()

        
hdu = hdulist[0]  # get the first observation
hdu.average_scans(hdulist[1:])#, threshold_sigma=0.1)
hdu.average_all_repeats()



hdu.make_composite_scan()
pl = RedshiftPlot()

pl.clear()
pl.plot(hdu.compfreq, 1000*hdu.compspectrum[0,:], linestyle='steps-mid')
pl.set_xlim(72.5, 111.5)

pl.set_xlabel('Frequency (GHz)')
pl.set_ylabel('TA* (mK)')
pl.set_subplot_title("%s Tint=%f hrs" %(hdu.header.SourceName, real_tint/4.0/3600.0))



