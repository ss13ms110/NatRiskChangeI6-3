import numpy as np
import pandas as pd
from astropy.io import ascii
import os

# Paths
stressPath = './../../../raw_data/stress_values'
outPath = './outputs/stressDF'
srcCataFile = './../../1_preProcess/outputs/newSrcmodCata.txt'

# prams
dirs = ['homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
models = ['MAS0', 'MAS', 'OOP', 'VM', 'MS', 'VMS']

dfColumns = ['lat', 'lon', 'dep', 'stress']
# load data from srcCata.txt
srcDat = ascii.read(srcCataFile)
trimmedIds = [x['srcmodId'][:17] for x in srcDat]
srcDat['srcmodId'][:] = trimmedIds

for i, di in enumerate(dirs):
    sdPath = '%s/%s' %(stressPath, di)
    stressDF = pd.DataFrame([], columns=dfColumns)
    DFPath = '%s/stressDF_%s.pkl' %(outPath, models[i])
    print '   Working on %s' %(di)

    for src in srcDat:
        srcID = src['srcmodId']
        print "SRC file: %s" %(srcID)

        # check for srcmod data
        srcDir = '%s/%s' %(sdPath, srcID)
        if not os.path.isdir(srcDir):
            continue

        ind = 0
        lat = []
        lon = []
        dep = []
        srcName = []
        stress = []
        for d in np.arange(2.5,50,5):
            filePath = '%s/%s_%s.txt' %(srcDir, srcID, str(d))
            
            # load file
            stressDat = np.loadtxt(filePath)

            if d == 2.5:
                lat1 = stressDat[:,0]
                lon1 = stressDat[:,1]
            lat = np.append(lat, lat1)
            lon = np.append(lon, lon1)
            dep = np.append(dep, np.full(len(lat1), d))
            # srcName = np.append(srcName, np.full(len(lat1), srcID))

            if di in ['GF_VM',  'GF_VMC',  'homo_MAS']:
                stress = np.append(stress, np.concatenate((stressDat[ind:,2], stressDat[:ind,2]))) # workaround for shifted arrays
            else:
                stress = np.append(stress, stressDat[:,2])
            ind+=1

        # put data in dataframe
        tmpDF = pd.DataFrame(np.column_stack((lat, lon, dep, stress)), columns=dfColumns)
        stressDF = stressDF.append(tmpDF)
    stressDF.to_pickle(DFPath)
