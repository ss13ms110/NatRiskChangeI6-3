# Date: 27.02.2020
# This script make events catalog from SRCMOD dataset
# and gives output in srcmodEvents
# Header: 'day month year lat lon depth mag srcmodFileName'


import numpy as np
import os
import sys

# read file
dirPath='/home/sharma/Work/Project/git/NatRiskChangeI6-3/raw_data/srcmod/srcmod_fsp_2019Mar'

fileList = os.listdir(dirPath)

fout = open('srcmodEvents.txt','w')

for f in fileList:
    fpath = '%s/%s' %(dirPath, f)
    fid = open(fpath,'r')

    for line in fid:
        column = line.split()

        if column:
            Ncol = len(column)
            if column[0] == '%':
                for n in range(Ncol):
                    if column[n].find('/', 5) > 0:
                        date = column[n].split('/')
                        mm = int(date[0])
                        dd = int(date[1])
                        yy = int(date[2])
                    if column[n] == 'Loc' and Ncol >= n+4 and column[n+3] == '=':
                        lat_hypo = float(column[n+4])
                        lon_hypo = float(column[n+7])
                        z_hypo = float(column[n+10])
                    if column[n] == 'Mw' and Ncol >= n+2 and column[n+1] == '=':
                        M = float(column[n+2])

    fout.write('%02d %02d %4d %8.3f %8.3f %6.1f %4.1f %s\n' %(dd, mm, yy, lat_hypo, lon_hypo, z_hypo, M, f))
    fid.close()
fout.close()
