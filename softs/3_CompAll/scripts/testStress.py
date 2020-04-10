import numpy as np
import funcFile
import os

class bcol:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


srcCataFile = './../1_preProcess/outputs/srcmodCata.txt'
stressDirPath = './../../raw_data/stress_values'

stressList = ['homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
srcmodPath = './../../raw_data/srcmod/srcmod_fsp_2019Mar'

Hdist = 100     # km
Dlist = np.arange(2.5,50,5)


# open the srcmodCatalog file to read mainshocks
srcFid = open(srcCataFile, 'r')

srcRows = srcFid.readlines()[1:]

fid = open('resp.file', 'w')
for srcRow in srcRows:
    srcFname = srcRow.split()[12]
    # get polygon buffer around the mainshock fault
    slpFile = srcmodPath + '/' + srcFname
    print bcol.OKBLUE + "Working on %s..." %(srcFname.split(".")[0]) + bcol.ENDC

    xBuffer, yBuffer, polyBuffer = funcFile.getBuffer(slpFile, Hdist)

    
    for stressDir in stressList:
        EvDirPath = stressDirPath + '/' + stressDir + '/' + srcFname.split('.')[0]
        
        evResp = 0
        if os.path.isdir(EvDirPath):
            evResp = 1
    
    # if stress files are there then execute the stress-aftershock allocation
    if evResp == 1:

        cList = []
        for stressDir in stressList:
            # path to event dir
            EvStressDir = stressDirPath + '/' + stressDir + '/' + srcFname.split('.')[0]

            # loop for layers
            for d in Dlist:
                stressFname = EvStressDir + '/' + srcFname.split('.')[0] + '_' + str(d) + '.txt'
                Sdata = np.loadtxt(stressFname)


                if d == 2.5:
                    areaIndex = funcFile.getRegion(Sdata[:,0:2], polyBuffer)

                if stressDir in stressList[:3]:
                    cList.append(len(Sdata[areaIndex,2]))

                else:
                    cList.append(len(Sdata[:,2]))
    
    if cList.count(cList[0]) == len(cList):
        resp = 1
    else:
        resp = 0

    fid.write('%s   %d\n' %(srcFname, resp))