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
combFile = './../3_CompAll/outputs/combData_7_2.pkl'
srcCataFile = './../1_preProcess/outputs/testCata.txt'
McValueFile = './../2_McCalc/outputs/Mc_MAXC_1Yr.txt'
outP = './outputs/t1'

#variables
binsize = 300
bin2 = 100      #background dots
mnths = 3
mulFactor = 1e-6    # convert Pa to MPa
Lcut1 = -5
Lcut2 = 0
Ucut = 5
tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
mcL = [5, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
lcL = [0, -1.5, -2.5, -0.5, 0, 0, 0]
ucL = [120, 1.5, 2.0, 4.0, 1.2, 2.5, 4.2]

cutList = {tag: mcL[i] for i, tag in enumerate(tags)}
lc = {tag: lcL[i] for i, tag in enumerate(tags)}
uc = {tag: ucL[i] for i, tag in enumerate(tags)}

outPath = outP

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
GRDict = dict()
RvSdict = dict()

for tag in tags:
    print tag
    # sort data in ascending order
    sortedDat = combData.sort_values(by=[tag], kind='quicksort')
    
    # calculate bValue and Mmax CUMULATIVE
    bValCu, bValErrCu, avgTagValCu = funcFile.calc_bCumm(sortedDat, binsize, tag)
    
    
    # get GR data
    magDict, RvSvals = funcFile.getGR(sortedDat, tag, cutList, lc, uc, tags)

    GRDict.update(magDict)
    RvSdict.update(RvSvals)

    # cumulative
    bValSave[tag+'Cu'] = avgTagValCu
    bValSave[tag+'_bValCu'] = bValCu
    bValSave[tag+'_bValErrCu'] = bValErrCu

    
# save GRDict
fGR = open(outP + '/GRdict.pkl', 'wb')
fRvS = open(outP + '/RvSdict.pkl', 'wb')
pickle.dump(GRDict, fGR)
pickle.dump(RvSdict, fRvS)
fGR.close()
fRvS.close()

# -------Saving to pickle ------------------
fbVal = open(outPath + '/bValDF.pkl', 'wb')
pickle.dump(bValSave, fbVal)
fbVal.close()
