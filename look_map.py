import sys
import getopt

from RSRController import RSRHandleArgs
from RSRMap import RSRMap
from RSRViewer import RSRMapViewer

def main(argv):
    a = RSRHandleArgs()
    V = RSRMapViewer()
    check = a.parse_args(argv,'look_map')
    if check == 0:
        V.init()
        scan = a.scan_list[0]
        for chassis_id,chassis in enumerate(a.chassis_list):
            m = RSRMap(a.date,scan,chassis,beamthrow=a.beam_throw,groupscan=a.groupscan,subscan=a.subscan,path=a.path)
            if m.check():
                if len(a.chassis_list)>1:
                    if chassis_id == 0:
                        V.init_big_fig(figno=1)
                    V.master_map_plot(m,a.board_list)
                else:
                    if len(a.process_list[chassis_id])>1:
                        V.plot_all(m,a.process_list[chassis_id],figno=1)
                    else:
                        V.init_fig(figno=1)
                        V.plot_map(m,a.process_list[chassis_id][0])
            m.close()


main(sys.argv[1:])
