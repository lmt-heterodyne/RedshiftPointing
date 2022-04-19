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
    obsNumArg = "95289:95294"
    obsNumArg = "98150:98155"
    
elif which == 'i':
    obsNumArg = "74898:74902"

try:
    obsNumArg = sys.argv[2]
except:
    pass

obsNumList = [int(x) for x in obsNumArg.split(':')]
obsNums = list(range(obsNumList[0], obsNumList[1]+1))
print(obsNums)
for obsNum in obsNums:
    flist = genericFileSearchRecursive(obsNum, None, full = True)
    for f in flist:
        filelist.append(f)

plist = [[],[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4]]
argv = ["-d", "", "-s", obsNumArg, "--chassis", "all", "--board", "all", "--list", str(plist), "--show", "True"]

rsr = RSRRunFocus()
#F = rsr.run(argv)
F = rsr.run(argv, filelist, obsNumArg)

