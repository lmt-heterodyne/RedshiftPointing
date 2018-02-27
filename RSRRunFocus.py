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

            m.find_focus()
            v.print_results(m)

            m.fit_focus_model()

            v.print_focus_model_fit(m)
            if a.show_it:
                v.init(a)
                #if a.show_ion == 1:
                    #v.plot_fits(m,figno=1)
                v.plot_fits(m,figno=1)
                v.plot_focus_model_fit(m,figno=2,obsNumArg=obsNumArg)

            images = map(Image.open, ['rsr_summary.png', 'rsr_focus_fits.png'])
            widths, heights = zip(*(i.size for i in images))

            total_width = sum(widths)
            max_height = max(heights)

            new_im = Image.new('RGB', (total_width, max_height))

            x_offset = 0
            for im in images:
                new_im.paste(im.resize((im.size[0], max_height), Image.ANTIALIAS), (x_offset,0))
                x_offset += im.size[0]

            desired_size = images[0].size[0]
            old_size = new_im.size
            ratio = float(desired_size)/max(old_size)
            new_size = tuple([int(x*ratio) for x in old_size])
            new_im = new_im.resize(new_size, Image.ANTIALIAS)
            new_im2 = Image.new("RGB", (desired_size, desired_size))
            new_im2.paste(new_im, ((desired_size-new_size[0])//2,
                                   (desired_size-new_size[1])//2))


            new_im2.save('rsr_summary.png')

            return m

