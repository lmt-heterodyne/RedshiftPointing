from fnmatch import fnmatch
from os  import listdir
from data_lmt import data_lmt

def vlbi1mmFileSearch (obsnum, root=None, full = True):
	root = data_lmt(root)
	baseDir = "%s/vlbi1mm/"%root

	listDir = listdir(baseDir)


	for ifile in listDir:
		if fnmatch(ifile,'vlbi1mm*_%06d_*.nc' %obsnum):
			if full:
				ifile = baseDir+ifile
			return ifile

	return "" 
