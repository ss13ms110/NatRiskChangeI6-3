import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from itertools import chain



# PATH
outPath = './outputs/bVal4'
figPath = './figs/bVal4'


# PRAMS
fileN = 'bValDF.pkl'
tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
titls = ['Distance', 'MAS$_0$', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
models = ['r<R (km)', '   s<S (MPa)   |   s>S (MPa)', '   s<S (MPa)   |   s>S (MPa)', 's<S (MPa)   |   s>S (MPa)', 's>S (MPa)', 's>S (MPa)', 's>S (MPa)']

val = '_bVal'
lbl = 'b'
Lcut1 = -8
Lcut2 = 0
Ucut = 8

# MAIN

# read pickle file

ylim1 = [0.85, 1.15]
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
            ax1.set_xticks(np.arange(Lcut1,Ucut,1))

        # ax1.scatter(df[tag], df[tag+val[ii]], marker='.', s=2**4, c='grey')
        ax1.errorbar(df[tag+'Cu'], df[tag+val+'Cu'], yerr=df[tag+val+'ErrCu'], marker='.', ms='10', linestyle="None", c='k', ecolor='grey')
        ax1.set_title('%s' %(titls[i]), fontsize=24)

        
    else:
        ax2 = fig2.add_axes([xmin[i%4], ymin[i%4], dx, dy])
        ax2.set_xlabel(models[i], fontsize=24)
        ax2.set_ylabel(lbl, fontsize=24)
        # ax2.set_xlim(Lcut2, Ucut)
        ax2.set_xticks(np.arange(Lcut2,Ucut,0.5))
        ax2.set_ylim(ylim1[0], ylim1[1])

        # ax2.scatter(df[tag], df[tag+val[ii]], marker='.', s=2**4, c='grey')
        ax2.errorbar(df[tag+'Cu'], df[tag+val+'Cu'], yerr=df[tag+val+'ErrCu'], marker='.', ms='10', linestyle="None", c='k', ecolor='grey')
        ax2.set_title('%s' %(titls[i]), fontsize=24)

# ------------ magAvg -------------------------------------
i = i+1
ax2 = fig2.add_axes([xmin[i%4], ymin[i%4], dx, dy])
ax2.set_xlabel(models[0], fontsize=24)
ax2.set_xlim(0, 20)
ax2.set_xticks(np.arange(0,120,5))
ax2.set_ylabel('$\\frac{\sum{(M_i - M_c(t)_i)}}{N}$', fontsize=24)

# ax2.set_ylim(0.475, 0.550)
ax2.scatter(df['RCu'], df['R_magAvgCu'], c='black', s=2**6, marker='.')
# ---------------------------------------------------------

fig1.savefig(figPath + '/' + fileN.split('.')[0] + '_1.png')
fig2.savefig(figPath + '/' + fileN.split('.')[0] + '_2.png')
