#!/usr/bin/env python


import sys
from RSRRunPointing import RSRRunPointing
from genericFileSearch import genericFileSearchAll
from genericFileSearch import genericFileSearchRecursive
from data_lmt import data_lmt

argv = ["-d", "2014-08-20", "-s", "101000003", "--show", "True"]
argv = ["-d", "2014-03-03", "-s", "16887", "--show", "True"]
argv = ["-d", "2014-11-01", "-s", "27064", "--show", "True"]
argv = ["-d", "2015-03-01", "-s", "37603", "--show", "True", "--chassis", "[0]"]
argv = ["-d", "2015-03-02", "-s", "37668", "--show", "True", "--throw" , "0", "--chassis", "[0]", "--board", "[0,1]", "--beam", "0"]
argv = ["-d", "2015-03-18", "-s", "38496", "--show", "True"]
argv = ["-d", "2016-02-16", "-s", "10056830", "--show", "True"]
argv = ["-d", "2018-02-27", "-s", "73014", "--chassis", "[1,2,3]", "--show", "True"]

root = data_lmt()
filelist = []
plist = None

#    parse the first argument (a single letter) followed by an optional obsnum
try:
    if sys.argv[1][0] == 'v':
        obsnum = 70868 #70880
        try:
            obsnum = int(sys.argv[2])
        except:
            pass
        chassis = [0]
        board = [i for i in range(6)]
        #board = [0,1,2,3]
        filelist = genericFileSearchAll ('vlbi1mm', obsnum, root, full = True)
    elif sys.argv[1][0] == 'l':
        print('lmttpm')
        obsnum = 102669
        obsnum = 75342
        try:
            obsnum = int(sys.argv[2])
        except:
            pass
        chassis = 'all'
        board = 'all'
        board = [0]
        filelist = genericFileSearchAll ('lmttpm', obsnum, root, full = True)
    elif sys.argv[1][0] == 's':
        print('spec')
        obsnum = 76406
        try:
            obsnum = int(sys.argv[2])
        except:
            pass
        chassis = 'all'
        board = 'all'
        chassis = [2]
        board = [i for i in range(4)]
        filelist = []
        for ch in chassis:
            inst = 'spec%d'%ch
            flist = genericFileSearchAll(inst, obsnum, root, full = True)
            for f in flist:
                filelist.append(f)
    elif sys.argv[1][0] == 'i' or sys.argv[1][0] == 'm':
        print('ifproc')
        if sys.argv[1][0] == 'm':
            print('msip1mm')
            obsnum = 75765
        elif sys.argv[1][0] == 'i':
            print('sequoia')
            obsnum = 75765
            obsnum = 102669
            obsnum = 74792
            obsnum = 76430
            obsnum = 76675
            obsnum = 77059
            obsnum = 76406
            obsnum = 77055
        try:
            obsnum = int(sys.argv[2])
        except:
            pass
        chassis = 'all'
        board = 'all'
        chassis = [0]
        board = [i for i in range(16)]
        filelist = genericFileSearchAll ('ifproc', obsnum, root, full = True)
    elif sys.argv[1][0] == 'a':
        print('all')
        obsnum = 73677
        obsnum = 102669
        obsnum = 75342
        try:
            obsnum = int(sys.argv[2])
        except:
            pass
        board = [i for i in range(6)]
        chassis = [i for i in range(6)]
        #board = [0]
        #chassis = [1]
        #plist = [[1],[0]]
        chassis = 'all'
        board = 'all'
        filelist = genericFileSearchRecursive (obsnum, root, full = True)
    elif sys.argv[1][0] == 'r':
        print('rsr')
        obsnum = 75182
        obsnum = 76805
        obsnum = 76565
        try:
            obsnum = int(sys.argv[2])
        except:
            pass
        chassis = [0,1,2,3]
        board = 'all'
        #plist = [[0],[0, 1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [0, 1, 2, 3, 4]]
        #plist = [[],[1], [], []]
        filelist = []
        for ch in chassis:
            inst = 'RedshiftChassis%d'%ch
            flist = genericFileSearchAll(inst, obsnum, root, full = True)
            for f in flist:
                filelist.append(f)
except Exception as e:
    print('---------', e)
    obsnum = 73014
    chassis = [1,2,3]
    board = [0,1,2,3,4,5]
    plist = None
    filelist = []
    for ch in chassis:
        inst = 'RedshiftChassis%d'%ch
        flist = genericFileSearchAll(inst, obsnum, root, full = True)
        for f in flist:
            filelist.append(f)
    pass


plist = [[0,1,2,3,4,5],[0,1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], [0,1, 2, 3, 4, 5]]
#plist = [[], [1], [], []]
argv = ["-d", " ", "-s", str(obsnum), "--chassis", str(chassis), "--board", str(board), "--list", str(plist), "--show", "True"]#, "-r"]
#argv += ["--beam", "-1"]

if plist is not None:
    argv.append("--list")
    argv.append(str(plist))

rsr = RSRRunPointing()
F = rsr.run(argv, filelist)
print(F)
sys.exit(0)
#F = rsr.run(argv)
print(('Average Pointing:      %5.1f %5.1f    %5.1f %5.1f    %5.1f %5.1f            %5.1f %5.1f' % 
       (F.mean_az_map_offset,
        F.mean_el_map_offset,
        F.mean_az_model_offset,
        F.mean_el_model_offset,
        F.mean_az_total_offset,
        F.mean_el_total_offset,
        F.mean_sep,
        F.mean_ang)
       ))
F.find_hpbw_result()
rsr_fp = open('rsr.csv', 'w')
rsr.v.write_pointing_log_header(rsr_fp)
rsr.v.write_pointing_log_entry(F,rsr_fp)


