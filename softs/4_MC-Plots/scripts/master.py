# Date: 02-04-2020
# This script use Montecarlo sumilation to 
# pick on slip model for each earthquake 
# and make various plots
# Inputs: combData.pkl, srcCatalog 
# Outputs: various plots

import numpy as np
import pandas as pd
import funcFile
from astropy.io import ascii
import matplotlib.pyplot as plt
import timeit as ti
import warnings
warnings.filterwarnings("ignore")

Stime = ti.default_timer()


#PATHS
combFile = './../3_CompAll/outputs/combData.pkl'
srcCataFile = './../1_preProcess/outputs/srcmodCata.txt'
McValueFile = './../2_McCalc/outputs/Mc_MAXC_1Yr.txt'
outPath = './outputs'
figPath = './figs'

#variables
itr = 10
binsize = 100
mulFactor = 1e-6    # convert Pa to MPa
a = 1  # scale
b = 0   # shift
Lcut1 = -5
Lcut2 = 0
Ucut = 5
binLen = 500
tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
models = ['R (km)', 'MAS$_0$ (MPa)', 'MAS (MPa)', 'OOP (MPa)', 'VM (MPa)', 'MS (MPa)', 'VMS (MPa)']

#--------------------------------------
#                 MAIN
#--------------------------------------

# load combData
combDataload = pd.read_pickle(combFile)
print funcFile.printLoad("Combined data loaded at", Stime)

# filter aftershocks above the Mc values [STEP 1]
combData = funcFile.filterMc(combDataload, McValueFile)
print funcFile.printProcess("Mc filter applied at", Stime)

# convert Pa to Mpa for homo_MAS, GF_MAS and GF_OOP
for tag in tags[1:]:
    if tag in tags[1:4]:
        combData[tag] = combData[tag] * mulFactor
        combData = combData[(combData[tag] >= Lcut1) & (combData[tag] <= Ucut)]
    else:
        combData = combData[(combData[tag] >= Lcut2) & (combData[tag] <= Ucut)]

print funcFile.printProcess("Converted from Pa to Mpa at", Stime)

# # filter (sigmoid filter) and scale stress values
# combData = funcFile.filterStress(combData, a, b, tags[1:])
# print funcFile.printProcess("Sigmoid filtered and scaled in", Stime)

# define dictionary for bins
binsDict = dict()
for tag in tags:
    if tag == tags[0]:
        binsDict[tag] = np.linspace(min(combData['R']), max(combData['R']), binLen)
    elif tag in tags[1:4]:
        binsDict[tag] = np.linspace(Lcut1, Ucut, binLen)
    else:
        binsDict[tag] = np.linspace(Lcut2, Ucut, binLen)


# load data from srcCata.txt
srcDat = ascii.read(srcCataFile)
print funcFile.printLoad("SRCMOD catalog loaded in", Stime)

trimmedIds = [x['srcmodId'][:17] for x in srcDat]

srcDat['srcmodId'][:] = trimmedIds

# generate empty dictionaly to hold b-values
bValDict = dict.fromkeys(tags)
MmaxValDict = dict.fromkeys(tags)

for tag in tags:
    bValDict[tag+'n'] = np.full(binLen-1, itr)
    MmaxValDict[tag+'n'] = np.full(binLen-1, itr)

# run montecarlo loop
for i in range(itr):
    print funcFile.printRun("Running iteration", i, Stime)
    # pass this data to a filter function to get on montecarlo realization
    srcMCdat = funcFile.MCreal(srcDat)
    
    # [STEP 2]
    combMCdat = combData[combData.MainshockID.isin(list(srcMCdat['srcmodId']))]

    # [STEP 3]
    for tag in tags:
        
        # sort data in ascending order
        sortedDat = combMCdat.sort_values(by=[tag], kind='quicksort')
        
        # calculate bValue and Mmax
        bVal, MmaxVal, avgTagVal = funcFile.calc_b(sortedDat, binsize, tag)
        
        # digitize values in bins
        binTagVal = np.digitize(avgTagVal, binsDict[tag])
        avgbVal = [bVal[binTagVal == j].mean() for j in range(1, len(binsDict[tag]))]
        avgMmax = [MmaxVal[binTagVal == j].mean() for j in range(1, len(binsDict[tag]))]

        avgbVal = np.array(avgbVal)
        avgMmax = np.array(avgMmax)

        # find index of NaN places and subtract 1 from N
        bNaNindx = np.where(np.isnan(avgbVal))
        mNaNindx = np.where(np.isnan(avgMmax))

        bValDict[tag+'n'][bNaNindx] -= 1
        MmaxValDict[tag+'n'][mNaNindx] -= 1

        # replace NaN by zero
        avgbVal = np.nan_to_num(avgbVal)
        avgMmax = np.nan_to_num(avgMmax)

        # sum values and add in dictionary
        if i == 0:
            bValDict[tag] = avgbVal
            MmaxValDict[tag] = avgMmax 

        else:
            bValDict[tag] = bValDict[tag] + avgbVal
            MmaxValDict[tag] = MmaxValDict[tag] + avgMmax

newbinsDict = dict()
for tag in tags:
    bValDict[tag] = bValDict[tag] / bValDict[tag+'n']
    MmaxValDict[tag] = MmaxValDict[tag] / MmaxValDict[tag+'n']

    # get midpoint of bins
    newbinsDict[tag] = [(a+b)/2.0 for a, b in zip(binsDict[tag][:len(binsDict[tag])-1], binsDict[tag][1:])]


# -------saving the data points-------
# create a comined dict
bValSave = dict()
MmaxSave = dict()
for tag in tags:
    bValSave[tag] = newbinsDict[tag]
    bValSave[tag+'-bVal'] = bValDict[tag]

    MmaxSave[tag] = newbinsDict[tag]
    MmaxSave[tag+'Mmax'] = MmaxValDict[tag]



bValDF = pd.DataFrame.from_dict(bValSave)
MmaxDF = pd.DataFrame.from_dict(MmaxSave)
#------------------------------
#         Plotting
#------------------------------
lbl = ['b-Value', 'M$_{max}$']
for ii,qnt in enumerate(['bVal', 'Mmax']):

    # initialise figure
    fig1 = plt.figure(figsize=(20,10))
    fig2 = plt.figure(figsize=(20,10))
    for i,tag in enumerate(tags):
        if tag in tags[:4]:
            ax1 = fig1.add_subplot(2, 2, i+1)
            ax1.set_xlabel(models[i], fontsize=24)
            ax1.set_ylabel(lbl[ii], fontsize=24)
            if qnt == 'bVal':
                ax1.scatter(newbinsDict[tag], bValDict[tag], s=4)
            else:
                ax1.scatter(newbinsDict[tag], MmaxValDict[tag], s=4)
            
            if tag == tags[0]:
                ax1.set_xlim(min(combData['R']), max(combData['R']))
            else:
                ax1.set_xlim(Lcut1, Ucut)
        else:
            ax2 = fig2.add_subplot(2, 2, i-3)
            ax2.set_xlabel(models[i], fontsize=24)
            ax2.set_ylabel(lbl[ii], fontsize=24)
            ax2.set_xlim(Lcut2, Ucut)
            if qnt == 'bVal':
                ax2.scatter(newbinsDict[tag], bValDict[tag], s=4)
            else:
                ax2.scatter(newbinsDict[tag], MmaxValDict[tag], s=4)

    # ax1.set_ylim(0,1.5)
    # ax2.set_ylim(0,1.5)

    fig1.savefig(figPath + '/' + qnt + '_1.png')
    fig2.savefig(figPath + '/' + qnt + '_2.png')


# NOTES
# Error bars
# bootstraping