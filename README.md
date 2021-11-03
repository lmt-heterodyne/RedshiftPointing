# RedshiftPointing

This package helps with with reducing pointing observations for RSR.

## Python packages we need:

    dreampy3
    PIL
    netCDF4
	
should go into **requirements.txt**	

## test1: runLineCheck.py

You need obsnums 27869 27870 27871 for this. 

    make test1

# data_lmt

Apart from the usual data in RedshiftChassisN (N=0,1,2,3), there are special calibration data trees needed as well:

1. $DATA_LMT/rsr       34MB   (for calibration of any data)
1. $DATA_LMT/rsrtpm     3GB   (for pointing?)

# Examples

## Plotting EL vs. hour 

      dreampy> from dreampy3.redshift.plots import RedshiftPlot
      dreampy> pl = RedshiftPlot()
      dreampy> pl.plot_horizon('<catalogo>',delimiter='\t')

      o
      dreampy> pl.plot_horizon('<catalogo>',delimiter=',')
      o
      dreampy> pl.plot_horizon('catalog_19may2014.lis',delimiter=',', add_planets=False, utcoffset=5)


## Para graficar El vs Az, a cierto lst

      dreampy> run skymap -i <catalogo> -t <LST(horas)>


## Reducir CAL

      dreampy> run look_cal -d 2014-05-19 -s 15100


## Reducir MAP

      dreampy> run look_map -d 2014-01-28 -s 15101


## Medir pointing offsets

      dreampy> run process_map -d 2014-05-19 -s 15100 -ba

NUEVA INSTRUCCION

      dreampy> run process_map -d 2014-05-19 -s 20645 -1 --show=True

PARA EL WIDE BEAM

      dreampy> run process_map -d 2014-05-19 -1 --show m -s 20386 -t 147


## Para medir la posicion de M2 (http://wiki.lmtgtm.org/lmtwiki/PeakUpMaps)

      dreampy> run fit_m2_all -d 2014-01-28 -f 15030 -l 15032
      dreampy> run fit_m2 -d 2014-01-28 -f 15030 -l 15032 -b 2 -p 0

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

      dreampy> help(<comando>)
      o
      dreampy> help(pl.plot_horizon)


## Special calibration observation

      dreampy> run look_mapscan -d 2014-01-28 -s 15029
	  

# History

* original code by Souccar, Wallace, Shloerb
* Imported from CVS to git, and converted to use python3/dreampy3 (November 2021)
