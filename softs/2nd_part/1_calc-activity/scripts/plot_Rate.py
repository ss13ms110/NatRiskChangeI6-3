import numpy as np
from pandas import read_pickle
import matplotlib.pyplot as plt
from funcFile import omoriRate

omoriFile = './outputs/omoriPrams.pkl'
figFile = './figs/omori/Rate_example/omori_fit_eg.pdf'

models = ['R', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
ut = ['km', 'MPa', 'MPa', 'MPa', 'MPa', 'MPa']
titls = ['Distance', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
xtext = [3, 10, 10, 10, 10, 10]

omoriData = read_pickle(omoriFile)
fig = plt.figure(figsize=(15,8))

for i, m in enumerate(models):
    R_t = omoriData[m+'R_t']
    t = omoriData[m+'t']
    omoriT = omoriData[m+'omoriT']
    mu = omoriData[m+'mu']
    K1 = omoriData[m+'K1']
    c = omoriData[m+'c']
    p = omoriData[m+'p']
    tagAvg = omoriData[m+'tagAvg']
    indx = np.argmin(abs(np.array(tagAvg) - 1))
    omoriR = omoriRate(omoriT[indx], mu[indx], K1[indx], c[indx], p[indx])
    
    # PLOT
    ax = fig.add_subplot(2, 3, i+1)

    ax.scatter(t[indx], R_t[indx], marker='o', c='black', label='Observed rate')
    ax.plot(omoriT[indx], omoriR, color='red', linewidth=2, label='Omori fit')
    # ax.set_title('Bin value 1 %s' %(ut[i]),bbox=dict(facecolor='grey', alpha=0.3, edgecolor='none'))
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_ylim(10, 3000)
    ax.set_xlim(0.001, 40)
    ax.set_xlabel('Days', fontsize=16)
    ax.set_ylabel('Rate', fontsize=16)
    ax.legend(loc='upper right')
    ax.text(0.002, 20, titls[i], fontweight='bold', bbox=dict(facecolor='grey', alpha=0.3, edgecolor='none'))
    ax.text(0.002, 40, 'Bin value 1 %s' %(ut[i]), color='red')
    
plt.subplots_adjust(wspace=0.25, hspace=0.45)
plt.savefig(figFile, bbox_inches = 'tight', pad_inches = 0.2)