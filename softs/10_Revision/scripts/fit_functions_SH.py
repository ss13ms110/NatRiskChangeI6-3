import os
import sys
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

def powerlawfunc(x, a, c, e):
  return a * (c+x)**e

def powerlawfunc1(x, a, e):
  return a * (1.0+x)**e

def linfunc(x, c, d):
  return c + d * x

def variancereduction(x, y, yfunc):
    fac = 1.0 - np.var(y - yfunc) / np.var(y)
    return 100.0 * fac

  

cumulative = True

metric = ['R', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
xlabelname = ['R  [km]', 'MAS  [MPa]', 'OOP  [MPa]', 'VM  [MPa]', 'MS  [MPa]', 'VMS  [MPa]']
plotlogscale = [1, 0, 0, 0, 0, 0]
panelnr = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)']
Rmax = 20.0  # [km]
Smin = 0.1   # [MPa]
x1 = [0, Smin, Smin, Smin, Smin, Smin]
x2 = [Rmax, 1e6, 1e6, 1e6, 1e6, 1e6]

# General Plot Properties
# make a bigger global font size and sans-serif style
plt.rc('font', family='sans-serif')
plt.rc('font', size=12)
plt.rc('legend', fontsize=10)
f, ax = plt.subplots(3, 2, figsize=(12,12) )

if cumulative:
    directory = 'data/cummulative/'
    setbounds = [0, 0, 0, 0, 0, 0]
    ylabelname = ['b (r < R)', 'b (s > MAS)','b (s > OOP)', 'b (s > VM)', 'b (s > MS)', 'b (s > VMS)']
    plt.subplots_adjust(hspace=0.2, wspace=0.25)
    b1 = 0.89
    b2 = 1.19
else:
    directory = 'data/non-cumulative/NonCumm-'
    setbounds = [0, 0, 0, 0, 0, 1]
    ylabelname = ['b', '', 'b', '', 'b', '']
    plt.subplots_adjust(hspace=0.2, wspace=0.1)
    b1 = 0.55
    b2 = 1.25

i = -1
for nr in range(3):
  for nc in range(2):
    i += 1
    data = np.loadtxt('%s%s-vs-b.txt' % (directory, metric[i]))
    data = data[(data[:,0]>0), :]
    x = data[:, 0]
    y = data[:, 1]
    dy = data[:, 2]
    ind = ((x>=x1[i]) & (x<=x2[i]))
    #print('\n\t %s: N=%d selected values' % (metric[i], len(x[ind])))
    # Linear correlation coefficient (Pearson):
    
    rcorr, pcorr = pearsonr(x[ind], y[ind])
    # linear fit:
    para, covar = curve_fit(linfunc, x[ind], y[ind], sigma=dy[ind])
    c = para[0]                  # constant c
    d = para[1]                  # slope d
    dc = np.sqrt(covar[0,0])     # standard deviation of pre-factor a
    dd = np.sqrt(covar[1,1])     # standard deviation of exponent e    
    R2 = variancereduction(x[ind], y[ind], linfunc(x[ind], c, d))
    # power-law fits:
    if setbounds[i] == 1:
      bd1 = (0, 0.1, -1)
      bd2 = (100, 100, 1.0)
      para, covar = curve_fit(powerlawfunc, x[ind], y[ind], sigma=dy[ind], bounds=(bd1, bd2))
    else:
      para, covar = curve_fit(powerlawfunc, x[ind], y[ind], sigma=dy[ind])
    a0 = para[0]                  # pre-factor a
    c0 = para[1]                  # delay c
    e0 = para[2]                  # exponent e
    da0 = np.sqrt(covar[0,0])     # standard deviation of pre-factor a
    dc0 = np.sqrt(covar[1,1])     # standard deviation of exponent e
    de0 = np.sqrt(covar[2,2])     # standard deviation of exponent e
    R20 = variancereduction(x[ind], y[ind], powerlawfunc(x[ind], a0, c0, e0))   
    para, covar = curve_fit(powerlawfunc1, x[ind], y[ind], sigma=dy[ind])
    a1 = para[0]                  # pre-factor a
    e1 = para[1]                  # exponent e
    da1 = np.sqrt(covar[0,0])     # standard deviation of pre-factor a
    de1 = np.sqrt(covar[1,1])     # standard deviation of exponent e    
    R21 = variancereduction(x[ind], y[ind], powerlawfunc(x[ind], a1, 1.0, e1))
    
    ax[nr,nc].errorbar(x, y, dy, c='gray', alpha=0.5)
    ax[nr,nc].errorbar(x[ind], y[ind], dy[ind], c='k', alpha=0.5, label=r'observed: r=%.2f (p=%.1e)' % (rcorr, pcorr))
    if not cumulative: 
      ax[nr,nc].plot(x[ind], linfunc(x[ind], c, d), c='g', lw=2, label=r'b=%.2f+%.3f*%s-->$R^2$=%.1f%%' % (c, d, metric[i], R2))
      #ax[nr,nc].plot(x[ind], powerlawfunc1(x[ind], a1, e1), c='b', lw=2, label=r'b=%.2f*(1+%s)^%.2f-->$R^2$=%.1f%%' % (a1, metric[i], e1, R21))
    ax[nr,nc].plot(x[ind], powerlawfunc(x[ind], a0, c0, e0), c='r', lw=3, label=r'$b=%.2f*(%.2f+%s)^{%.2f}$-->$R^2$=%.1f%%' % (a0, c0, metric[i], e0, R20))
    if plotlogscale[i] == 1:
        ax[nr,nc].set_xscale('log')
    else:
      ax[nr,nc].set_xlim(0, 1.01*np.max(x))
    #ax[nr,nc].set_ylim(b1, b2)
    ax[nr,nc].set_xlabel('%s' % (xlabelname[i]))
    ax[nr,nc].set_ylabel('%s' % (ylabelname[i]))
    if metric[i] == 'R':
      ax[nr,nc].legend(fontsize=10, loc=1)
    else:
      ax[nr,nc].legend(fontsize=10, loc=4)
    ax[nr,nc].text(-0.2, 0.99, panelnr[i], fontsize=14, color='k', horizontalalignment='left', transform=ax[nr,nc].transAxes)

if cumulative:
  figname = './figs/fits_cumulativevalues.png'
else:
  figname = './figs/fits_NONcumulativevalues.png'
plt.savefig(figname, dpi=300, bbox_inches = 'tight')
print('\n\t OUTPUT: %s\n' % (figname))



