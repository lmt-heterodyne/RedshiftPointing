import os
import sys
from PIL import Image
from RSRFit import RSRMapFit
from RSRViewer import RSRFitViewer
from RSRController import RSRMapController,RSRHandleArgs
import traceback

class RSRRunPointing():
    def run(self, argv, filelist=False):

        filelist = sorted(filelist)
        print("RSRRunPointing: filelist = ", filelist)
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
            if True or (F.nresults > 0 and F.pointing_result):
                if a.show_it:
                    v.plot_pointing_summary(F, figno=(F.nchassis+1))
            # print the hpbw results too
            ###v.print_hpbw_result(F)

            try:
                image_files = ['rsr_summary.png', 'rsr_pointing_maps.png']
                if os.path.isfile('lp_spec.png'):
                    image_files = image_files + ['lp_spec.png']
                print(image_files)
                images = list(map(Image.open, image_files))
                widths, heights = list(zip(*(i.size for i in images)))

                max_width = max(widths)
                total_height = 0
                for im in images:
                    total_height = total_height + im.size[1]*max_width/im.size[0]

                new_im = Image.new('RGB', (int(max_width), int(total_height)))

                x_offset = 0
                y_offset = 0
                for im in images:
                    new_im.paste(im.resize((int(max_width), int(im.size[1]*max_width/im.size[0])), Image.ANTIALIAS), (int(x_offset),int(y_offset)))
                    y_offset += im.size[1]*max_width/im.size[0]

                new_im.save('rsr_summary.png')
                #os.system('rm -f rsr_pointing_maps.png lp_spec.png')

            except Exception as e:
                print(e)
                traceback.print_exc()
                pass

            return F



