import os
import sys
import numpy
from PIL import Image
from RSRFit import RSRMapFit
from RSRViewer import RSRFitViewer
from RSRController import RSRMapController,RSRHandleArgs
import traceback

class RSRRunPointing():
    def run(self, argv, filelist=False):

      try:
        filelist = sorted(filelist)
        print("RSRRunPointing: filelist = ", filelist)
        c = RSRMapController()
        self.v = RSRFitViewer()
        a = RSRHandleArgs(show_type=1)

        check=a.parse_args(argv,'process_map',1)

# test to see whether arguments properly decoded
        if check == 0:
            if True or a.show_it:
                self.v.init(a)
            # we reduce the map for first scan in a possible scan_list 
            scan = a.scan_list[0]
            F = c.reduce_map(a,scan,a.show_it,filelist)

            if F.pointing_result == False:
                F.find_pointing_result()
        
            # printed output
            ###self.v.print_header(F)
            ###self.v.print_result(F)
            ###self.v.print_summary_pointing(F)
 
            # plot the pointing errors for this map
            if True or (F.nresults > 0 and F.pointing_result):
                if True or a.show_it:
                    self.v.plot_pointing_summary(F, figno=(F.nchassis+1))
            # print the hpbw results too
            ###self.v.print_hpbw_result(F)
            if a.show_it:
                self.v.show()

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

            if True:
                results_dict = dict()
                results_dict['mean_az_map_offset'] = F.mean_az_map_offset
                results_dict['mean_el_map_offset'] = F.mean_el_map_offset
                results_dict['std_az_map_offset'] = F.std_az_map_offset
                results_dict['std_el_map_offset'] = F.std_el_map_offset
                results_dict['mean_hpbw_az_map'] = F.mean_hpbw_az_map
                results_dict['mean_hpbw_el_map'] = F.mean_hpbw_el_map
                results_dict['std_hpbw_az_map'] = F.std_hpbw_az_map
                results_dict['std_hpbw_el_map'] = F.std_hpbw_el_map
                results_dict['mean_az_model_offset'] = F.mean_az_model_offset
                results_dict['mean_el_model_offset'] = F.mean_el_model_offset
                results_dict['mean_az_total_offset'] = F.mean_az_total_offset
                results_dict['mean_el_total_offset'] = F.mean_el_total_offset
                results_dict['mean_sep'] = F.mean_sep
                results_dict['std_sep'] = F.std_sep
                results_dict['mean_ang'] = F.mean_ang
                results_dict['std_ang'] = F.std_ang
                results_dict['chassis_id'] = F.chassis_id_numbers.tolist()
                results_dict['board_id'] = F.board_id_numbers.tolist()
                print('-------> Intensity', F.Intensity, numpy.shape(F.Intensity), F.isGood)
                results_dict['intensity'] = F.Intensity.tolist()
                results_dict['mean_intensity'] = F.mean_intensity
                results_dict['std_intensity'] = F.std_intensity
                results_dict['mean_intensity_snr'] = F.mean_intensity_snr
                results_dict['std_intensity_snr'] = F.std_intensity_snr
                results_dict['tracking_beam'] = int(F.tracking_beam)
                results_dict['fit_beam_single'] = bool(F.fit_beam_single)
                results_dict['clipped'] = bool(F.clipped)
                return results_dict
            
            return F

      except Exception as e:
        traceback.print_exc()



