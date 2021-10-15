from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
from pandas import read_pickle
import funcFileMC as funcFile
import timeit as ti
import warnings
warnings.filterwarnings("ignore")
Stime = ti.default_timer()

# path
combPath = './outputs/CombData_9-4.pkl'
RvSfn1 = './figs/bVal4/RvSplot/Reg_RvSplot.pdf'


tags = ['R', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
# models = ['R (Km)', 'MAS (MPa)', 'OOP (MPa)', 'VM (MPa)', 'MS (MPa)', 'VMS (MPa)']
titls = ['MAS', 'OOP', 'VM', 'MS', 'VMS']

mulFactor = 1e-6    # convert Pa to MPa
Lcut1 = -8
Lcut2 = 0
Ucut = 8
bin_num = 480
D = 120
bins = np.linspace(0,D,bin_num)
Rvals = (bins[1:] + bins[:-1])/2
ytext = [0.3, 6.5, 4, 6.3, 6.8]
xtext = [0.15, 30, 40, 40, 30]
# main
combDataload = read_pickle(combPath)
print funcFile.printLoad("Combined data loaded at", Stime)

# apply filters in combData
combData = combDataload[combDataload['mag'] > combDataload['Mc(t)']]
print funcFile.printProcess("Mc filter applied at", Stime)

combData.loc[(combData['R']>D), 'R'] = D

for tag in tags[1:]:
    if tag in tags[1:3]:
        combData[tag] = combData[tag] * mulFactor
        combData.loc[(combData[tag] < Lcut1), tag] =  Lcut1
        combData.loc[(combData[tag] > Ucut), tag] = Ucut
    else:
        combData.loc[(combData[tag] > Ucut), tag] = Ucut

print funcFile.printProcess("Converted from Pa to Mpa at", Stime)

fig = plt.figure(figsize=(15,8))
R = combData['R'].to_numpy(dtype=np.double)

for i, tag in enumerate(tags[1:]):
    
    S = combData[tag].to_numpy(dtype=np.double)
    
    ax = fig.add_subplot(2, 3, i+1)

    ax.set_xlabel('R (km)', fontsize=16)
    ax.set_ylabel('Stress (MPa)', fontsize=16)
    # ax.set_xlim(0, D)
    ax.set_xscale('log')
    ax.set_xlim(0.1, 120)
    Savg, _, _ = stats.binned_statistic(R, S, statistic='mean', bins=bins)
    
    ax.scatter(Rvals, Savg, color='black', s=2**3)
    ax.text(xtext[i], ytext[i], titls[i], fontweight='bold', bbox=dict(facecolor='grey', alpha=0.3, edgecolor='none'))
    #legend
    # ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2), ncol=1, fancybox=True)
    
plt.subplots_adjust(wspace=0.25, hspace=0.3)
# plt.show()
plt.savefig(RvSfn1, bbox_inches = 'tight', pad_inches = 0.2)