import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import chain
from math import ceil, log10



# path
GRPath = './outputs/MC/GRTesting/mag-Mct/bin_500'
GRfig = './figs/MC/GRTesting/mag-Mct/bin_500'

# prams
Rtol = 2
# Mains
# load ValDF
bDic = pd.read_pickle(GRPath + '/bValDF.pkl')
bDf = pd.DataFrame()
bDf['R'] = list(chain(*bDic['R']))
bDf['R_bVal'] = bDic['R_bVal']

fig = plt.figure(figsize=(15,10))
j = 1
for i in range(10, 131, 20):
    GRfile = GRPath + '/GRDF_' + str(i) + '.pkl'

    # get R_bVal for given R (i)
    bDfNew = bDf[(bDf['R'] > i-Rtol) & (bDf['R'] < i+Rtol)]

    # read df
    GRdf = pd.read_pickle(GRfile)
    # calculate cumulative numbers
    magCum = list(reversed(np.cumsum(list(reversed(GRdf['magHist'])))))

    b = np.mean(bDfNew['R_bVal'])
    a = np.log10(magCum[0])
    midMag = np.array(GRdf['midMag'])[0]
    magHist = np.array(GRdf['magHist'])
    
    mXval = midMag[magHist != 0]
    bYval = 10**(a - b*mXval)
    
    ax = fig.add_subplot(3, 3, j)
    ax.set_yscale('log')
    ax.set_xlabel('Mag')
    ax.set_ylabel('# of events')
    ylim = ceil(log10(max(magCum)))
    ax.set_ylim(1, 10**ylim)
    ax.set_xlim(-0.5, 7)
    ax.scatter(midMag, magHist, c='black', s=10)
    ax.plot(mXval, bYval, c='g', lw=3)
    ax.scatter(midMag, magCum, c='red', s=10)
    ax.set_title("Distance = %d $\pm$ 2 km | b = %4.2f" %(i, b))

    j += 1

plt.subplots_adjust(wspace=0.4, hspace=0.4)
fig.suptitle("GR plots for 100 binsize")
plt.savefig(GRfig + '/GRplot.png')