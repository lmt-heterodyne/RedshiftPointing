from dreampy.redshift.netcdf import RedshiftNetCDFFile
from dreampy.redshift.plots import RedshiftPlotChart
from dreampy.redshift.utils.correlate_lines import CrossCorrelation
import numpy
from scipy.stats import nanmean
import os.path
from rsrFileSearch import rsrFileSearch

class RSRRunTsys():
    def run(self, argv, obsNum):

        filename = rsrFileSearch (obsNum, 0)
        nc = RedshiftNetCDFFile(filename)
        nc.hdu.get_cal()    
        pl  = RedshiftPlotChart()
        pl.plot_tsys(nc)
        tsys = nanmean(nc.hdu.cal.Tsys.flatten())
        print 'Average Tsys = %6.2f K' % tsys
        pl.hlines(tsys,70,115)
        pl.annotate("Average Tsys =%6.2fK"%tsys, [114,tsys-1], fontsize=13, fontweight='bold', stretch='250', horizontalalignment='right', verticalalignment='top')
        pl.savefig('rsr_summary.png', bbox_inches='tight')
