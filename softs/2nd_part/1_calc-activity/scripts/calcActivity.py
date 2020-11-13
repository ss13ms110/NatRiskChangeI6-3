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


# PARAMS ---------------------------------------------------------
t_inc = 0.01       # day
T_INC_FACTOR = 2.0
MONTHS = 6
BINSIZE = 2000
MUin = 1.0
TAGS = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
MUL_FACTOR = 1e-6    # convert Pa to MPa
L_CUT = -8
U_CUT = 8
# initialize parameters
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

for tag in TAGS:
    print funcFile.printProcess("Working on %s at" %(tag), Stime)

    if tag in TAGS[1:4]:
        combData[tag] = combData[tag] * MUL_FACTOR
    if tag in TAGS[1:]:
        combData = combData[(combData[tag] >= L_CUT) & (combData[tag] <= U_CUT)]

    if tag=='R':
        # sort data in ascending order
        sortedDat = combData.sort_values(by=[tag], kind='quicksort')

        # calculate event rates
        R_t, t, omoriT, tagAvg = funcFile.calcRate(sortedDat, t_inc, T_INC_FACTOR, BINSIZE, tag)

        # calculate Omori parameters
        K, c, p = funcFile.calcOmori(Kin, Cin, Pin, omoriT)
        
        omoriDict[tag+'R_t'] = R_t
        omoriDict[tag+'t'] = t
        omoriDict[tag+'omoriT'] = omoriT
        omoriDict[tag+'tagAvg'] = tagAvg
        omoriDict[tag+'K'] = K
        omoriDict[tag+'c'] = c
        omoriDict[tag+'p'] = p
        j = 0
        while j != 999:
            j = int(raw_input("Enter no. "))
            # plot one omori
            funcFile.plotOmori(R_t[j], t[j], omoriT[j], K[j], c[j], p[j])

fout = open(omoriPramFile, 'wb')
dump(omoriDict, fout)
fout.close()