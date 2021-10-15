from shapely.geometry import Polygon, LinearRing, Point
import numpy as np

# distance in 2D
def dist(lat1, lon1, lat2, lon2):
        """
        Surface distance (in km) between points given as [lat,lon]
        """
        R0 = 6367.3        
        D = R0 * np.arccos(
            np.sin(np.radians(lat1)) * np.sin(np.radians(lat2)) +
            np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.cos(np.radians(lon1-lon2)))
        return D

# distance 3D
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

# to read srcmod .fsp file
def read_fsp_file(inname):

    Nfault = []
    lat = []
    lon = []
    z = []
    slip = []
    fin = open(inname, "r")
    for line in fin:
        column = line.split()
        Ncol = len(column)
        if column:
            Ncol = len(column)
            if column[0] == "%":
                for n in range(Ncol):
                    if column[n] == 'Loc' and Ncol >= n+4 and column[n+3] == '=':
                        lat_hypo = float(column[n+4])
                        lon_hypo = float(column[n+7])
                    if column[n] == 'Nsbfs' and column[n+1] == '=':
                        Nfault.append(int(column[n+2]))
            else:
                lat.append(float(column[0]))
                lon.append(float(column[1]))
                z.append(float(column[4]))
                slip.append(float(column[5]))
    fin.close()
    return lat_hypo, lon_hypo, Nfault, lat, lon, z, slip

# this function uses shapley to calculate buffer values
def createBuffer(las, los, distDeg):
    poly = Polygon()
    for Nplane in range(len(las)):
        coords = [(los[Nplane][0],las[Nplane][0]), (los[Nplane][1],las[Nplane][1]), (los[Nplane][2],las[Nplane][2]), (los[Nplane][3],las[Nplane][3])]

        lr = LinearRing(coords)
        polyTmp = Polygon(lr).buffer(distDeg)
        poly = poly.union(polyTmp)

    return np.array(poly.exterior.xy), poly

# get srcmod buffer
def getBuffer(filePath, Hdist):
    
    lat_hypo, lon_hypo, Nfault, lat, lon, z, slip = read_fsp_file(filePath)
    
    na = 0
    nb = 0
    la_corners = [[]]*len(Nfault)
    lo_corners = [[]]*len(Nfault)
    i = 0
    for nf in Nfault:
        nb += nf
        n_depths = len(np.unique(z[na:nb]))
        n_strk = int(nf/float(n_depths))

        la_corners_tmp = [lat[na+0], lat[na+n_strk-1], lat[na+nf-1], lat[na+nf-n_strk]]
        lo_corners_tmp = [lon[na+0], lon[na+n_strk-1], lon[na+nf-1], lon[na+nf-n_strk]]
        
         
        la_corners[i] = la_corners[i] + la_corners_tmp
        lo_corners[i] = lo_corners[i] + lo_corners_tmp
        i += 1
        na += nf

    long2km = dist(lat_hypo, lon_hypo-0.5, lat_hypo, lon_hypo+0.5)
    distDeg = Hdist/long2km

    [xBuffer, yBuffer], polyBuffer = createBuffer(la_corners, lo_corners, distDeg)

    return xBuffer, yBuffer, polyBuffer

# get poly region
def getRegion(latlon, polyBuffer):

    areaIndex = []
    for i in range(len(latlon)):
        pt = Point(latlon[i,1], latlon[i,0])

        areaIndex.append(polyBuffer.contains(pt))
    return areaIndex

# function to calculate nearest distance between the fault and the aftershock
# given some cutoff for slip
def CalcR(filePath, catalog, slipTol):
    d1, d2, d3, lat, lon, z, slip = read_fsp_file(filePath)      # d# dummies
    lat = np.array(lat)
    lon = np.array(lon)
    z = np.array(z)
    slip = np.array(slip)

    R = []

    for i in range(len(catalog['latitude'])):
        lati = float(catalog['latitude'][i])
        loni = float(catalog['longitude'][i])
        zi = float(catalog['depth'][i])

        r = dist3D(lati, loni, zi, lat, lon, z)
        # slipCut = np.median(slip)
        # slipCut = max(slip)*(1-slipTol/100.0)
        # R.append(min(r[(slip > slipCut)]))
        R.append(min(r[(slip > 0)]))            # take all slip values positive
        # R.append(min(r))

    return np.array(R)