# Date: 20-03-2020
# This script compile all aftershock, mainshock and 
# stress data in one binary (pickle) file
# Inputs: Stress values (MAS, OOP, VM, VMC, MS), mainshock 
# catalog, aftershock pickle file, polygons
# Outputs: CompData.pkl
# Header: ['time', 'MainshockID', 'latitude', 'longitude', 'depth', 'mag', 'R', 'Mw-mag', 'Mc(t)', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']

import numpy as np
import pandas as pd
import funcFile
import os
import datetime as dt
import matplotlib.pyplot as plt


# user inputs
ASResp = raw_input(funcFile.bcol.BOLD + "Read AS data from saved [Y] or from ISCpkl [N]: " + funcFile.bcol.ENDC)


# Paths
srcCataFile = './data/t2Cata.txt'
srcmodPath = './../../raw_data/srcmod/srcmod_fsp_2019Mar'
McFile = './../2_McCalc/outputs/Mc_MAXC_1Yr.txt'
iscPkl = './../1_preProcess/outputs/isc_events.pkl'
ASpklPath = './data/ASpkl'
stressDirPath = './../../raw_data/stress_values'
CombPklFile = './data/combData_t2.pkl'


# variables
dT = 92      # 1 year
Hdist = 100     # km
Vdist = 50      # km
Dlist = np.arange(2.5,50,5)
slipTol = 20    # in %  | DEPRECATED median slip is used instead

stressList = ['homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']

# -----------------------------------------------------------------------
#                                 MAIN
# -----------------------------------------------------------------------
# load pkl file in memory
ISCdf = pd.read_pickle(iscPkl)
print funcFile.bcol.OKGREEN+"Pickle file loaded...\n" + funcFile.bcol.ENDC

# open the srcmodCatalog file to read mainshocks
srcFid = open(srcCataFile, 'r')

srcRows = srcFid.readlines()[1:]

# declare df columns
dfColumns = ['time', 'MainshockID', 'latitude', 'longitude', 'depth', 'mag', 'R', 'Mw-mag', 'Mc(t)', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']

# create an empty dataframe to hold all the combined data
CombDf = pd.DataFrame([], columns=dfColumns)

# load Mc data
Mcdat = np.genfromtxt(McFile, dtype='str')

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
    
    adp = Dlist[np.argmin(Dlist - Dp)]
    
    try:
        Mc = float([Mcrow[1] for Mcrow in Mcdat if Mcrow[0] == srcFname.split('.')[0]][0])
    except:
        Mc = 0
    # get all aftershocks related to this mainshock 
    # for next 1 year in a region of 100x100x50

    print funcFile.bcol.OKBLUE + "Working on %s..." %(srcFname.split(".")[0]) + funcFile.bcol.ENDC
   
    # get polygon buffer around the mainshock fault
    slpFile = srcmodPath + '/' + srcFname
    xBuffer, yBuffer, polyBuffer = funcFile.getBuffer(slpFile, Hdist)


    # check for aftershocks, if pkl files are present of not
    if ASResp == 'N' or ASResp == 'n':
        # buffered list of aftershocks in the polygon region and within given time frame
        sDate = dt.datetime(Yr, Mn, Dy, Hr, Mi, int(Se)) + dt.timedelta(seconds=1)   # 1 second after the mainshock
        eDate = sDate + dt.timedelta(days=dT) - dt.timedelta(seconds=1)     # sTime + time duration (e.g. 
                                                                            # 365) - 1 second to be within 
                                                                            # time duration
        ISCdfNew, resp = funcFile.getISCcata(ISCdf, sDate, eDate, polyBuffer, Vdist)

        ASfileFlg = 0
        if resp == 1:
            
            ASpklFname = ASpklPath + '/' + srcFname.split('.')[0] + '.pkl'

            ASpklDf = ISCdfNew[['latitude', 'longitude', 'mag', 'depth', 'time']]
            
            # write individual AS data to pickle files
            ASpklDf.to_pickle(ASpklFname)
            ASfileFlg = 1

    elif ASResp == 'Y' or ASResp == 'y':
        ASfileFlg = 0
        ASpklFname = ASpklPath + '/' + srcFname.split('.')[0] + '.pkl'
        
        if os.path.isfile(ASpklFname):
            ASpklDf = pd.read_pickle(ASpklFname)
            ASfileFlg = 1  

    else:
        print funcFile.bcol.FAIL + "Wrong input for AS pickle!! Terminating" + funcFile.bcol.ENDC
        quit()
    
# -----------------------------------------------------------------------
#             AS data at one place
# -----------------------------------------------------------------------

    if ASfileFlg == 1:
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
    #             calculate Mc(t) for each aftershock using eq. 
    #                    from Helmstetter et.al. 2006
    # -----------------------------------------------------------------------
        MSdatetime = dt.datetime(Yr, Mn, Dy, Hr, Mi, int(Se))
        Mct = funcFile.CalcMct(Mw, MSdatetime, catalog['time'], Mc)

    # -----------------------------------------------------------------------
    #              accumulate all stress data in one dataframe
    # -----------------------------------------------------------------------
        # check if stress files are present for all models
        evResp = 1
        for stressDir in stressList:
            EvDirPath = stressDirPath + '/' + stressDir + '/' + srcFname.split('.')[0]
                        
            if not os.path.isdir(EvDirPath):
                evResp = 0
        
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
                ind = 0
                for d in Dlist:
                    stressFname = EvStressDir + '/' + srcFname.split('.')[0] + '_' + str(d) + '.txt'
                    Sdata = np.loadtxt(stressFname)
                
                
                    if d == 2.5:
                        areaIndex = funcFile.getRegion(Sdata[:,0:2], polyBuffer)
                    
                    if stressDir in stressList[:3]:
                        latAll = np.append(latAll, Sdata[areaIndex,0])
                        lonAll = np.append(lonAll, Sdata[areaIndex,1])
                        stressAll = np.append(stressAll, Sdata[areaIndex,2])
                        depAll = np.append(depAll, np.full(len(Sdata[areaIndex,0]), d))

                    else:
                        strTP = np.concatenate((Sdata[ind:,2], Sdata[:ind,2]))  # workaround for shifter arrays
                        stressAll = np.append(stressAll, strTP)

                    ind += 1              
                
                    
                if stressDir == 'homo_MAS':
                    stressDf = pd.DataFrame(np.column_stack((latAll, lonAll, depAll, stressAll)), columns=['lat', 'lon', 'dep', '%s' %(stressDir)])
                
                else:
                    stressDf['%s' %(stressDir)] = stressAll
                
                
    # -----------------------------------------------------------------------
    #              for each aftershock create a database
    #              with mainshockId, R and stress values
    # -----------------------------------------------------------------------
                # update lat, lon and depth from dataframe
                latAll = np.array(stressDf['lat'])
                lonAll = np.array(stressDf['lon'])
                depAll = np.array(stressDf['dep'])
            vm = np.array(stressDf['GF_MAS'])
            
                       
                # print stressDf
            plt.figure()
            lap = latAll[depAll == adp]
            lop = lonAll[depAll == adp]
            vmp = vm[depAll == adp]
            s1, s2, ds = -2, 5, 0.2
            vmp[np.where(vmp < s1)] = s1 + 0.001
            vmp[np.where(vmp >= s2)] = s2 - 0.001
            CS2 = plt.tricontourf(lop, lap, vmp, np.linspace(s1, s2, 100), vmin = s1, vmax = s2, cmap="Reds", levels=np.linspace(s1, s2, 100))
            cb2=plt.colorbar(CS2, ticks=np.linspace(s1, s2, 10), fraction=0.047, pad=0.04)
            for i in range(len(catalog['latitude'])):
                laAS = catalog['latitude'][i]
                loAS = catalog['longitude'][i]
                deAS = catalog['depth'][i]
                tmAs = catalog['time'][i]
                mgAs = catalog['mag'][i]

                
                # calculate the nearest distance to the grid
                dd = funcFile.dist3D(laAS, loAS, deAS, latAll, lonAll, depAll)
                mn = np.min(dd)
                depMinIndx = np.argmin(dd)
                
                if R[i] < 1:
                    plt.scatter(loAS, laAS, marker='.', c='black', s=2**6)
                    sslo = stressDf.iloc[depMinIndx, [1]].to_numpy().tolist()
                    ssla = stressDf.iloc[depMinIndx, [0]].to_numpy().tolist()
                    plt.scatter(sslo, ssla, marker='s', c='green', s=2**4)
                    print R[i], laAS, loAS, deAS, stressDf.iloc[depMinIndx].to_numpy().tolist()
                # print depMinIndx
                tmpList = [tmAs, srcFname.split('.')[0], laAS, loAS, deAS, mgAs, R[i], Mw-mgAs, Mct[i]] 
                
                tmpList = tmpList + stressDf.iloc[depMinIndx, [3,4,5,6,7,8]].to_numpy().tolist()
                
                CombDf = CombDf.append(pd.Series(tmpList, index=CombDf.columns), ignore_index=True)
            plt.show()
# save dataframe to a pickle file
CombDf.to_pickle(CombPklFile)