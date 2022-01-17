import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# FUNCTION
def lin_fit(x, y, xlim):
    xval = x[(x>0) & (x<xlim)]
    yval = y[(x>0) & (x<xlim)]
    coef = np.polyfit(np.log(xval), np.log(yval), 1)
    yfit = np.exp(np.polyval(coef, np.log(x[x>0])))
    return yfit, coef[0]


# PATHS
datFile = './outputs/omoriPrams.pkl'
figPath = './figs/omori'

# PRAMS
models = ['R', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
titls = ['Distance', 'MAS', 'OOP', 'VM', 'MS', 'VMS']

L_CUT = [0, -3, -0.5, 0, 0, 0]
U_CUT = [120, 3, 6, 2, 6, 6]
xlims = [10, 7, 6, 7, 4, 6]
ylim1 = [0.001, 0.15, 0.1]
txt_x = [87, 1.35, 4.22, 1.45, 4.34, 4.34]

# read pickle
dat = pd.read_pickle(datFile)

# initialise figure
fig = plt.figure(figsize=(20, 15))
xmin = [0.150, 0.57, 0.150, 0.57, 0.150, 0.57]
ymin = [0.805, 0.805, 0.525, 0.525, 0.245, 0.245]
dx = 0.14 
dy = 0.07


for i, tag in enumerate(models):
    # read data
    xAvg = np.array(dat[tag+'tagAvg'])
    yNexp = np.array(dat[tag+'Nexp'])
    yNobs = np.array(dat[tag+'Nobs'])

    ax = fig.add_subplot(3,2,i+1)
    ax.set_ylabel('N', fontsize=20)
    ax.set_xlim(L_CUT[i], U_CUT[i])
    ax.set_ylim(0, 0.15)

    ax2 = fig.add_axes([xmin[i], ymin[i], dx, dy])
    ax2.yaxis.tick_right()
    ax2.yaxis.set_label_position("right")
    ax2.set_ylabel('N$_{exp}$', fontsize=12)
    ax2.tick_params(labelsize=12)
    ax2.set_xscale('log')
    ax2.set_yscale('log')

    if tag == 'R':
        ax.set_xlabel('R (km)', fontsize=18)
        ax2.set_xlabel('R (km)', fontsize=12)
        ax2.set_xlim(1,120)
        ax2.set_ylim(ylim1[0], ylim1[1])

        # PLOT
        ax.scatter(xAvg, yNobs, marker='*', s=2**7, c='red', label='Observed')
        ax.scatter(xAvg, yNexp, marker='.', s=2**7, c='black', label='Expected')
        ax2.scatter(xAvg, yNexp, marker='.', s=2**6, c='grey')
        #fit
        yfit, expnt = lin_fit(xAvg, yNexp, xlims[i])
        ax2.plot(xAvg, yfit, '--', color='black', linewidth=2, zorder=100)
    
    elif tag in models[1:3]:
        ax.set_xlabel('Stress (MPa)', fontsize=18)
        ax2.set_xlabel('Stress (MPa)', fontsize=12)
        ax.set_xticks(np.arange(L_CUT[i], U_CUT[i], 0.1), minor=True)
        ax2.set_xlim(0.1,10)
        ax2.set_ylim(ylim1[0], ylim1[2])

        indxP = xAvg>0
        indxN = xAvg<0
        # PLOT
        ax.scatter(xAvg, yNobs, marker='*', s=2**7, c='red', label='Observed')
        ax.scatter(xAvg, yNexp, marker='.', s=2**7, c='black', label='Expected')
        
        #fitP
        ax2.scatter(xAvg[indxP], yNexp[indxP], marker='.', s=2**7, c='grey')
        yfitP, expnt = lin_fit(xAvg[indxP], yNexp[indxP], xlims[i])
        ax2.plot(xAvg[indxP], yfitP, '--', color='black', linewidth=2, zorder=100)
        #fitN
        if len(xAvg[indxN]) > 5:
            ax2.scatter(-xAvg[indxN], yNexp[indxN], marker='.', s=2**6, c='red')
            yfitN, expnt = lin_fit(-xAvg[indxN], yNexp[indxN], xlims[i])
            ax2.plot(-xAvg[indxN], yfitN, '--', color='brown', linewidth=2, zorder=100)
    else:
        ax.set_xlabel('Stress (MPa)', fontsize=18)
        ax2.set_xlabel('Stress (MPa)', fontsize=12)
        ax.set_xticks(np.arange(L_CUT[i], U_CUT[i], 0.1), minor=True)
        ax2.set_xlim(0.1,10)
        ax2.set_ylim(ylim1[0], ylim1[2])
        
        # PLOT
        ax.scatter(xAvg, yNobs, marker='*', s=2**7, c='red', label='Observed')
        ax.scatter(xAvg, yNexp, marker='.', s=2**7, c='black', label='Expected')
        ax2.scatter(xAvg, yNexp, marker='.', s=2**6, c='grey')
        #fit
        yfit, expnt = lin_fit(xAvg, yNexp, xlims[i])
        ax2.plot(xAvg, yfit, '--', color='black', linewidth=2, zorder=100)

    leg = ax.legend(title=r"$\bf{" + titls[i] + "}$", fontsize=16)
    plt.setp(leg.get_title(),fontsize='xx-large')

    ax.text(txt_x[i],0.08, '$\kappa$ = %4.2f' %(expnt), fontweight='bold', fontsize = 18, bbox=dict(facecolor='grey', alpha=0.3, edgecolor='none'))
plt.subplots_adjust(wspace=0.2, hspace=0.3)
fig.savefig('%s/Nexp_Nobs_loglog.pdf' %(figPath), bbox_inches = 'tight', pad_inches = 0.2)
