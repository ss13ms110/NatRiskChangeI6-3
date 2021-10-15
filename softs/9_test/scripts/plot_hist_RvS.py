import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# path
RvS = './outputs/bVal4/RvSdict.pkl'
RvSfn1 = './figs/bVal4/RvSplot/hist_RvSplot.pdf'


# tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
# models = ['R (Km)', 'MAS$_0$ (MPa)', 'MAS (MPa)', 'OOP (MPa)', 'VM (MPa)', 'MS (MPa)', 'VMS (MPa)']
tags = ['R', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
models = ['R (Km)', 'MAS (MPa)', 'OOP (MPa)', 'VM (MPa)', 'MS (MPa)', 'VMS (MPa)']
titls = ['MAS', 'OOP', 'VM', 'MS', 'VMS']

# mcL = [2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
# lcL = [0, -6.0, -6.0, -0.5, 0, 0, 0]
# ucL = [120, 6.0, 6.0, 6.0, 3.5, 6.5, 7.0]
mcL = [2, 0.2, 0.2, 0.2, 0.2, 0.2]
lcL = [0, -6.0, -0.5, 0, 0, 0]
ucL = [120, 6.0, 6.0, 3.5, 6.5, 7.0]

bin = 120
cutList = {tag: mcL[i] for i, tag in enumerate(tags)}
lc = {tag: lcL[i] for i, tag in enumerate(tags)}
uc = {tag: ucL[i] for i, tag in enumerate(tags)}


RvS = pd.read_pickle(RvS)


fig = plt.figure(figsize=(15,8))

for i, tag in enumerate(tags[1:]):
    
    lcR = list(RvS['lcR'+tag])
    ucR = list(RvS['ucR'+tag])

    ax = fig.add_subplot(2, 3, i+1)

    ax.set_xlabel('R (km)')
    ax.set_ylabel('Frequency')
    ax.set_xlim(0, 120)
    ax.hist(lcR, bin, histtype='stepfilled', color='lightcoral', log=True, label='%3.2f < %s < %3.2f' %(lc[tag], titls[i], lc[tag]+cutList[tag]))
    ax.hist(ucR, bin, histtype='stepfilled', color='dimgrey', log=True, label='%3.2f < %s < %3.2f' %(uc[tag]-cutList[tag], titls[i], uc[tag]))

    ax2 = ax.twinx()
    ax2.set_ylabel('Cumulative frequency')
    ax2.hist(lcR, bin, histtype='step', color='firebrick', cumulative=True, log=True, linewidth=2**0.5, label='%3.2f < %s < %3.2f' %(lc[tag], titls[i], lc[tag]+cutList[tag]))
    ax2.hist(ucR, bin, histtype='step', color='black', cumulative=True, log=True, linewidth=2**0.5, label='%3.2f < %s < %3.2f' %(uc[tag]-cutList[tag], titls[i], uc[tag]))


    #legend
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2), ncol=1, fancybox=True)
    
    

plt.subplots_adjust(wspace=0.45, hspace=0.45)
# plt.show()
plt.savefig(RvSfn1, bbox_inches = 'tight', pad_inches = 0.2)