import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from itertools import chain


# PATH
outPath = './outputs/bVal5'
figPath = './figs/bVal5'

labels = ['=max-slip', '>=mean-slip', '>=80% max-slip', '>=50% max-slip', '>=20% max-slip', '>= 0']
cols = ['black', 'blue', 'red', 'green', 'orange', 'deepskyblue']
# PRAMS
fileN = 'bValDF'

# MAIN
# initialise figure
fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(1,1,1)
ax.set_xlabel('r<R (km)', fontsize=20)
ax.set_ylabel('b', fontsize=20)
ax.tick_params(axis='x', labelsize=18)
ax.tick_params(axis='y', labelsize=18)
ax.set_ylim(0.88, 1.1)
ax.set_xlim(0, 120)
ax2 = fig.add_axes([0.58, 0.6, 0.3, 0.25])
ax2.set_xlabel('r<R (km)', fontsize=16)
ax2.set_ylabel('b', fontsize=16)
ax2.set_ylim(0.88, 1.1)
ax2.set_xlim(0, 15)
for i in range(1,7):
    # read pickle file
    df=pd.read_pickle(outPath + '/' + fileN + '_' + str(i) + '.pkl')
    
    # plt.errorbar(df['RCu'], df['R_bValCu'], yerr=df['R_bValErrCu'], marker='.', ms=2**2, linestyle="None", label=labels[i-1])
    ax.scatter(df['RCu'], df['R_bValCu'], marker='.', s=2**6, label=labels[i-1], color=cols[i-1])
    ax2.plot(df['RCu'], df['R_bValCu'], lw=2, color=cols[i-1])
    # plt.plot(df['RCu'], df['R_bValCu'], lw=2, label=labels[i-1])

eb=ax.errorbar(7.5, 0.885, xerr=7.5, marker='.', ms=0, linestyle="None", capsize=5, color='red')
eb[-1][0].set_linestyle('--')   # errorbar line style
ax.text(5,0.888, 'Inset')
leg = ax.legend(loc='upper left', bbox_to_anchor=(0.03, 0.98), markerscale=1.5, fontsize=14)
leg.set_title('R calculated from slip patches', prop={'size':14, 'weight': 800})

plt.savefig(figPath + '/b-valVsR.pdf', bbox_inches = 'tight', pad_inches = 0.2)