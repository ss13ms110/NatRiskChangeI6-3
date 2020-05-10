import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import funcFile

figPath='./../../tmpFigs'

# load poly
polyD = np.loadtxt("./../../2_McCalc/outputs/polys/s2002DENALI01HAYE.poly")

#load AS
df=pd.read_pickle("./../../3_CompAll/outputs/ASpkl/s2002DENALI01HAYE.pkl")

# pram
cR = 150
#read srcmod
d1, d2, d3, lat, lon, z, slip = funcFile.read_fsp_file("../../../raw_data/srcmod/srcmod_fsp_2019Mar/s2002DENALI01HAYE.fsp")
lat=np.array(lat)
lon=np.array(lon)
z=np.array(z)
slip=np.array(slip)

slipTol=20
# slipCut=max(slip)*(1-slipTol/100.0)
# slipCut=np.median(slip)
slipCut=np.min(slip)

latS=lat[(slip > slipCut)]
lonS=lon[(slip > slipCut)]

latA=np.array(list(df['latitude']))
lonA=np.array(list(df['longitude']))
zA=np.array(list(df['depth']))

R = []
for i in range(len(latA)):
    r = funcFile.dist3D(latA[i], lonA[i], zA[i], lat, lon, z)
    R.append(min(r))

R = np.array(R)

latC = latA[(R>cR)]
lonC = lonA[R>cR]
zC = zA[R>cR]

print zC

plt.figure(figsize=(12,12))
plt.scatter(polyD[:,0], polyD[:,1], label="poly")
plt.scatter(lonA, latA, label="AS")
plt.scatter(lonC, latC, label="ASCut")
plt.scatter(lon, lat, label="lat-lon", marker='x')
plt.scatter(lonS, latS, label="slip", c='black')
plt.legend()
plt.xlabel("lon")
plt.ylabel("lat")
plt.title('Max Slip = %6.3f  |  Slip Cut = %6.3f' %(max(slip), slipCut))

# plt.show()
plt.savefig('%s/slipTolKOBE_MEDIAN.png' %(figPath))

# plt.figure()
# plt.hist(slip)
# plt.xlabel("# counts")
# plt.ylabel("Slip")
# plt.show()