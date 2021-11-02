from fnmatch import fnmatch
from os  import listdir

def rsrFileSearch (obsnum, chassis, root='/data_lmt/', full = True):
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

def rsrFileSearchAll (obsnum, root='/data_lmt/', full = True):
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
