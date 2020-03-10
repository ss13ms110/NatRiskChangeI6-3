# Date: 28.02.2020
# This script make pkl file of all events by compiling all hdf files
# input: all hdf files (here: 1964-2016)
# output: isc_eve.pkl
# Header: [flg', 'year', 'month', 'day', 'hour', 'minute', 'second', 'latitude', 'longitude', 'depth', 'magnitude', 'magnitude_type']

import numpy as np
import pandas as pd
import datetime as dt

#FUNCTIONS
def readFile(fname, yrF):
    fid=open(fname, 'r')
    fData = []
    
    for line in fid:
        rev = 0
        isol = str(line[1:4])
        mnF = int(line[9:11])
        dyF = int(line[12:14])
        hrF = int(line[16:18])
        minF = int(line[19:21])
        secF = float(line[22:27])
        latF = float(line[29:36])
        lonF = float(line[36:44])
        depF = float(line[51:56])
        Mw = float(line[65:68])

        if Mw == 0.0:
            mag = float(line[57:60]) #mb
            magt = 'mb'
        else:
            mag = Mw  
            magt = 'Mw'              

        if isol == 'FEQ':
            rev = 1

        if secF == 60.0:
            secF = 59.99
        sec = int(secF)
        msec = int(str(secF).split('.')[1])*10000
  

        evDt = dt.datetime(yrF, mnF, dyF, hrF, minF, sec, msec)
        fData.append([rev, yrF, mnF, dyF, hrF, minF, secF, latF, lonF, depF, mag, magt, evDt])

    return fData


#MAIN
# paths
hdfPath = '../../../raw_data/isc_data/hdf_files'
pklFile = 'isc_eve.pkl'
sYr = 1964
eYr = 2016

yrList = np.arange(sYr, eYr+1)

df = pd.DataFrame()
for yr in yrList:
    fhdfN = hdfPath + '/' + str(yr) + '.hdf'

    evData = readFile(fhdfN, yr)

    dfTmp = pd.DataFrame(evData, columns=['flg', 'year', 'month', 'day', 'hour', 'minute', 'second', 'latitude', 'longitude', 'depth', 'magnitude', 'magnitude_type', 'datetime'])

    df = df.append(dfTmp)

df.to_pickle(pklFile)






