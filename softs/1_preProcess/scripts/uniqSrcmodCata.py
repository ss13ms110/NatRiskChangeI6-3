import numpy as np
from astropy.io import ascii
import random
from astropy.table import Table

srcCataFile = './outputs/newSrcmodCata.txt'
outFile = './outputs/uniwSrcmodCata.txt'

# load data from srcCata.txt
srcDat = ascii.read(srcCataFile)

# trimmedIds = [x['srcmodId'][:17] for x in srcDat]

# srcDat['srcmodId'][:] = trimmedIds



srcIDall = list(srcDat['srcmodId'])
    
srcIDuniq = sorted(set([i[:11] for i in srcIDall]))

# loop for every unique event
OnceModels = []
for srcName in srcIDuniq:
    # filter all slip models for this particular event
    eventRows = [list(x) for x in srcDat if x['srcmodId'][:11] == srcName]
    
    # randomly choose on model of all slip models
    oneSlp = random.choice(eventRows)

    # append to the list
    OnceModels.append(oneSlp)

# convert lists into a table
srcMCdat = Table(rows=OnceModels, names=srcDat.colnames)

ascii.write(srcMCdat, outFile, overwrite=True)