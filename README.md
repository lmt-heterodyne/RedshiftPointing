# RedshiftPointing

This package helps with with reducing pointing observations for the RSR receiver.

## Python packages we need for installation

    dreampy3
    PIL
    netCDF4
	
(and maybe more) should go into **requirements.txt**	

# Testing

See also the Makefile, where we keep the code that works.

## test1: runLineCheck.py

You need obsnums 27869 27870 27871 for this. 

    make test1
	
## test2: runFocus.py 

Usage:

      runFocus.py  action 
	  
where **action** is a single letter action, which has pre-programmed set of obsnums. An additional
argument can override a range of obsnums

      r obsnum_range        uses 77687:77689 (default) - mars - RSR  [failure in RSRMap - no duration]
	  i obsnum_range        uses 74898:74902 - mars - SEQ   [this works]
	  
	
## runPointing.py

Usage:

      runPointing.py  action [obsnum]
	
where **action** is a single letter action, of which most also allow an optional obsnum. If not provided,
a classic known case will be used:

      v                     vlbi1mm - 70868  ['RSRMapFit' object has no attribute 'receiver']
	  l  obsnum             lmttpm - 75342
	  s  obsnum             spec - 76406
	  i  obsnum             ifproc for sequoia - 77055
	  m  obsnum             ifproc for msip1mm - 75765
	  a  obsnum             all chassis/board - 75342
	  r  obsnum             rsr - 76565 (3c273)
      <failure>             73014 (0721+713)

downstream processing is hardcoded, and uses the following flags:

    -d yyyy-mm-dd
	-s obsnum
	--chassis chassis
	--board board
	--show True




# DATA_LMT

Apart from the usual data in RedshiftChassisN (N=0,1,2,3), there are special calibration data trees needed as well
for taking pointing off-site

1. $DATA_LMT/rsr       34MB   (for calibration of any data)
1. $DATA_LMT/rsrtpm     3GB   (for pointing?)

# Examples

These were taken from a **dreampy_funcs.txt** description, and will need some cleanup.

## Plotting EL vs. hour 

      dreampy> from dreampy3.redshift.plots import RedshiftPlot
      dreampy> pl = RedshiftPlot()
      dreampy> pl.plot_horizon('<catalogo>',delimiter='\t')

      dreampy> pl.plot_horizon('<catalogo>',delimiter=',')
      dreampy> pl.plot_horizon('catalog_19may2014.lis',delimiter=',', add_planets=False, utcoffset=5)


## Para graficar El vs Az, a cierto lst

      dreampy> run skymap -i <catalogo> -t <LST(horas)>


## Reducir CAL

      dreampy> run look_cal -d 2014-05-19 -s 15100
	  
-> doesn't find the file


## Reducir MAP

      dreampy> run look_map -d 2014-01-28 -s 15101

      python look_map.py -d 2014-01-28 -s 15101


## Medir pointing offsets

      dreampy> run process_map -d 2014-05-19 -s 15100 -ba

      python process_map.py -d 2014-05-19 -s 15100 -ba

NUEVA INSTRUCCION

      dreampy> run process_map -d 2014-05-19 -s 20645 -1 --show=True
	  
      python process_map.py -d 2014-05-19 -s 20645 -1 --show=True


PARA EL WIDE BEAM

      dreampy> run process_map -d 2014-05-19 -1 --show m -s 20386 -t 147

      python process_map.py -d 2014-05-19 -1 --show m -s 20386 -t 147


## Para medir la posicion de M2 (http://wiki.lmtgtm.org/lmtwiki/PeakUpMaps)

      dreampy> run fit_m2_all -d 2014-01-28 -f 15030 -l 15032
      dreampy> run fit_m2 -d 2014-01-28 -f 15030 -l 15032 -b 2 -p 0
	  
	  # script does not exist
      python fit_m2_all.py -d 2014-01-28 -f 15030 -l 15032 
	  #
	  python fit_m2.py -d 2014-01-28 -f 15030 -l 15032 -b 2 -p 0


NUEVA INSTRUCCION

      dreampy> run fit_m2 -d 2014-05-19 -s 20651:20654 -c[0,3] --show=True -1


    -d date in yyyy-mm-dd format
    -f obsnum of FIRST scan in the sequence for fitting
    -l obsnum of LAST scan in the sequence for fitting
    -c chassis number
    -b band (or board)
    -w window for gaussian fit (arcsec)
    -p M2 parameter to fit (0=z; 1=y; 2=x)


# Ver opciones de un comando

      dreampy> help(<command>)
      dreampy> help(pl.plot_horizon)

## Special calibration observation

      dreampy> run look_mapscan -d 2014-01-28 -s 15029
	  
# History

* original code by Souccar, Wallace, Shloerb
* Imported from CVS to git, and converted to use python3/dreampy3 (November 2021)
