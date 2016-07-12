# Read data from measurement file
# File has a certain number of columns and multiple measurement sets
# Sets are separated by a newline
# Single title line and ', ' field delimeter

import numpy as np
from collections import OrderedDict

def readdat(filename):
    f = open(filename,'r')
    variables = {}
    ivar = 0
    mylists = {}
    col = []
    currentvarname =""

    line = f.readline()
    line = line.strip("\n").strip("#")
    print line
    names = line.split(', ')
    print names

    block =[]
    arrayofdicts = []
    for point in f:
        if point == '\n':
            block = np.asarray(block)
            block = block.T
            newdict=OrderedDict()
            for name,dat in zip(names,block):
                newdict[name] = dat
            arrayofdicts.append(newdict)
            block = []
            continue
        point = [float(x) for x in point.strip('\n').split(', ')]
        block.append(point)

    return arrayofdicts





    '''
        varfound = line.find('<')
        varendfound = line.find('/')
        if varendfound != -1:
            mylists[currentvarname] = np.array(col)
            col = []
        elif varfound != -1:
            line = line.strip("\n").strip(">").strip("<")
            words = line.split()
            vartype = words[0]
            varname = words[1]
            print vartype, varname
    	if vartype == 'Qucs':
	    continue
	elif vartype == 'indep' or vartype=='dep':
            currentvarname = varname
    elif varfound == -1:
	if 'j' not in line:
	    col.append(float(line))
	else:
	    ij = line.find('j')
	    x = float(line[0:ij-1])
	    y = float(line[ij-1:].replace("j",""))
	    col.append( complex(x,y) )
    return mylists
    '''
