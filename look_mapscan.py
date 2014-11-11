#!/usr/bin/env python



import sys, getopt
from dreampy.redshift.netcdf import RedshiftNetCDFFile
import matplotlib.pyplot as pl

def main(argv):
    # defaults
    date = '2014-02-22'
    scan = '16667'
    chassis = '2'
    band = 0

    # get options
    try:
        opts, arg = getopt.getopt(argv,"hc:d:s:b:",["chassis=","date=","scan=","band="])
    except getopt.GetoptError:
        print 'bad argument: usage: look_map.py'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'usage: look_map.py'
            print '-c chassis'
            print '-d date in yyyy-mm-dd format'
            print '-s OBSNUM'
            print '-b band (or board) to view'
            sys.exit()
        elif opt in ("-c","--chassis"):
            chassis = arg
        elif opt in ("-d","--date"):
            date = arg
        elif opt in ("-s","--scan"):
            scan = arg
        elif opt in ("-b","--band"):
            band = eval(arg)
    

    filename = make_filename(date,scan,chassis)
    nc = RedshiftNetCDFFile(filename)
    pl.ion()
    pl.clf()
    pl.figure(1)
    pl.plot(nc.hdu.data.AccAverage[:,band])
    print 'Gains= ',nc.hdu.header.Gain
    pl.show()


def make_filename(date,scan,chassis):
    # makes a filename from date and obnum
    filename = '/data_lmt/RedshiftChassis%s/RedshiftChassis%s_%s_%06d_01_0001.nc' % (chassis, chassis, date, eval(scan))
    return filename


main(sys.argv[1:])
