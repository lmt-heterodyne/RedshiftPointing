#!/usr/bin/env python


import sys
from RSRRunTsys import RSRRunTsys
from Vlbi1mmRunTsys import Vlbi1mmRunTsys

### CHANGE THESE ObsNum for every science spectrum ###
#obsNum = 27869
obsNum = 65223

#rsr = RSRRunTsys()
#F = rsr.run(sys.argv,obsNum)

vlbi1mm = Vlbi1mmRunTsys()
F = vlbi1mm.run(sys.argv,obsNum)
