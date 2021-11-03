import sys
import os
import glob
import numpy
from dreampy.lmtnetcdf import LMTNetCDFFile
import matplotlib.pyplot as pl
from data_lmt import data_lmt

def most_recent_file(glob_pattern):
    return max(glob.iglob(glob_pattern), key=os.path.getctime)

def get_telnc_file(obsnum, basepath=None,
                   most_recent=True):
    basepath = data_lmt() + '/lmttpm'
    glob_pattern = os.path.join(basepath, "lmttpm_*_%06d_*.nc" % obsnum)
    if most_recent:
        return most_recent_file(glob_pattern)
    fnames = glob.glob(glob_pattern)
    if fnames:
        return fnames[0]

msip1mm_pixel_description = {0: 'P0_USB',
                             1: 'P0_LSB',
                             2: 'P1_LSB',
                             3: 'P1_USB'}

def get_Tsys(obsnum, msip1mm=True):
    try:
        telnc = LMTNetCDFFile(get_telnc_file(obsnum))
    except:
        print("Cannot find filename with obsnum %d" % obsnum)
        return []
    if telnc.hdu.header.get('Dcs.ObsPgm') != 'Cal':
        print("Not a CAL Scan")
        return []
    if 'LmtTpm' not in telnc.hdu.header:
        print("Not an LmtTpm Scan")
        return []
    rx = telnc.hdu.header.get('Dcs.Receiver')
    time = telnc.hdu.data.TelTime
    idxh = numpy.where(telnc.hdu.data.BufPos == 3)
    idxc = numpy.where(telnc.hdu.data.BufPos == 2)
    numpixels = 1 #telnc.hdu.data.Signal.shape[1]
    tsys = numpy.zeros(numpixels)
    for pixel in range(numpixels):
        Ph = telnc.hdu.data.Signal[idxh, pixel].mean()
        Pc = telnc.hdu.data.Signal[idxc, pixel].mean()
        if rx == 'B4r': Pb = -8.9
        else: Pb = 0
        tsys[pixel] = 280 * (Pc - Pb) /(Ph - Pc)
    return time,telnc.hdu.data.Signal,tsys,rx

    
class LmtTpmRunTsys():
    def run(self, argv, obsNum):

        fig = pl.figure()
        x,y,tsys,rx = get_Tsys(obsNum)
        xp = x-x[-1]
        legend = []
        for i,d in enumerate(tsys):
            legend.append('Pixel %2d %6.1f'%(i,tsys[i]))
            yp = y[:,i]
            pl.plot(xp,yp,'.')
        pl.legend(legend,prop={'size': 10})
        pl.title("TSys %s ObsNum: %d"%(rx,obsNum))
        pl.savefig('rsr_summary.png', bbox_inches='tight')

def main():
    obsNum = 77926
    try:
        obsNum = int(sys.argv[1])
    except Exception as e:
        pass
    tsys = LmtTpmRunTsys()
    tsys.run(sys.argv, obsNum)

if __name__ == '__main__':
    main()
    
    
