import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from itertools import chain



# PATH
outPath = './outputs/MC/3egTest/bin_500'
figPath = './figs/MC/3egTest/bin_500'


# PRAMS
fileN = ['bValDF.pkl', 'Mw-magDF.pkl']
tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
models = ['R (km)', 'MAS$_0$ (MPa)', 'MAS (MPa)', 'OOP (MPa)', 'VM (MPa)', 'MS (MPa)', 'VMS (MPa)']
val = ['_bVal_', '_Mw-mag_']
lbl = ['b-Value', 'M$_{main}-M_w$']
cl=['r', 'g', 'b']
Lcut1 = -5
Lcut2 = 0
Ucut = 5

# MAIN

# read pickle file

ylim1 = [[0, 2], [3.0, 6.0]]
# lbl = ['b-Value', 'M$_{max}$']
for ii,fl in enumerate(fileN):
    df=pd.read_pickle(outPath + '/' + fl)

    # initialise figure
    fig1 = plt.figure(figsize=(20,10))
    fig2 = plt.figure(figsize=(20,10))
    xmin = [0.1, 0.55, 0.1, 0.55]
    ymin = [0.55, 0.55, 0.08, 0.08]
    dx = 0.38
    dy = 0.30
    for i,tag in enumerate(tags):
        if tag in tags[:4]:
            ax1 = fig1.add_axes([xmin[i%4], ymin[i%4], dx, dy])
            ax1.set_xlabel(models[i], fontsize=24)
            ax1.set_ylabel(lbl[ii], fontsize=24)
            ax1.set_ylim(ylim1[ii][0], ylim1[ii][1])
            if tag == tags[0]:
                ax1.set_xlim(min([min(df[tag+'_'+str(n)]) for n in range(3)]), 120)
            else:
                ax1.set_xlim(Lcut1, Ucut)

            for n in range(3):
                ax1.scatter(df[tag+'_'+str(n)], df[tag+val[ii]+str(n)], s=2**4, c=cl[n], marker='.')
 
            
        else:
            ax2 = fig2.add_axes([xmin[i%4], ymin[i%4], dx, dy])
            ax2.set_xlabel(models[i], fontsize=24)
            ax2.set_ylabel(lbl[ii], fontsize=24)
            ax2.set_xlim(Lcut2, Ucut)
            ax2.set_ylim(ylim1[ii][0], ylim1[ii][1])
            for n in range(3):
                ax2.scatter(df[tag+'_'+str(n)], df[tag+val[ii]+str(n)], s=2**4, c=cl[n], marker='.')


    fig1.savefig(figPath + '/' + fl.split('.')[0] + '_1.png')
    fig2.savefig(figPath + '/' + fl.split('.')[0] + '_2.png')
