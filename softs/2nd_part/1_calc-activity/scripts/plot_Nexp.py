import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# FUNCTION
def lin_fit(x, y, xlim):
    xval = x[(x>0) & (x<xlim)]
    yval = y[(x>0) & (x<xlim)]
    coef = np.polyfit(np.log(xval), yval, 1)
    yfit = np.polyval(coef, np.log(x[x>0]))
    return yfit


# PATHS
datFile = './outputs/omoriPrams.pkl'
figPath = './figs/omori'

# PRAMS
models = ['R', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
titls = ['Distance', 'MAS', 'OOP', 'VM', 'MS', 'VMS']

L_CUT = [0, -3, -0.5, 0, 0, 0]
U_CUT = [120, 3, 6, 2, 6, 6]
xlims = [10, 7, 6, 7, 4, 6]
ylim1 = [-0.01, 0.15, 0.1]
txt_x = [100, 2.37, 5.4, 1.85, 5.5, 5.4]

# read pickle
dat = pd.read_pickle(datFile)

# initialise figure
fig = plt.figure(figsize=(15, 15))
xmin = [0.137, 0.56, 0.137, 0.56, 0.137, 0.56]
ymin = [0.805, 0.805, 0.525, 0.525, 0.245, 0.245]
dx = 0.14 
dy = 0.07


for i, tag in enumerate(models):

    # read data
    xAvg = np.array(dat[tag+'tagAvg'])
    yNexp = np.array(dat[tag+'Nexp'])

    ax = fig.add_subplot(3,2,i+1)
    ax.set_ylabel('N$_{exp}$', fontsize=18)
    ax.set_xlim(L_CUT[i], U_CUT[i])
    ax.set_ylim(0, 0.15)

    ax2 = fig.add_axes([xmin[i], ymin[i], dx, dy])
    ax2.yaxis.tick_right()
    ax2.yaxis.set_label_position("right")
    ax2.set_ylabel('N$_{exp}$', fontsize=8)
    ax2.tick_params(labelsize=8)
    ax2.set_xscale('log')

    if tag == 'R':
        ax.set_xlabel('R (km)', fontsize=18)
        ax2.set_xlabel('R (km)', fontsize=8)
        ax2.set_xlim(1,120)
        ax2.set_ylim(ylim1[0], ylim1[1])

        # PLOT
        ax.scatter(xAvg, yNexp, marker='.', s=2**5, c='black')
        ax2.scatter(xAvg, yNexp, marker='.', s=2**5, c='grey')
        #fit
        yfit = lin_fit(xAvg, yNexp, xlims[i])
        ax2.plot(xAvg, yfit, '--', color='black', linewidth=2, zorder=100)
    
    elif tag in models[1:3]:
        ax.set_xlabel('Stress (MPa)', fontsize=14)
        ax2.set_xlabel('Stress (MPa)', fontsize=8)
        ax.set_xticks(np.arange(L_CUT[i], U_CUT[i], 0.1), minor=True)
        ax2.set_xlim(0.1,10)
        ax2.set_ylim(ylim1[0], ylim1[2])

        indxP = xAvg>0
        indxN = xAvg<0
        # PLOT
        ax.scatter(xAvg, yNexp, marker='.', s=2**5, c='black')
        #fitP
        ax2.scatter(xAvg[indxP], yNexp[indxP], marker='.', s=2**5, c='grey')
        yfitP = lin_fit(xAvg[indxP], yNexp[indxP], xlims[i])
        ax2.plot(xAvg[indxP], yfitP, '--', color='black', linewidth=2, zorder=100)
        #fitN
        if len(xAvg[indxN]) > 5:
            ax2.scatter(-xAvg[indxN], yNexp[indxN], marker='.', s=2**5, c='red')
            yfitN = lin_fit(-xAvg[indxN], yNexp[indxN], xlims[i])
            ax2.plot(-xAvg[indxN], yfitN, '--', color='brown', linewidth=2, zorder=100)
    else:
        ax.set_xlabel('Stress (MPa)', fontsize=14)
        ax2.set_xlabel('Stress (MPa)', fontsize=8)
        ax.set_xticks(np.arange(L_CUT[i], U_CUT[i], 0.1), minor=True)
        ax2.set_xlim(0.1,10)
        ax2.set_ylim(ylim1[0], ylim1[2])
        
        # PLOT
        ax.scatter(xAvg, yNexp, marker='.', s=2**5, c='black')
        ax2.scatter(xAvg, yNexp, marker='.', s=2**5, c='grey')
        #fit
        yfit = lin_fit(xAvg, yNexp, xlims[i])
        ax2.plot(xAvg, yfit, '--', color='black', linewidth=2, zorder=100)

    ax.text(txt_x[i],0.13, titls[i], fontweight='bold', bbox=dict(facecolor='grey', alpha=0.3, edgecolor='none'))

plt.subplots_adjust(wspace=0.2, hspace=0.3)
fig.savefig('%s/Nexp.pdf' %(figPath), bbox_inches = 'tight', pad_inches = 0.2)
