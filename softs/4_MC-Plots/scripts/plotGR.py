import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import ceil, log10

# path
GRPath = './outputs/MC/GRTesting/mag-Mct/bin_100'
GRfig = './figs/MC/GRTesting/mag-Mct/bin_100'

# Mains

fig = plt.figure(figsize=(15,10))
j = 1
for i in range(10, 131, 20):
    GRfile = GRPath + '/GRDF_' + str(i) + '.pkl'

    # read df
    GRdf = pd.read_pickle(GRfile)
    # calculate cumulative numbers
    magCum = list(reversed(np.cumsum(list(reversed(GRdf['magHist'])))))

    
    ax = fig.add_subplot(3, 3, j)
    ax.set_yscale('log')
    ax.set_xlabel('Mag')
    ax.set_ylabel('# of events')
    ylim = ceil(log10(max(magCum)))
    ax.set_ylim(1, 10**ylim)
    ax.scatter(GRdf['midMag'], GRdf['magHist'], c='black', s=10)
    ax.scatter(GRdf['midMag'], magCum, c='red', s=10)
    ax.set_title("Distance = %d $\pm$ 2 km" %(i))



    j += 1

plt.subplots_adjust(wspace=0.4, hspace=0.4)
fig.suptitle("GR plots for 100 binsize")
plt.savefig(GRfig + '/GRplot.png')