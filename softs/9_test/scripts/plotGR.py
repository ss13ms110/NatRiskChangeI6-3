import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import chain
from math import ceil, log10

# path
GRP = './outputs/bVal4/GRdict.pkl'
GRfn = './figs/bVal4/GRplot/GRplot_new.png'


tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
mcL = [2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
lcL = [0, -6.0, -6.0, -0.5, 0, 0, 0]
ucL = [120, 6.0, 6.0, 6.0, 3.5, 6.5, 7.0]

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

    # x-axis points for GR fit
    lcmXval = lcmidMag[0][lcmagHist != 0]
    ucmXval = ucmidMag[0][ucmagHist != 0]

    # y-axis points for GR fit
    lcbYval = 10**(lca - lcb*lcmXval)
    ucbYval = 10**(uca - ucb*ucmXval)

    # start plotting
    ax = fig.add_subplot(3, 3, j)
    ax.set_yscale('log')
    ax.set_xlabel('Mag')
    ax.set_ylabel('# of events')
    ylim = ceil(log10(max(lcmagCumN+ucmagCumN)))
    # ax.set_ylim(1, 10**ylim)
    ax.set_ylim(0.000001, 1)
    ax.set_xlim(-0.5, 7)

    # for lower cut
    # ax.scatter(lcmidMag, lcmagHist, c='red', s=10, marker='^')
    # ax.plot(lcmXval, lcbYval, '--', c='red', lw=1)
    ax.scatter(lcmidMag, lcmagCumN, c='red', s=10, marker='.')

    # for upper cut
    # ax.scatter(ucmidMag, ucmagHist, c='black', s=10, marker='^')
    # ax.plot(ucmXval, ucbYval, '--', c='black', lw=1)
    ax.scatter(ucmidMag, ucmagCumN, c='black', s=10, marker='.')

    # if tag in ['homo_MAS', 'GF_MAS', 'GF_OOP']:
    #     ax.set_title("%s | b = %5.3f, %5.3f \n red < %3.2f | black > %3.2f" %(tag, lcb, ucb, cutList[tag], cutList[tag]))
    
    # elif tag == 'R':
    #     ax.set_title("%s | b = %5.3f, %5.3f \n red < %3.2f | black < %3.2f" %(tag, lcb, ucb, cutList[tag], uc[tag]))

    # else:
    #     ax.set_title("%s | b = %5.3f, %5.3f \n red > %3.2f | black > %3.2f" %(tag, lcb, ucb, lc[tag], cutList[tag]))
    
    ax.set_title("%s | b = %5.3f, %5.3f \n %3.2f < red < %3.2f | %3.2f < black < %3.2f" %(tag, lcb, ucb, lc[tag], lc[tag]+cutList[tag], uc[tag]-cutList[tag], uc[tag]))

    j += 1


plt.subplots_adjust(wspace=0.2, hspace=0.6)
fig.suptitle("GR plots before and after kink")
# plt.show()
plt.savefig(GRfn)