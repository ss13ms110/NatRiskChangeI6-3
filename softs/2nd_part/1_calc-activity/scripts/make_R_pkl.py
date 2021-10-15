import numpy as np
import pandas as pd
from astropy.io import ascii
import os
import pklFunc as funcFile

# Paths
stressPath = './../../../raw_data/stress_values/GF_VM'
outPath = './outputs/stressDF'
srcCataFile = './../../1_preProcess/outputs/newSrcmodCata.txt'
srcmodPath = './../../../raw_data/srcmod/srcmod_fsp_2019Mar'


# prams
slipTol = 20

dfColumns = ['lat', 'lon', 'dep', 'R']
# load data from srcCata.txt
srcDat = ascii.read(srcCataFile)
trimmedIds = [x['srcmodId'][:17] for x in srcDat]
srcDat['srcmodId'][:] = trimmedIds

stressDF = pd.DataFrame([], columns=dfColumns)
DFPath = '%s/stressDF_R.pkl' %(outPath)

for src in srcDat:
    srcID = src['srcmodId']
    print "SRC file: %s" %(srcID)

    # check for srcmod data
    srcDir = '%s/%s' %(stressPath, srcID)
    if not os.path.isdir(srcDir):
        continue
    
    slpFile = srcmodPath + '/' + srcID + '.fsp'

    lat = []
    lon = []
    dep = []
    catalog = dict()
    for d in np.arange(2.5,50,5):
        filePath = '%s/%s_%s.txt' %(srcDir, srcID, str(d))
        
        # load file
        latlonDat = np.loadtxt(filePath, usecols=(0,1))

        if d == 2.5:
            lat1 = latlonDat[:,0]
            lon1 = latlonDat[:,1]
        lat = np.append(lat, lat1)
        lon = np.append(lon, lon1)
        dep = np.append(dep, np.full(len(lat1), d))

    catalog['latitude'] = list(lat)
    catalog['longitude'] = list(lon)
    catalog['depth'] = list(dep)

    slpFile = srcmodPath + '/' + srcID + '.fsp'
    R = funcFile.CalcR(slpFile, catalog, slipTol)

    # put data in dataframe
    tmpDF = pd.DataFrame(np.column_stack((lat, lon, dep, R)), columns=dfColumns)
    stressDF = stressDF.append(tmpDF)
stressDF.to_pickle(DFPath)
