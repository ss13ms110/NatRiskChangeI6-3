import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
from scipy.stats import pearsonr



# FUNCTION
def lin_fit(x, y, xlim):
    xval = x[(x>0) & (x<xlim)]
    yval = y[(x>0) & (x<xlim)]
    coef = np.polyfit(np.log(xval), np.log(yval), 1)
    yfit = np.exp(np.polyval(coef, np.log(x[x>0])))
    yfit2 = np.polyval(coef, np.log(xval))
    Rsq = r2_score(np.log(yval), yfit2)
    return yfit, coef[1], coef[0], Rsq


# PATHS
datFile = './outputs/omoriPrams_err.pkl'
figPath = './figs/omori'
fitParamFile = './outputs/fit_params_Nexp.txt'

# PRAMS
models = ['R', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
titls = ['Distance', 'MAS', 'OOP', 'VM', 'MS', 'VMS']

L_CUT = [0, 0, 0, 0, 0, 0]
U_CUT = [100, 3, 6, 2, 6, 6]
xlims = [120, 7, 6, 7, 4, 6]
ylim1 = [0.001, 0.15, 0.1]
txt_x = [70, 2.18, 4.22, 1.45, 4.34, 4.34]
panelnr = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)']

# read pickle
dat = pd.read_pickle(datFile)

# initialise figure
plt.rc('font', family='sans-serif')
plt.rc('font', size=26)
plt.rc('legend', fontsize=14)
fig = plt.figure(figsize=(25, 18))
xmin = [0.150, 0.59, 0.150, 0.59, 0.150, 0.59]
ymin = [0.800, 0.800, 0.520, 0.520, 0.235, 0.235]
dx = 0.14 
dy = 0.07


# open file to write fit parameters
f_fit = open(fitParamFile, 'w')
f_fit.write('Metric    c1    c2    Rsquare\n')


for i, tag in enumerate(models):
    # read data
    print(tag)
    xAvg = np.array(dat[tag+'tagAvg'])
    yNexp = np.array(dat[tag+'Nexp'])
    yNobs = np.array(dat[tag+'Nobs'])

    ax = fig.add_subplot(3,2,i+1)
    ax.set_ylabel('D', fontsize=24)
    ax.set_xlim(L_CUT[i], U_CUT[i])
    ax.set_ylim(0, 0.15)

    ax2 = fig.add_axes([xmin[i], ymin[i], dx, dy])
    ax2.yaxis.tick_right()
    ax2.yaxis.set_label_position("right")
    ax2.set_ylabel('D', fontsize=20)
    ax2.tick_params(labelsize=12)
    ax2.set_xscale('log')
    ax2.set_yscale('log')

    if tag == 'R':
        ax.set_xlabel('R (km)', fontsize=24)
        ax.text(-0.18, 0.99, panelnr[i], fontsize=24, color='k', weight='bold', horizontalalignment='left', transform=ax.transAxes)
        ax2.set_xlabel('R (km)', fontsize=22)
        ax2.set_xlim(1,100)
        ax2.set_ylim(ylim1[0], 1)

        # PLOT
        ax.scatter(xAvg, yNobs, marker='.', s=2**7, c='black', label='Observed')
        # ax.scatter(xAvg, yNexp, marker='.', s=2**7, c='black', label='Expected')
        ax2.scatter(xAvg, yNexp, marker='.', s=2**6, c='grey')
        rcorr, pcorr = pearsonr(xAvg, yNexp)
        print('C      ',  rcorr, pcorr)
        #fit
        yfit, c1, c2, Rsq = lin_fit(xAvg, yNexp, xlims[i])
        f_fit.write('%6s    %7.4f    %7.4f    %7.4f\n' %(tag, c1, c2, Rsq))
        ax2.plot(xAvg, yfit, '--', color='black', linewidth=2, zorder=100)
    
    elif tag in models[1:3]:
        ax.set_xlabel('Stress (MPa)', fontsize=24)
        ax.text(-0.18, 0.99, panelnr[i], fontsize=24, color='k', weight='bold', horizontalalignment='left', transform=ax.transAxes)
        ax2.set_xlabel('Stress (MPa)', fontsize=22)
        ax.set_xticks(np.arange(L_CUT[i], U_CUT[i], 0.1), minor=True)
        ax2.set_xlim(0.1,10)
        ax2.set_ylim(ylim1[0], ylim1[2])

        indxP = xAvg>0
        indxN = xAvg<0
        # PLOT
        ax.scatter(xAvg[indxP], yNobs[indxP], marker='.', s=2**7, c='black', label='Observed')
        # ax.scatter(xAvg, yNexp, marker='.', s=2**7, c='black', label='Expected')
        
        #fitP
        ax2.scatter(xAvg[indxP], yNexp[indxP], marker='.', s=2**7, c='grey')
        rcorr, pcorr = pearsonr(xAvg, yNexp)
        print('C      ',  rcorr, pcorr)
        yfitP, c1, c2, Rsq = lin_fit(xAvg[indxP], yNexp[indxP], xlims[i])
        f_fit.write('%6s    %7.4f    %7.4f    %7.4f\n' %(tag, c1, c2, Rsq))
        ax2.plot(xAvg[indxP], yfitP, '--', color='black', linewidth=2, zorder=100)
        #fitN
        if len(xAvg[indxN]) > 5:
            # ax2.scatter(-xAvg[indxN], yNexp[indxN], marker='.', s=2**6, c='red')
            yfitN, c1, c2, Rsq = lin_fit(-xAvg[indxN], yNexp[indxN], xlims[i])
            f_fit.write('%6s    %7.4f    %7.4f    %7.4f\n' %(tag, c1, c2, Rsq))
            # ax2.plot(-xAvg[indxN], yfitN, '--', color='brown', linewidth=2, zorder=100)
    else:
        ax.set_xlabel('Stress (MPa)', fontsize=24)
        ax.text(-0.18, 0.99, panelnr[i], fontsize=24, color='k', weight='bold', horizontalalignment='left', transform=ax.transAxes)
        ax2.set_xlabel('Stress (MPa)', fontsize=22)
        ax.set_xticks(np.arange(L_CUT[i], U_CUT[i], 0.1), minor=True)
        ax2.set_xlim(0.1,10)
        ax2.set_ylim(ylim1[0], ylim1[2])
        
        # PLOT
        ax.scatter(xAvg, yNobs, marker='.', s=2**7, c='black', label='Observed')
        # ax.scatter(xAvg, yNexp, marker='.', s=2**7, c='black', label='Expected')
        rcorr, pcorr = pearsonr(xAvg, yNexp)
        print('C      ',  rcorr, pcorr)
        ax2.scatter(xAvg, yNexp, marker='.', s=2**6, c='grey')
        #fit
        yfit, c1, c2, Rsq = lin_fit(xAvg, yNexp, xlims[i])
        f_fit.write('%6s    %7.4f    %7.4f    %7.4f\n' %(tag, c1, c2, Rsq))
        ax2.plot(xAvg, yfit, '--', color='black', linewidth=2, zorder=100)

    # leg = ax.legend(title=r"$\bf{" + titls[i] + "}$", fontsize=16)
    # plt.setp(leg.get_title(),fontsize='xx-large')

    ax.text(txt_x[i],0.1, '%s' %(titls[i]), fontweight='bold', fontsize = 24, bbox=dict(facecolor='grey', alpha=0.3, edgecolor='none'))
plt.subplots_adjust(wspace=0.3, hspace=0.4)
fig.savefig('%s/Nexp_Nobs_loglog_NEW.pdf' %(figPath), bbox_inches = 'tight', pad_inches = 0.2)
