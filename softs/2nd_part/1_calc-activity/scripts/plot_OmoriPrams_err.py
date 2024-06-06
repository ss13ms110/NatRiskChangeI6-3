import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from sklearn.metrics import r2_score


# FUNCTION
def lin_fit(x, y, w=[]):
    print(w)
    w[np.isnan(w)] = 0.0001
    if len(w) != 0:
        
        coef = np.polyfit(x, y, 1, w=1/w)
    else:
        coef = np.polyfit(x, y, 1)
    yfit = np.polyval(coef, x)
    Rsq = r2_score(y, yfit)

    return yfit, coef[1], coef[0], Rsq

def linfunc(x, c, d):
  return c + d * x

def variancereduction(x, y, yfunc):
    fac = 1.0 - np.var(y - yfunc) / np.var(y)
    return 100.0 * fac


def linear_fit(x, y, dy):
    dy[np.isnan(dy)] = np.nanmean(dy)
    rcorr, pcorr = pearsonr(x, y)
    # linear fit:
    para, covar = curve_fit(linfunc, x, y, sigma=dy)
    c = para[0]                  # constant c
    d = para[1]                  # slope d
    dc = np.sqrt(covar[0,0])     # standard deviation of pre-factor a
    dd = np.sqrt(covar[1,1])     # standard deviation of exponent e    
    R2 = variancereduction(x, y, linfunc(x, c, d))

    return rcorr, pcorr, d, c, R2, linfunc(x,c,d)

# PATHS
datFile = './outputs/less-than-50/omoriPrams_err.pkl'
figPath = './figs/less-than-50'
fitParamFile = './outputs/less-than-50/fit_param.txt'


# PRAMS
models = ['R', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
titls = ['Distance', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
labl = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)']
L_CUT = [0, 0.1, 0.1, 0.1, 0.1, 0.1]
U_CUT = [100, 1e6, 1e6, 1e6, 1e6, 1e6]

xlim1 = (0, 0, 0, 0, 0, 0)
xlim2 = (100, 3, 6, 2, 6, 6)


# read pickle
dat = pd.read_pickle(datFile)

# initialise figure
plt.rc('font', family='sans-serif')
plt.rc('font', size=20)
plt.rc('legend', fontsize=16)
fig = plt.figure(figsize=(18,25))
xmin = [0.1, 0.60, 0.1, 0.60, 0.1, 0.60]
ymin = [0.8, 0.8, 0.55, 0.55, 0.3, 0.3]
dx = 0.38
dy = 0.10

# open file to write fit parameters
f_fit = open(fitParamFile, 'w')
f_fit.write('Metric,    param,    c1,    c2,    Rsquare\n')

for i, tag in enumerate(models):
    print(tag, '--------------')
    # read data
    xAvg = np.array(dat[tag+'tagAvg'])
    # yK = np.array(dat[tag+'K'])
    yc = np.array(dat[tag+'c'])
    yp = np.array(dat[tag+'p'])
    # yK_err = np.array(dat[tag+'K_err'])
    yc_err = np.array(dat[tag+'c_err'])
    yp_err = np.array(dat[tag+'p_err'])
    
    # declare axis
    # axK = fig.add_axes([xmin[i], ymin[i], dx, dy])
    axc = fig.add_axes([xmin[i], ymin[i]+dy, dx, dy])
    axp = fig.add_axes([xmin[i], ymin[i]+2*dy, dx, dy])
    # axc.set_xticks()
    # axp.set_xticks()
    axp.tick_params(labelbottom=False, width=3, length=8, labelsize=18)  
    axc.tick_params(width=3, length=8, labelsize=18) 
    # axK.set_ylabel('K$_n$', fontsize=18)
    axc.set_ylabel('c', fontsize=28)
    axp.set_ylabel('p', fontsize=28)
    # axK.set_yticks(np.arange(0, 0.015, 0.005))
    # axK.set_ylim(0, 0.01)
    axc.set_yticks(np.arange(-0.2, 1.7, 0.3))
    # axc.set_ylim(-0.2,1.2)
    # axp.set_yticks(np.arange(0.3, 1.4, 0.2))
    axp.set_ylim(0.2,1.8)
    axp.text(0.5,0.8,'%s' %(titls[i]), fontsize=20, weight='bold', bbox=dict(facecolor='grey', alpha=0.3, edgecolor='none'),transform=axp.transAxes)
    # axK.set_xlim(xlim1[i], xlim2[i])
    axp.set_xlim(xlim1[i], xlim2[i])
    axc.set_xlim(xlim1[i], xlim2[i])
    
    ind = ((xAvg>=L_CUT[i]) & (xAvg<=U_CUT[i]))
    xAvg = xAvg[ind]
    # yK, yK_err = yK[ind], yK_err[ind]
    yc, yc_err = yc[ind], yc_err[ind]
    yp, yp_err = yp[ind], yp_err[ind]
    
    if tag == 'R':
        axc.set_xlabel('R (km)', fontsize=30)

        # PLOT
        # axK.scatter(xAvg, yK, marker='.', s=2**5, c='red')
        # axK.errorbar(xAvg, yK, yerr=yK_err, marker='.', ms='7', linestyle="None", c='red', ecolor='red')

        # axc.scatter(xAvg, yc, marker='.', s=2**5, c='green')
        axc.errorbar(xAvg, yc, yerr=yc_err, marker='.', ms='9', linestyle="None", c='green', alpha=0.5)
        # ycfit, c1, c2, Rsq = lin_fit(xAvg, yc, yc_err)
        rcorr, pcorr, c2, c1, Rsq, ycfit = linear_fit(xAvg, yc, yc_err)
        print('C      ',  rcorr, pcorr)
        # y = mx +c
        # y = c2*x + c1
        # y = d*x + c
        f_fit.write('%6s,    %3s,    %7.4f,    %7.4f,    %7.4f\n' %(tag, 'c', c1, c2, Rsq))
        axc.plot(xAvg, ycfit, '--', color='green', zorder=100)

        # axp.scatter(xAvg, yp, marker='.', s=2**5, c='blue')
        axp.errorbar(xAvg, yp, yerr=yp_err, marker='.', ms='7', linestyle="None", c='blue', alpha=0.5)
        # ypfit, c1, c2, Rsq = lin_fit(xAvg, yp, yp_err)
        rcorr, pcorr, c2, c1, Rsq, ypfit = linear_fit(xAvg, yp, yp_err)
        print('P  ',  rcorr, pcorr)
        f_fit.write('%6s,    %3s,    %7.4f,    %7.4f,    %7.4f\n' %(tag, 'p', c1, c2, Rsq))
        axp.plot(xAvg, ypfit, '--', color='blue', zorder=100)
        # ax1p.set_title('%s' %(titls[i]), fontsize=20)

    else:
        axc.set_xlabel('Stress (MPa)', fontsize=26)
        # axK.set_xticks(np.arange(L_CUT[i], U_CUT[i], 0.1), minor=True)
        
        # PLOT
        # axK.scatter(xAvg, yK, marker='.', s=2**5, c='red')
        # axK.errorbar(xAvg, yK, yerr=yK_err, marker='.', ms='7', linestyle="None", c='red', ecolor='red')
        # axc.scatter(xAvg, yc, marker='.', s=2**5, c='green')
        axc.errorbar(xAvg, yc, yerr=yc_err, marker='.', ms='7', linestyle="None", c='green', alpha=0.5)
        # axp.scatter(xAvg, yp, marker='.', s=2**5, c='blue')
        axp.errorbar(xAvg, yp, yerr=yp_err, marker='.', ms='7', linestyle="None", c='blue', alpha=0.5)
        if tag == 'MAS':
            # c-fit
            # ycfit_neg, c1, c2, Rsq = lin_fit(xAvg[xAvg<0], yc[xAvg<0], yc_err[xAvg<0])
            # rcorr, pcorr, c2, c2, Rsq, ycfit_neg = linear_fit(xAvg[xAvg<0], yc[xAvg<0], yc_err[xAvg<0])
            # f_fit.write('%6s,    %3s,    %7.4f,    %7.4f,    %7.4f\n' %(tag, 'c', c1, c2, Rsq))
            # axc.plot(xAvg[xAvg<0], ycfit_neg, '--', color='green', zorder=100)
            # ycfit_pos, c1, c2, Rsq = lin_fit(xAvg[xAvg>0], yc[xAvg>0], yc_err[xAvg>0])
            print('111111')
            rcorr, pcorr, c2, c1, Rsq, ycfit_pos = linear_fit(xAvg, yc, yc_err)
            f_fit.write('%6s,    %3s,    %7.4f,    %7.4f,    %7.4f\n' %(tag, 'c', c1, c2, Rsq))
            print('C      ',  rcorr, pcorr)
            axc.plot(xAvg, ycfit_pos, '--', color='green', zorder=100)
            # p-fit
            # ypfit_neg, c1, c2, Rsq = lin_fit(xAvg[xAvg<0], yp[xAvg<0], yp_err[xAvg<0])
            # rcorr, pcorr, c1, c2, Rsq, ypfit_neg = linear_fit(xAvg[xAvg<0], yp[xAvg<0], yp_err[xAvg<0])
            # f_fit.write('%6s,    %3s,    %7.4f,    %7.4f,    %7.4f\n' %(tag, 'p', c1, c2, Rsq))
            # axp.plot(xAvg[xAvg<0], ypfit_neg, '--', color='blue', zorder=100)
            # ypfit_pos, c1, c2, Rsq = lin_fit(xAvg[xAvg>0], yp[xAvg>0], yp_err[xAvg>0])
            print('222222')
            rcorr, pcorr, c2, c1, Rsq, ypfit_pos = linear_fit(xAvg, yp, yp_err)
            
            print('P  ',  rcorr, pcorr)
            f_fit.write('%6s,    %3s,    %7.4f,    %7.4f,    %7.4f\n' %(tag, 'p', c1, c2, Rsq))
            axp.plot(xAvg, ypfit_pos, '--', color='blue', zorder=100)
        else:

            # c-fit
            # ycfit, c1, c2, Rsq = lin_fit(xAvg, yc, yc_err)
            rcorr, pcorr, c2, c1, Rsq, ycfit = linear_fit(xAvg, yc, yc_err)
            print('C      ',  rcorr, pcorr)
            f_fit.write('%6s,    %3s,    %7.4f,    %7.4f,    %7.4f\n' %(tag, 'c', c1, c2, Rsq))
            axc.plot(xAvg, ycfit, '--', color='green', zorder=100)
            # p-fit
            # ypfit, c1, c2, Rsq = lin_fit(xAvg, yp, yp_err)
            rcorr, pcorr, c2, c1, Rsq, ypfit = linear_fit(xAvg, yp, yp_err)
            print('P  ',  rcorr, pcorr)
            f_fit.write('%6s,    %3s,    %7.4f,    %7.4f,    %7.4f\n' %(tag, 'p', c1, c2, Rsq))
            axp.plot(xAvg, ypfit, '--', color='blue', zorder=100)
        
    axp.text(-0.15, 0.99, labl[i], fontsize=24, weight='bold', color='k', horizontalalignment='left', transform=axp.transAxes)

fig.savefig('%s/omori_new.pdf' %(figPath), bbox_inches = 'tight', pad_inches = 0.2)
