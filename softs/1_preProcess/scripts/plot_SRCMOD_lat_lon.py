import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

# stations
latlonPath = './outputs/SRCMOD_lat_lon.txt'
figpath = './figs/SRCMOD_lat_lon_map.pdf'


# load data
countries = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

# load sta data
lat, lon, mag = np.loadtxt(latlonPath, usecols=(1,2,3), unpack=True)
col = np.array(['s']*len(mag))
for i,j in zip([4,6,8],['red', 'green', 'blue']):
    col[(mag>=i) & (mag<i+2)] = j

# init plot
fig, ax = plt.subplots(figsize=(15,12))
plt.ylim(-65, 85)
plt.xlabel('Longitude', fontsize=12)
plt.ylabel('Latitude', fontsize=12)

# plot map
countries.plot(color='lightgrey', ax=ax)

# plot station
plt.scatter(lon, lat, s=2**7, color=col, marker='.')

plt.savefig(figpath, bbox_inches = 'tight', pad_inches = 0.2)