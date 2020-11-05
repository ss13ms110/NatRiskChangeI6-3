# script to plot dual histograms on same plot

import numpy as np
from pandas import read_pickle, unique, DataFrame
import matplotlib.pyplot as plt
import funcFileMC as funcFile
import timeit as ti
from astropy.io import ascii

Stime = ti.default_timer()

# paths
combPath = './outputs/CombData_9-4.pkl'
maxEqPath = './outputs/magSR/magSR.out'
McValueFile = './../2_McCalc/outputs/Mc_MAXC_1Yr.txt'
figP = './figs/magSR/hist_log.pdf'
# params
mulFactor = 1e-6    # convert Pa to MPa
Lcut1 = -8
Lcut2 = 0
Ucut = 8
tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
models = ['R (km)', 'MAS$_0$ (MPa)', 'MAS (MPa)', 'OOP (MPa)', 'VM (MPa)', 'MS (MPa)', 'VMS (MPa)']


# main
# read combData
combDataload = read_pickle(combPath)
print funcFile.printLoad("Combined data loaded at", Stime)

sD = ascii.read(maxEqPath)


# apply filters in combData
combData = combDataload[combDataload['mag'] > combDataload['Mc(t)']]
print funcFile.printProcess("Mc filter applied at", Stime)



for tag in tags[1:]:
    if tag in tags[1:4]:
        combData[tag] = combData[tag] * mulFactor
        combData = combData[(combData[tag] >= Lcut1) & (combData[tag] <= Ucut)]
    else:
        combData = combData[(combData[tag] >= Lcut2) & (combData[tag] <= Ucut)]

print funcFile.printProcess("Converted from Pa to Mpa at", Stime)

weights = []
# get weighs
for mID in unique(combData['MainshockID']):
    tmpDf = combData[combData['MainshockID'] == mID]
    dflen = len(tmpDf)
    weights = np.append(weights, np.full(dflen, 1)/float(dflen))

# start plotting
fig = plt.figure(figsize=(15,10))
j = 1
for i, tag in enumerate(tags):
    ax = fig.add_subplot(3, 3, j)
    ax.set_xlabel('%s' %(models[i]))
    ax.set_ylabel('# of occurences')
    if tag in ['homo_MAS', 'GF_MAS', 'GF_OOP']:
        ax.set_xlim(0.0001,1)
    elif tag == 'R':
        ax.set_xlim(0.001,1000)
    else:
        ax.set_xlim(0.0001,1)
    
    lns1 = ax.hist(list(combData[tag]), 1000, weights=weights, density=False, histtype='step', color='black', label='All data')
    ax.set_xscale('log')
    

    ax2 = ax.twinx()
    lns2 = ax2.hist(sD[tag], 100, density=False, histtype='step', color='red', label='Max mag')
    ax2.set_ylabel('# of occurences')
    #legend
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1+h2, l1+l2)

    #title
    ax.set_title('%s' %(models[i]))
    j += 1

plt.subplots_adjust(wspace=0.6, hspace=0.6)

# plt.show()
plt.savefig(figP)