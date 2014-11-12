#!/usr/bin/env python


import sys
from RSRRunTsys import RSRRunTsys

### CHANGE THESE ObsNum for every science spectrum ###
obsNum = 27869

rsr = RSRRunTsys()
F = rsr.run(sys.argv,obsNum)
