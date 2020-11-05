import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# path
RvS = './outputs/bVal4/RvSdict.pkl'
RvSfn1 = './figs/bVal4/RvSplot/hist_RvSplot_1.png'


tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
models = ['R (Km)', 'MAS$_0$ (MPa)', 'MAS (MPa)', 'OOP (MPa)', 'VM (MPa)', 'MS (MPa)', 'VMS (MPa)']
mcL = [2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
lcL = [0, -6.0, -6.0, -0.5, 0, 0, 0]
ucL = [120, 6.0, 6.0, 6.0, 3.5, 6.5, 7.0]
cutList = {tag: mcL[i] for i, tag in enumerate(tags)}
lc = {tag: lcL[i] for i, tag in enumerate(tags)}
uc = {tag: ucL[i] for i, tag in enumerate(tags)}


RvS = pd.read_pickle(RvS)


fig = plt.figure(figsize=(10,15))

for i, tag in enumerate(tags[1:]):
    
    
    lcR = list(RvS['lcR'+tag])
    
    ucR = list(RvS['ucR'+tag])

    ax = fig.add_subplot(3, 2, i+1)

    # ax.set_yscale('log')
    ax.set_xlabel('R (km)')
    ax.set_ylabel('#')
    # ylim = ceil(log10(max(lcmagCumN+ucmagCumN)))
    # ax.set_ylim(1, 10**ylim)
    # ax.set_ylim(0,0.125)
    ax.set_xlim(0, 120)

    ax.hist(lcR, 120, histtype='step', color='red', label='%3.2f < Red < %3.2f' %(lc[tag], lc[tag]+cutList[tag]))

    ax2 = ax.twinx()
    # ax2.set_ylim(0,0.125)
    ax2.hist(ucR, 120, histtype='step', color='black', label='%3.2f < Black < %3.2f' %(uc[tag]-cutList[tag], uc[tag]))


    #legend
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    legend = ax.legend(h1+h2, l1+l2, loc=1)
    frame = legend.get_frame()
    frame.set_facecolor('white')
    #title
    ax.set_title('%s' %(models[i+1]))
plt.subplots_adjust(wspace=0.5, hspace=0.5)
fig.suptitle("R vs Stress histogram for end-points GR plots")
# plt.show()
plt.savefig(RvSfn1)