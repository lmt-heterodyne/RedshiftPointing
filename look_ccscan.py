"""Module with script to look at an RSR Compressed Continuum Scan

Uses:   RSRHandleArgs, RSRScanViewer, RSRCC
Author: FPS
Date:   May 5, 2014
Changes:
"""
import sys
from RSRController import RSRHandleArgs
from RSRCC import RSRCC
from RSRViewer import RSRScanViewer

def main(argv):
    a = RSRHandleArgs()
    V = RSRScanViewer()
    check = a.parse_args(argv,'look_ccscan')
    if check == 0:
        V.init()
        index = 0
        scan = a.scan_list[0]
        for chassis_id,chassis in enumerate(a.chassis_list):
            cc = RSRCC(a.date,scan,chassis,groupscan=a.groupscan,subscan=a.subscan,path=a.path)
            if len(a.chassis_list)>1:
                if chassis_id == 0:
                    V.init_big_fig(figno=1)
                V.master_scan_plot(cc,a.process_list[chassis_id])
            else:
                if len(a.process_list[chassis_id])>1:
                    V.plot_all_scans(cc,a.process_list[chassis_id],figno=chassis_id+1)
                else:
                    V.init_fig(figno=chassis_id+1)
                    V.plot_scan(cc,a.process_list[chassis_id][0])

            cc.close()


main(sys.argv[1:])
