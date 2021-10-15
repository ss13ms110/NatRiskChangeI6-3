import numpy as np
import pandas as pd
from astropy.io import ascii
import os
import pklFunc as funcFile

# Paths
stressPath = './../../../raw_data/stress_values'
outPath = './outputs/stressDF'
srcCataFile = './../../1_preProcess/outputs/newSrcmodCata.txt'
srcmodPath = './../../../raw_data/srcmod/srcmod_fsp_2019Mar'


# prams
dirs = ['GF_VM', 'GF_MS', 'GF_VMC']
models = ['VM', 'MS', 'VMS']
Hdist = 100     # km

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
        
        # get polygon buffer around the mainshock fault
        slpFile = srcmodPath + '/' + srcID + '.fsp'
        xBuffer, yBuffer, polyBuffer = funcFile.getBuffer(slpFile, Hdist)

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
            #     areaIndex = funcFile.getRegion(stressDat[:,0:2], polyBuffer)

               lat1 = stressDat[:,0]
               lon1 = stressDat[:,1]
            lat = np.append(lat, lat1)
            lon = np.append(lon, lon1)
            dep = np.append(dep, np.full(len(lat1), d))
            # srcName = np.append(srcName, np.full(len(lat1), srcID))

            if di in ['GF_VM', 'GF_MS', 'GF_VMC']:
                stress = np.append(stress, np.concatenate((stressDat[ind:,2], stressDat[:ind,2]))) # workaround for shifted arrays
            
            else:
                stress = np.append(stress, stressDat[areaIndex,2])
            ind+=1

        # put data in dataframe
        print len(lat), len(lon), len(dep), len(stress)
        tmpDF = pd.DataFrame(np.column_stack((lat, lon, dep, stress)), columns=dfColumns)
        stressDF = stressDF.append(tmpDF)
    stressDF.to_pickle(DFPath)
