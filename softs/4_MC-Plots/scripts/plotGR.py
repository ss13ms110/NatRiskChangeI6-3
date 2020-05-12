import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import ceil, log10

# path
GRPath = './outputs/MC/ALl/bin_200'
GRfig = './figs/MC/All/bin_200'

# Mains

fig = plt.figure(figsize=(15,10))
j = 1
for i in range(10, 131, 20):
    GRfile = GRPath + '/GRDF_' + str(i) + '.pkl'

    # read df
    GRdf = pd.read_pickle(GRfile)
    ax = fig.add_subplot(3, 3, j)
    ax.set_yscale('log')
    ax.set_xlabel('Mag')
    ax.set_ylabel('# of events')
    ylim = ceil(log10(max(GRdf['magHist'])))
    ax.set_ylim(1, 10**ylim)
    ax.scatter(GRdf['midMag'], GRdf['magHist'])
    ax.set_title("Distance = %d $\pm$ 2 km" %(i))



    j += 1

plt.subplots_adjust(wspace=0.5, hspace=0.4)
fig.suptitle("GR plots for 100 binsize")
plt.savefig(GRfig + '/GRplot.png')