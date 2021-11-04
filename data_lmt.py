#
# generic routine which finds the DATA_LMT root directory
# backwards compatible with the old hardcoded /data_lmt system
#
import os

def data_lmt(root = None, debug=False):
    """
    Find and return the DATA_LMT root directory if no root is given:
      1. $DATA_LMT
      2. /data_lmt
      3  None (failure)
    """
    if root == None:
        if 'DATA_LMT' in os.environ:
            root = os.environ['DATA_LMT']
        elif os.path.exists('/data_lmt'):
            root = '/data_lmt'
        else:
            # should never happen
            print("FATAL: $DATA_LMT and /data_lmt do not exist")
            print("       Most likely your code will now fail")
    if debug:
        print("DATA_LMT = ",root)
    return root
