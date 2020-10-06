import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from itertools import chain



# PATH
outPath = './outputs/bVal'
figPath = './figs/bVal'


# PRAMS
fileN = 'bValDF.pkl'
tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
models = ['r<R (km)', 'MAS$_0$ (MPa)', 'MAS (MPa)', 'OOP (MPa)', 'VM (s>S MPa)', 'MS (s>S MPa)', 'VMS (s>S MPa)']
val = '_bVal'
lbl = 'b-Value'
Lcut1 = -5
Lcut2 = 0
Ucut = 5

# MAIN

# read pickle file

ylim1 = [0.7, 1.1]
df=pd.read_pickle(outPath + '/' + fileN)

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
        ax1.set_ylabel(lbl, fontsize=24)
        ax1.set_ylim(ylim1[0], ylim1[1])
        
        if tag == tags[0]:
            ax1.set_xlim(0, 120)
            ax1.set_xticks(np.arange(0,120,5))
        else:
            # ax1.set_xlim(Lcut1, Ucut)
            ax1.set_xticks(np.arange(Lcut1,Ucut,0.5))

        # ax1.scatter(df[tag], df[tag+val[ii]], marker='.', s=2**4, c='grey')
        ax1.errorbar(df[tag+'Cu'], df[tag+val+'Cu'], yerr=df[tag+val+'ErrCu'], marker='.', ms='10', linestyle="None", c='k', ecolor='grey')

        
    else:
        ax2 = fig2.add_axes([xmin[i%4], ymin[i%4], dx, dy])
        ax2.set_xlabel(models[i], fontsize=24)
        ax2.set_ylabel(lbl, fontsize=24)
        # ax2.set_xlim(Lcut2, Ucut)
        ax2.set_xticks(np.arange(Lcut2,Ucut,0.5))
        ax2.set_ylim(ylim1[0], ylim1[1])

        # ax2.scatter(df[tag], df[tag+val[ii]], marker='.', s=2**4, c='grey')
        ax2.errorbar(df[tag+'Cu'], df[tag+val+'Cu'], yerr=df[tag+val+'ErrCu'], marker='.', ms='10', linestyle="None", c='k', ecolor='grey')

fig1.savefig(figPath + '/' + fileN.split('.')[0] + '_1.pdf')
fig2.savefig(figPath + '/' + fileN.split('.')[0] + '_2.pdf')
