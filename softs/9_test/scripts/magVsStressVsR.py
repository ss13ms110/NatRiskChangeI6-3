# script to get MainshockID, Maxmag, R, Stress

import pandas as pd
import numpy as np
from astropy.io import ascii


# PATHS
combFile = './outputs/CombData_9-4.pkl'
McValueFile = './../2_McCalc/outputs/Mc_MAXC_1Yr.txt'
srcCataFile = './../1_preProcess/outputs/newSrcmodCata.txt'
outP = './outputs/magSR/magSR.out'

# PARAMS
mulFactor = 1e-6    # convert Pa to MPa
Lcut1 = -8
Lcut2 = 0
Ucut = 8
tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
# load comb file
combData = pd.read_pickle(combFile)

# convert Pa to Mpa for homo_MAS, GF_MAS and GF_OOP
for tag in tags[1:]:
    if tag in tags[1:4]:
        combData[tag] = combData[tag] * mulFactor
    if tag in tags[1:]:
        combData = combData[(combData[tag] >= Lcut1) & (combData[tag] <= Ucut)]


# load srcCata
srcDat = ascii.read(srcCataFile)

trimmedIds = [x['srcmodId'][:17] for x in srcDat]

srcDat['srcmodId'][:] = trimmedIds


fid = open(McValueFile, 'r')
fout = open(outP, 'w')
fout.write('%s  %s  %s  %s  %s  %s  %s  %s  %s\n' %('MainshockID', 'mag', 'R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC'))
for line in fid:
    srcName = line.split()[0]

    combDataTmp = combData[combData.MainshockID.isin([srcName])]
    
    combDataTmp = combDataTmp[combDataTmp['mag'] > combDataTmp['Mc(t)']]

    if not combDataTmp.empty:
        # sort by max mag
        combDataSorted = combDataTmp.sort_values(by=['mag'], kind='quicksort', ascending=False)
        row1 = combDataSorted.iloc[0]

        mainMag = srcDat[srcDat['srcmodId'] == srcName]['Mag']
        i = 1
        while i <= 10:

            if row1['mag'] < mainMag:
                combrow = row1
                break
            else:
                row1 = combDataSorted.iloc[i]
                
            i += 1

        wl = list(combrow[['MainshockID', 'mag', 'R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']])
        print '%s  %4.1f  %7.3f  %7.3f  %7.3f  %7.3f  %7.3f  %7.3f  %7.3f\n' %(wl[0], wl[1], wl[2], wl[3], wl[4], wl[5], wl[6], wl[7], wl[8])
        fout.write('%s  %4.1f  %7.3f  %7.3f  %7.3f  %7.3f  %7.3f  %7.3f  %7.3f\n' %(wl[0], wl[1], wl[2], wl[3], wl[4], wl[5], wl[6], wl[7], wl[8]))


fout.close()
fid.close()