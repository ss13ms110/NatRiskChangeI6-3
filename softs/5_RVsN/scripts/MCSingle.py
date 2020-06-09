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


#PATHS
combFile = './../3_CompAll/outputs/combData.pkl'
srcCataFile = './../1_preProcess/outputs/testCata.txt'
McValueFile = './../2_McCalc/outputs/Mc_MAXC_1Yr.txt'
outP = './outputs/MC/singleTest'

#variables
binsize = 500
mulFactor = 1e-6    # convert Pa to MPa
Lcut1 = -5
Lcut2 = 0
Ucut = 5
tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']

outPath = outP + '/bin_' + str(binsize)

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


# load data from srcCata.txt
srcDat = ascii.read(srcCataFile)
print funcFile.printLoad("SRCMOD catalog loaded in", Stime)

trimmedIds = [x['srcmodId'][:17] for x in srcDat]

srcDat['srcmodId'][:] = trimmedIds

bValSave = dict()
MmagSave = dict()

for tag in tags:
    
    # sort data in ascending order
    sortedDat = combData.sort_values(by=[tag], kind='quicksort')
    
    # calculate bValue and Mmax
    bVal, bValErr, MmagVal, MmagValStd, avgTagVal = funcFile.calc_bErr(sortedDat, binsize, tag)
    
    bValSave[tag] = MmagSave[tag] = avgTagVal
    bValSave[tag+'_bVal'] = bVal
    bValSave[tag+'_bValErr'] = bValErr
    MmagSave[tag+'_Mw-mag'] = MmagVal
    MmagSave[tag+'_Mw-magErr'] = MmagValStd


# -------Saving to pickle ------------------
fbVal = open(outPath + '/bValDF.pkl', 'wb')
fMmax = open(outPath + '/Mw-magDF.pkl', 'wb')
pickle.dump(bValSave, fbVal)
pickle.dump(MmagSave, fMmax)
fbVal.close()
fMmax.close()
