import os
import sys
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

def linfunc(x, c, d):
  return c + d * x

def variancereduction(x, y, yfunc):
    fac = 1.0 - np.var(y - yfunc) / np.var(y)
    return 100.0 * fac

  

parameter = ['c', 'p']
nparameter = (3, 4)
nparametererr = (6, 7)

metric = ['R', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
xlabelname = ['R  [km]', 'MAS  [MPa]', 'OOP  [MPa]', 'VM  [MPa]', 'MS  [MPa]', 'VMS  [MPa]']
panelnr = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)']
Rmax = 100.0  # [km]
Smin = 0.1    # [MPa]
x1 = [0, Smin, Smin, Smin, Smin, Smin]
x2 = [Rmax, 1e6, 1e6, 1e6, 1e6, 1e6]

print(' ')

xlim1 = (0, 0, 0, 0, 0, 0)
xlim2 = (120, 3, 6, 2, 6, 6)

for npara in range(len(parameter)):

  pa = parameter[npara]
  n1 = nparameter[npara]
  n2 = nparametererr[npara]
  
  # General Plot Properties
  # make a bigger global font size and sans-serif style
  plt.rc('font', family='sans-serif')
  plt.rc('font', size=12)
  plt.rc('legend', fontsize=10)
  f, ax = plt.subplots(3, 2, figsize=(12,12) )

  ylabelname = [pa, '', pa, '', pa, '']
  plt.subplots_adjust(hspace=0.25, wspace=0.17)

  i = -1
  for nr in range(3):
    for nc in range(2):
      i += 1
      datname = 'DATA/OMORI-PARAMETER/parameter-%s.dat' % (metric[i])
      data = np.loadtxt(datname, skiprows=1)
      data = data[(data[:,0]>0), :]
      x = data[:, 0]
      y = data[:, n1]
      dy = data[:, n2]

      # ATTENTION: Replace nan-values by the mean-value (excluding nan):
      ii = np.where(np.isnan(dy))
      dy[ii] = np.nanmean(dy)

      ind = ((x>=x1[i]) & (x<=x2[i]))
      
      # Linear correlation coefficient (Pearson):
      rcorr, pcorr = pearsonr(x[ind], y[ind])

      # linear fit:
      para, covar = curve_fit(linfunc, x[ind], y[ind], sigma=dy[ind])
      c = para[0]                  # constant c
      d = para[1]                  # slope d
      dc = np.sqrt(covar[0,0])     # standard deviation of pre-factor a
      dd = np.sqrt(covar[1,1])     # standard deviation of exponent e    
      R2 = variancereduction(x[ind], y[ind], linfunc(x[ind], c, d))
      ax[nr,nc].scatter(x, y, c='gray', marker='o', s=50, alpha=0.5)
      ax[nr,nc].errorbar(x, y, dy, c='gray', fmt="none", alpha=0.5)
      ax[nr,nc].scatter(x[ind], y[ind], c='k', marker='o', s=50, alpha=0.5, label=r'observed: r=%.2f (p=%.1e)' % (rcorr, pcorr))
      ax[nr,nc].errorbar(x[ind], y[ind], dy[ind], c='k', fmt="none", alpha=0.5)
      ax[nr,nc].plot(x[ind], linfunc(x[ind], c, d), c='g', lw=2, label=r'%s=%.2f+%.3f*%s-->$R^2$=%.1f%%' % (pa, c, d, metric[i], R2))
      #ax[nr,nc].set_xlim(0, 1.01*np.max(x))
      ax[nr,nc].set_xlim(xlim1[i], xlim2[i])
      #ax[nr,nc].set_ylim(ylim1[i], ylim2[i])
      ax[nr,nc].set_xlabel('%s' % (xlabelname[i]))
      ax[nr,nc].set_ylabel('%s' % (ylabelname[i]))
      ax[nr,nc].legend(fontsize=10)
      ax[nr,nc].text(-0.15, 0.99, panelnr[i], fontsize=14, color='k', horizontalalignment='left', transform=ax[nr,nc].transAxes)

  figname = 'fits_%s.png' % (pa)
  plt.savefig(figname, dpi=300, bbox_inches = 'tight')
  print('\t OUTPUT: %s' % (figname))

print(' ')


