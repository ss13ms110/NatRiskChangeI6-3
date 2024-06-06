import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import r2_score


# FUNCTION
def lin_fit(x, y, xlim):
    xval = x[(x>0) & (x<xlim)]
    yval = y[(x>0) & (x<xlim)]
    coef = np.polyfit(np.log(xval), yval, 1)
    
    yfit = np.polyval(coef, np.log(x[x>0]))
    yfit2 = np.polyval(coef, np.log(xval))
    Rsq = r2_score(yval, yfit2)
    return yfit, coef[1], coef[0], Rsq


# PATH
outPath = './outputs/bValRevision2-less-than-50'
figPath = './figs/bValRevision2-less-than-50'
fitParamFile = './outputs/bValRevision2-less-than-50/fit_param.txt'


# PRAMS
fileN = 'bValDF_final.pkl'
tags = ['R', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']

titls = ['Distance', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
txt_x = [100, 6.5, 7.1, 3.6, 7.1, 7.4]
xlims = [120, 7, 6, 7, 4, 6]
modelsY = [r'b$(r<R)$', r'b$(sgn(S)\times s>|S|$)', r'b$(sgn(S)\times s>|S|$)', r'b$(s>S)$', r'b$(s>S)$', r'b$(s>S)$']
modelsX = ['R (km)', 'S (MPa)', 'S (MPa)', 'S (MPa)', 'S (MPa)', 'S (MPa)']

val = '_bVal'
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
ymin = [0.795, 0.795, 0.517, 0.517, 0.238, 0.238]
dx = 0.16 
dy = 0.08

# open file to write fit parameters
f_fit = open(fitParamFile, 'w')
f_fit.write('Metric    c1    c2    Rsquare\n')

for i,tag in enumerate(tags):
    ax = fig.add_subplot(3,2,i+1)
    ax.set_xlabel(modelsX[i], fontsize=14)
    ax.set_ylabel(modelsY[i], fontsize=16)
    ax.set_ylim(ylim1[0], ylim1[1])
    # ax.set_title('%s' %(titls[i]), fontsize=20)
    ax2 = fig.add_axes([xmin[i], ymin[i], dx, dy])
    ax2.yaxis.tick_right()
    ax2.yaxis.set_label_position("right")
    ax2.set_xlabel(modelsX[i], fontsize=10)
    ax2.set_ylabel(modelsY[i], fontsize=10)
    ax2.set_ylim(ylim1[0], ylim1[2])
    ax2.tick_params(labelsize=8)
    ax2.set_xscale('log')
    # ax.set_xscale('log')
    if tag == tags[0]:            
        ax.set_xlim(0, 120)
        ax.errorbar(df[tag+'Cu'], df[tag+val+'Cu'], yerr=df[tag+val+'ErrCu'], marker='.', ms=2**3, linestyle="None", c='k', ecolor='grey')
        
        ax2.set_xlim(1,120)
        ax2.errorbar(df[tag+'Cu'], df[tag+val+'Cu'], yerr=df[tag+val+'ErrCu'], marker='.', ms=2**2, linestyle="None", c='grey', ecolor='grey')
        yfit, c1, c2, Rsq = lin_fit(df[tag+'Cu'], df[tag+val+'Cu'], xlims[i])
        f_fit.write('%6s    %7.4f    %7.4f    %7.4f\n' %(tag, c1, c2, Rsq))
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
        yfitp, c1, c2, Rsq = lin_fit(xp, yp, xlims[i])
        f_fit.write('%6s    %7.4f    %7.4f    %7.4f\n' %(tag, c1, c2, Rsq))
        ax2.plot(xp[(xp>0)], yfitp, '--', color='black', zorder=100)
        yfitn, c1, c2, Rsq = lin_fit(xn, yn, xlims[i])
        f_fit.write('%6s    %7.4f    %7.4f    %7.4f\n' %(tag, c1, c2, Rsq))
        ax2.plot(xn[(xn>0)], yfitn, '--', color='brown', zorder=100)
        # -----------------------------------------
    else:
        ax.errorbar(df[tag+'Cu'], df[tag+val+'Cu'], yerr=df[tag+val+'ErrCu'], marker='.', ms=2**3, linestyle="None", c='k', ecolor='grey')        
        ax2.set_xlim(0.1,10)
        ax2.errorbar(df[tag+'Cu'], df[tag+val+'Cu'], yerr=df[tag+val+'ErrCu'], marker='.', ms=2**2, linestyle="None", c='grey', ecolor='grey')
        yfit, c1, c2, Rsq = lin_fit(df[tag+'Cu'][1:], df[tag+val+'Cu'][1:], xlims[i])
        f_fit.write('%6s    %7.4f    %7.4f    %7.4f\n' %(tag, c1, c2, Rsq))
        ax2.plot(df[tag+'Cu'][1:], yfit, '--', color='black', zorder=100 )

    ax.text(txt_x[i],1.25, titls[i], fontweight='bold', bbox=dict(facecolor='grey', alpha=0.3, edgecolor='none'))
    
    

plt.subplots_adjust(wspace=0.2, hspace=0.3)
fig.savefig(figPath + '/b-valVsSR_3.pdf', bbox_inches = 'tight', pad_inches = 0.2)