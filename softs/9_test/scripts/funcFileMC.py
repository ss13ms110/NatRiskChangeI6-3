# this script contains all functions used in master.py

import numpy as np
import pandas as pd
from astropy.table import Table
import random
import timeit as ti
import datetime as dt
import matplotlib.pyplot as plt

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

# function to filter earthquakes within x months of mainshock
def filterMnths(dat, mnths, srcDat):
    filteredDat = pd.DataFrame()

    for i in range(len(srcDat)):
        yr = int(srcDat[i]['Yr'])
        mn = int(srcDat[i]['Mn'])
        dy = int(srcDat[i]['Dy'])
        hr = int(srcDat[i]['Hr'])
        mi = int(srcDat[i]['Mi'])
        se = int(srcDat[i]['Sec'])
        srcN = srcDat[i]['srcmodId']

        sDT = dt.datetime(yr, mn, dy, hr, mi, se) + dt.timedelta(seconds=1)
        eDT = sDT + dt.timedelta(days=int(mnths*30))
        
        datTmp = dat[dat['MainshockID'] == srcN]
        datTmp = datTmp[datTmp['time'] >= sDT]
        datTmp = datTmp[datTmp['time'] <= eDT]
        
        filteredDat = filteredDat.append(datTmp)

    return filteredDat

# calculate b value and ERROR using Aki estimator
def bVal_Mmag_avgTag(dat, tag, i):
    magAvg = np.mean(dat['mag'] - dat['Mc(t)'])
    

    n = len(dat['mag'] - dat['Mc(t)'])
    b = 1/(np.log(10)*magAvg)

    bErr = b/np.sqrt(n)
    

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
    return b, bErr, magAvg, avgTag

def bVal_Mmag_avgTag_R(dat, tag, tagi):
    magAvg = np.mean(dat['mag'] - dat['Mc(t)'])

    n = len(dat['mag'] - dat['Mc(t)'])
    b = 1/(np.log(10)*magAvg)

    bErr = b/np.sqrt(n)
    

    if tag in ['homo_MAS', 'GF_MAS', 'GF_OOP']:
        if tagi < 0:
            avgTag = np.max(dat[tag])
        else:
            avgTag = np.min(dat[tag])
    else:
        avgTag = np.min(dat[tag])
    if tag == 'R':
        avgTag = np.max(dat[tag])
    # avgTag = np.mean(dat[tag])
    return b, bErr, magAvg, avgTag



# calculate b-value for CUMULATIVE binned aftershocks
def calc_bCumm(dat, binsize, tag, dR, dS):
    
    bVal = []
    bValErr = []
    magAvgVal = []
    avgTagVal = []

    tgMin, tgMax = min(dat[tag]), max(dat[tag])
    print tgMin, "---", tgMax
    dd = dS
    if tag == 'R':
        dd = dR
    tagRange = np.arange(tgMin, tgMax, dd)
    
    for i in tagRange[:-1]:
        if tag in ['homo_MAS', 'GF_MAS', 'GF_OOP']:
            if i < 0:
                binnedDf = dat[(dat[tag] <= i)]
            else:
                binnedDf = dat[(dat[tag] >= i)]
        elif tag == 'R':
            # binnedDf = dat[(dat[tag] >= i) & (dat[tag] < i+dd)]
            binnedDf = dat[(dat[tag] <= i)]
            
        else:
            binnedDf = dat[(dat[tag] >= i)]

        if len(binnedDf) > 500:
            b, bErr, magAvg, avgTag = bVal_Mmag_avgTag(binnedDf, tag, i)

            bVal.append(b)
            bValErr.append(bErr)
            magAvgVal.append(magAvg)
            avgTagVal.append(avgTag)

    
    bVal = np.array(bVal)
    bValErr = np.array(bValErr)
    magAvgVal = np.array(magAvgVal)
    avgTagVal = np.array(avgTagVal)
    return bVal, bValErr, magAvgVal, avgTagVal

# calculate b-value for CUMULATIVE binned aftershocks adding 100 bins in R
def calc_bCumm_R(dat, binR, tag):
    print "        cumm RR"
    bVal = []
    bValErr = []
    magAvgVal = []
    avgTagVal = []

    tgData = np.array(dat[tag])
    tgMax = max(tgData)
    tgLen = len(tgData)

    i = binR
    
    while tgData[i] <= tgMax:
        
        if tag in ['homo_MAS', 'GF_MAS', 'GF_OOP']:
            if tgData[i] < 0:
                binnedDf = dat[(dat[tag] <= tgData[i])]
            else:
                binnedDf = dat[(dat[tag] >= tgData[i])]
        
        elif tag == 'R':
            binnedDf = dat[(dat[tag] <= tgData[i])]

        else:
            binnedDf = dat[(dat[tag] >= tgData[i])]
        
        b, bErr, magAvg, avgTag = bVal_Mmag_avgTag_R(binnedDf, tag, tgData[i])

        bVal.append(b)
        bValErr.append(bErr)
        magAvgVal.append(magAvg)
        avgTagVal.append(avgTag)

        # i INCREMENT
        i += binR
        if i > tgLen:
            break

    
    bVal = np.array(bVal)
    bValErr = np.array(bValErr)
    magAvgVal = np.array(magAvgVal)
    avgTagVal = np.array(avgTagVal)
    return bVal, bValErr, magAvgVal, avgTagVal

# function to get GR data
def getGR(dat, tag, cutList, lc, uc, tags):
    
    RvSdict = dict()
    magBins = np.arange(0,10.1,0.1)

    if tag == 'R':
        lcDat = dat[(dat[tag] > lc[tag]) & (dat[tag] < lc[tag]+cutList[tag])]
        ucDat = dat[(dat[tag] > uc[tag]-cutList[tag]) & (dat[tag] < uc[tag])]
        for tg in tags:
            RvSdict.update({'lc1'+tg: lcDat[tg], 'uc1'+tg: ucDat[tg]})
        
    else:
        lcDat = dat[(dat[tag] > lc[tag]) & (dat[tag] < lc[tag]+cutList[tag])]
        ucDat = dat[(dat[tag] > uc[tag]-cutList[tag]) & (dat[tag] < uc[tag])]
        RvSdict.update({'lcR'+tag: lcDat['R'], 'lcS'+tag: lcDat[tag], 'ucR'+tag: ucDat['R'], 'ucS'+tag: ucDat[tag]})
       


    lcmags = list(lcDat['mag'] - lcDat['Mc(t)'])
    ucmags = list(ucDat['mag'] - ucDat['Mc(t)'])

    lcbVal = 1/(np.log(10)*np.mean(lcmags))
    ucbVal = 1/(np.log(10)*np.mean(ucmags))


    lcHist, lcEdges = np.histogram(lcmags, magBins)
    ucHist, ucEdges = np.histogram(ucmags, magBins)

    magDict = dict({'lcHist'+tag: lcHist, 'lcMidMag'+tag: [(lcEdges[1:] + lcEdges[:-1])/2], 'lcbVal'+tag: lcbVal})
    magDict.update({'ucHist'+tag: ucHist, 'ucMidMag'+tag: [(ucEdges[1:] + ucEdges[:-1])/2], 'ucbVal'+tag: ucbVal})
    
    return magDict, RvSdict
