import numpy as np
import datetime as dt
import pandas as pd
from astropy.io import ascii
from functools import partial

# FUNCTION
def getDays(dat, MSdt):
    diff = (dat - MSdt)
    days = diff.days + diff.seconds/86400.
    return days

# paths
srcCataFile = './../../1_preProcess/outputs/newSrcmodCata.txt'
combFile = './../../9_test/outputs/CombData_9-3.pkl'
newCombFile = './outputs/new1CombData.pkl'

# load data from srcCata.txt
srcDat = ascii.read(srcCataFile)
trimmedIds = [x['srcmodId'][:17] for x in srcDat]
srcDat['srcmodId'][:] = trimmedIds

# load combData
combData = pd.read_pickle(combFile)

omoriT = []
for line in srcDat:
    yr = line['Yr']
    mn = line['Mn']
    dy = line['Dy']
    hr = line['Hr']
    mi = line['Mi']
    sec = line['Sec']
    srcID = line['srcmodId']
    print "Working on %s" %(srcID)

    MSdt = dt.datetime(yr, mn, dy, hr, mi, int(sec))
    MScomb = combData[combData['MainshockID'] == srcID]
    
    MSdays = map(partial(getDays, MSdt=MSdt), list(MScomb['time']))
    
    omoriT = np.append(omoriT, MSdays)

combData['omoriT'] = np.round(omoriT, 3)

combData.to_pickle(newCombFile)