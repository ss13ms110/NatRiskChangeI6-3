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

# using binsize
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

# using incremental bin
def calcRate1(dat, t_inc, T_INC_FACTOR, dR, dS, tag):
    tagAvg = []
    rate = []
    t = []
    omoriT = []
    tgMin, tgMax = min(dat[tag]), max(dat[tag])
    dd = dS
    if tag == 'R':
        dd = dR

    tagRange = np.arange(tgMin, tgMax, dd)
    x=[]
    y=[]
    for tag1, tag2 in zip(tagRange[:-1], tagRange[1:]):

        binnedDf = dat[(dat[tag] >= tag1) & (dat[tag] < tag2)]
        if len(binnedDf) >= 500:

            tagAvg.append(np.mean(binnedDf[tag]))

            oT = binnedDf.sort_values(by=['omoriT'], kind='quicksort')['omoriT']
            omoriT.append(list(oT))
            
            # ---------------------------------------------
            if tag == 'R':
                x.append(tagAvg[-1])
                y.append(len(binnedDf))
            # ---------------------------------------------

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

    # ----------------------------------------------------
    if tag == 'R':
        plt.figure()
        plt.scatter(x, y)
        plt.xlabel('R')
        plt.ylabel('Number')
        plt.title('Number vs Distance')
        plt.show()
    # ----------------------------------------------------
    return rate, t, omoriT, tagAvg

# using cumulative bin
def calcRateCumm(dat, t_inc, T_INC_FACTOR, dR, dS, tag):
    tagAvg = []
    rate = []
    t = []
    omoriT = []
    tgMin, tgMax = min(dat[tag]), max(dat[tag])
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
            binnedDf = dat[(dat[tag] <= i)]
            
        else:
            binnedDf = dat[(dat[tag] >= i)]

        if len(binnedDf) >= 1000:
            if tag in ['homo_MAS', 'GF_MAS', 'GF_OOP']:
                if i < 0:
                    tagAvg.append(np.max(binnedDf[tag]))
                else:
                    tagAvg.append(np.min(binnedDf[tag]))
            elif tag == 'R':
                tagAvg.append(np.max(binnedDf[tag]))
            else:
                tagAvg.append(np.min(binnedDf[tag]))

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
def omoriRate(t, mu, K, c, p):
    return mu + K/(c + t)**p

def funcOmori(args, t_1, T1, T2):
    """ LL calculated using Omori, 1983. Assuming background rate 0"""
    mu1 = np.square(args[0])
    K1 = np.square(args[1])
    c1 = np.square(args[2])
    p1 = np.square(args[3])

    Rintegrated = mu1*(T2 - T1)

    if p1 == 1.0:
        Rintegrated += K1 * (np.log(c1 + T2) - np.log(c1 + T1))
    
    else:
        Rintegrated += (K1/(1.0-p1)) * ((c1+T2)**(1.0-p1) - (c1+T1)**(1.0-p1))

    sumLogR = np.sum(np.log(omoriRate(t_1, mu1, K1, c1, p1)))

    LL = sumLogR - Rintegrated

    return -LL

def LLfit_omori(MUin, Kin, Cin, Pin, t_1):
    T1, T2 = min(t_1), max(t_1)

    x0 = [np.sqrt(MUin), np.sqrt(Kin), np.sqrt(Cin), np.sqrt(Pin)]

    res = minimize(funcOmori, x0, args=(t_1, T1, T2), method='Powell')

    sqrtMU, sqrtK, sqrtC, sqrtP = res.x

    mu_fit = np.square(sqrtMU)
    K_fit = np.square(sqrtK)
    c_fit = np.square(sqrtC)
    p_fit = np.square(sqrtP)

    return mu_fit, K_fit, c_fit, p_fit

# Function to calculate Omori parameters
def calcOmori(MUin, Kin, Cin, Pin, t):
    mu = []
    K = []
    c = []
    p = []
    for i in range(len(t)):
        x = LLfit_omori(MUin, Kin, Cin, Pin, np.array(t[i]))
        mu.append(x[0])
        K.append(x[1])
        c.append(x[2])
        p.append(x[3])

    return mu, K, c, p

def plotOmori(rate, t, omoriT, mu, K, c, p, tagAvg, figPath):
    
    omoriR = omoriRate(omoriT, mu, K, c, p)
    plt.figure()
    plt.scatter(t, rate, marker='o', c='black')
    plt.plot(omoriT, omoriR, color='red', linewidth=2)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Days')
    plt.ylabel('Rate')
    plt.title('Omori law fit for %s_Avg = %6.2f\n mu = %5.2f  K = %03d  c = %4.2f  p = %4.2f' %(figPath.split('/')[-1], tagAvg, mu, K, c, p))
    plt.savefig('%s/omoriFit_(%06.2f).png' %(figPath, tagAvg))
    plt.close()
    