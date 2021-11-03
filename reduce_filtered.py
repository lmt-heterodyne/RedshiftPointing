from dreampy3.redshift.netcdf import RedshiftNetCDFFile
from dreampy3.redshift.plots import RedshiftPlot
from dreampy3.redshift.utils.correlate_lines import CrossCorrelation
import numpy
import os.path
from genericFileSearch import genericFileSearch



import numpy
from numpy.fft import fft, ifft, fftshift, fftfreq
from scipy.signal import lfilter
from scipy.signal import butter

def filter(hdu):

        nchasis = hdu.spectrum.shape[1]
        for i in range (0,nchasis):
                cspec = hdu.spectrum[0,i,:]
                wgood = numpy.where(numpy.isfinite(cspec))
                gspec = cspec[wgood]
                fspec = fft (gspec)
                ffspec = fftfreq(len(gspec))
                if i == 3:
                        cut = 0.03
                else:
                        cut = 0.03
                wx = numpy.where (numpy.abs(ffspec) < cut)
                fspec[wx] = 0.0
                hdu.spectrum[0,i,wgood] = ifft(fspec).real



hdulist = []
windows = {}
windows[0] = [(73.5, 76.8), (76.9, 79.0) ]
windows[1] = [(86.6, 91.3)]
windows[2] = [(80, 80.95), (82.3,85.4)]
windows[3] = [(92.2, 95.5), (97.4,98.0)]
windows[4] = [(105.23, 110.0)]
windows[5] = [(100, 103.5)]


tint = 0.0
real_tint = 0.0
usedChassis = 0



### CHANGE THESE TWO THINGS for every science spectrum ###
Obslist = [23481,23482,23483, 23485, 23486, 23487, 23489,23490, 23491, 23493, 23494, 23495, 23533, 23534, 23535,23537, 23538, 23539,23541, 23542, 23543, 23546 ]

for ObsNum in Obslist:
    for chassis in (0,1,2,3):
	filename = genericFileSearch ('RedshiftChassis%d'%chassis,ObsNum)
	
	if filename == "":
		raise Exception ('File not found for chassis %d ObsNumber: %s ' % (chassis,ObsNum))
		

        nc = RedshiftNetCDFFile(filename)

	usedChassis +=1
        nc.hdu.process_scan(corr_linear=True) 
        nc.hdu.baseline(order = 1, subtract=True)
        nc.hdu.average_all_repeats(weight='sigma')
        integ = 2*int(nc.hdu.header.get('Bs.NumRepeats'))*int(nc.hdu.header.get('Bs.TSamp'))
        tint += integ
	list(filter (nc.hdu))
        real_tint += (nc.hdu.data.AccSamples/48124.).mean(axis=1).sum()        
        hdulist.append(nc.hdu)
        nc.sync()
        nc.close()

        
hdu = hdulist[0]  # get the first observation
hdu.average_scans(hdulist[1:], threshold_sigma=0.01)
hdu.average_all_repeats()


#hdu.smooth(nchan=3)
hdu.make_composite_scan()
#hdu.baseline_compspectrum(order = 1, subtract=True)
pl1 = RedshiftPlot()
#pl2 = RedshiftPlot()
pl = RedshiftPlot()
pl1.plot_spectra(hdu)
# pl1.plot_line_frequencies(hdu, elim=['H', 'EtCN', 'SO2', 'CH3OH',
#                                    '13CS', 'N2H+', 'C34S', 'H13CN',
#                                    'OCS', '34SO', '(CH3)2O', 'CH3CN',
#                                     'SiO'],
#                                   'H13CO+', 'HNCO', 'C18O', 'C17O',
#                          z=3.26)

pl.clear()
pl.plot(hdu.compfreq, 1000*hdu.compspectrum[0,:], linestyle='steps-mid')
pl.set_xlim(72.5, 111.5)
#pl.set_ylim(-1., 2.)
pl.set_xlabel('Frequency (GHz)')
pl.set_ylabel('TA* (mK)')
pl.set_subplot_title("%s Tint=%f hrs" %(hdu.header.SourceName, real_tint/4.0/3600.0))


yloc = 0.023
yline = [0.021, 0.022]
z = 2.479

lines = [(r'CO (3-2)', (345.7959899, 1.5)),
         (r'CO (4-3)', (461.0407682, 2.4)),
         (r'CO (5-4)', (576.2679305, 5)),
         (r'CO (6-5)', (691.4730763, 4)),
         (r'CO (7-6)', (806.6518060, 4)),
         #(r'$\ ^{\rm 13}$CO', (330.587960, 4.0))
         ]

#for lname, (freq, yl) in lines:
#    f  = freq/(z + 1)
#    pl.set_text(f, yl, lname, rotation='vertical', horizontalalignment='center',
#                verticalalignment='center', size=10.0)

cc = CrossCorrelation(hdu)
zb, ts, zvalues, corr_funct = cc.cross_correlate(zmin=2, zmax=5, zinc=0.0005, species={'CO': 1.0}, linewidth=250) #'HCN' : 0.3,'HNC' : 0.3,'HCOP' : 0.3}, linewidth=250)
#zb, ts, zvalues, corr_funct = cc.cross_correlate(zmin=0.002, zmax=0.3, zinc=0.000005, species={'CO': 2.0,'HCN':1.0}, linewidth=120)

#pl2 = RedshiftPlot()
#pl2.plot(zvalues, corr_funct, linestyle='steps')
#pl2.set_xlabel('z')
#pl2.set_ylabel('Cross-corr Probability')

