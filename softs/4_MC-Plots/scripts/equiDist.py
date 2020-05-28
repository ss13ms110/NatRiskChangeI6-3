# Date: 02-04-2020
# This script use Montecarlo sumilation to 
# pick one slip model for each earthquake 
# and make various plots
# Inputs: combData.pkl, srcCatalog 
# Outputs: various plots

import numpy as np
import pandas as pd
import funcFile
from itertools import chain
from astropy.io import ascii
import matplotlib.pyplot as plt
import pickle
import timeit as ti
import warnings
warnings.filterwarnings("ignore")

Stime = ti.default_timer()

GRdist = int(raw_input("GRDist: "))
# binNum = int(raw_input("binNum"))
#PATHS
combFile = './../3_CompAll/outputs/combData.pkl'
srcCataFile = './../1_preProcess/outputs/testCata.txt'
McValueFile = './../2_McCalc/outputs/Mc_MAXC_1Yr.txtCOPY'
outP = './outputs/MC/binNumTesting'

#variables
itr = 500
binNum = 800    # this means binsize ~ 100 (~80000 in sortedCata)
mulFactor = 1e-6    # convert Pa to MPa
Lcut1 = -5
Lcut2 = 0
Ucut = 5
binLen = 500
# GRdist = 10
tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
models = ['R (km)', 'MAS$_0$ (MPa)', 'MAS (MPa)', 'OOP (MPa)', 'VM (MPa)', 'MS (MPa)', 'VMS (MPa)']

# outpath set here
outPath = outP + '/itr_' + str(itr) + '/bin_' + str(binNum)

#--------------------------------------
#                 MAIN
#--------------------------------------

# load combData
combDataload = pd.read_pickle(combFile)
print funcFile.printLoad("Combined data loaded at", Stime)

# filter aftershocks above the Mc and Mct values [STEP 1]
combData = funcFile.filterMc(combDataload, McValueFile)
print funcFile.printProcess("Mc filter applied at", Stime)

# convert Pa to Mpa for homo_MAS, GF_MAS and GF_OOP
for tag in tags[1:]:
    if tag in tags[1:4]:
        combData[tag] = combData[tag] * mulFactor
        combData = combData[(combData[tag] >= Lcut1) & (combData[tag] <= Ucut)]
    else:
        combData = combData[(combData[tag] >= Lcut2) & (combData[tag] <= Ucut)]

print funcFile.printProcess("Converted from Pa to Mpa at", Stime)

# define dictionary for bins
binsDict = dict()
for tag in tags:
    if tag == tags[0]:
        binsDict[tag] = np.linspace(min(combData['R']), max(combData['R']), binLen)
    elif tag in tags[1:4]:
        binsDict[tag] = np.linspace(Lcut1, Ucut, binLen)
    else:
        binsDict[tag] = np.linspace(Lcut2, Ucut, binLen)

# generate empty dictionaly to hold b-values
bValDict = dict.fromkeys(tags)
MmaxValDict = dict.fromkeys(tags)

# create empty list, later to hold all montecarlo realizations
for tag in tags:
    bValDict[tag] = [[]]*(binLen-1)
    MmaxValDict[tag] = [[]]*(binLen-1)


# load data from srcCata.txt
srcDat = ascii.read(srcCataFile)
print funcFile.printLoad("SRCMOD catalog loaded in", Stime)

trimmedIds = [x['srcmodId'][:17] for x in srcDat]

srcDat['srcmodId'][:] = trimmedIds

# run montecarlo loop
magValList = []
for i in range(itr):
    print funcFile.printRun("Running iteration", i, Stime)
    # pass this data to a filter function to get on montecarlo realization
    srcMCdat = funcFile.MCreal(srcDat)
    
    # [STEP 2]
    combMCdat = combData[combData.MainshockID.isin(list(srcMCdat['srcmodId']))]

    # [STEP 3]
    for tag in tags:
        
        # sort data in ascending order
        sortedDat = combMCdat.sort_values(by=[tag], kind='quicksort')
        
        # calculate bValue and Mmax
        bVal, MmaxVal, avgTagVal, magVal = funcFile.calc_bEqui(sortedDat, binNum, tag, GRdist)

        if magVal:
            magValList.append(magVal)
            # print len(list(chain(*magVal)))
        
        # digitize values in bins
        binTagVal = np.digitize(avgTagVal, binsDict[tag])
        avgbVal = [bVal[binTagVal == j].mean() for j in range(1, len(binsDict[tag]))]
        avgMmax = [MmaxVal[binTagVal == j].mean() for j in range(1, len(binsDict[tag]))]

        avgbVal = np.array(avgbVal)
        avgMmax = np.array(avgMmax)

        bValDict[tag] = [ lst + [avgbVal[j]] for j,lst in enumerate(bValDict[tag])]
        MmaxValDict[tag] = [ lst + [avgMmax[j]] for j,lst in enumerate(MmaxValDict[tag])]


#---------Mag Histogram-------
magBins = np.arange(0,10.1,0.1)
magValList = list(chain(*list(chain(*magValList))))
magHist, magEdges = np.histogram(magValList, magBins)
# save hist and edges to dict and then to pkl
magDict = dict({'magHist': magHist, 'midMag': [(magEdges[1:] + magEdges[:-1])/2]})
fMmag = open(outPath + '/GRDF_' + str(GRdist) + '.pkl', 'wb')
pickle.dump(magDict, fMmag)
fMmag.close()
#-----------------------------

# remove NaNs from the lists
bValSave = dict()
MmaxSave = dict()
midbinsDict = dict()
for tag in tags:
    # get midpoint of bins
    midbinsDict[tag] = [(a+b)/2.0 for a, b in zip(binsDict[tag][:len(binsDict[tag])-1], binsDict[tag][1:])]

    tmpLst = []
    for lst in bValDict[tag]:
        tmpLst.append([j for j in lst if str(j) != 'nan'])
        bValDict[tag] = tmpLst

    tmpLst = []
    for lst in MmaxValDict[tag]:
        tmpLst.append([j for j in lst if str(j) != 'nan'])
        MmaxValDict[tag] = tmpLst

    # remove empty sub-lists and their corresponding bin values
    # calculate mean, std and save them in a dictionary
    tmpLstM = []
    tmpLstS = []
    tmpBin = []
    for i, lst in enumerate(bValDict[tag]):
        if lst:
            tmpLstM.append(np.mean(lst))
            tmpLstS.append(np.std(lst))
            tmpBin.append(map(midbinsDict[tag].__getitem__, [i]))
    bValSave[tag] = tmpBin
    bValSave[tag+'_err'] = tmpLstS
    bValSave[tag+'_bVal'] = tmpLstM

    tmpLstM = []
    tmpLstS = []
    tmpBin = []
    for i, lst in enumerate(MmaxValDict[tag]):
        if lst:
            tmpLstM.append(np.mean(lst))
            tmpLstS.append(np.std(lst))
            tmpBin.append(map(midbinsDict[tag].__getitem__, [i]))
    MmaxSave[tag] = tmpBin
    MmaxSave[tag+'_err'] = tmpLstS
    MmaxSave[tag+'_Mw-mag'] = tmpLstM


# -------Saving to pickle ------------------
fbVal = open(outPath + '/bValDF.pkl', 'wb')
fMmax = open(outPath + '/Mw-magDF.pkl', 'wb')
pickle.dump(bValSave, fbVal)
pickle.dump(MmaxSave, fMmax)
fbVal.close()
fMmax.close()

# NOTES
# Error bars
# bootstraping
# log distance plots
# make GR map for bins
# make inset plot for stress vs distance
# make plots for larger binNum
# calculate difference to Mc vs # of events
# verify bath's law
# how many events in each stress bin
# correction for Mc and Mct
# equidistant bins
