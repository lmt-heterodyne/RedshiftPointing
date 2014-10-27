#!/usr/bin/env python


import sys
from RSRRunPointing import RSRRunPointing

argv = ["-d", "2014-03-03", "-s", "16887", "--show", "True"]
argv = ["-d", "2014-08-20", "-s", "101000003", "--show", "True"]
rsr = RSRRunPointing()
F = rsr.run(argv)
print ('Average Pointing:      %5.1f %5.1f    %5.1f %5.1f            %5.1f %5.1f' % 
       (F.mean_az_map_offset,
        F.mean_el_map_offset,
        F.mean_az_model_offset,
        F.mean_el_model_offset,
        F.mean_sep,
        F.mean_ang)
       )


raw_input("press any key to exit: ")
