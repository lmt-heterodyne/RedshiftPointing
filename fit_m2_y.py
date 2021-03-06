"""Module with the fit_m2 script which finds optimum position of M2 from pointing maps.

Uses:    sys, RSRMapController, RSRHandleArgs, RSRMapFit, RSRM2Fit, RSRM2FitViewer
Author:  FPS
Date:    May 5, 2014
Changes:
"""
import sys

from RSRController import RSRMapController,RSRHandleArgs
from RSRFit import RSRMapFit
from RSRFit import RSRM2Fit
from RSRViewer import RSRM2FitViewer

def main(argv):
    a = RSRHandleArgs()
    C = RSRMapController()
    V = RSRM2FitViewer()

    check = a.parse_args(argv,'fit_m2',1)

    if check == 0:
        F = C.reduce_maps(a)

        M = RSRM2Fit(F,1)

        M.find_focus()
        V.print_results(M)
        V.print_summary_fit(M)

        if a.show_it:
            V.init(a)
            V.plot_fits(M,figno=1)

main(sys.argv[1:])
