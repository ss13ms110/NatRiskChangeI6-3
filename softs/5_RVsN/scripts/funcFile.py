# this script contains all functions used in master.py

import numpy as np
import pandas as pd
from astropy.table import Table
import random
import timeit as ti

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

# Print function
def printLoad(strng, Stime):
    return bcol.OKGREEN + "\n" + strng + bcol.ENDC + " %0.2f " %((ti.default_timer() - Stime)/60.0) + bcol.OKGREEN + "minutes\n" + bcol.ENDC

def printProcess(strng, Stime):
    return bcol.OKBLUE + strng + bcol.ENDC + " %0.2f " %((ti.default_timer() - Stime)/60.0) + bcol.OKBLUE + "minutes" + bcol.ENDC

def printRun(strng, i, Stime):
    return bcol.OKBLUE + strng + bcol.ENDC + " %d " %(i+1) + bcol.OKBLUE + "at" + bcol.ENDC + " %0.2f " %((ti.default_timer() - Stime)/60.0) + bcol.OKBLUE + "minutes" + bcol.ENDC

# sigmoid filter
def sigmoid(arry, scale, shift):
    d1 = scale*arry - shift
    d2 = np.exp(-d1)
    sig = 1/(1+d2)

    return sig

# function to choose aftershocks only above Mc
def filterMc(combDataload, McValueFile):

    combData = pd.DataFrame()
    fid = open(McValueFile, 'r')

    for line in fid:
        srcName = line.split()[0]

        combDataTmp = combDataload[combDataload.MainshockID.isin([srcName])]
        
        combDataTmp = combDataTmp[combDataTmp['mag'] > combDataTmp['Mc(t)']]
        
        combData = combData.append(combDataTmp)
    
    return combData

# function to filter and scale stress values
def filterStress(df, a, b, tags):
    for tag in tags:
        df[tag] = sigmoid(df[tag], a, b)  

    # remove infs and naNs
    df = df.replace([np.inf, -np.inf], np.NaN).dropna()
    return df

# calculate b value using Aki estimator
def bVal_Mmax_avgTag(dat, tag):
    magAvg = np.mean(dat['mag'] - dat['Mc(t)'])
    b = 1/(np.log(10)*magAvg)

    Mmax = np.mean(dat['Mw-mag'])

    avgTag = np.mean(dat[tag])

    return b, Mmax, avgTag

# calculate b value and ERROR using Aki estimator
def bVal_Mmag_avgTag(dat, tag, i):
    magAvg = np.mean(dat['mag'] - dat['Mc(t)'])
    n = len(dat['mag'] - dat['Mc(t)'])
    b = 1/(np.log(10)*magAvg)

    bErr = b/np.sqrt(n)

    Mmagmax = np.median(dat['Mw-mag'])
    

    if tag in ['homo_MAS', 'GF_MAS', 'GF_OOP']:
        if i < 0:
            avgTag = np.max(dat[tag])
        else:
            avgTag = np.min(dat[tag])
    else:
        avgTag = np.min(dat[tag])
    if tag == 'R':
        avgTag = np.max(dat[tag])
    # avgTag = np.mean(dat[tag])
    return b, bErr, Mmagmax, avgTag



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

# monteCarlo function for Bootstraping
def MCrealBS(srcDat, BSpram):
    
    # convert table rows to lists
    eventRows = [list(x) for x in srcDat]

    # get boot-straped rows
    Models = random.sample(eventRows, BSpram)

    # convert lists to table
    srcMCBSdat = Table(rows=Models, names=srcDat.colnames)

    return srcMCBSdat

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

    
    bVal = np.array(bVal)
    MmaxVal = np.array(MmaxVal)
    avgTagVal = np.array(avgTagVal)
    return bVal, MmaxVal, avgTagVal

# calculate b-value and ERROR for binned aftershocks
def calc_bErr(dat, binsize, tag):
    
    bVal = []
    bValErr = []
    MmagVal = []
    MmagValStd = []
    avgTagVal = []
    for i in range(0, dat.shape[0], binsize):
        binnedDf = dat.iloc[i:i+binsize]

        b, bErr, Mmag, MmagStd, avgTag = bVal_Mmag_avgTag(binnedDf, tag)
        bVal.append(b)
        bValErr.append(bErr)
        MmagVal.append(Mmag)
        MmagValStd.append(MmagStd)
        avgTagVal.append(avgTag)

    
    bVal = np.array(bVal)
    bValErr = np.array(bValErr)
    MmagVal = np.array(MmagVal)
    MmagValStd = np.array(MmagValStd)
    avgTagVal = np.array(avgTagVal)
    return bVal, bValErr, MmagVal, MmagValStd, avgTagVal

# calculate b-value CUMULATIVE for binned aftershocks
def calc_bNEW(dat, binsize, tag):
    
    bVal = []
    bValErr = []
    MmagVal = []
    avgTagVal = []
    for i in range(0, dat.shape[0], binsize):
        binnedDf = dat.iloc[i:i+binsize]

        b, bErr, Mmagmax, avgTag = bVal_Mmag_avgTag(binnedDf, tag, i)

        bVal.append(b)
        bValErr.append(bErr)
        MmagVal.append(Mmagmax)
        avgTagVal.append(avgTag)

    
    bVal = np.array(bVal)
    bValErr = np.array(bValErr)
    MmagVal = np.array(MmagVal)
    avgTagVal = np.array(avgTagVal)
    return bVal, bValErr, MmagVal, avgTagVal


#_____________________________________________________
#               NEW
def calc_bCumm(dat, binsize, tag):
    
    bVal = []
    bValErr = []
    MmagVal = []
    avgTagVal = []

    tgMin, tgMax = min(dat[tag]), max(dat[tag])

    tagRange = np.linspace(tgMin, tgMax, binsize)
    print tagRange
    for i in tagRange[:-1]:
        if tag in ['homo_MAS', 'GF_MAS', 'GF_OOP']:
            if i < 0:
                binnedDf = dat[(dat[tag] <= i)]
            else:
                binnedDf = dat[(dat[tag] >= i)]
        else:
            binnedDf = dat[(dat[tag] >= i)]

        if tag == 'R':
            binnedDf = dat[(dat[tag] <= i)]

        b, bErr, Mmagmax, avgTag = bVal_Mmag_avgTag(binnedDf, tag, i)

        bVal.append(b)
        bValErr.append(bErr)
        MmagVal.append(Mmagmax)
        avgTagVal.append(avgTag)

    
    bVal = np.array(bVal)
    bValErr = np.array(bValErr)
    MmagVal = np.array(MmagVal)
    avgTagVal = np.array(avgTagVal)
    return bVal, bValErr, MmagVal, avgTagVal
#_____________________________________________________


def calcRVsTag(dat, binsize, tag):
    avgR = []
    avgTagVal = []

    for i in range(0, dat.shape[0], binsize):
        binnedDf = dat.iloc[i:i+binsize]

        avgR.append(np.mean(binnedDf['R']))
        avgTagVal.append(np.mean(binnedDf[tag]))

    avgR = np.array(avgR)
    avgTagVal = np.array(avgTagVal)

    return avgR, avgTagVal
