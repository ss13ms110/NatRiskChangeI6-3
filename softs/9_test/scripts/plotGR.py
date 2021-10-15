import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import chain
from math import ceil, log10

# path
GRP = './outputs/bVal4/GRdict.pkl'
GRfn = './figs/bVal4/GRplot/GRplot_new.pdf'


# tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
tags = ['R', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']

# titls = ['R', 'MAS$_0$', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
titls = ['R', 'MAS', 'OOP', 'VM', 'MS', 'VMS']

# mcL = [2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
# lcL = [0, -6.0, -6.0, -0.5, 0, 0, 0]
# ucL = [120, 6.0, 6.0, 6.0, 3.5, 6.5, 7.0]
mcL = [2, 0.2, 0.2, 0.2, 0.2, 0.2]
lcL = [0, -6.0, -0.5, 0, 0, 0]
ucL = [120, 6.0, 6.0, 3.5, 6.5, 7.0]

xlimM = [4, 3, 5, 5, 5, 5]
textyR = [0.1, 0.1,0.1, 0.1,0.1, 0.1 ]
textyB = [0.01, 0.01,0.01, 0.01,0.01, 0.01 ]
cutList = {tag: mcL[i] for i, tag in enumerate(tags)}
lc = {tag: lcL[i] for i, tag in enumerate(tags)}
uc = {tag: ucL[i] for i, tag in enumerate(tags)}

# Mains
# load ValDF
GRd = pd.read_pickle(GRP)

fig = plt.figure(figsize=(15,10))

j = 1
for tag in tags:
    
    # histograms
    lcmagHist = GRd['lcHist'+tag]
    ucmagHist = GRd['ucHist'+tag]
    
    # mid mags
    lcmidMag = GRd['lcMidMag'+tag]
    ucmidMag = GRd['ucMidMag'+tag]
    
    # calculate cumulative numbers
    lcmagCum = list(reversed(np.cumsum(list(reversed(lcmagHist)))))
    lcmagCum = np.array([float(x) for x in lcmagCum])
    lcmagCumN = lcmagCum/max(lcmagCum)

    ucmagCum = list(reversed(np.cumsum(list(reversed(ucmagHist)))))
    ucmagCum = np.array([float(x) for x in ucmagCum])
    ucmagCumN = ucmagCum/max(ucmagCum)

    # calculate a-value for lc and uc
    lca = np.log10(lcmagCumN[0])
    uca = np.log10(ucmagCumN[0])

    # get b-value saved in Dict
    lcb = GRd['lcbVal'+tag]
    ucb = GRd['ucbVal'+tag]

    # start plotting
    ax = fig.add_subplot(3, 3, j)
    ax.set_yscale('log')
    ax.set_xlabel('Magnitude', fontsize=10)
    ax.set_ylabel('Cumulative frequency')
    ylim = ceil(log10(max(lcmagCumN+ucmagCumN)))
    ax.set_ylim(1, 10**ylim)
    ax.set_ylim(0.000001, 1)
            
    ax.set_xlim(-0.5, xlimM[j-1])
    ax.set_xticks(np.arange(0,xlimM[j-1]+1))

    # for lower cut
    if tag == 'R':
        # for upper cut
        ax.scatter(lcmidMag, lcmagCumN, c='red', s=10, marker='.', label='%d < %s < %d' %(lc[tag], titls[j-1], lc[tag]+cutList[tag]))
        ax.scatter(ucmidMag, ucmagCumN, c='black', s=10, marker='.', label='%d < %s < %d' %(uc[tag]-cutList[tag], titls[j-1], uc[tag]))
    else:
        # for upper cut
        ax.scatter(lcmidMag, lcmagCumN, c='red', s=10, marker='.', label='%3.2f < %s < %3.2f' %(lc[tag], titls[j-1], lc[tag]+cutList[tag]))
        ax.scatter(ucmidMag, ucmagCumN, c='black', s=10, marker='.', label='%3.2f < %s < %3.2f' %(uc[tag]-cutList[tag], titls[j-1], uc[tag]))

    # mark b-value
    ax.text(1.5, textyR[j-1], 'b=%5.3f'%(lcb), color='R', fontsize=8)
    ax.text(0.5, textyB[j-1], 'b=%5.3f'%(ucb), color='black', fontsize=8)
    
    # ax.set_title("%s | b = %5.3f, %5.3f \n %3.2f < red < %3.2f | %3.2f < black < %3.2f" %(titls[j-1], lcb, ucb, lc[tag], lc[tag]+cutList[tag], uc[tag]-cutList[tag], uc[tag]))
    ax.legend(loc='lower left', markerscale=2)
    j += 1


plt.subplots_adjust(wspace=0.3, hspace=0.3)
# fig.suptitle("GR plots for end points")
# plt.show()
plt.savefig(GRfn, bbox_inches = 'tight', pad_inches = 0.2)