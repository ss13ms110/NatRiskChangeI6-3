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
        Mc = float(line.split()[1])
        Mct = float(line.split()[2])

        if Mc < Mct:
            Mc = Mct

        combDataTmp = combDataload[combDataload.MainshockID.isin([srcName])]
        
        combDataTmp = combDataTmp[combDataTmp['mag'] >= Mc]
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
    magAvg = np.mean(abs(dat['mag'] - dat['Mc(t)']))
    b = 1/(np.log(10)*magAvg)

    Mmax = np.mean(dat['Mw-mag'])

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

# monteCarlo function for Bootstraping
def MCrealBS(srcDat, BSpram):
    
    # convert table rows to lists
    eventRows = [list(x) for x in srcDat]

    # get boot-straped rows
    Models = random.sample(eventRows, BSpram)

    # convert lists to table
    srcMCBSdat = Table(rows=Models, names=srcDat.colnames)

    return srcMCBSdat

# function to calculate Mc
def MagHist(MagList, fname):
    magBins = np.arange(0, 10.1, 0.2)

    hist, edges = np.histogram(MagList, magBins)
    print MagList

    midPoint = (edges[1:] + edges[:-1])/2

    fid = open(fname, 'w')
    for i in range(len(hist)):
        fid.write('%d   %f\n' %(hist[i], midPoint[i]))
    
    return "OK"

# calculate b-value for binned aftershocks
def calc_b(dat, binsize, tag, outPath):
    
    bVal = []
    MmaxVal = []
    avgTagVal = []
    magVal = []
    for i in range(0, dat.shape[0], binsize):
        binnedDf = dat.iloc[i:i+binsize]

        b, Mmax, avgTag = bVal_Mmax_avgTag(binnedDf, tag)
        bVal.append(b)
        MmaxVal.append(Mmax)
        avgTagVal.append(avgTag)

    #     if 195 <= avgTagVal[-1] <= 205:
    #         magVal.append(binnedDf['mag'])
    
    # # get mag histogram and save values
    # fname = outPath + str(binsize) + '/histEdges.txt'
    # ok = MagHist(magVal, fname)

    bVal = np.array(bVal)
    MmaxVal = np.array(MmaxVal)
    avgTagVal = np.array(avgTagVal)
    return bVal, MmaxVal, avgTagVal

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
