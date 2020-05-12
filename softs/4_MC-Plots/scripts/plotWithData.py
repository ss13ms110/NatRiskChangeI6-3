import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from itertools import chain



# PATH
outPath = './outputs/MC/All/bin_200'
figPath = './figs/MC/All/bin_200'
RSPath = './outputs/RVsStress/All/bin_200/RVsStressDF.pkl'

# PRAMS
fileN = ['bValDF.pkl', 'Mw-magDF.pkl']
tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
models = ['R (km)', 'MAS$_0$ (MPa)', 'MAS (MPa)', 'OOP (MPa)', 'VM (MPa)', 'MS (MPa)', 'VMS (MPa)']
Lcut1 = -5
Lcut2 = 0
Ucut = 5
binLen = 500
# MAIN

# read pickle file
RSdf = pd.read_pickle(RSPath)
val = ['_bVal', '_Mw-mag']
lbl = ['b-Value', 'M$_{main}-M_w$']
# lbl = ['b-Value', 'M$_{max}$']
for ii,fl in enumerate(fileN):
    df=pd.read_pickle(outPath + '/' + fl)

    # initialise figure
    fig1 = plt.figure(figsize=(20,10))
    fig2 = plt.figure(figsize=(20,10))
    xmin = [0.1, 0.55, 0.1, 0.55]
    ymin = [0.55, 0.55, 0.08, 0.08]
    dx = 0.40
    dy = 0.40
    for i,tag in enumerate(tags):
        if tag in tags[:4]:
            ax1 = fig1.add_axes([xmin[i%4], ymin[i%4], dx, dy])
            ax1.set_xlabel(models[i], fontsize=24)
            ax1.set_ylabel(lbl[ii], fontsize=24)
            
            ax1.errorbar(list(chain(*df[tag])), df[tag+val[ii]], yerr=df[tag+'_err'], marker='.', ms='10', linestyle="None")
            
            if tag == tags[0]:
                ax1.set_xlim(min(list(chain(*df[tag]))), max(list(chain(*df[tag]))))
                # ax1.set_xscale('log')
            else:
                ax1.set_xlim(Lcut1, Ucut)
                ax1a = fig1.add_axes([xmin[i%4]+0.26, ymin[i%4]+0.25, dx/3, dy/3])
                ax1a.scatter(RSdf[tag+'_R'], RSdf[tag], c='black', s=2)
                ax1a.set_xlabel(models[0], fontweight='bold')
                ax1a.set_ylabel(models[i], fontweight='bold')
        else:
            ax2 = fig2.add_axes([xmin[i%4], ymin[i%4], dx, dy])
            ax2a = fig2.add_axes([xmin[i%4]+0.26, ymin[i%4]+0.25, dx/3, dy/3])
            ax2.set_xlabel(models[i], fontsize=24)
            ax2.set_ylabel(lbl[ii], fontsize=24)
            ax2.set_xlim(Lcut2, Ucut)
            ax2.errorbar(list(chain(*df[tag])), df[tag+val[ii]], yerr=df[tag+'_err'], marker='.', ms='10', linestyle="None")
            
            ax2a.scatter(RSdf[tag+'_R'], RSdf[tag], c='black', s=2)
            ax2a.set_xlabel(models[0], fontweight='bold')
            ax2a.set_ylabel(models[i], fontweight='bold')


    fig1.savefig(figPath + '/' + fl.split('.')[0] + '_1.png')
    fig2.savefig(figPath + '/' + fl.split('.')[0] + '_2.png')

# GR plot
# GRfile = outPath + '/GRDF.pkl'

# GRdf = pd.read_pickle(GRfile)
# print GRdf
# plt.figure()
# plt.scatter(GRdf['midMag'], GRdf['magHist'])
# plt.yscale('log')
# plt.show()