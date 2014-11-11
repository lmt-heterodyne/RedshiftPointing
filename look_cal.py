import sys, getopt
from dreampy.redshift.netcdf import RedshiftNetCDFFile
from dreampy.redshift.plots import RedshiftPlot
from scipy.stats import nanmean

def main(argv):
    # defaults
    date = '2013-06-12'
    scan = '10491'
    chassis = '0'

    # get options
    try:
        opts, arg = getopt.getopt(argv,"hc:d:s:",["chassis=","date=","scan="])
    except getopt.GetoptError:
        print 'bad argument: usage: look_cal.py'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'usage: look_map.py'
            print '-d date in yyyy-mm-dd format'
            print '-c chassis'
            print '-s OBSNUM'
            sys.exit()
        elif opt in ("-c","--chassis"):
            chassis = arg
        elif opt in ("-d","--date"):
            date = arg
        elif opt in ("-s","--scan"):
            scan = arg
    

    scan = int(scan)
    chassis = int (chassis)
    filename = make_filename(date,scan,chassis)
    nc = RedshiftNetCDFFile(filename)
    nc.hdu.get_cal()    
    pl  = RedshiftPlot()
    pl.plot_tsys(nc)
    tsys = nanmean(nc.hdu.cal.Tsys.flatten())
    print 'Average Tsys = %6.2f K' % tsys
    pl.hlines(tsys,70,115)
    # Places a label for average Tsys so that you don't have to look at the terminal
    pl.annotate("Average Tsys =%6.2fK"%tsys, [114,tsys-1], fontsize=13, fontweight='bold',\
        stretch='250', horizontalalignment='right', verticalalignment='top') # Extra kwargs to make it pretty




def make_filename(date,scan,chassis):
    # makes a filename from date and obnum
    filename = '/data_lmt/RedshiftChassis%s/RedshiftChassis%s_%s_%06d_01_0001.nc' % (chassis, chassis, date, scan)
    return filename


main(sys.argv[1:])
