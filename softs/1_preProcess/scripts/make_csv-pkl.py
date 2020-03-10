# Date: 03.03.2020
# This script make pkl file of all events by compiling all csv files
# input: all csv files (here: 1900-2018)
# output: isc_events_inc-NaN.pkl [this includes all NaN values as well]
# Header: ['status', 'latitude', 'longitude', 'depth', 'magnitude', 'magnitude_type', 'time']
# 'status' is 1 for reviewed and 0 for automatic

import numpy as np
import pandas as pd
from dateutil import rrule
import datetime as dt


#MAIN
# paths
hdfPath = '../../../raw_data/isc_data/1900-2019_csv'
pklFile = 'isc_events_inc-NaN.pkl'
sYr = 1900
sMn = 1
sDy = 1
stDate = dt.datetime(sYr, sMn, sDy)

eYr = 2018
eMn = 12
eDy = 31
eHr = 23
eMi = 59
eSe = 59
enDate = dt.datetime(eYr, eMn, eDy, eHr, eMi, eSe)

DateList = rrule.rrule(rrule.MONTHLY, dtstart=stDate , until=enDate)



df = pd.DataFrame()
for date in DateList:
    dateSplt = str(date.date()).split("-") 
    dateStr = dateSplt[0] + "-" + dateSplt[1].replace("0","") + "-" + dateSplt[2].replace("0","")

    csvfN = hdfPath + '/' + dateStr + '.csv'

    csvdf = pd.read_csv(csvfN)

    # remove "T" and "Z"
    strDateTime = [s.split("T")[0] + " " + s.split("T")[1].split("Z")[0] for s in csvdf["time"]]

    CSVdateTime = [dt.datetime.strptime(i, '%Y-%m-%d %H:%M:%S.%f') for i in strDateTime]

    csvdf["time"] = CSVdateTime

    # replace "reviewed" in status with "1"
    csvdf.loc[csvdf["status"] == "reviewed", "status"] = 1
    csvdf.loc[csvdf["status"] == "automatic", "status"] = 0

    df = df.append(csvdf[["status", "latitude", "longitude", "depth", "mag", "magType", "time"]])

df.to_pickle(pklFile)


# in order to remove NaN values from the pkl file use 
# df = pd.read_pickle('isc_events_inc-NaN.pkl')
# dfNew = df.dropna()
# dfNew.to_pickle('isc_events.pkl')