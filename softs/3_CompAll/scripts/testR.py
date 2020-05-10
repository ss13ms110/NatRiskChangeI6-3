import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import ascii
import random
from astropy.table import Table

dfpath = './outputs/combDataAll.pkl'
srcCataFile = './../1_preProcess/outputs/srcmodCata.txt'
mcVal = './../2_McCalc/outputs/Mc_MAXC_1Yr.txt'


df=pd.read_pickle(dfpath)

# filter MC
combData = pd.DataFrame()
fid = open(mcVal, 'r')

for line in fid:
    srcName = line.split()[0]
    Mc = float(line.split()[1])
    Mct = float(line.split()[2])

    if Mc < Mct:
        Mc = Mct

    combDataTmp = df[df.MainshockID.isin([srcName])]
    
    combDataTmp = combDataTmp[combDataTmp['mag'] >= Mc]
    combData = combData.append(combDataTmp)

# load data from srcCata.txt
srcDat = ascii.read(srcCataFile)

trimmedIds = [x['srcmodId'][:17] for x in srcDat]

srcDat['srcmodId'][:] = trimmedIds

srcIDall = list(srcDat['srcmodId'])
    
srcIDuniq = sorted(set([i[:11] for i in srcIDall]))

# loop for every unique event
OnceModels = []
for srcName in srcIDuniq:
    # filter all slip models for this particular event
    eventRows = [list(x) for x in srcDat if x['srcmodId'][:11] == srcName]
    
    # randomly choose on model of all slip models
    oneSlp = random.choice(eventRows)

    # append to the list
    OnceModels.append(oneSlp)

# convert lists into a table
srcMCdat = Table(rows=OnceModels, names=srcDat.colnames)

combMCdat = combData[combData.MainshockID.isin(list(srcMCdat['srcmodId']))]




binn = int(combMCdat.shape[0]/100)
plt.figure()
dfTmp = combMCdat[combMCdat['R']>125]
plt.hist(dfTmp['R'], bins=binn)
plt.show()