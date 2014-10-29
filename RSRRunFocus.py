import sys
from RSRFit import RSRM2Fit
from RSRViewer import RSRM2FitViewer
from RSRController import RSRMapController,RSRHandleArgs

class RSRRunFocus():
    def run(self, argv, filelist=False, obsNumArg=False):

        print "filelist = ", filelist
        c = RSRMapController()
        v = RSRM2FitViewer()
        a = RSRHandleArgs(show_type=1)

        check=a.parse_args(argv,'fit_m2',1)

# test to see whether arguments properly decoded
        if check == 0:
            # we reduce the map for first scan in a possible scan_list 
            f = c.reduce_maps(a,filelist)

            m = RSRM2Fit(f)

            m.find_focus()
            v.print_results(m)

            m.fit_focus_model()

            v.print_focus_model_fit(m)
            if a.show_it:
                v.init(a)
                if a.show_ion == 1:
                    v.plot_fits(m,figno=1)
                v.plot_focus_model_fit(m,figno=2,obsNumArg=obsNumArg)

            return m



