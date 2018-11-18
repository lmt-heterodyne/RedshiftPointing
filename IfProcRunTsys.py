import sys
import os
import glob
import numpy
from dreampy.lmtnetcdf import LMTNetCDFFile
import matplotlib.pyplot as pl

def most_recent_file(glob_pattern):
    return max(glob.iglob(glob_pattern), key=os.path.getctime)

def get_telnc_file(obsnum, basepath='/data_lmt/ifproc',
                   most_recent=True):
    glob_pattern = os.path.join(basepath, "ifproc_*_%06d_*.nc" % obsnum)
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
        print "Cannot find filename with obsnum %d" % obsnum
        return []
    if telnc.hdu.header.get('Dcs.ObsPgm') != 'Cal':
        print "Not a CAL Scan"
        return []
    if not telnc.hdu.header.has_key('IfProc'):
        print "Not an IFProc Scan"
        return []
    rx = telnc.hdu.header.get('Dcs.Receiver')
    time = telnc.hdu.data.BasebandTime
    idxh = numpy.where(telnc.hdu.data.BufPos == 3)
    idxc = numpy.where(telnc.hdu.data.BufPos == 2)
    numpixels = telnc.hdu.data.BasebandLevel.shape[1]
    tsys = numpy.zeros(numpixels)
    for pixel in range(numpixels):
        Ph = telnc.hdu.data.BasebandLevel[idxh, pixel].mean()
        Pc = telnc.hdu.data.BasebandLevel[idxc, pixel].mean()
        Pb = 0
        tsys[pixel] = 280 * (Pc - Pb) /(Ph - Pc)
    return time,telnc.hdu.data.BasebandLevel,tsys,rx

    
class IfProcRunTsys():
    def run(self, argv, obsNum):

        x,y,tsys,rx = get_Tsys(obsNum)
        if rx == 'Msip1mm':
            with open('/var/www/vlbi1mm/vlbi1mm_tsys.html', 'w') as fp:
                for i,d in enumerate(tsys):
                    desc =  msip1mm_pixel_description.get(i)
                    val = tsys[i]
                    fp.write("%s %3.1f\n" %(desc, val))
                fp.write("ObsNum %d\n" %(obsNum))
                fp.write("Time %3.1f\n" %(x))
                print plotlabel

        fig = pl.figure()
        xp = x-x[-1]
        legend = []
        for i,d in enumerate(tsys):
            if rx == 'msip1mm':
                desc = msip1mm_pixel_description.get(i)
            else:
                desc = "Pixel %2d" % (i)
            legend.append('%s %6.1f'%(desc,tsys[i]))
            yp = y[:,i]
            pl.plot(xp,yp,'.')
        pl.legend(legend,prop={'size': 10})
        pl.title("TSys %s ObsNum: %d"%(rx,obsNum))
        pl.savefig('rsr_summary.png', bbox_inches='tight')

def main():
    obsNum = 76391
    try:
        obsNum = int(sys.argv[1])
    except Exception as e:
        pass
    tsys = IfProcRunTsys()
    tsys.run(sys.argv, obsNum)

if __name__ == '__main__':
    main()
    
    
