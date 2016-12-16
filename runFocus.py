#!/usr/bin/env python


import sys
from RSRRunFocus import RSRRunFocus

argv = ["-d", "2016-02-16", "-s", "56830:56833", "--show", "True"]

filelist = []
filelist.append("./data_lmt/RedshiftChassis0_2016-02-16_10056830_01_0001.nc");
filelist.append("./data_lmt/RedshiftChassis0_2016-02-16_10056831_01_0001.nc");
filelist.append("./data_lmt/RedshiftChassis0_2016-02-16_10056832_01_0001.nc");
filelist.append("./data_lmt/RedshiftChassis0_2016-02-16_10056833_01_0001.nc");
filelist.append("./data_lmt/RedshiftChassis1_2016-02-16_10056830_01_0001.nc");
filelist.append("./data_lmt/RedshiftChassis1_2016-02-16_10056831_01_0001.nc");
filelist.append("./data_lmt/RedshiftChassis1_2016-02-16_10056832_01_0001.nc");
filelist.append("./data_lmt/RedshiftChassis1_2016-02-16_10056833_01_0001.nc");
filelist.append("./data_lmt/RedshiftChassis2_2016-02-16_10056830_01_0001.nc");
filelist.append("./data_lmt/RedshiftChassis2_2016-02-16_10056831_01_0001.nc");
filelist.append("./data_lmt/RedshiftChassis2_2016-02-16_10056832_01_0001.nc");
filelist.append("./data_lmt/RedshiftChassis2_2016-02-16_10056833_01_0001.nc");
filelist.append("./data_lmt/RedshiftChassis3_2016-02-16_10056830_01_0001.nc");
filelist.append("./data_lmt/RedshiftChassis3_2016-02-16_10056831_01_0001.nc");
filelist.append("./data_lmt/RedshiftChassis3_2016-02-16_10056832_01_0001.nc");
filelist.append("./data_lmt/RedshiftChassis3_2016-02-16_10056833_01_0001.nc");

rsr = RSRRunFocus()
#F = rsr.run(argv)
F = rsr.run(argv, filelist, 4)

raw_input("press any key to exit: ")
