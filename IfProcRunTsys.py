import sys
import os
import glob
import numpy
from dreampy.lmtnetcdf import LMTNetCDFFile
import matplotlib.pyplot as plt

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
    time = telnc.hdu.data.BasebandTime
    idxh = numpy.where(telnc.hdu.data.BufPos == 3)
    idxc = numpy.where(telnc.hdu.data.BufPos == 2)
    numpixels = telnc.hdu.data.BasebandLevel.shape[1]
    Tsys = []
    for pixel in range(numpixels):
        dic = {}
        Ph = telnc.hdu.data.BasebandLevel[idxh, pixel].mean()
        Pc = telnc.hdu.data.BasebandLevel[idxc, pixel].mean()
        dic['Tsys'] = 280 * Pc/(Ph - Pc)
        if msip1mm:
            dic['desc'] = msip1mm_pixel_description.get(pixel)
        else:
            dic['desc'] = "Pixel %d" % (pixel + 1)
        Tsys.append(dic)
    return time[-1],Tsys

    
class IfProcRunTsys():
    def run(self, argv, obsNum):

        plotlabel = ""
        time,tsys = get_Tsys(obsNum)
        with open('/var/www/vlbi1mm/vlbi1mm_tsys.html', 'w') as fp:
            for d in tsys:
                desc = d['desc']
                val = d['Tsys']
                print desc, val
                fp.write("%s %3.1f\n" %(desc, val))
                plotlabel = plotlabel + "%s %3.1f\n" %(desc, val)
            fp.write("ObsNum %d\n" %(obsNum))
            fp.write("Time %3.1f\n" %(time))
            print plotlabel

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.text(0.1, 0.5, plotlabel, clip_on=True)
	ax.set_title("ObsNum: %d"% obsNum)  
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        plt.savefig('rsr_summary.png', bbox_inches='tight')

def main():
    obsNum = 74892
    try:
        obsNum = int(sys.argv[1])
    except Exception as e:
        pass
    tsys = IfProcRunTsys()
    tsys.run(sys.argv, obsNum)

if __name__ == '__main__':
    main()
    
    
