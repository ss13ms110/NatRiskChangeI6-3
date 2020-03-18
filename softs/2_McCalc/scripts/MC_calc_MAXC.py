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
# inputs
polyResp = raw_input(bcol.BOLD + "Polygon from saved or generate NEW [S/N]: " + bcol.ENDC)

# Path
srcmodPath = '/home/sharma/Work/Project/git/NatRiskChangeI6-3/raw_data/srcmod/srcmod_fsp_2019Mar'
srcmodCata = './../1_preProcess/outputs/srcmodCata.txt'
iscPkl = './../1_preProcess/outputs/isc_events.pkl'
polyDir = 'outputs/polys'
McFile = './outputs/Mc_MAXC_1Yr.txt'
McFigsPath = './figs/Mc_plots'

# open output file
fout = open(McFile, 'w')

# parameters
dT = 365          # 1 year
Hdist = 100     # km
dHdist = 5
Vdist = 50      # depth of volume (km)
dVdist = 5
binSize = 0.2
McBuff = 0.2 


# load pkl file in memory
ISCdf = pd.read_pickle(iscPkl)
print bcol.OKGREEN+"Pickle file loaded...\n" + bcol.ENDC

# open mainshock catalog
srcmodFid = open(srcmodCata, 'r')

dummy = srcmodFid.readline()

for line in srcmodFid:
    srcmodFlN = line.split()[12]
    Yr = int(line.split()[0])
    Mn = int(line.split()[2])
    Dy = int(line.split()[3])
    Hr = int(line.split()[4])
    Mi = int(line.split()[5])
    Se = float(line.split()[6])
    la = float(line.split()[7])
    lo = float(line.split()[8])

    print bcol.OKBLUE + "Working on %s..." %(srcmodFlN.split(".")[0]) + bcol.ENDC
    # condition to use polygons from saved files or to generate new
    if polyResp == 'N' or polyResp == 'n':
        # get polygon buffer around the mainshock fault
        slpFile = srcmodPath + '/' + srcmodFlN
        xBuffer, yBuffer, polyBuffer = funcFile.getBuffer(slpFile, Hdist)

        polyFname = polyDir + '/' + srcmodFlN.split('.')[0] + '.poly'
        polyFid = open(polyFname, 'w')
        for i, xBuf in enumerate(xBuffer):
            polyFid.write('%8.3f  %8.3f\n' %(xBuf, yBuffer[i]))

    elif polyResp == 'S' or polyResp == 's':
        polyFname = polyDir + '/' + srcmodFlN.split('.')[0] + '.poly'
        polyData = np.loadtxt(polyFname)

        polyBuffer = funcFile.XY2Buffer(polyData)

    else:
        print bcol.FAIL + "Wrong input for Polygon!! Terminating" + bcol.ENDC
        quit()

    # buffered list of aftershocks in the polygon region and within given time frame
    sDate = dt.datetime(Yr, Mn, Dy, Hr, Mi, int(Se)) + dt.timedelta(seconds=1)   # 1 second after the mainshock
    eDate = sDate + dt.timedelta(days=dT) - dt.timedelta(seconds=1)     # sTime + time duration (e.g. 
                                                                        # 365) - 1 second to be within 
                                                                        # time duration
    AScata, resp = funcFile.getISCcata(ISCdf, sDate, eDate, polyBuffer)
    
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

        # write to file
        fout.write('%s  %6.2f\n' %(srcmodFlN.split(".")[0], Mc))
        
        # for figure
        f = plt.figure(figsize=(15,5))
        ax1 = f.add_subplot(121)
        ax2 = f.add_subplot(122)
        # plotting
        ax1.set_xlabel('Days')
        ax1.set_ylabel('Mag')
        ax1.scatter(ASdays, AScata['mag'])
        ax1.set_ylim(0,10)
        ax1.set_xlim(-5,365)

        ax2.set_xlabel('Mag')
        ax2.set_ylabel('# of events')
        ax2.set_yscale('log')
        ax2.scatter((edges[1:] + edges[:-1])/2, hist)
        ax2.vlines(Mc, min(hist), max(hist))
        ax2.set_xlim(-0.1,10)
        ylim = int(np.ceil(np.log10(max(hist))))
        ax2.set_ylim(0.1, 10**ylim)
        f.suptitle("%s" %(srcmodFlN.split(".")[0]), fontsize=20)
        f.savefig("%s/%s.png" %(McFigsPath, srcmodFlN.split(".")[0]), dpi=200)

fout.close()
        