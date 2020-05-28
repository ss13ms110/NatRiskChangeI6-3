import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from itertools import chain



# PATH
outPath = './outputs/MC/lenTest/itr_1000/bin_100'
figPath = './figs/MC/lenTest/itr_1000/bin_100'


# PRAMS
fileN = ['bValDF.pkl', 'Mw-magDF.pkl']
tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
models = ['R (km)', 'MAS$_0$ (MPa)', 'MAS (MPa)', 'OOP (MPa)', 'VM (MPa)', 'MS (MPa)', 'VMS (MPa)']
Lcut1 = -5
Lcut2 = 0
Ucut = 5

# MAIN

# read pickle file
val = ['_bVal', '_Mw-mag']
lbl = ['b-Value', 'M$_{main}-M_w$']
ylim1 = [[0.5, 1.5], [3.0, 5.0]]
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
            ax1a = fig1.add_axes([xmin[i%4], ymin[i%4]+dy, dx, 0.10])
            ax1.set_xlabel(models[i], fontsize=24)
            ax1.set_ylabel(lbl[ii], fontsize=24)
            ax1.set_ylim(ylim1[ii][0], ylim1[ii][1])
            if tag == tags[0]:
                ax1.set_xlim(min(list(chain(*df[tag]))), 120)
                ax1a.set_xlim(min(list(chain(*df[tag]))), 120)
            else:
                ax1.set_xlim(Lcut1, Ucut)
                ax1a.set_xlim(Lcut1, Ucut)

            ax1.errorbar(list(chain(*df[tag])), df[tag+val[ii]], yerr=df[tag+'_err'], marker='.', ms='10', linestyle="None")

            ax1a.set_ylabel('# of points')
            ax1a.tick_params(labelbottom=False)    
            ax1a.set_ylim(0, max(df[tag+'Len'])+50)
            ax1a.plot(list(chain(*df[tag])), df[tag+'Len'], c='grey')    
            
        else:
            ax2 = fig2.add_axes([xmin[i%4], ymin[i%4], dx, dy])
            ax2a = fig2.add_axes([xmin[i%4], ymin[i%4]+dy, dx, 0.10])
            ax2.set_xlabel(models[i], fontsize=24)
            ax2.set_ylabel(lbl[ii], fontsize=24)
            ax2.set_xlim(Lcut2, Ucut)
            ax2a.set_xlim(Lcut2, Ucut)
            ax2.set_ylim(ylim1[ii][0], ylim1[ii][1])
            ax2.errorbar(list(chain(*df[tag])), df[tag+val[ii]], yerr=df[tag+'_err'], marker='.', ms='10', linestyle="None")

            ax2a.set_ylabel('# of points')
            ax2a.tick_params(labelbottom=False)    
            ax2a.set_ylim(0, max(df[tag+'Len'])+50)
            ax2a.plot(list(chain(*df[tag])), df[tag+'Len'], c='grey')    

    fig1.savefig(figPath + '/' + fl.split('.')[0] + '_1.png')
    fig2.savefig(figPath + '/' + fl.split('.')[0] + '_2.png')
