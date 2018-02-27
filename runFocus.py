#!/usr/bin/env python


import sys
from RSRRunFocus import RSRRunFocus

argv = ["-d", "2018-02-27", "-s", "73014:73020", "--chassis", "[1,2,3]", "--show", "True"]


filelist = [
"./data_lmt/RedshiftChassis1/RedshiftChassis1_2018-02-27_073014_01_0000.nc", 
"./data_lmt/RedshiftChassis1/RedshiftChassis1_2018-02-27_073015_01_0000.nc", 
"./data_lmt/RedshiftChassis1/RedshiftChassis1_2018-02-27_073016_01_0000.nc", 
"./data_lmt/RedshiftChassis1/RedshiftChassis1_2018-02-27_073017_01_0000.nc", 
"./data_lmt/RedshiftChassis1/RedshiftChassis1_2018-02-27_073018_01_0000.nc", 
"./data_lmt/RedshiftChassis1/RedshiftChassis1_2018-02-27_073019_01_0000.nc", 
"./data_lmt/RedshiftChassis1/RedshiftChassis1_2018-02-27_073020_01_0000.nc", 
"./data_lmt/RedshiftChassis2/RedshiftChassis2_2018-02-27_073014_01_0000.nc", 
"./data_lmt/RedshiftChassis2/RedshiftChassis2_2018-02-27_073015_01_0000.nc", 
"./data_lmt/RedshiftChassis2/RedshiftChassis2_2018-02-27_073016_01_0000.nc", 
"./data_lmt/RedshiftChassis2/RedshiftChassis2_2018-02-27_073017_01_0000.nc", 
"./data_lmt/RedshiftChassis2/RedshiftChassis2_2018-02-27_073018_01_0000.nc", 
"./data_lmt/RedshiftChassis2/RedshiftChassis2_2018-02-27_073019_01_0000.nc", 
"./data_lmt/RedshiftChassis2/RedshiftChassis2_2018-02-27_073020_01_0000.nc", 
"./data_lmt/RedshiftChassis3/RedshiftChassis3_2018-02-27_073014_01_0000.nc", 
"./data_lmt/RedshiftChassis3/RedshiftChassis3_2018-02-27_073015_01_0000.nc", 
"./data_lmt/RedshiftChassis3/RedshiftChassis3_2018-02-27_073016_01_0000.nc", 
"./data_lmt/RedshiftChassis3/RedshiftChassis3_2018-02-27_073017_01_0000.nc", 
"./data_lmt/RedshiftChassis3/RedshiftChassis3_2018-02-27_073018_01_0000.nc", 
"./data_lmt/RedshiftChassis3/RedshiftChassis3_2018-02-27_073019_01_0000.nc", 
"./data_lmt/RedshiftChassis3/RedshiftChassis3_2018-02-27_073020_01_0000.nc",
    ]
rsr = RSRRunFocus()
#F = rsr.run(argv)
F = rsr.run(argv, filelist, 7)

raw_input("press any key to exit: ")
