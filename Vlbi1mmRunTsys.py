try:
    from dreampy3.onemm.netcdf import OnemmNetCDFFile
    from genericFileSearch import genericFileSearch
except:
    pass
import matplotlib.pyplot as plt
import numpy
from scipy.stats import nanmean
import os.path

class Vlbi1mmRunTsys():
    def run(self, argv, obsNum):

        plotlabel = ''
        try:
            filename = genericFileSearch('vlbi1mm',obsNum)
            nc = OnemmNetCDFFile(filename)
            nc.hdu.process_scan()
            try:
                obsNum = nc.hdu.header.ObsNum[0]
            except:
                obsNum = nc.hdu.header.ObsNum
                time = nc.hdu.data.Time

            with open('/var/www/vlbi1mm/vlbi1mm_tsys.html', 'w') as fp:
                fp.write("LCP %3.1f\n" %(nc.hdu.Tsys['APower']))
                fp.write("RCP %3.1f\n" %(nc.hdu.Tsys['BPower']))
                fp.write("ObsNum %d\n" %(obsNum))
                fp.write("Time %3.1f\n" %(time[-1]))
                plotlabel = "LCP %3.1f K, RCP %3.1f K" %(nc.hdu.Tsys['APower'],nc.hdu.Tsys['BPower'])

        except:
            pass
            

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.text(0.1, 0.5, plotlabel, clip_on=True)
	ax.set_title("ObsNum: %d"% obsNum)  
        ax.set_yticklabels([])
        ax.set_xticklabels([])
#        plt.axis('off')
#        plt.show()
        plt.savefig('rsr_summary.png', bbox_inches='tight')
