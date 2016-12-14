from dreampy.redshift.netcdf import RedshiftNetCDFFile
from dreampy.redshift.plots import RedshiftPlot
from dreampy.redshift.utils.correlate_lines import CrossCorrelation
import numpy
import os.path
from rsrFileSearch import rsrFileSearch


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



### CHANGE THESE ObsNum for every science spectrum ###

#Obslist = [55240,55241,55242,55244,55245,55246,55248,55249,55250,55253,55254,55255]
Obslist = range (54708, 54710+1)
Obslist.extend (range (54712, 54714+1))
Obslist.extend (range (54717, 54719+1))
Obslist.extend (range (54721, 54723+1))

Obslist.extend (range (55164, 55166+1))
Obslist.extend (range (55168, 55170+1))
Obslist.extend (range (55172, 55174+1))
Obslist.extend (range (55178, 55180+1))
Obslist.extend (range (55182, 55184+1))
Obslist.extend (range (55186, 55188+1))


Obslist.extend (range (55309, 55311+1))
Obslist.extend (range (55313, 55315+1))
Obslist.extend (range (55317, 55319+1))
Obslist.extend (range (55323, 55325+1))
Obslist.extend (range (55331, 55333+1))

Obslist.extend (range (55473, 55475+1))
Obslist.extend (range (55477, 55479+1))
Obslist.extend (range (55481, 55483+1))
Obslist.extend (range (55487, 55489+1))
#Obslist.extend (range (55491, 55493+1))

#7 feb
Obslist.extend (range (55808, 55810+1))
Obslist.extend (range (55812, 55814+1))
Obslist.extend (range (55816, 55818+1))
Obslist.extend (range (55820, 55822+1))
Obslist.extend (range (55826, 55828+1))
#Obslist.extend (range (55830, 55832+1))
#Obslist.extend (range (55834, 55836+1))


#8 feb
Obslist.extend (range (55932, 55934+1))
Obslist.extend (range (55936, 55938+1))
Obslist.extend (range (55940, 55942+1))
Obslist.extend (range (55955, 55957+1))
Obslist.extend (range (55959, 55961+1))
Obslist.extend (range (55963, 55965+1))
Obslist.extend (range (55967, 55969+1))
Obslist.extend (range (55971, 55973+1))

for ObsNum in Obslist:
    for chassis in (0,1,2,3):

	#filename= '/data_lmt/RedshiftChassis%d/RedshiftChassis%d_%s_%06d_00_0001.nc' % (chassis, chassis, datestg, ObsNum)
	filename = rsrFileSearch (ObsNum, chassis)
	
	if filename == "":
		raise Exception ('File not found for chassis %d ObsNumber: %s ' % (chassis,ObsNum))
		

        nc = RedshiftNetCDFFile(filename)
        nc.hdu.process_scan(corr_linear=True) 
        nc.hdu.baseline(order = 1, subtract=True)
        nc.hdu.average_all_repeats(weight='sigma')
        integ = 2*int(nc.hdu.header.get('Bs.NumRepeats'))*int(nc.hdu.header.get('Bs.TSamp'))
        tint += integ
        real_tint += (nc.hdu.data.AccSamples/48124.).mean(axis=1).sum()        
        hdulist.append(nc.hdu)
        nc.sync()
        nc.close()

        
hdu = hdulist[0]  # get the first observation
hdu.average_scans(hdulist[1:])#, threshold_sigma=0.007)
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

#print "Used data %d of %d" % (usedChassis, totalChassis)

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

