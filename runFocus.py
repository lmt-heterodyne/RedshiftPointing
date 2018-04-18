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


argv = ["-d", "2018-02-27", "-s", "73098:73103", "--chassis", "[1,2,3]", "--show", "True"]

filelist = [
    "./data_lmt/RedshiftChassis1/RedshiftChassis1_2018-02-27_073098_01_0000.nc", 
    "./data_lmt/RedshiftChassis1/RedshiftChassis1_2018-02-27_073099_01_0000.nc", 
    "./data_lmt/RedshiftChassis1/RedshiftChassis1_2018-02-27_073100_01_0000.nc",
    "./data_lmt/RedshiftChassis1/RedshiftChassis1_2018-02-27_073101_01_0000.nc",
    "./data_lmt/RedshiftChassis1/RedshiftChassis1_2018-02-27_073102_01_0000.nc",
    "./data_lmt/RedshiftChassis1/RedshiftChassis1_2018-02-27_073103_01_0000.nc",

    "./data_lmt/RedshiftChassis2/RedshiftChassis2_2018-02-27_073098_01_0000.nc", 
    "./data_lmt/RedshiftChassis2/RedshiftChassis2_2018-02-27_073099_01_0000.nc", 
    "./data_lmt/RedshiftChassis2/RedshiftChassis2_2018-02-27_073100_01_0000.nc",
    "./data_lmt/RedshiftChassis2/RedshiftChassis2_2018-02-27_073101_01_0000.nc",
    "./data_lmt/RedshiftChassis2/RedshiftChassis2_2018-02-27_073102_01_0000.nc",
    "./data_lmt/RedshiftChassis2/RedshiftChassis2_2018-02-27_073103_01_0000.nc",

    "./data_lmt/RedshiftChassis3/RedshiftChassis3_2018-02-27_073098_01_0000.nc", 
    "./data_lmt/RedshiftChassis3/RedshiftChassis3_2018-02-27_073099_01_0000.nc", 
    "./data_lmt/RedshiftChassis3/RedshiftChassis3_2018-02-27_073100_01_0000.nc",
    "./data_lmt/RedshiftChassis3/RedshiftChassis3_2018-02-27_073101_01_0000.nc",
    "./data_lmt/RedshiftChassis3/RedshiftChassis3_2018-02-27_073102_01_0000.nc",
    "./data_lmt/RedshiftChassis3/RedshiftChassis3_2018-02-27_073103_01_0000.nc",
    ]

filelist = [
"/data_lmt/ifproc/ifproc_2018-04-18_074793_01_0000.nc",
"/data_lmt/ifproc/ifproc_2018-04-18_074794_01_0000.nc",
"/data_lmt/ifproc/ifproc_2018-04-18_074795_01_0000.nc",
"/data_lmt/ifproc/ifproc_2018-04-18_074796_01_0000.nc",
"/data_lmt/ifproc/ifproc_2018-04-18_074797_01_0000.nc",
"/data_lmt/ifproc/ifproc_2018-04-18_074798_01_0000.nc"
    ]

filelist = [
"/data_lmt/ifproc/ifproc_2018-04-18_074793_01_0000.nc",
"/data_lmt/ifproc/ifproc_2018-04-18_074794_01_0000.nc",
"/data_lmt/ifproc/ifproc_2018-04-18_074795_01_0000.nc",
    ]

argv = ["-d", "2018-04-18", "-s", "74793:74795", "--chassis", "[0]", "--board", "[0]", "--show", "True"]

rsr = RSRRunFocus()
#F = rsr.run(argv)
F = rsr.run(argv, filelist, 7)

raw_input("press any key to exit: ")
