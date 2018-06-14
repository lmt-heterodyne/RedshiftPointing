#!/usr/bin/env python


import sys
from RSRRunFocus import RSRRunFocus
from genericFileSearch import genericFileSearchRecursive

try:
    which = sys.argv[1]
except:
    which = 'r'

filelist = []
obsNums = []

if which == 'r':
    obsNumArg = "77687:77689"
elif which == 'i':
    obsNumArg = "74898:74902"

obsNumList = [int(x) for x in obsNumArg.split(':')]
obsNums = range(obsNumList[0], obsNumList[1]+1)
print obsNums
for obsNum in obsNums:
    flist = genericFileSearchRecursive(obsNum, '/data_lmt', full = True)
    for f in flist:
        filelist.append(f)

argv = ["-d", "", "-s", obsNumArg, "--chassis", "all", "--board", "all", "--show", "True"]

rsr = RSRRunFocus()
#F = rsr.run(argv)
F = rsr.run(argv, filelist, obsNumArg)

raw_input("press any key to exit: ")
