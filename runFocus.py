#!/usr/bin/env python


import sys
from RSRRunFocus import RSRRunFocus

argv = ["-d", "2016-02-16", "-s", "56830:56833", "--show", "True"]
#argv = ["-d", "2016-02-16", "-s", "10056830:10056833", "--show", "True"]
rsr = RSRRunFocus()
F = rsr.run(argv)

raw_input("press any key to exit: ")
