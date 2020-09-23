# generate plot on cumulative [tag] value
# plots (b vs r<R etc.)
# use only aftershocks within 3 months

import numpy as np
import pandas as pd
import funcFile
from itertools import chain
from astropy.io import ascii
import pickle
import timeit as ti
import warnings
warnings.filterwarnings("ignore")

Stime = ti.default_timer()


#PATHS
combFile = './../3_CompAll/outputs/combData.pklOLD'
srcCataFile = './../1_preProcess/outputs/testCata.txt'
McValueFile = './../2_McCalc/outputs/Mc_MAXC_1Yr.txt'
outP = './outputs/MCmnth'

#variables
binsize = 100
mnths = 3
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
combDataTmp = funcFile.filterMc(combDataload, McValueFile)
print funcFile.printProcess("Mc filter applied at", Stime)

# ===========filter aftershocks within x months=========
# load data from srcCata.txt
srcDat = ascii.read(srcCataFile)
print funcFile.printLoad("SRCMOD catalog loaded in", Stime)

trimmedIds = [x['srcmodId'][:17] for x in srcDat]

srcDat['srcmodId'][:] = trimmedIds

combData = funcFile.filterMnths(combDataTmp, mnths, srcDat)

# convert Pa to Mpa for homo_MAS, GF_MAS and GF_OOP
for tag in tags[1:]:
    if tag in tags[1:4]:
        combData[tag] = combData[tag] * mulFactor
        combData = combData[(combData[tag] >= Lcut1) & (combData[tag] <= Ucut)]
    else:
        combData = combData[(combData[tag] >= Lcut2) & (combData[tag] <= Ucut)]

print funcFile.printProcess("Converted from Pa to Mpa at", Stime)

bValSave = dict()
MmagSave = dict()


for tag in tags:
    print tag
    # sort data in ascending order
    sortedDat = combData.sort_values(by=[tag], kind='quicksort')
    
    # calculate bValue and Mmax CUMULATIVE
    bValCu, bValErrCu, MmagValCu, avgTagValCu = funcFile.calc_bCumm(sortedDat, binsize, tag)

    # non cumulative
    bVal, bValErr, MmagVal, avgTagVal = funcFile.calc_bNEW(sortedDat, binsize, tag)

    # cumulative
    bValSave[tag+'Cu'] = MmagSave[tag+'Cu'] = avgTagValCu
    bValSave[tag+'_bValCu'] = bValCu
    bValSave[tag+'_bValErrCu'] = bValErrCu
    MmagSave[tag+'_Mw-magCu'] = MmagValCu

    bValSave[tag] = MmagSave[tag] = avgTagVal
    bValSave[tag+'_bVal'] = bVal
    bValSave[tag+'_bValErr'] = bValErr
    MmagSave[tag+'_Mw-mag'] = MmagVal


# -------Saving to pickle ------------------
fbVal = open(outPath + '/bValDF.pkl', 'wb')
fMmax = open(outPath + '/Mw-magDF.pkl', 'wb')
pickle.dump(bValSave, fbVal)
pickle.dump(MmagSave, fMmax)
fbVal.close()
fMmax.close()
