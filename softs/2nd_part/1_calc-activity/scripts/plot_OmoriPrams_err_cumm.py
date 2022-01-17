import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# FUNCTION
def lin_fit(x, y, w=[]):
    
    if len(w) != 0:
        coef = np.polyfit(x, y, 1, w=1/np.sqrt(w))
    else:
        coef = np.polyfit(x, y, 1)
    yfit = np.polyval(coef, x)
    return yfit



# PATHS
datFile = './outputs/omoriPrams_cumm.pkl'
figPath = './figs/cumm'

# PRAMS
models = ['R', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
xlbl = [r'$r<R$', r'$sgn(S)\times s>|S|$', r'$sgn(S)\times s>|S|$', r'$s>S$', r'$s>S$', r'$s>S$']
titls = ['Distance', 'MAS', 'OOP', 'VM', 'MS', 'VMS']

L_CUT = [0, -3, -0.5, 0, 0, 0]
U_CUT = [120, 3, 6, 2, 6, 6]

# read pickle
dat = pd.read_pickle(datFile)

# initialise figure
fig = plt.figure(figsize=(15,20))
xmin = [0.1, 0.55, 0.1, 0.55, 0.1, 0.55]
ymin = [0.8, 0.8, 0.55, 0.55, 0.3, 0.3]
dx = 0.38
dy = 0.06

for i, tag in enumerate(models):

    # read data
    xAvg = np.array(dat[tag+'tagAvg'])
    yK = np.array(dat[tag+'K'])
    yc = np.array(dat[tag+'c'])
    yp = np.array(dat[tag+'p'])
    yK_err = np.array(dat[tag+'K_err'])
    yc_err = np.array(dat[tag+'c_err'])
    yp_err = np.array(dat[tag+'p_err'])
    
    # declare axis
    axK = fig.add_axes([xmin[i], ymin[i], dx, dy])
    axc = fig.add_axes([xmin[i], ymin[i]+dy, dx, dy])
    axp = fig.add_axes([xmin[i], ymin[i]+2*dy, dx, dy])
    axc.set_xticks([])
    axp.set_xticks([])
    axK.set_ylabel('K$_n$', fontsize=18)
    axc.set_ylabel('c', fontsize=18)
    axp.set_ylabel('p', fontsize=18)
    # axK.set_yticks(np.arange(0, 0.015, 0.005))
    # axK.set_ylim(0, 0.01)
    axc.set_yticks(np.arange(-0.1, 0.7, 0.2))
    axc.set_ylim(0,0.7)
    axp.set_yticks(np.arange(0.3, 1.4, 0.2))
    axp.set_ylim(0.4,1.5)
    axp.set_title('%s' %(titls[i]), fontsize=14, bbox=dict(facecolor='grey', alpha=0.3, edgecolor='none'))
    axK.set_xlim(L_CUT[i], U_CUT[i])
    axp.set_xlim(L_CUT[i], U_CUT[i])
    axc.set_xlim(L_CUT[i], U_CUT[i])
    
    if tag == 'R':
        axK.set_xlabel(xlbl[i], fontsize=18)

        # PLOT
        # axK.scatter(xAvg, yK, marker='.', s=2**5, c='red')
        axK.errorbar(xAvg, yK, yerr=yK_err, marker='.', ms='7', linestyle="None", c='red', ecolor='red')

        # axc.scatter(xAvg, yc, marker='.', s=2**5, c='green')
        axc.errorbar(xAvg, yc, yerr=yc_err, marker='.', ms='7', linestyle="None", c='green', ecolor='green')
        ycfit = lin_fit(xAvg, yc)
        axc.plot(xAvg, ycfit, '--', color='green', zorder=100)
        
        # axp.scatter(xAvg, yp, marker='.', s=2**5, c='blue')
        axp.errorbar(xAvg, yp, yerr=yp_err, marker='.', ms='7', linestyle="None", c='blue', ecolor='blue')
        ypfit = lin_fit(xAvg, yp)
        axp.plot(xAvg, ypfit, '--', color='blue', zorder=100)
        # ax1p.set_title('%s' %(titls[i]), fontsize=20)

    else:
        axK.set_xlabel(xlbl[i], fontsize=14)
        axK.set_xticks(np.arange(L_CUT[i], U_CUT[i], 0.1), minor=True)
        
        # PLOT
        # axK.scatter(xAvg, yK, marker='.', s=2**5, c='red')
        axK.errorbar(xAvg, yK, yerr=yK_err, marker='.', ms='7', linestyle="None", c='red', ecolor='red')
        # axc.scatter(xAvg, yc, marker='.', s=2**5, c='green')
        axc.errorbar(xAvg, yc, yerr=yc_err, marker='.', ms='7', linestyle="None", c='green', ecolor='green')
        # axp.scatter(xAvg, yp, marker='.', s=2**5, c='blue')
        axp.errorbar(xAvg, yp, yerr=yp_err, marker='.', ms='7', linestyle="None", c='blue', ecolor='blue')
        if tag == 'MAS':
            # c-fit
            ycfit_neg = lin_fit(xAvg[xAvg<0], yc[xAvg<0])
            axc.plot(xAvg[xAvg<0], ycfit_neg, '--', color='green', zorder=100)
            ycfit_pos = lin_fit(xAvg[xAvg>0], yc[xAvg>0])
            axc.plot(xAvg[xAvg>0], ycfit_pos, '--', color='green', zorder=100)
            # p-fit
            ypfit_neg = lin_fit(xAvg[xAvg<0], yp[xAvg<0])
            axp.plot(xAvg[xAvg<0], ypfit_neg, '--', color='blue', zorder=100)
            ypfit_pos = lin_fit(xAvg[xAvg>0], yp[xAvg>0])
            axp.plot(xAvg[xAvg>0], ypfit_pos, '--', color='blue', zorder=100)
        else:

            # c-fit
            ycfit = lin_fit(xAvg, yc)
            axc.plot(xAvg, ycfit, '--', color='green', zorder=100)
            # p-fit
            ypfit = lin_fit(xAvg, yp)
            axp.plot(xAvg, ypfit, '--', color='blue', zorder=100)
        

fig.savefig('%s/omori_err_cumm.pdf' %(figPath), bbox_inches = 'tight', pad_inches = 0.2)
