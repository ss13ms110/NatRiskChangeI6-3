import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import binned_statistic

# path
RvS = './outputs/bVal4/RvSdict.pkl'
RvSfn1 = './figs/bVal4/RvSplot/RvSplot_1.png'
RvSfn2 = './figs/bVal4/RvSplot/RvSplot_2.png'


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
    
    Rbin = np.arange(0, 121, 1)
    RbinMid = (Rbin[1:] + Rbin[:-1])/2
    lcR = list(RvS['lcR'+tag])
    lcS = list(RvS['lcS'+tag])
    lc_stat = binned_statistic(lcR, lcS, statistic='mean', bins=Rbin)

    lcSavg = lc_stat.statistic    
    

    ucR = list(RvS['ucR'+tag])
    ucS = list(RvS['ucS'+tag])
    # # hist
    ucRdigi = np.digitize(ucR, Rbin)
    uc_stat = binned_statistic(ucR, ucS, statistic='mean', bins=Rbin)

    ucSavg = uc_stat.statistic   

    ax = fig.add_subplot(3, 2, i+1)

    # ax.set_yscale('log')
    ax.set_xlabel('R')
    ax.set_ylabel(models[i+1])
    # ylim = ceil(log10(max(lcmagCumN+ucmagCumN)))
    # ax.set_ylim(1, 10**ylim)
    ax.set_xlim(0, 120)
    ax.set_ylim(lc[tag], lc[tag]+cutList[tag])

    ax.scatter(RbinMid, lcSavg, c='red', s=2**4, marker='.', label='%3.2f < Red < %3.2f' %(lc[tag], lc[tag]+cutList[tag]))

    ax2 = ax.twinx()
    ax2.set_ylim(uc[tag]-cutList[tag], uc[tag])
    ax2.scatter(RbinMid, ucSavg, c='black', s=2**4, marker='.', label='%3.2f < Black < %3.2f' %(uc[tag]-cutList[tag], uc[tag]))

    #legend
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    legend = ax.legend(h1+h2, l1+l2, loc=1)
    frame = legend.get_frame()
    frame.set_facecolor('white')

plt.subplots_adjust(wspace=0.5, hspace=0.5)
fig.suptitle("R vs Stress plots for end-points GR plots")
# plt.show()
plt.savefig(RvSfn1)


# For R
fig = plt.figure(figsize=(10,15))

for i, tag in enumerate(tags[1:]):
    
    lcRbin = np.arange(lc[tags[0]], lc[tags[0]]+cutList[tags[0]], 0.1)
    lcRbinMid = (lcRbin[1:] + lcRbin[:-1])/2
    lcR = list(RvS['lc1'+tags[0]])
    lcS = list(RvS['lc1'+tag])
    # hist
    lc_stat = binned_statistic(lcR, lcS, statistic='mean', bins=lcRbin)
    lcSavg = lc_stat.statistic 
    
    ucRbin = np.arange(uc[tags[0]]-cutList[tags[0]], uc[tags[0]], 0.1)
    ucRbinMid = (ucRbin[1:] + ucRbin[:-1])/2
    ucR = list(RvS['uc1'+tags[0]])
    ucS = list(RvS['uc1'+tag])
    # hist
    uc_stat = binned_statistic(ucR, ucS, statistic='mean', bins=ucRbin)
    ucSavg = uc_stat.statistic 
    
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2)

    ax1.set_xlabel('R')
    ax1.set_ylabel("S")
    ax2.set_xlabel('R')
    ax2.set_ylabel("S")
    
    ax1.set_xlim(lc[tags[0]], lc[tags[0]]+cutList[tags[0]])
    ax1.set_ylim(-100, 150)
    ax2.set_xlim(uc[tags[0]]-cutList[tags[0]], uc[tags[0]])
    # ax2.set_ylim(-0.05, 0.05)
    if i in [0,1,2]:
        lcSavg, ucSavg = np.array(lcSavg)*1e-6, np.array(ucSavg)*1e-6
    ax1.scatter(lcRbinMid, lcSavg, s=2**6, marker='.', label='%s' %(models[i+1]))
    ax2.scatter(ucRbinMid, ucSavg, s=2**6, marker='.', label='%s' %(models[i+1]))


    ax1.legend()
    ax2.legend()

plt.subplots_adjust(wspace=0.5, hspace=0.5)
fig.suptitle("R vs Stress plots for end-points of R vs bValue plots")
# plt.show()
plt.savefig(RvSfn2)