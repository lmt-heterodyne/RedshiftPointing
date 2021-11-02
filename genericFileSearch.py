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

def genericFileSearchRecursive (obsnum, baseDirs='/data_lmt', full = True):
        all = []
        if isinstance(baseDirs, str):
                baseDirs = [baseDirs]
        print('genericFileSearchRecursive in', baseDirs)
        for baseDir in baseDirs:
            for root, dirnames, filenames in os.walk(baseDir):
                    for ifile in filenames:
                            if fnmatch(ifile,'*_%06d_*.nc' %(obsnum)):
                                    if full:
                                            ifile = os.path.join(root, ifile)
                                    all.append(ifile)
        return all 

def genericFileSearchInstList (obsnum, baseDir='/data_lmt', insts=[], full = True):
        all = []

        for inst in insts:
                files = genericFileSearchAll (inst, obsnum, baseDir, full)
                if files:
                        all += files
                        
        return all 


if __name__ == '__main__':
        print(genericFileSearchInstList(103393, '/data_lmt', ['lmttpm', 'tel', 'ifproc']))
