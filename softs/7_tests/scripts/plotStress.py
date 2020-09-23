# script to plot stress maps for an event
# user input required: srcmodID of event

import numpy as np
import matplotlib.pyplot as plt
import subprocess as sp
import pandas as pd
import os


# FUNCTIONS =============================================================

def sigFilter(cfs, a, b):
    dummy1 = a*cfs - b
    dummy2 = np.exp(-dummy1)
    sig = 1/(1 + dummy2)
    return sig

def dist3D(lat1, lon1, z1,  lat2, lon2, z2):
    """
    Surface distance (in km) between points given as [lat,lon]
    """
    R0 = 6367.3        
    D = R0 * np.arccos(
        np.sin(np.radians(lat1)) * np.sin(np.radians(lat2)) +
        np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.cos(np.radians(lon1-lon2)))
    r = np.sqrt(np.square(D) + np.square(z1-z2))
    return r
# =========================================================================


# MAIN
# paths =======================================
stressPath = "./../../raw_data/stress_values"
CombPath = "./../3_CompAll/outputs/combData_7_1.pkl"
cataPath = "./../1_preProcess/outputs/srcmodCata.txt"
figPath = "./figs/t2"
# =============================================

# prams =======================================
xxyy = [140.933, 35.684]
lim = 1
sMin = 0.001
sMax = 1.5
a = 10
b = 1
dd = 2.5
tags = ['homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
sType = ['MAS0', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
# =============================================

# ask user for stress metric =====================================
smResp = int(raw_input("MAS0, MAS, OOP, VM, MS, VMS? [1/2/3/4/5/6]: "))
if not smResp in [1, 2, 3, 4, 5, 6]:
    print "Wrong input... [1,2,3,4,5,6]"
    quit()
print
smResp = smResp - 1
stressDir = stressPath + '/' + tags[smResp]

srcmodID = raw_input("Enter SRCMOD ID of slip model: ")
evDir = stressDir + '/' + srcmodID
if not os.path.exists(evDir):
    print "Event %s does not exist. Quiting..." %(srcmodID)
    quit()
print

depth = float(raw_input("Enter depth for stress map: "))
if not depth in np.arange(2.5,50,5):
    print "Wrong depth. Quiting..."
    quit()
print
# ================================================================

# get lat lon of main shock
cataRow = sp.check_output("cat %s | grep %s.fsp" %(cataPath, srcmodID), shell=True)
Mlat = float(cataRow.split()[7])
Mlon = float(cataRow.split()[8])


# get aftershocks from combdata file
# load pkl
df = pd.read_pickle(CombPath)
# filter for mainshock
df = df[df['MainshockID'] == srcmodID]
# filter above Mc(t)
df = df[df['mag'] > df['Mc(t)']]
# filter for depth range
df = df[(df['depth'] > depth-dd) & (df['depth'] < depth+dd)]

df1 = df[(df['R'] > 100) & (df['R'] < 120)]
ASrows = np.array(df[['latitude', 'longitude', 'mag', 'depth']])
ASrows1 = np.array(df1[['latitude', 'longitude', 'mag', 'depth']])
print df1
# load stress data
evFile = evDir + '/' + srcmodID + '_' + str(depth) + '.txt'


# load stress an smoothen values
sVals = np.loadtxt(evFile)

sVals[np.where(sVals[:,2] < sMin),2] = sMin + 0.001
sVals[np.where(sVals[:,2] >=sMax),2] = sMax - 0.001


# get aftershock grids
indx = np.zeros(len(sVals))

ASlat = []
ASlon = []
for ASrow in ASrows:
    dist = dist3D(ASrow[0], ASrow[1], depth, sVals[:,0], sVals[:,1], depth)
    
    imin = np.argmin(np.array(dist))
    ASlat.append(sVals[imin, 0])
    ASlon.append(sVals[imin, 1])

ASlat1 = []
ASlon1 = []
for ASrow1 in ASrows1:
    dist1 = dist3D(ASrow1[0], ASrow1[1], depth, sVals[:,0], sVals[:,1], depth)
    
    imin1 = np.argmin(np.array(dist1))
    ASlat1.append(sVals[imin1, 0])
    ASlon1.append(sVals[imin1, 1])



# plotting CFS
plt.figure(figsize=(8, 8))

CS2 = plt.tricontourf(sVals[:,1], sVals[:,0], sVals[:,2], np.linspace(sMin, sMax, 100), vmin = sMin, vmax = sMax, cmap="Reds", levels=[sMin, 0.5, sMax])

m2 = plt.cm.ScalarMappable(cmap="Reds")
m2.set_array(sVals[:,2])
m2.set_clim(sMin,sMax)
cb2=plt.colorbar(CS2, ticks=[sMin, 0.5, sMax], fraction=0.047, pad=0.04)
cb2.set_label('%s (Mpa)' %(sType[smResp]), fontsize=20)
plt.scatter(ASlon, ASlat, marker='s', c='black', s=20)
plt.scatter(ASlon1, ASlat1, marker='s', c='green', s=20)
plt.scatter(ASrows[:,1], ASrows[:,0], marker='.', c='white', s=2**2)
plt.scatter(Mlon, Mlat, marker='*', c='yellow', s=400)
# plt.scatter(xxyy[0], xxyy[1], marker='^', c='green', s=2**6)
plt.xlim(min(sVals[:,1])-lim, max(sVals[:,1])+lim)
plt.ylim(min(sVals[:,0])-lim, max(sVals[:,0])+lim)
plt.tick_params(axis="x", labelsize=18)
plt.tick_params(axis="y", labelsize=18)
plt.gca().set_aspect('equal', adjustable='box')
plt.xlabel("Longitude")
plt.ylabel("Latitute")
plt.show()
# plt.savefig("%s/%s_%s.pdf" %(figPath,  sType[int(smResp)-1], srcmodID), dpi=500)