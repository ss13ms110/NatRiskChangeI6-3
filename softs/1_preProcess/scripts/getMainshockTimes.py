# Date: 27.02.2020
# This script get excat time of SRCMOD mainshocks from ISC events catalog
# yearwise ISC catalog files are in HDF format
# output is 'srcmodCata.txt'
# Header: 'Origin-time(yr jday mn dy hr min sec)	lat	lon	depth	mag	srcmodID'


import numpy as np
import datetime

# function
# def readFile(fname):
# 	fid=open(fname, 'r')
# 	isol = []
# 	fData = []
# 	for line in fid:
# 		isol.append(str(line[1:4]))
# 		mnF = int(line[9:11])
# 		dyF = int(line[12:14])
# 		hrF = int(line[16:18])
# 		minF = int(line[19:21])
# 		secF = float(line[22:27])
# 		latF = float(line[29:36])
# 		lonF = float(line[36:44])
# 		depF = float(line[51:56])
# 		mb = float(line[57:60])
# 		Mw = float(line[65:68])
		
# 		#print mnF, dyF, hrF, minF, secF, latF, lonF, depF, mb, Mw
	
# 	return "ss"
	
	
# sort
def Sort(sub_li): 
    sub_li.sort(key = lambda x: x[3]) 
    return sub_li 

# open catalogue

fcata = open('srcmodEvents.txt', 'r')
hdfPath = '../../../raw_data/isc_data/hdf_files'
fevent = open('srcmodCata.txt', 'w')
fnoEq = open('noEq.data', 'w')
latTol = 0.8
lonTol = 0.8

fevent.write('     Origin-time      Lat      Lon      Dp      Mag\n')

for line in fcata:
	yr = int(line.split()[2])
	mn = int(line.split()[1])
	dy = int(line.split()[0])
	lat= float(line.split()[3])
	lon= float(line.split()[4])
	dep= float(line.split()[5])
	mag= float(line.split()[6])
	fileN = line.split()[7]

	date = '%4d-%02d-%02d' %(yr, mn, dy)
	fname = hdfPath + '/' + str(yr) + '.hdf'

	fid = open(fname, 'r')

	dayRow = []
	for lineF in fid:
		mnF = int(lineF[9:11])
		dyF = int(lineF[12:14])

		dateF = '%4d-%02d-%02d' %(yr, mnF, dyF)

		if dateF == date:
			latF = float(lineF[29:36])
			lonF = float(lineF[36:44])


			if latF >= lat-latTol and latF <= lat+latTol and lonF >= lon-lonTol and lonF <= lon+latTol:
				mb = float(lineF[57:60])
				Mw = float(lineF[65:68])
				hrF = int(lineF[16:18])
				minF = int(lineF[19:21])
				secF = float(lineF[22:27])
				
				if Mw != 0:
					magF = Mw
				else:
					magF = mb
				dayRow.append([hrF, minF, secF, magF])
				
	fid.close()

	if dayRow:
		
		Eq_Row = Sort(dayRow)[-1]

		hr = int(Eq_Row[0])
		mi = int(Eq_Row[1])
		se = int(Eq_Row[2])

		# julian day
		dtt = datetime.datetime(yr, mn, dy)
		jday = dtt.timetuple().tm_yday

		fevent.write('%4d (%03d) %02d %02d %02d %02d %05.2f  %8.3f  %8.3f %6.1f %4.1f %4d%03d%02d%02d%02d  %s\n' %(yr, jday, mn, dy, hr, mi, se, lat, lon, dep, mag, yr,jday,hr,mi,int(float(se)), fileN))	


	else:
		fnoEq.write('%s' %(line))
fevent.close()
fnoEq.close()
fcata.close()
    
    
    
    
    
    

