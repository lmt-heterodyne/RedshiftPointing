import sys
from RSRFit import RSRMapFit
from RSRViewer import RSRFitViewer
from RSRController import RSRMapController,RSRHandleArgs

class RSRRunPointing():
    def run(self, argv, filelist=False):

        print "filelist = ", filelist
        c = RSRMapController()
        v = RSRFitViewer()
        a = RSRHandleArgs(show_type=1)

        check=a.parse_args(argv,'process_map',1)

# test to see whether arguments properly decoded
        if check == 0:
            if a.show_it:
                v.init(a)
            # we reduce the map for first scan in a possible scan_list 
            scan = a.scan_list[0]
            F = c.reduce_map(a,scan,a.show_it,filelist)

            if F.pointing_result == False:
                F.find_pointing_result()
        
            # printed output
            ###v.print_header(F)
            ###v.print_result(F)
            ###v.print_summary_pointing(F)
 
            # plot the pointing errors for this map
            if F.nresults > 1:
                if a.show_it:
                    v.plot_pointing_summary(F, figno=(F.nchassis+1))
            # print the hpbw results too
            ###v.print_hpbw_result(F)

            return F



