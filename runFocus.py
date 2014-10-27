#!/usr/bin/env python


import sys
from RSRRunFocus import RSRRunFocus

argv = ["-d", "2014-02-22", "-s", "16664:16667", "--show", "True"]
rsr = RSRRunFocus()
F = rsr.run(argv)

raw_input("press any key to exit: ")
