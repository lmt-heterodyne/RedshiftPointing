from fnmatch import fnmatch
from os  import listdir

def vlbi1mmFileSearch (obsnum, root='/data_lmt', full = True):
	
	baseDir = "%s/vlbi1mm/"%root

	listDir = listdir(baseDir)


	for ifile in listDir:
		if fnmatch(ifile,'vlbi1mm*_%06d_*.nc' %obsnum):
			if full:
				ifile = baseDir+ifile
			return ifile

	return "" 
