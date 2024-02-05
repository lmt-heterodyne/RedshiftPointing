from fnmatch import fnmatch
from data_lmt import data_lmt
import os

def genericFileSearch (inst, obsnum, root=None, full = True):
    root = data_lmt(root)
      
    baseDir = "%s/%s/"%(root,inst)

    listDir = os.listdir(baseDir)

      
    for ifile in listDir:
        if fnmatch(ifile,'%s*_%06d_*.nc' %(inst,obsnum)):
            if full:
                ifile = baseDir+ifile
            return ifile

    return "" 

def genericFileSearchAll (inst, obsnum, root=None, full = True):
        root = data_lmt(root)        
        all = []
      
        baseDir = "%s/%s/"%(root,inst)

        listDir = os.listdir(baseDir)

        for ifile in listDir:
                if fnmatch(ifile,'%s*_%06d_*.nc' %(inst,obsnum)):
                        if full:
                                ifile = baseDir+ifile
                        all.append(ifile)

        return all 

def genericFileSearchRecursive (obsnum, baseDirs=None, full = True):
        baseDirs = data_lmt(baseDirs)
        all = []
        if isinstance(baseDirs, str):
                baseDirs = [baseDirs]
        #print('genericFileSearchRecursive in', baseDirs)
        for baseDir in baseDirs:
            for root, dirnames, filenames in os.walk(baseDir, followlinks=True):
                    for ifile in filenames:
                            if fnmatch(ifile,'*_%06d_*.nc' %(obsnum)):
                                    if full:
                                            ifile = os.path.join(root, ifile)
                                    all.append(ifile)
        return all 

def genericFileSearchInstList (obsnum, baseDir=None, insts=[], full = True):
        baseDir = data_lmt(baseDir)
        all = []

        for inst in insts:
                files = genericFileSearchAll (inst, obsnum, baseDir, full)
                if files:
                        all += files
                        
        return all 

if __name__ == '__main__':
        root = data_lmt(None)
        print(genericFileSearchInstList(103393, root, ['lmttpm', 'tel', 'ifproc']))
