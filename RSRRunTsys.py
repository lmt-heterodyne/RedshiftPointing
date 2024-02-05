from dreampy3.redshift.netcdf import RedshiftNetCDFFile
import numpy
import matplotlib.pyplot as pl
from matplotlib.font_manager import FontProperties
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
        y_max = 0
        y_min = 300
        for board in boards:
            y_min = numpy.min([y_min, numpy.min(hdu.cal.Tsys[board, :])])
            y_max = numpy.max([y_max, numpy.max(hdu.cal.Tsys[board, :])])
            try:
                pl.plot(hdu.frequencies[board, :], hdu.cal.Tsys[board, :],
                        linestyle='steps-mid', label='%d.%d' % (int(hdu.header.ChassisNumber), board))
            except:
                pl.plot(hdu.frequencies[board, :], hdu.cal.Tsys[board, :],
                        label='%d.%d' % (int(hdu.header.ChassisNumber), board))
        y_min = numpy.max([y_min*1.1, 0])
        y_max = numpy.min([y_max*1.1, 300])
        print('min/max = ', y_min, y_max)
        pl.set_ylim(y_min, y_max)
        pl.legend(loc='best', prop=FontProperties(size="xx-small"))
        pl.set_ylabel("Tsys (K)")

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
    

    def run(self, argv, obsNum):

        self.chassis_list = [0, 1, 2, 3]
        for i,arg in enumerate(argv):
            if arg in ("-c","--chassis"):
                self.decode_chassis_string(argv[i+1])
        pl.clf()
        #pl.figure(figsize=(6,12))
        for i,use_chassis in enumerate(self.chassis_list):
            print(use_chassis)
            ax = pl.subplot(len(self.chassis_list), 1, i+1)
            filename = genericFileSearch ('RedshiftChassis%d'%use_chassis, obsNum)
            if i == 0:
                pl.title('ObsNum %s' % (obsNum))
            try:
                nc = RedshiftNetCDFFile(filename)
            except:
                ax.annotate("File not found for Chassis %d"%(use_chassis), [0.2,0.5], fontsize=13, fontweight='bold', stretch='250', horizontalalignment='left', verticalalignment='top')
                continue
            nc.hdu.get_cal()
            #tsys = nanmean(nc.hdu.cal.Tsys.flatten())
            tsys_data = nc.hdu.cal.Tsys.flatten()
            tsys_data = tsys_data[numpy.where(numpy.isfinite(tsys_data))]
            tsys = numpy.median (tsys_data)
            print('Average Tsys = %6.2f K' % tsys)
            self.plot_tsys(ax, FontProperties, nc)
            #pl.ylim(0.0,3*tsys)
            if tsys < 1000:
                ax.hlines(tsys,70,115)
                ax.annotate("Average Tsys =%6.2fK on  Chassis %d"%(tsys,use_chassis), [71,tsys-1], fontsize=13, fontweight='bold', stretch='250', horizontalalignment='left', verticalalignment='top')

        pl.xlabel("Frequency (GHz)")
        pl.savefig('rsr_summary.png', bbox_inches='tight')

if __name__ == '__main__':
    #obsNumList = [65970]
    obsNumList = [91180]
    obsNumList = [95233]
    obsNumList = [106904]
    rsr = RSRRunTsys()
    M = rsr.run(sys.argv,obsNumList[-1])
        
