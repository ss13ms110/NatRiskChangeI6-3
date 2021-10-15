import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# PATHS
datFile = './outputs/omoriPrams_3mnt.pkl'
figPath = './figs/omori'

# PRAMS
models = ['R', 'MAS0', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
titls = ['Distance', 'MAS$_0$', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
Tlabel = ['r<R (km)', '   s<-S (MPa)   |   s>S (MPa)', '   s<-S (MPa)   |   s>S (MPa)', 's<-S (MPa)   |   s>S (MPa)', 's>S (MPa)', 's>S (MPa)', 's>S (MPa)']
Tlabel2 = ['R (km)', 'S (MPa)', 'S (MPa)', 'S (MPa)', 'S (MPa)', 'S (MPa)', 'S (MPa)']

L_CUT = -8
U_CUT = 8

# read pickle
dat = pd.read_pickle(datFile)

# initialise figure
fig1 = plt.figure(figsize=(20,10))
fig2 = plt.figure(figsize=(20,10))
xmin = [0.1, 0.55, 0.1, 0.55]
ymin = [0.55, 0.55, 0.08, 0.08]
dx = 0.38
dy = 0.12

for i, tag in enumerate(models):

    # read data
    xAvg = dat[tag+'tagAvg']
    yK = dat[tag+'K']
    yc = dat[tag+'c']
    yp = dat[tag+'p']
    if tag in models[:4]:
        # declare axis
        ax1K = fig1.add_axes([xmin[i%4], ymin[i%4], dx, dy])
        ax1c = fig1.add_axes([xmin[i%4], ymin[i%4]+dy, dx, dy])
        ax1p = fig1.add_axes([xmin[i%4], ymin[i%4]+2*dy, dx, dy])

        ax1K.set_xlabel(Tlabel2[i], fontsize=18)
        ax1K.set_ylabel('K$_n$', fontsize=18)
        ax1c.set_ylabel('c', fontsize=18)
        ax1p.set_ylabel('p', fontsize=18)
        ax1c.set_xticks([])
        ax1p.set_xticks([])
        # ax1K.set_ylim(0,800)
        ax1c.set_ylim(0,0.5)
        # ax1p.set_ylim(0,1.0)
        if tag == 'R':
            ax1K.set_xlim(0,120)
            ax1c.set_xlim(0,120)
            ax1p.set_xlim(0,120)

        # PLOT
        ax1K.scatter(xAvg, yK, marker='.', s=2**5, c='red')
        ax1c.scatter(xAvg, yc, marker='.', s=2**5, c='green')
        ax1p.scatter(xAvg, yp, marker='.', s=2**5, c='blue')
        ax1p.set_title('%s' %(titls[i]), fontsize=20)

    else:
        # declare axis
        ax2K = fig2.add_axes([xmin[i%4], ymin[i%4], dx, dy])
        ax2c = fig2.add_axes([xmin[i%4], ymin[i%4]+dy, dx, dy])
        ax2p = fig2.add_axes([xmin[i%4], ymin[i%4]+2*dy, dx, dy])

        ax2K.set_xlabel(Tlabel2[i], fontsize=18)
        ax2K.set_ylabel('K$_n$', fontsize=18)
        ax2c.set_ylabel('c', fontsize=18)
        ax2p.set_ylabel('p', fontsize=18)
        ax2K.set_xticks(np.arange(L_CUT, U_CUT, 0.1), minor=True)
        ax2c.set_xticks([])
        ax2p.set_xticks([])
        # ax2K.set_ylim(0,600)
        ax2c.set_ylim(0,0.5)
        # ax2p.set_ylim(0,1.0)
        # PLOT
        ax2K.scatter(xAvg, yK, marker='.', s=2**5, c='red')
        ax2c.scatter(xAvg, yc, marker='.', s=2**5, c='green')
        ax2p.scatter(xAvg, yp, marker='.', s=2**5, c='blue')
        ax2p.set_title('%s' %(titls[i]), fontsize=20)

fig1.savefig('%s/omori_1.png' %(figPath))
fig2.savefig('%s/omori_2.png' %(figPath))
