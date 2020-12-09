# script to calculate aftershock activity
# by calculating aftershock density in a distance range.
# The distance is calculated from the mainshock.

import numpy as np
import pandas as pd
from astropy.io import ascii
import funcFile
import timeit as ti
from pickle import dump

Stime = ti.default_timer()

# PATHS ----------------------------------------------------------
combFile = './outputs/newCombData.pkl'
srcCataFile = './../../1_preProcess/outputs/newSrcmodCata.txt'
omoriPramFile = './outputs/omoriPrams.pkl'
figDir = './figs'


# PARAMS ---------------------------------------------------------
t_inc = 0.01       # day
T_INC_FACTOR = 1.5
MONTHS = 1
BINSIZE = 5000
dR = 1.0
dS = 0.05
TAGS = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
models = ['R', 'MAS0', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
MUL_FACTOR = 1e-6    # convert Pa to MPa
L_CUT = -8
U_CUT = 8
# initialize parameters
MUin = 1.0
Kin = 1.0
Cin = 0.01
Pin = 1.1

# MAINS ----------------------------------------------------------
# load combData
combDataload = pd.read_pickle(combFile)
print funcFile.printLoad("Combined data loaded at", Stime)

# load data from srcCata.txt
srcDat = ascii.read(srcCataFile)
print funcFile.printLoad("SRCMOD catalog loaded in", Stime)

trimmedIds = [x['srcmodId'][:17] for x in srcDat]

srcDat['srcmodId'][:] = trimmedIds

# filter aftershocks above the Mc and Mct values [STEP 1]
combDataTmp = funcFile.filterMc(combDataload, srcDat['srcmodId'])
print funcFile.printProcess("Mc filter applied at", Stime)

# filter aftershocks for months
combData = funcFile.filterMnths(combDataTmp, MONTHS, srcDat)
print funcFile.printProcess("Aftershock filtered for %s months at" %(MONTHS), Stime)

omoriDict = dict()

for i, tag in enumerate(TAGS):
    print funcFile.printProcess("Working on %s at" %(tag), Stime)
    figPath = '%s/%s' %(figDir, models[i])
    if tag == 'R':
        combData = combData[combData[tag] <= 120]
        combData.to_pickle('./outputs/tmp.pkl')
    if tag in TAGS[1:4]:
        combData[tag] = combData[tag] * MUL_FACTOR
    if tag in TAGS[1:]:
        combData = combData[(combData[tag] >= L_CUT) & (combData[tag] <= U_CUT)]

    # sort data in ascending order
    # sortedDat = combData.sort_values(by=[tag], kind='quicksort')

    # calculate event rates
    # R_t, t, omoriT, tagAvg = funcFile.calcRate(sortedDat, t_inc, T_INC_FACTOR, BINSIZE, tag)
    R_t, t, omoriT, tagAvg = funcFile.calcRate1(combData, t_inc, T_INC_FACTOR, dR, dS, tag)
    # R_t, t, omoriT, tagAvg = funcFile.calcRateCumm(sortedDat, t_inc, T_INC_FACTOR, dR, dS, tag)

    # calculate Omori parameters
    mu, K, c, p = funcFile.calcOmori(MUin, Kin, Cin, Pin, omoriT)
    
    omoriDict[models[i]+'R_t'] = R_t
    omoriDict[models[i]+'t'] = t
    omoriDict[models[i]+'omoriT'] = omoriT
    omoriDict[models[i]+'tagAvg'] = tagAvg
    omoriDict[models[i]+'mu'] = mu
    omoriDict[models[i]+'K'] = K
    omoriDict[models[i]+'c'] = c
    omoriDict[models[i]+'p'] = p
    
    # plot one omori
    for j in range(len(t)):
        funcFile.plotOmori(R_t[j], t[j], omoriT[j], mu[j], K[j], c[j], p[j], tagAvg[j], figPath)

fout = open(omoriPramFile, 'wb')
dump(omoriDict, fout)
fout.close()