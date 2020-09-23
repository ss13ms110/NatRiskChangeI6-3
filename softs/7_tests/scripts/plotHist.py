# script to plot dual histograms on same plot

import numpy as np
from pandas import read_pickle
import matplotlib.pyplot as plt
import funcFile
import timeit as ti
from astropy.io import ascii

Stime = ti.default_timer()

# paths
combPath = './../3_CompAll/outputs/combData_7_1.pkl'
maxEqPath = './outputs/magSR/magSR.out'
McValueFile = './../2_McCalc/outputs/Mc_MAXC_1Yr.txt'
figP = './figs/magSR/hist_linear.pdf'
# params
mulFactor = 1e-6    # convert Pa to MPa
Lcut1 = -1
Lcut2 = 0
Ucut = 1
tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
models = ['R (km)', 'MAS$_0$ (MPa)', 'MAS (MPa)', 'OOP (MPa)', 'VM (MPa)', 'MS (MPa)', 'VMS (MPa)']


# main
# read combData
combDataload = read_pickle(combPath)
print funcFile.printLoad("Combined data loaded at", Stime)

sD = ascii.read(maxEqPath)


# apply filters in combData
combData = funcFile.filterMc(combDataload, McValueFile)
print funcFile.printProcess("Mc filter applied at", Stime)

for tag in tags[1:]:
    if tag in tags[1:4]:
        combData[tag] = combData[tag] * mulFactor
        combData = combData[(combData[tag] >= Lcut1) & (combData[tag] <= Ucut)]
    else:
        combData = combData[(combData[tag] >= Lcut2) & (combData[tag] <= Ucut)]

print funcFile.printProcess("Converted from Pa to Mpa at", Stime)

# start plotting
fig = plt.figure(figsize=(15,10))
j = 1
for i, tag in enumerate(tags):
    ax = fig.add_subplot(3, 3, j)
    if tag in ['homo_MAS', 'GF_MAS', 'GF_OOP']:
        ax.set_xlim(-0.5,0.5)
    elif tag == 'R':
        ax.set_xlim(0,150)
    else:
        ax.set_xlim(0,0.5)

    lns1 = ax.hist(combData[tag], 1000, histtype='step', color='black', label='All data')
    # ax.set_xscale('log')
    

    ax2 = ax.twinx()
    lns2 = ax2.hist(sD[tag], 100, histtype='step', color='red', label='Max mag')
    
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