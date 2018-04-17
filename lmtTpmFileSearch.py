from fnmatch import fnmatch
from os  import listdir

def lmtTpmFileSearch (obsnum, root='/data_lmt', full = True):
	
	baseDir = "%s/lmttpm/"%root

	listDir = listdir(baseDir)


	for ifile in listDir:
		if fnmatch(ifile,'lmttpm*_%06d_*.nc' %obsnum):
			if full:
				ifile = baseDir+ifile
			return ifile

	return "" 

def lmtTpmFileSearchAll (obsnum, root='/data_lmt', full = True):
        all = []
	
	baseDir = "%s/lmttpm/"%root

	listDir = listdir(baseDir)


	for ifile in listDir:
		if fnmatch(ifile,'lmttpm*_%06d_*.nc' %obsnum):
			if full:
				ifile = baseDir+ifile
			all.append(ifile)

	return all 
