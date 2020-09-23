import numpy as np
import matplotlib.pyplot as plt
from astropy.io import ascii


# PATH
outPath = './outputs/magSR/magSR.out'
figPath = './figs/magSR'


# PRAMS
tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
models = ['R (km)', 'MAS$_0$ (MPa)', 'MAS (MPa)', 'OOP (MPa)', 'VM (MPa)', 'MS (MPa)', 'VMS (MPa)']
Lcut1 = -1
Lcut2 = 0
Ucut = 1

# MAIN

# read ascii file
sD = ascii.read(outPath)


ylim = [[Lcut1, Ucut], [Lcut2, Ucut]]


# initialise figure
fig1 = plt.figure(figsize=(20,10))
xmin = [0.1, 0.40, 0.70, 0.1, 0.40, 0.70]
ymin = [0.55, 0.55, 0.55, 0.08, 0.08, 0.08]
dx = 0.25
dy = 0.30
for i,tag in enumerate(tags[1:]):
    ax1 = fig1.add_axes([xmin[i], ymin[i], dx, dy])
    ax1.set_xlabel('mag', fontsize=20)
    ax1.set_ylabel(models[i+1], fontsize=20)

    if tag in tags[:4]:
        ax1.set_ylim(ylim[0][0], ylim[0][1])
    else:
        ax1.set_ylim(ylim[1][0], ylim[1][1])
    ps = sD['R']
    sc = ax1.scatter(sD['mag'], sD[tag], marker='.', s=ps, c='grey')
    # print sc.legend_elements()
    # ax1.legend(*sc.legend_elements("sizes", num=4))
    

fig1.savefig(figPath + '/magSR.png')
