# Date: 02-04-2020
# This script use Montecarlo sumilation to 
# pick on slip model for each earthquake 
# and make various plots
# Inputs: combData.pkl, srcCatalog 
# Outputs: various plots

import numpy as np
import pandas as pd
import funcFile
from astropy.io import ascii
import matplotlib.pyplot as plt


#PATHS
combFile = './../3_CompAll/outputs/combData.pkl'
srcCataFile = './../1_preProcess/outputs/srcmodCata.txt'
McValueFile = './../2_McCalc/outputs/Mc_MAXC_1Yr.txt'

#variables
itr = 1
binsize = 50
# tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
tags = ['R']

#MAIN

# load combData
combDataload = pd.read_pickle(combFile)

# filter aftershocks above the Mc values [STEP 1]
combData = funcFile.filterMc(combDataload, McValueFile)

# load data from srcCata.txt
srcDat = ascii.read(srcCataFile)

trimmedIds = [x['srcmodId'][:17] for x in srcDat]

srcDat['srcmodId'][:] = trimmedIds

plt.figure()
# run montecarlo loop
for i in range(itr):
    # pass this data to a filter function to get on montecarlo realization

    srcMCdat = funcFile.MCreal(srcDat)
    
    # [STEP 2]
    combMCdat = combData[combData.MainshockID.isin(list(srcMCdat['srcmodId']))]

    # [STEP 3]
    for tag in tags:
    
        sortedDat = combMCdat.sort_values(by=[tag], kind='quicksort')

        
        bVal, MmaxVal, avgTagVal = funcFile.calc_b(sortedDat, binsize, tag)


plt.scatter(avgTagVal, bVal)
plt.show()    


