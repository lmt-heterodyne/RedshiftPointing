from dreampy.redshift.netcdf import RedshiftNetCDFFile
try:
    from dreampy.redshift.plots import RedshiftPlotChart
    from dreampy.redshift.utils.correlate_lines import CrossCorrelation
    dreampy_plot = True
except:
    dreampy_plot = False
import numpy
try:
    from scipy.stats import nanmean
except:
    pass
import sys
import os.path
from genericFileSearch import genericFileSearch

class RSRRunTsys():

    def plot_tsys(self, pl, FontProperties, nc, board=None, hold=False,
                  set_subplot_title=True,
                  *args, **kwargs):
        """Plots the redshift Tsys data. This is to be obtained
        from the CalObsNum scan in a prescribed way. If the Cal data is not
        available in the scan, it will produce an error"""
        if isinstance(nc, RedshiftNetCDFFile):
            hdu = nc.hdu
        elif isinstance(nc, RedshiftScan):
            hdu = nc
        else:
            raise LMTRedshiftError("plot tsys", "Argument nc should be of type RedshiftNetCDFFile or RedshiftScan")
        if not hasattr(hdu, 'cal'):
            raise LMTRedshiftError("plot tsys", "hdu does not have cal object. Process first with get_cal()")
        if board is None:
            boards = hdu.header.BoardNumber
        else:
            boards = [board]
        for board in boards:
            pl.plot(hdu.frequencies[board, :], hdu.cal.Tsys[board, :],
                      linestyle='steps-mid', label='%d.%d' % (int(hdu.header.ChassisNumber), board))
        pl.xlabel("Frequency (GHz)")
        pl.legend(loc='best', prop=FontProperties(size="xx-small"))
        pl.ylabel("Tsys (K)")
        pl.title('%s: Source %s' % (hdu.header.obs_string(), hdu.header.SourceName))        


    def run(self, argv, obsNum):

        filename = genericFileSearch ('RedshiftChassis2', obsNum)
        nc = RedshiftNetCDFFile(filename)
        nc.hdu.get_cal()
        #tsys = nanmean(nc.hdu.cal.Tsys.flatten())
	tsys_data = nc.hdu.cal.Tsys.flatten()
	tsys_data = tsys_data[numpy.where(numpy.isfinite(tsys_data))]
	tsys = numpy.median (tsys_data)
        print 'Average Tsys = %6.2f K' % tsys
        if dreampy_plot:
            print 'using dreampy_plot'
            pl  = RedshiftPlotChart()
            pl.plot_tsys(nc)
	    pl.set_ylim(0.0,3*tsys)
        else:
            print 'using matplotlib_plot'
            import matplotlib.pyplot as pl
            from matplotlib.font_manager import FontProperties
            self.plot_tsys(pl, FontProperties, nc)
	    #pl.ylim(0.0,3*tsys)
        pl.hlines(tsys,70,115)
        pl.annotate("Average Tsys =%6.2fK on  Chassis %d"%(tsys,2), [114,tsys-1], fontsize=13, fontweight='bold', stretch='250', horizontalalignment='right', verticalalignment='top')
        pl.savefig('rsr_summary.png', bbox_inches='tight')

if __name__ == '__main__':
    obsNumList = [65970]
    rsr = RSRRunTsys()
    M = rsr.run(sys.argv,obsNumList[-1])
        
