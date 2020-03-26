# Date: 20-03-2020
# This script compile all aftershock, mainshock and 
# stress data in one binary (pickle) file
# Inputs: Stress values (MAS, OOP, VM, VMC, MS), mainshock 
# catalog, aftershock pickle file, polygons
# Outputs: CompData.pkl
# Header: []

import numpy as np
import pandas as pd
import funcFile
import os
import datetime as dt

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


# user inputs
polyResp = raw_input(bcol.BOLD + "Read Polygon from saved [Y] or generate NEW [N]: " + bcol.ENDC)
ASResp = raw_input(bcol.BOLD + "Read AS data from saved [Y] or from ISCpkl [N]: " + bcol.ENDC)


# Paths
srcCataFile = './../1_preProcess/outputs/testCata.txt'
srcmodPath = './../../raw_data/srcmod/srcmod_fsp_2019Mar'
polyDir = './../2_McCalc/outputs/polys'
iscPkl = './../1_preProcess/outputs/isc_events.pkl'
ASpklPath = './outputs/ASpkl'
stressDirPath = './../../raw_data/stress_values'


# variables
dT = 365        # 1 year
Hdist = 100     # km
Dlist = np.arange(2.5,50,5)
slipTol = 80    # in %

stressList = ['homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']

# -----------------------------------------------------------------------
#                                 MAIN
# -----------------------------------------------------------------------
# load pkl file in memory
ISCdf = pd.read_pickle(iscPkl)
print bcol.OKGREEN+"Pickle file loaded...\n" + bcol.ENDC

# open the srcmodCatalog file to read mainshocks
srcFid = open(srcCataFile, 'r')

srcRows = srcFid.readlines()[1:]

for srcRow in srcRows:
    Yr = int(srcRow.split()[0])
    Mn = int(srcRow.split()[2])
    Dy = int(srcRow.split()[3])
    Hr = int(srcRow.split()[4])
    Mi = int(srcRow.split()[5])
    Se = float(srcRow.split()[6])
    La = float(srcRow.split()[7])
    Lo = float(srcRow.split()[8])
    Dp = float(srcRow.split()[9])
    Mw = float(srcRow.split()[10])
    srcFname = srcRow.split()[12]

    # get all aftershocks related to this mainshock 
    # for next 1 year in a region of 100x100x50

    print bcol.OKBLUE + "Working on %s..." %(srcFname.split(".")[0]) + bcol.ENDC
    # condition to use polygons from saved files or to generate new
    if polyResp == 'N' or polyResp == 'n':
        # get polygon buffer around the mainshock fault
        slpFile = srcmodPath + '/' + srcFname
        xBuffer, yBuffer, polyBuffer = funcFile.getBuffer(slpFile, Hdist)

        polyFname = polyDir + '/' + srcFname.split('.')[0] + '.poly'
        polyFid = open(polyFname, 'w')
        for i, xBuf in enumerate(xBuffer):
            polyFid.write('%8.3f  %8.3f\n' %(xBuf, yBuffer[i]))

    elif polyResp == 'Y' or polyResp == 'y':
        polyFname = polyDir + '/' + srcFname.split('.')[0] + '.poly'
        polyData = np.loadtxt(polyFname)

        polyBuffer = funcFile.XY2Buffer(polyData)

    else:
        print bcol.FAIL + "Wrong input for Polygon!! Terminating" + bcol.ENDC
        quit()

    # check for aftershocks, if pkl files are present of not
    if ASResp == 'N' or ASResp == 'n':
        # buffered list of aftershocks in the polygon region and within given time frame
        sDate = dt.datetime(Yr, Mn, Dy, Hr, Mi, int(Se)) + dt.timedelta(seconds=1)   # 1 second after the mainshock
        eDate = sDate + dt.timedelta(days=dT) - dt.timedelta(seconds=1)     # sTime + time duration (e.g. 
                                                                            # 365) - 1 second to be within 
                                                                            # time duration
        ISCdfNew, resp = funcFile.getISCcata(ISCdf, sDate, eDate, polyBuffer)

        if resp == 1:
            ASpklFname = ASpklPath + '/' + srcFname.split('.')[0] + '.pkl'

            ASpklDf = ISCdfNew[['latitude', 'longitude', 'mag', 'depth', 'time']]
            
            # write individual AS data to pickle files
            ASpklDf.to_pickle(ASpklFname)

    elif ASResp == 'Y' or ASResp == 'y':
        ASpklFname = ASpklPath + '/' + srcFname.split('.')[0] + '.pkl'
        
        ASpklDf = pd.read_pickle(ASpklFname)     

    else:
        print bcol.FAIL + "Wrong input for AS pickle!! Terminating" + bcol.ENDC
        quit()
    
# -----------------------------------------------------------------------
#             AS data at one place
# -----------------------------------------------------------------------

    # create a dictionary of AS data
    catalog = dict()

    catalog['latitude'] = list(ASpklDf['latitude'])
    catalog['longitude'] = list(ASpklDf['longitude'])
    catalog['mag'] = list(ASpklDf['mag'])
    catalog['depth'] = list(ASpklDf['depth'])
    catalog['time'] = list(ASpklDf['time'])

# -----------------------------------------------------------------------
#     calculate nearest diatance of aftershock from the fault plane
# -----------------------------------------------------------------------
    slpFile = srcmodPath + '/' + srcFname
    R = funcFile.CalcR(slpFile, catalog, slipTol)
    
# -----------------------------------------------------------------------
#              accumulate all stress data in one dataframe
# -----------------------------------------------------------------------
    # check if stress files are present for all models
    for stressDir in stressList:
        EvDirPath = stressDirPath + '/' + stressDir + '/' + srcFname.split('.')[0]
        
        evResp = 0
        if os.path.isdir(EvDirPath):
            evResp = 1
    
    # if stress files are there then execute the stress-aftershock allocation
    if evResp == 1:

        # loop for stress models
        for stressDir in stressList:
            # path to event dir
            EvStressDir = stressDirPath + '/' + stressDir + '/' + srcFname.split('.')[0]

            latAll = []
            lonAll = []
            depAll = []
            stressAll = []
            # loop for layers
            for d in Dlist:
                stressFname = EvStressDir + '/' + srcFname.split('.')[0] + '_' + str(d) + '.txt'
                Sdata = np.loadtxt(stressFname)
            
            
                if d == 2.5:
                    areaIndex = funcFile.getRegion(Sdata[:,0:2], polyBuffer)
                
                if stressDir == 'homo_MAS':
                    latAll = np.append(latAll, Sdata[areaIndex,0])
                    lonAll = np.append(lonAll, Sdata[areaIndex,1])
                    stressAll = np.append(stressAll, Sdata[areaIndex,2])
                    depAll = np.append(depAll, np.full(len(Sdata[areaIndex,0]), d))

                else:
                    stressAll = np.append(stressAll, Sdata[areaIndex,2])
                    
                
            if stressDir == 'homo_MAS':
                stressDf = pd.DataFrame(np.column_stack((latAll, lonAll, depAll, stressAll)), columns=['lat', 'lon', 'dep', '%s' %(stressDir)])
            
            else:
                stressDf['%s' %(stressDir)] = stressAll

            print stressDf, "ss"

