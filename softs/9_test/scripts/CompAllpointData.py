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


# user inputs
ASResp = raw_input(funcFile.bcol.BOLD + "Read AS data from saved [Y] or from ISCpkl [N]: " + funcFile.bcol.ENDC)


# Paths
srcCataFile = './../1_preProcess/outputs/newSrcmodCata.txt'
srcmodPath = './../../raw_data/srcmod/srcmod_fsp_2019Mar'
McFile = './../2_McCalc/outputs/Mc_MAXC_1Yr.txt'
iscPkl = './../1_preProcess/outputs/isc_events.pkl'
ASpklPath = './outputs/ASpkl'
stressDirPath = './../../raw_data/pointStressData'
CombPklFile = './outputs/CombData_9-1.pkl'
notFile = './outputs/notWorked.txt'


# variables
dT = 365        # 1 year
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
fidNot = open(notFile, 'w')
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
    #     calculate nearest distance of aftershock from the fault plane
    # -----------------------------------------------------------------------
        slpFile = srcmodPath + '/' + srcFname
        R = funcFile.CalcR(slpFile, catalog, slipTol)
        
    # -----------------------------------------------------------------------
    #             calculate Mc(t) for each aftershock using eq. 
    #                    from Helmstetter et.al. 2006
    # -----------------------------------------------------------------------
        MSdatetime = dt.datetime(Yr, Mn, Dy, Hr, Mi, int(Se))
        Mct = funcFile.CalcMct(Mw, MSdatetime, catalog['time'], Mc)
        Mct = np.array(Mct)
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
            
            for depth in Dlist:
                
                deAS = np.array(catalog['depth'])
                deIndx = (deAS > depth-2.5) & (deAS <= depth+2.5)
                
                if not deIndx.any():
                    continue
                deLoc = np.where(deIndx)[0]
                deASLoc = deAS[deLoc]
                Ras = R[deLoc]
                MctAS = Mct[deLoc]
                laAS = np.array(catalog['latitude'])[deLoc]
                loAS = np.array(catalog['longitude'])[deLoc]
                tmAS = np.array(catalog['time'])[deLoc]
                mgAS = np.array(catalog['mag'])[deLoc]
                msID = np.full(len(laAS), srcFname.split('.')[0])
                stressArry = []
                stressFileResp = True
                clen = 0
                for stressDir in stressList:
                    # path to event dir
                    EvStressDir = stressDirPath + '/' + stressDir + '/' + srcFname.split('.')[0]

                    EvStressFile = EvStressDir + '/' + srcFname.split('.')[0] + '_' + str(depth) + '.txt'
                    
                    # check if file exist
                    if not os.path.isfile(EvStressFile):
                        stressFileResp = False
                        break
                    
                    try:
                        stressAll = np.loadtxt(EvStressFile, usecols=(2))
                        if len(stressAll.shape) == 0:
                            stressAll = np.array([stressAll])
                    except:
                        stressAll = np.loadtxt(EvStressFile, skiprows=(2))
                        stressAll = np.array([stressAll])
                        
                    
                    rlen = len(stressAll)

                    stressArry = np.append(stressArry, [stressAll])
                    clen += 1
                    
                if stressFileResp:
                    stressArryRe = np.reshape(stressArry, (clen, rlen))
                    stressArryRe = stressArryRe.T
                    
                    if len(stressArryRe) == len(laAS):
                        stackedArry = np.column_stack((tmAS, msID, laAS, loAS, deASLoc, mgAS, Ras, Mw-mgAS, MctAS, stressArryRe))
                        CombDf = CombDf.append(pd.DataFrame(stackedArry, columns=dfColumns), ignore_index=True)
                    else:
                        fidNot.write('%s\n' %(srcFname.split('.')[0]))
                        print "Not worked..."
                    
fidNot.close()
# save dataframe to a pickle file
CombDf.to_pickle(CombPklFile)
