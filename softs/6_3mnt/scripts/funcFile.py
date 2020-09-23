# this script contains all functions used in master.py

import numpy as np
import pandas as pd
from astropy.table import Table
import random
import timeit as ti
import datetime as dt

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
        eDT = sDT + dt.timedelta(days=mnths*30)
        
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

# calculate b value and ERROR using Aki estimator
def bVal_Mmag_avgTagNEW(dat, tag, i):
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


# calculate b-value for binned aftershocks
def calc_bNEW(dat, binsize, tag):
    
    bVal = []
    bValErr = []
    MmagVal = []
    avgTagVal = []
    for i in range(0, dat.shape[0], binsize):
        binnedDf = dat.iloc[i:i+binsize]

        b, bErr, Mmagmax, avgTag = bVal_Mmag_avgTagNEW(binnedDf, tag, i)

        bVal.append(b)
        bValErr.append(bErr)
        MmagVal.append(Mmagmax)
        avgTagVal.append(avgTag)

    
    bVal = np.array(bVal)
    bValErr = np.array(bValErr)
    MmagVal = np.array(MmagVal)
    avgTagVal = np.array(avgTagVal)
    return bVal, bValErr, MmagVal, avgTagVal


# calculate b-value for CUMULATIVE binned aftershocks
def calc_bCumm(dat, binsize, tag):
    
    bVal = []
    bValErr = []
    MmagVal = []
    avgTagVal = []

    tgMin, tgMax = min(dat[tag]), max(dat[tag])

    tagRange = np.linspace(tgMin, tgMax, binsize)
    
    for i in tagRange[:-1]:
        if tag in ['homo_MAS', 'GF_MAS', 'GF_OOP']:
            if i < 0:
                binnedDf = dat[(dat[tag] <= i)]
            else:
                binnedDf = dat[(dat[tag] >= i)]
        elif tag == 'R':
            binnedDf = dat[(dat[tag] <= i)]
        else:
            binnedDf = dat[(dat[tag] >= i)]


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

# calculate b-value for CUMULATIVE binned aftershocks adding 100 bins in R
def calc_bCumm_R(dat, binR, tag):
    print "        cumm RR"
    bVal = []
    bValErr = []
    MmagVal = []
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

        b, bErr, Mmagmax, avgTag = bVal_Mmag_avgTag(binnedDf, tag, i)

        bVal.append(b)
        bValErr.append(bErr)
        MmagVal.append(Mmagmax)
        avgTagVal.append(avgTag)

        # i INCREMENT
        i += binR
        if i > tgLen:
            break

    
    bVal = np.array(bVal)
    bValErr = np.array(bValErr)
    MmagVal = np.array(MmagVal)
    avgTagVal = np.array(avgTagVal)
    return bVal, bValErr, MmagVal, avgTagVal

# -----------------------FUNCTION FOR magVsStressVsR.py-----------------------
# function to choose aftershocks only above Mc
def getMagSR(combDataload, McValueFile, srcDat):

    combData = pd.DataFrame()
    fid = open(McValueFile, 'r')

    for line in fid:
        srcName = line.split()[0]

        combDataTmp = combDataload[combDataload.MainshockID.isin([srcName])]
        
        combDataTmp = combDataTmp[combDataTmp['mag'] > combDataTmp['Mc(t)']]

        if not combDataTmp.empty:
            # sort by max mag
            combDataSorted = combDataTmp.sort_values(by=['mag'], kind='quicksort', ascending=False)
            row1 = combDataSorted.iloc[0]

            mainMag = srcDat[srcDat['srcmodId'] == srcName]['Mag']
            i = 1
            while i <= 5:

                if row1['mag'] < mainMag:
                    combrow = row1
                    break
                else:
                    row1 = combDataSorted.iloc[i]
                    print i
                i += 1

            print list(combrow[['MainshockID', 'mag', 'R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']])
        

        
        
        
        # print list(MaxMagDat[['MainshockID', 'mag', 'R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']])
        
        # combData = combData.append(combDataTmp)
    
    return "combData"
