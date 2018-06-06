import sys
from PIL import Image
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

            if m.m2pos == -1:
                return m

            m.find_focus()
            v.print_results(m)

            m.fit_focus_model()

            v.print_focus_model_fit(m)
            if a.show_it:
                v.init(a)
                v.init_big_fig(figno=1,chassis_list=c.chassis_list, process_list=c.process_list,filelist=filelist)
                v.plot_fits(m,figno=1)
                v.plot_focus_model_fit(m,figno=2,obsNumArg=obsNumArg)

            images = map(Image.open, ['rsr_summary.png', 'rsr_focus_fits.png'])
            widths, heights = zip(*(i.size for i in images))

            total_width = sum(widths)
            total_height = sum(heights)
            max_width = max(widths)
            max_height = max(heights)

            new_im = Image.new('RGB', (max_width, total_height))

            x_offset = 0
            y_offset = 0
            for im in images:
                new_im.paste(im.resize((max_width, im.size[1]), Image.ANTIALIAS), (x_offset,y_offset))
                y_offset += im.size[1]

            new_im.save('rsr_summary.png')

            return m

