# Date: 25-04-2020
# This script use Montecarlo sumilation to 
# pick one slip model for each earthquake 
# and save R vs stress data
# Inputs: combData.pkl, srcCatalog 
# Outputs: RVsStressDF.pkl

import numpy as np
import pandas as pd
import funcFile
from astropy.io import ascii
import pickle
import timeit as ti
import warnings
warnings.filterwarnings("ignore")

Stime = ti.default_timer()


#PATHS
combFile = './../3_CompAll/outputs/combData.pkl'
srcCataFile = './../1_preProcess/outputs/srcmodCata.txt'
McValueFile = './../2_McCalc/outputs/Mc_MAXC_1Yr.txt'
outPath = './outputs/RVsStress/bin_200'

#variables
itr = 1000
binsize = 200
mulFactor = 1e-6    # convert Pa to MPa
Lcut1 = -5
Lcut2 = 0
Ucut = 5
binLen = 500
tags = ['homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
models = ['R (km)', 'MAS$_0$ (MPa)', 'MAS (MPa)', 'OOP (MPa)', 'VM (MPa)', 'MS (MPa)', 'VMS (MPa)']

#--------------------------------------
#                 MAIN
#--------------------------------------

# load combData
combDataload = pd.read_pickle(combFile)
print funcFile.printLoad("Combined data loaded at", Stime)

# filter aftershocks above the Mc values [STEP 1]
combData = funcFile.filterMc(combDataload, McValueFile)
print funcFile.printProcess("Mc filter applied at", Stime)

# convert Pa to Mpa for homo_MAS, GF_MAS and GF_OOP
for tag in tags:
    if tag in tags[:3]:
        combData[tag] = combData[tag] * mulFactor
        combData = combData[(combData[tag] >= Lcut1) & (combData[tag] <= Ucut)]
    else:
        combData = combData[(combData[tag] >= Lcut2) & (combData[tag] <= Ucut)]

print funcFile.printProcess("Converted from Pa to Mpa at", Stime)

# R bins
binsR = np.linspace(min(combData['R']), max(combData['R']), binLen)


# generate empty dictionaly to hold b-values
binTagValDict = dict.fromkeys(tags)

# create empty list, later to hold all montecarlo realizations
for tag in tags:
    binTagValDict[tag] = [[]]*(binLen-1)


# load data from srcCata.txt
srcDat = ascii.read(srcCataFile)
print funcFile.printLoad("SRCMOD catalog loaded in", Stime)

trimmedIds = [x['srcmodId'][:17] for x in srcDat]

srcDat['srcmodId'][:] = trimmedIds

# run montecarlo loop
for i in range(itr):
    print funcFile.printRun("Running iteration", i, Stime)
    # pass this data to a filter function to get on montecarlo realization
    srcMCdat = funcFile.MCreal(srcDat)
    
    # [STEP 2]
    combMCdat = combData[combData.MainshockID.isin(list(srcMCdat['srcmodId']))]

    # sort data in ascending order
    sortedDat = combMCdat.sort_values(by=['R'], kind='quicksort')

    # [STEP 3]
    for tag in tags:
        
        # calculate bValue and Mmax
        avgR, avgTagVal = funcFile.calcRVsTag(sortedDat, binsize, tag)
        
        # digitize values in bins
        binRVal = np.digitize(avgR, binsR)
        binTagVal = [avgTagVal[binRVal == j].mean() for j in range(1, binLen)]

        binTagVal = np.array(binTagVal)

        binTagValDict[tag] = [ lst + [binTagVal[j]] for j,lst in enumerate(binTagValDict[tag])]



# remove NaNs from the lists
binTagValSave = dict()
# get midpoint of bins
midBinR = [(a+b)/2.0 for a, b in zip(binsR[:len(binsR)-1], binsR[1:])]

for tag in tags:
    
    tmpLst = []
    for lst in binTagValDict[tag]:
        tmpLst.append([j for j in lst if str(j) != 'nan'])
        binTagValDict[tag] = tmpLst

    # remove empty sub-lists and their corresponding bin values
    # calculate mean, std and save them in a dictionary
    tmpLstM = []
    tmpLstS = []
    tmpBin = []
    for i, lst in enumerate(binTagValDict[tag]):
        if lst:
            tmpLstM.append(np.mean(lst))
            tmpLstS.append(np.std(lst))
            
            tmpBin.append(map(midBinR.__getitem__, [i]))
    binTagValSave[tag+'_R'] = tmpBin
    binTagValSave[tag+'_err'] = tmpLstS
    binTagValSave[tag] = tmpLstM


# -------Saving to pickle ------------------
fid = open(outPath + '/RVsStressDF.pkl', 'wb')
pickle.dump(binTagValSave, fid)
fid.close()