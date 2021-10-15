import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# FUNCTION
def lin_fit(x, y, xlim):
    xval = x[(x>0) & (x<xlim)]
    yval = y[(x>0) & (x<xlim)]
    coef = np.polyfit(np.log(xval), yval, 1)
    yfit = np.polyval(coef, np.log(x[x>0]))
    return yfit


# PATH
outPath = './outputs/bVal5'
figPath = './figs/bVal5'


# PRAMS
fileN = 'bValDF_3.pkl'
tags = ['R', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']

titls = ['Distance', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
txt_x = [100, 6.5, 7.3, 3.6, 7.1, 7.4]
xlims = [10, 7, 6, 7, 4, 6]
models = ['r<R (km)', '   s<S (MPa)   |   s>S (MPa)', 's<S (MPa)   |   s>S (MPa)', 's>S (MPa)', 's>S (MPa)', 's>S (MPa)']
models2 = ['r<R (km)', '|s|>S (MPa)', '|s|>S (MPa)', 's>S (MPa)', 's>S (MPa)', 's>S (MPa)']

val = '_bVal'
lbl = 'b'
Lcut1 = -8
Lcut2 = 0
Ucut = 8

# MAIN
# read pickle file
ylim1 = [0.85, 1.30, 1.15]
df=pd.read_pickle(outPath + '/' + fileN)

# initialise figure
fig = plt.figure(figsize=(15,15))
xmin = [0.137, 0.56, 0.137, 0.56, 0.137, 0.56]
ymin = [0.815, 0.815, 0.535, 0.535, 0.257, 0.257]
dx = 0.14 
dy = 0.06

for i,tag in enumerate(tags):
    ax = fig.add_subplot(3,2,i+1)
    ax.set_xlabel(models2[i], fontsize=16)
    ax.set_ylabel(lbl, fontsize=16)
    ax.set_ylim(ylim1[0], ylim1[1])
    # ax.set_title('%s' %(titls[i]), fontsize=20)
    ax2 = fig.add_axes([xmin[i], ymin[i], dx, dy])
    ax2.yaxis.tick_right()
    ax2.yaxis.set_label_position("right")
    ax2.set_xlabel(models2[i], fontsize=8)
    ax2.set_ylabel(lbl, fontsize=8)
    ax2.set_ylim(ylim1[0], ylim1[2])
    ax2.tick_params(labelsize=8)
    ax2.set_xscale('log')
    # ax.set_xscale('log')
    if tag == tags[0]:            
        ax.set_xlim(0, 120)
        ax.errorbar(df[tag+'Cu'], df[tag+val+'Cu'], yerr=df[tag+val+'ErrCu'], marker='.', ms=2**3, linestyle="None", c='k', ecolor='grey')
        
        ax2.set_xlim(1,120)
        ax2.errorbar(df[tag+'Cu'], df[tag+val+'Cu'], yerr=df[tag+val+'ErrCu'], marker='.', ms=2**2, linestyle="None", c='grey', ecolor='grey')
        yfit = lin_fit(df[tag+'Cu'], df[tag+val+'Cu'], xlims[i])
        ax2.plot(df[tag+'Cu'][(df[tag+'Cu']>0)], yfit, '--', color='black')

    elif tag in tags[1:3]:
        if tag == 'GF_OOP':
            ax.set_xticks(np.arange(-1, 9, 1))
            ax.set_xlim(-1,8)
        ax.errorbar(df[tag+'Cu'], df[tag+val+'Cu'], yerr=df[tag+val+'ErrCu'], marker='.', ms=2**3, linestyle="None", c='k', ecolor='grey')

        ax2.set_xlim(0.01,10)
        # -----------------------------------------
        indxP = df[tag+'Cu']>0
        xp = df[tag+'Cu'][indxP]
        yp = df[tag+val+'Cu'][indxP]
        errP = df[tag+val+'ErrCu'][indxP]
        indxN = df[tag+'Cu']<0
        xn = (-1)*df[tag+'Cu'][indxN]
        yn = df[tag+val+'Cu'][indxN]
        errN = df[tag+val+'ErrCu'][indxN]
        ax2.errorbar(xp, yp, yerr=errP, marker='.', ms=2**2, linestyle="None", c='grey', ecolor='grey')
        ax2.errorbar(xn, yn, yerr=errN, marker='.', ms=2**2, linestyle="None", c='red', ecolor='red')
        yfitp = lin_fit(xp, yp, xlims[i])
        ax2.plot(xp[(xp>0)], yfitp, '--', color='black', zorder=100)
        yfitn = lin_fit(xn, yn, xlims[i])
        ax2.plot(xn[(xn>0)], yfitn, '--', color='brown', zorder=100)
        # -----------------------------------------
    else:
        ax.errorbar(df[tag+'Cu'], df[tag+val+'Cu'], yerr=df[tag+val+'ErrCu'], marker='.', ms=2**3, linestyle="None", c='k', ecolor='grey')
        ax2.set_xlim(0.1,10)
        ax2.errorbar(df[tag+'Cu'], df[tag+val+'Cu'], yerr=df[tag+val+'ErrCu'], marker='.', ms=2**2, linestyle="None", c='grey', ecolor='grey')
        yfit = lin_fit(df[tag+'Cu'][1:], df[tag+val+'Cu'][1:], xlims[i])
        ax2.plot(df[tag+'Cu'][1:], yfit, '--', color='black', zorder=100 )

    ax.text(txt_x[i],1.25, titls[i], fontweight='bold', bbox=dict(facecolor='grey', alpha=0.3, edgecolor='none'))
    

plt.subplots_adjust(wspace=0.2, hspace=0.3)
fig.savefig(figPath + '/b-valVsSR.pdf', bbox_inches = 'tight', pad_inches = 0.2)