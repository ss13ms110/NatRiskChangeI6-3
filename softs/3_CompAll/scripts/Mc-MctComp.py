import numpy as np
import pandas as pd

CdfPath = './combDataAll.pkl'
McPath = './../../2_McCalc/outputs/Mc_MAXC_1Yr.txt'
outFile = './combDataNew.pkl'

# load pkl
Cdf = pd.read_pickle(CdfPath)

Mcdat = np.genfromtxt(McPath, dtype='str')

df = pd.DataFrame()
for Mcrow in Mcdat:
    srcmod = Mcrow[0].split('.')[0]
    Mc = float(Mcrow[1])
    
    dftmp = Cdf[Cdf.MainshockID.isin([srcmod])]
    
    if not dftmp.empty:
        indx = dftmp['Mc(t)'] < Mc
        
        dftmp.loc[indx, 'Mc(t)'] = Mc
    
        df = df.append(dftmp)

df.to_pickle(outFile)