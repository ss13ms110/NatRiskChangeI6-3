import numpy as np
import csv
from dateutil import rrule
from shapely.geometry import Polygon, LinearRing, Point
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
#func


evName = 's2007BENKUL01JIxx'
srcmodCata = '../1_preProcess/outputs/srcmodCata.txt'
hdfPath = '../../raw_data/isc_data/1900-2019_csv'
polyPath = 'outputs/polys'

# get poly limits
polyFname = polyPath + '/' + evName + '.poly'

polyData = np.loadtxt(polyFname)
poly_lst = []
for row in polyData:
    poly_lst.append(list(row))

poly_pairs = LinearRing(poly_lst)
Poly = Polygon(poly_pairs)
# loMin, laMin, loMax, laMax = list(Poly.bounds)

########
srcFid = open(srcmodCata, 'r')
srcLines = srcFid.readlines()[1:]

for line in srcLines:
    nm = line.split()[12].split(".")[0]
    if nm == evName:
        yr = int(line.split()[0])
        mn = int(line.split()[2])
        dy = int(line.split()[3])
        hr = int(line.split()[4])
        mi = int(line.split()[5])
        se = float(line.split()[6])
        la = float(line.split()[7])
        lo = float(line.split()[8])
srcFid.close()

sDate = dt.datetime(yr, mn, dy, hr, mi, int(se))
eDate = sDate + dt.timedelta(days=366)

DateList = rrule.rrule(rrule.MONTHLY, dtstart=sDate , until=eDate)
ISCdf = pd.DataFrame()

# for date in DateList:

#     dateSplt = str(date.date()).split("-") 
#     dateStr = dateSplt[0] + "-" + str(int(dateSplt[1])) + "-1"

#     csvfN = hdfPath + '/' + dateStr + '.csv'
    
#     csvFid = open(csvfN, 'r')
#     # read csv file and reverse the order as csv files starts from the last day of the month
#     csvRows = csv.reader(csvFid)
    
#     # convert to list
#     csvRowsList = list(csvRows)

#     # get reversed csv rows
#     csvRevRows = list(reversed(csvRowsList[1:]))

#     csvdf = pd.DataFrame(csvRevRows, columns=csvRowsList[0])

#     # remove "T" and "Z"
#     strDateTime = [s.split("T")[0] + " " + s.split("T")[1].split("Z")[0] for s in csvdf["time"]]

#     CSVdateTime = [dt.datetime.strptime(i, '%Y-%m-%d %H:%M:%S.%f') for i in strDateTime]

#     csvdf["time"] = CSVdateTime
    
#     csvdf = csvdf.dropna()
#     # filter for lat lon and time
#     csvdf = csvdf[(csvdf.time > sDate) & (csvdf.time < eDate)]


#     # for i in range(csvdf.shape[0]):
#     #     print '%8.3f   %7.3f' %(float(csvdf.iloc[[i]].longitude), float(csvdf.iloc[[i]].latitude))
#         # plt.scatter(float(csvdf.iloc[[i]].longitude), float(csvdf.iloc[[i]].latitude))

#     ISCdfNew = pd.DataFrame()
#     # loop for polygon region
#     for i in range(len(csvdf['time'])):
#         Ala = float(csvdf.iloc[i]['latitude'])
#         Alo = float(csvdf.iloc[i]['longitude'])
        
#         pt = Point(Alo, Ala)
#         if Poly.contains(pt):
#             ISCdfNew = ISCdfNew.append(csvdf.iloc[[i]])

#     # csvdfN = csvdf[(csvdf.latitude > laMin) & (csvdf.latitude < laMax) & (csvdf.longitude > loMin) & (csvdf.longitude < loMax)]
    
#     ISCdf = ISCdf.append(ISCdfNew[["latitude", "longitude", "depth", "mag", "magType", "time"]])
    
#     csvFid.close()

######################################################################################
csvdf = pd.read_pickle("isc_rev.pkl")
csvdf = csvdf.dropna()
# filter for lat lon and time
csvdf = csvdf[(csvdf.datetime > sDate) & (csvdf.datetime < eDate)]


# for i in range(csvdf.shape[0]):
#     print '%8.3f   %7.3f' %(float(csvdf.iloc[[i]].longitude), float(csvdf.iloc[[i]].latitude))
    # plt.scatter(float(csvdf.iloc[[i]].longitude), float(csvdf.iloc[[i]].latitude))

ISCdfNew = pd.DataFrame()
# loop for polygon region
for i in range(len(csvdf['datetime'])):
    Ala = float(csvdf.iloc[i]['latitude'])
    Alo = float(csvdf.iloc[i]['longitude'])
    
    pt = Point(Alo, Ala)
    if Poly.contains(pt):
        ISCdfNew = ISCdfNew.append(csvdf.iloc[[i]])

# csvdfN = csvdf[(csvdf.latitude > laMin) & (csvdf.latitude < laMax) & (csvdf.longitude > loMin) & (csvdf.longitude < loMax)]

ISCdf = ISCdf.append(ISCdfNew[["latitude", "longitude", "depth", "magnitude", "magnitude_type", "datetime"]])
ISCdf[['magnitude']] = ISCdf[['magnitude']].apply(pd.to_numeric, errors='coerce')
ISCdf = ISCdf.replace(r'^\s*$', np.nan, regex=True)
ISCdf = ISCdf[(ISCdf.magnitude.notnull())]
######################################################################################

#make dict
AScata = dict()
AScata['time'] = list(ISCdf['datetime'])
AScata['mag'] = list(ISCdf['magnitude'])


secInDay = 86400.0
dateTime = AScata['time']
jday1 = dateTime[0].date().timetuple().tm_yday
tm = 0
d = []
for i in range(len(dateTime)):
    jday = dateTime[i].date().timetuple().tm_yday

    tim = dateTime[i].time()
    evSec = tim.hour*3600 + tim.minute*60 + tim.second
    fracSec = evSec/secInDay

    if jday == jday1:
        d.append(tm + fracSec)
    else:
        dysTmp = (dateTime[i].date() - dateTime[i-1].date()).days
        if dysTmp == 0:
            dys = 1
        else:
            dys = dysTmp
        tm += dys
        jday1 = jday
        d.append(tm + fracSec)
    print d[i], jday, dateTime[i]
d = np.array(d)

plt.figure()
plt.xlabel('Days')
plt.ylabel('Mag')
plt.scatter(d, AScata['mag'])
plt.ylim(0,10)
plt.xlim(-5,365)
plt.show()