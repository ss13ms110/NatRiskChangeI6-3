# script to plot dual histograms on same plot

import numpy as np
from pandas import read_pickle, unique, DataFrame
import matplotlib.pyplot as plt
import funcFileMC as funcFile
import timeit as ti
from astropy.io import ascii
import warnings
warnings.filterwarnings("ignore")
Stime = ti.default_timer()

# paths
combPath = './outputs/CombData_9-4.pkl'
maxEqPath = './outputs/magSR/magSR.out'
# figP = './figs/bVal4/magSR/hist_log_normed.pdf'
figP = './figs/bVal4/magSR/hist_linear_normed.pdf'

# params
mulFactor = 1e-6    # convert Pa to MPa
Lcut1 = -8
Lcut2 = 0
Ucut = 8
bin = 200
# tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
# models = ['R (km)', 'MAS$_0$ (MPa)', 'MAS (MPa)', 'OOP (MPa)', 'VM (MPa)', 'MS (MPa)', 'VMS (MPa)']
tags = ['R', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
models = ['R (km)', 'MAS (MPa)', 'OOP (MPa)', 'VM (MPa)', 'MS (MPa)', 'VMS (MPa)']



# main
# read combData
combDataload = read_pickle(combPath)
print funcFile.printLoad("Combined data loaded at", Stime)

sD = ascii.read(maxEqPath)


# apply filters in combData
combData = combDataload[combDataload['mag'] > combDataload['Mc(t)']]
print funcFile.printProcess("Mc filter applied at", Stime)



for tag in tags[1:]:
    if tag in tags[1:3]:
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
    ax.set_ylabel('Frequency')
    
    if tag == 'R':
        # ax.set_xlim(1,120)
        ax.set_xlim(0,120)
    elif tag in tags[1:3]:
        # ax.set_xlim(0.001,1)
        ax.set_xlim(-1,1)
    else:
        # ax.set_xlim(0.001,1)
        ax.set_xlim(0,1)
    
    
    ax.hist(list(combData[tag]), bin, weights=weights, density=False, histtype='stepfilled', color='dimgrey', label='All data')
    ax.hist(sD[tag], bin, density=False, histtype='stepfilled', color='lightcoral', label='Max mag')
    # ax.set_xscale('log')

    ax2 = ax.twinx()
    ax2.set_ylabel('Cumulative frequency')
    
    ax2.hist(list(combData[tag]), bin, weights=weights, density=False, cumulative=True, histtype='step', linewidth=2**0.5, color='black')
    ax2.hist(sD[tag], bin, density=False, histtype='step', cumulative=True, linewidth=2**0.5, color='firebrick')
    # ax2.set_xscale('log')
    
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2, fancybox=True)

    j += 1

plt.subplots_adjust(wspace=0.5, hspace=0.4)

# plt.show()
plt.savefig(figP, bbox_inches = 'tight', pad_inches = 0.2)