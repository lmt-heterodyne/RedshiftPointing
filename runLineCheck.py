#!/usr/bin/env python


import sys
from RSRRunLineCheck import RSRRunLineCheck

### CHANGE THESE ObsNum for every science spectrum ###
obsList = [27870,27871]
obsList = [95187, 95186]

rsr = RSRRunLineCheck()
F = rsr.run(sys.argv,obsList)
