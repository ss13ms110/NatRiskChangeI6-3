# This script uses MAXC method of Wiemer and Wyss 2000
# to estimate Mc and MLE to estimate b-value
# Input: 'srcmodCata.txt' and 'isc_events.pkl'
# Output: Mc_MAXC_1Yr.txt
# Header: ['fileName', 'StartTime', 'latitude', 'longitude', 'Mc', 'b-value', 'b-err', 'a-value', 'a-err']

import numpy as np
import pandas as pd
import funcFile
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from scipy.stats import linregress


# FUNCTIONS
# For coloured outputs in terminal
class bcol:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# MAINS

# Path
srcmodPath = '/home/rebhu-dev-l1/Work/NRC/raw_data/srcmod/srcmod_fsp_2019Mar'
srcmodCata = './srcmodCata.txt'
iscPkl = './../1_preProcess/outputs/isc_events.pkl'
McFigsPath = './'


# parameters
dT = 90          # 1 year
Hdist = 100     # km
dHdist = 5
Vdist = 50      # depth of volume (km)
dVdist = 5
binSize = 0.2
McBuff = 0.2
lbl = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)', '(g)', '(h)']
lbl1 = ['(a\')', '(b\')', '(c\')', '(d\')', '(e\')', '(f\')', '(g\')', '(h\')']

plt.rc('font', family='sans-serif')
plt.rc('font', size=14)
plt.rc('legend', fontsize=12)
font = font_manager.FontProperties(family='monospace',
                                   weight='normal',
                                   style='normal', size=14)
# load pkl file in memory
ISCdf = pd.read_pickle(iscPkl)
print(bcol.OKGREEN+"Pickle file loaded...\n" + bcol.ENDC)

# open mainshock catalog
srcmodFid = open(srcmodCata, 'r')


for ii,line in enumerate(srcmodFid):
    srcmodFlN = line.split()[12]
    Yr = int(line.split()[0])
    Mn = int(line.split()[2])
    Dy = int(line.split()[3])
    Hr = int(line.split()[4])
    Mi = int(line.split()[5])
    Se = float(line.split()[6])
    la = float(line.split()[7])
    lo = float(line.split()[8])
    Mw = float(line.split()[10])

    eq_label = '$M_w$ = %3.1f\nDatetime: %02d-%02d-%04d %02d:%02d:%02d\nLocation: %8.3f, %8.3f' %(Mw, Dy, Mn, Yr, Hr, Mi, Se, lo, la)
    
    print(bcol.OKBLUE + "Working on %s..." %(srcmodFlN.split(".")[0]) + bcol.ENDC)
   
    # get polygon buffer around the mainshock fault
    slpFile = srcmodPath + '/' + srcmodFlN
    xBuffer, yBuffer, polyBuffer = funcFile.getBuffer(slpFile, Hdist)

    # buffered list of aftershocks in the polygon region and within given time frame
    sDate = dt.datetime(Yr, Mn, Dy, Hr, Mi, int(Se)) + dt.timedelta(seconds=1)   # 1 second after the mainshock
    eDate = sDate + dt.timedelta(days=dT) - dt.timedelta(seconds=1)     # sTime + time duration (e.g. 
                                                                        # 365) - 1 second to be within 
                                                                        # time duration
    AScata, resp = funcFile.getISCcata(ISCdf, sDate, eDate, polyBuffer)
    print(resp)
    # check for the length of aftershock catalog
    if resp == 1:    
        #----------------------------------
        # calculate Mc
        #----------------------------------

        # get days distribution of aftershocks
        ASdays = funcFile.getDays(AScata)

        # create mag bins
        magBins = np.arange(0,10.1,binSize)

        hist, edges, Mc = funcFile.McCalc(AScata, magBins, McBuff)
        hist_cumsum = np.cumsum(hist[::-1])[::-1]
        # calculate Mc(t) using eq. from Helmstetter et.al. 2006
        Mct = Mw - 4.5 - 0.75*np.log(dT)

        if Mct < 2:
            Mct = 2

        # for linear regression
        tmp = (edges[1:] + edges[:-1])/2
        xin = tmp[(tmp>Mc)]
        yin = hist_cumsum[tmp>Mc]
        xin = xin[yin!=0]
        yin = yin[yin!=0]
        slope, intercept, r_value, p_value, std_err = linregress(xin, np.log10(yin))
        print(slope, intercept, r_value, p_value, std_err)
        
        # ==================================
        
        # for figure
        f = plt.figure(figsize=(15,5))
        ax1 = f.add_subplot(121)
        ax2 = f.add_subplot(122)
        # plotting
        ax1.set_xlabel('Days')
        ax1.set_ylabel('Magnitude')
        ddy = 0
        ax1.scatter(ASdays, AScata['mag'], c='black', s=2, label='_nplegend_')
        if Mw < max(AScata['mag'][:10]):
            Mw = max(AScata['mag'][:10])
            ddy = ASdays[np.argmax(AScata['mag'][:10])]
        ax1.scatter(ddy, Mw, c='red', s=2**4, marker='*', label=eq_label)
        # ax1.plot([],[],' ', label=eq_label)
        ax1.set_ylim(0,10)
        ax1.set_xlim(-5,95)
        # ax1.text(-0.15, 0.99, lbl[ii], fontsize=14, color='k', horizontalalignment='left', transform=ax1.transAxes)
        ax1.legend(prop=font)
        
        ax2.set_xlabel('Magnitude')
        ax2.set_ylabel('Number of events (N)')
        ax2.set_yscale('log')
        ax2.scatter((edges[1:] + edges[:-1])/2, hist, c='black', s=4, label='Non cumulative')
        ax2.scatter((edges[1:] + edges[:-1])/2, hist_cumsum, c='red', s=4, label='Cumulative')
        ax2.plot(xin, 10**(slope*xin+intercept), c='red', label="GR-law fit\n" + r'$log_{10}N = {%.2f} - ({%.2f}\pm{%.2f})M$'%(intercept, abs(slope), std_err) + "\n" + r'$R^2$=%6.3f' %(r_value))
        ax2.vlines(Mc, min(hist), max(hist_cumsum), color='gray', linewidth=2, linestyle='dashed')
        ax2.set_xlim(-0.1,10)
        # ax2.text(-0.15, 0.99, lbl1[ii], fontsize=14, color='k', horizontalalignment='left', transform=ax2.transAxes)
        ax2.text(Mc+0.5, 1, '$M_c$=%3.1f' %(Mc), fontsize=12, color='gray', horizontalalignment='left')
        ylim = int(np.ceil(np.log10(max(hist_cumsum))))
        ax2.set_ylim(0.1, 10**ylim)
        ax2.legend(loc='upper right')
        # f.suptitle("%s" %(srcmodFlN.split(".")[0]), fontsize=20)
        f.savefig("%s/%05d_%s.png" %(McFigsPath, ii, srcmodFlN.split(".")[0]), dpi=400, bbox_inches = 'tight')

        