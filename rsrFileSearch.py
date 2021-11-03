from fnmatch import fnmatch
from data_lmt import data_lmt
from os  import listdir

def rsrFileSearch (obsnum, chassis, root=None, full = True):
        root = data_lmt(root)
	if chassis < 0 or chassis >3:
		print("Error no chassis %d" % chassis)
		return ""

	chassisDir = "%s/RedshiftChassis%d/"%(root,chassis)

	listDir = listdir(chassisDir)


	for ifile in listDir:
		if fnmatch(ifile,'RedshiftChassis%d_*_%06d_*.nc' %(chassis, obsnum)):
			if full:
				ifile = chassisDir+ifile
			return ifile

	return "" 

def rsrFileSearchAll (obsnum, root=None, full = True):
        root = data_lmt(root)
        all = []
        for chassis in range(4):
	        chassisDir = "%s/RedshiftChassis%d/"%(root,chassis)

	        listDir = listdir(chassisDir)


	        for ifile in listDir:
		        if fnmatch(ifile,'RedshiftChassis%d_*_%06d_*.nc' %(chassis, obsnum)):
			        if full:
				        ifile = chassisDir+ifile
			        all.append(ifile)

	return all 
