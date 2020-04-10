# this script contains all functions used in master.py

import numpy as np
import pandas as pd
from astropy.table import Table
import random

# For coloured outputs in terminal
class bcol:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# function to choose aftershocks only above Mc
def filterMc(combDataload, McValueFile):

    combData = pd.DataFrame()
    fid = open(McValueFile, 'r')

    for line in fid:
        srcName = line.split()[0]
        Mc = float(line.split()[1])

        combDataTmp = combDataload[combDataload.MainshockID.isin([srcName])]

        combDataTmp = combDataTmp[combDataTmp['mag'] >= Mc]
        combData = combData.append(combDataTmp)
    
    return combData

# calculate b value using Aki estimator
def bVal_Mmax_avgTag(dat, tag):
    magAvg = np.mean(abs(dat['mag'] - dat['Mc(t)']))
    b = 1/(np.log(10)*magAvg)

    Mmax = max(dat['mag'])

    avgTag = np.mean(dat[tag])

    return b, Mmax, avgTag


# monteCarlo function
def MCreal(srcDat):
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

    return srcMCdat


# calculate b-value for binned aftershocks
def calc_b(dat, binsize, tag):
    bVal = []
    MmaxVal = []
    avgTagVal = []
    for i in range(0, dat.shape[0], binsize):
        binnedDf = dat.iloc[i:i+binsize]

        b, Mmax, avgTag = bVal_Mmax_avgTag(binnedDf, tag)
        bVal.append(b)
        MmaxVal.append(Mmax)
        avgTagVal.append(avgTag)

    return bVal, MmaxVal, avgTagVal


