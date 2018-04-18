from fnmatch import fnmatch
import os

def genericFileSearch (inst, obsnum, root='/data_lmt', full = True):
	
	baseDir = "%s/%s/"%(root,inst)

	listDir = os.listdir(baseDir)


	for ifile in listDir:
		if fnmatch(ifile,'%s*_%06d_*.nc' %(inst,obsnum)):
			if full:
				ifile = baseDir+ifile
			return ifile

	return "" 

def genericFileSearchAll (inst, obsnum, root='/data_lmt', full = True):
        all = []
	
	baseDir = "%s/%s/"%(root,inst)

	listDir = os.listdir(baseDir)

	for ifile in listDir:
		if fnmatch(ifile,'%s*_%06d_*.nc' %(inst,obsnum)):
			if full:
				ifile = baseDir+ifile
			all.append(ifile)

	return all 

def genericFileSearchRecursive (obsnum, baseDir='/data_lmt', full = True):
        all = []

        for root, dirnames, filenames in os.walk(baseDir):
                for ifile in filenames:
		        if fnmatch(ifile,'*_%06d_*.nc' %(obsnum)):
			        if full:
				        ifile = os.path.join(root, ifile)
			        all.append(ifile)
	return all 
