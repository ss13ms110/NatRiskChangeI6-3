import numpy as np
import timeit as ti
import pandas as pd
import datetime as dt
from scipy.optimize import minimize
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


# function to choose aftershocks only above Mc
def filterMc(combDataload, srcIDs):

    combData = pd.DataFrame()

    for srcName in srcIDs:

        combDataTmp = combDataload[combDataload.MainshockID.isin([srcName])]
        
        combDataTmp = combDataTmp[combDataTmp['mag'] > combDataTmp['Mc(t)']]
        
        combData = combData.append(combDataTmp)
    
    return combData

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

def calcRate(dat, t_inc, T_INC_FACTOR, BINSIZE, tag):
    tagAvg = []
    rate = []
    t = []
    omoriT = []
    n = dat.shape[0] - dat.shape[0]%BINSIZE
    for i in range(0, n, BINSIZE):
        binnedDf = dat.iloc[i:i+BINSIZE]

        tagAvg.append(np.mean(binnedDf[tag]))

        oT = binnedDf.sort_values(by=['omoriT'], kind='quicksort')['omoriT']
        omoriT.append(list(oT))
        
        # generate time bins
        t_bins = []
        t_start = min(oT)
        dt = t_inc
        while t_start < max(oT):
            t_bins.append(t_start)
            t_start += dt
            dt *= T_INC_FACTOR
        t_bins.append(max(oT))
        
        # calculate rate
        hist, edges = np.histogram(list(oT), t_bins)
        rate.append(hist/(edges[1:]-edges[:-1]))
        t.append((edges[1:] + edges[:-1])/2.)

    return rate, t, omoriT, tagAvg

# -----------------------OMORI support functions -------------------------
def omoriRate(t, K, c, p):
    return K/((c + t)**p)

def funcOmori(args, t_1, T1, T2):
    """ LL calculated using Omori, 1983. Assuming background rate 0"""
    K1 = np.square(args[0])
    c1 = np.square(args[1])
    p1 = np.square(args[2])

    Rintegrated = 0.0         # assuming background rate to be zero

    if p1 == 1.0:
        Rintegrated += K1 * (np.log(c1 + T2) - np.log(c1 + T1))
    
    else:
        Rintegrated += (K1/(1.0-p1)) * ((c1+T2)**(1.0-p1) - (c1+T1)**(1.0-p1))

    sumLogR = np.sum(np.log(omoriRate(t_1, K1, c1, p1)))

    LL = sumLogR - Rintegrated

    return -LL

def LLfit_omori(Kin, Cin, Pin, t_1):
    T1, T2 = min(t_1), max(t_1)

    x0 = [np.sqrt(Kin), np.sqrt(Cin), np.sqrt(Pin)]

    res = minimize(funcOmori, x0, args=(t_1, T1, T2), method='Powell')

    sqrtK, sqrtC, sqrtP = res.x

    K_fit = np.square(sqrtK)
    c_fit = np.square(sqrtC)
    p_fit = np.square(sqrtP)

    return K_fit, c_fit, p_fit

# Function to calculate Omori parameters
def calcOmori(Kin, Cin, Pin, t):

    K = []
    c = []
    p = []
    for i in range(len(t)):
        
        x = LLfit_omori(Kin, Cin, Pin, np.array(t[i]))
        K.append(x[0])
        c.append(x[1])
        p.append(x[2])

    return K, c, p

def plotOmori(rate, t, omoriT, K, c, p):
    
    omoriR = omoriRate(omoriT, K, c, p)
    plt.figure()
    plt.scatter(t, rate, marker='o', c='black')
    plt.plot(omoriT, omoriR, color='red', linewidth=2)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Days')
    plt.ylabel('Rate')
    plt.show()
    