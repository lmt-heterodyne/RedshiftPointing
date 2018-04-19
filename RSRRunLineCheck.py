from dreampy.redshift.netcdf import RedshiftNetCDFFile
from dreampy.redshift.plots import RedshiftPlotChart
from dreampy.redshift.utils.correlate_lines import CrossCorrelation
import numpy
import os.path
from genericFileSearch import genericFileSearch


class RSRRunLineCheck():
    def run(self, argv, obsList):

        hdulist = []

        tint = 0.0
        real_tint = 0.0

        for obsNum in obsList:
            #for chassis in [0,1,2,3]:
            for chassis in [1,2,3]:

                filename = genericFileSearch ('RedshiftChassis%d'%chassis, obsNum)
	
                if filename == "":
                    raise Exception ('File not found for chassis %d obsNumber: %s ' % (chassis,obsNum))
		

                nc = RedshiftNetCDFFile(filename)
                nc.hdu.process_scan(corr_linear=False) 
                nc.hdu.average_all_repeats(weight='sigma')
                integ = 2*int(nc.hdu.header.get('Bs.NumRepeats'))*int(nc.hdu.header.get('Bs.TSamp'))
                tint += integ
                real_tint += (nc.hdu.data.AccSamples/48124.).mean(axis=1).sum()        
                hdulist.append(nc.hdu)
                nc.nc.sync()
                nc.nc.close()

        
        hdu = hdulist[0]  # get the first observation
        hdu.average_scans(hdulist[1:])#, threshold_sigma=0.1)
        hdu.average_all_repeats()


        hdu.make_composite_scan()
        pl = RedshiftPlotChart()

        pl.clear()
        pl.plot(hdu.compfreq, 1000*hdu.compspectrum[0,:], linestyle='steps-mid')
        pl.set_xlim(72.5, 111.5)
        pl.set_xlabel('Frequency (GHz)')
        pl.set_ylabel('TA* (mK)')
        pl.set_subplot_title("[%d:%d] -- %s Tint=%f hrs" %(min(obsList),max(obsList),hdu.header.SourceName, real_tint/4.0/3600.0))
        pl.savefig('rsr_summary.png', bbox_inches='tight')



