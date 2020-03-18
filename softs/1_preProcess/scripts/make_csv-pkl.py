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
import csv


#MAIN
# paths
hdfPath = '../../../raw_data/isc_data/1900-2019_csv'
RAWpklFile = 'isc_events_inc-NaN.pkl'
pklFile = 'isc_events.pkl'
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
    dateStr = dateSplt[0] + "-" + str(int(dateSplt[1])) + "-" + str(int(dateSplt[2]))
    
    csvfN = hdfPath + '/' + dateStr + '.csv'
    
    # check for the presence of one event
    with open(csvfN) as f:
        Nl = sum(1 for line in f)
    
    f.close()
    if Nl > 1:
        csvFid = open(csvfN, 'r')
        # read csv file and reverse the order as csv files starts from the last day of the month
        csvRows = csv.reader(csvFid)

        # convert to list
        csvRowsList = list(csvRows)

        # get reversed csv rows
        csvRevRows = list(reversed(csvRowsList[1:]))

        csvdf = pd.DataFrame(csvRevRows, columns=csvRowsList[0])
        
        # remove "T" and "Z"
        strDateTime = [s.split("T")[0] + " " + s.split("T")[1].split("Z")[0] for s in csvdf["time"]]

        CSVdateTime = [dt.datetime.strptime(i, '%Y-%m-%d %H:%M:%S.%f') for i in strDateTime]

        csvdf["time"] = CSVdateTime

        # replace "reviewed" in status with "1"
        csvdf.loc[csvdf["status"] == "reviewed", "status"] = 1
        csvdf.loc[csvdf["status"] == "automatic", "status"] = 0

        df = df.append(csvdf[["status", "latitude", "longitude", "depth", "mag", "magType", "time"]])

df.to_pickle(RAWpklFile)

# quality filtering
# convert strings to numbers
df[['mag', 'depth', 'latitude', 'longitude']]=df[['mag', 'depth', 'latitude', 'longitude']].apply(pd.to_numeric, errors='coerce')

# drop NaNs
dfNew = df.dropna()
dfNew.to_pickle(pklFile)