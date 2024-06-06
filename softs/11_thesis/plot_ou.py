# This script uses MAXC method of Wiemer and Wyss 2000
# to estimate Mc and MLE to estimate b-value
# Input: 'srcmodCata.txt' and 'isc_events.pkl'
# Output: Mc_MAXC_1Yr.txt
# Header: ['fileName', 'StartTime', 'latitude', 'longitude', 'Mc', 'b-value', 'b-err', 'a-value', 'a-err']

import numpy as np
import pandas as pd
import funcFile
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import numdifftools as nd
from scipy.optimize import minimize



# FUNCTIONS
# For coloured outputs in terminal
class bcol:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# -----------------------OMORI support functions -------------------------
def omoriRate(t, mu, K, c, p):
    return mu + K/(c + t)**p

def funcOmori(args, t_1, T1, T2):
    """ LL calculated using Omori, 1983. Assuming background rate 0"""
    mu1 = np.square(args[0])
    K1 = np.square(args[1])
    c1 = np.square(args[2])
    p1 = np.square(args[3])

    Rintegrated = mu1*(T2 - T1)
    

    if p1 == 1.0:
        Rintegrated += K1 * (np.log(c1 + T2) - np.log(c1 + T1))
    
    else:
        Rintegrated += (K1/(1.0-p1)) * ((c1+T2)**(1.0-p1) - (c1+T1)**(1.0-p1))

    sumLogR = np.sum(np.log(omoriRate(t_1, mu1, K1, c1, p1)))

    LL = sumLogR - Rintegrated

    return -LL

def funcOmori_nonSqr(args, mu1, t_1, T1, T2):
    """ LL calculated using Omori, 1983. Assuming background rate 0"""
    K1 = args[0]
    c1 = args[1]
    p1 = args[2]

    Rintegrated = mu1*(T2 - T1)

    if p1 == 1.0:
        Rintegrated += K1 * (np.log(c1 + T2) - np.log(c1 + T1))
    
    else:
        Rintegrated += (K1/(1.0-p1)) * ((c1+T2)**(1.0-p1) - (c1+T1)**(1.0-p1))

    sumLogR = np.sum(np.log(omoriRate(t_1, mu1, K1, c1, p1)))

    LL = sumLogR - Rintegrated

    return -LL


def LLfit_omori(MUin, Kin, Cin, Pin, t_1):
    T1, T2 = min(t_1), max(t_1)

    x0 = [np.sqrt(MUin), np.sqrt(Kin), np.sqrt(Cin), np.sqrt(Pin)]

    res = minimize(funcOmori, x0, args=(t_1, T1, T2), method='Powell')

    sqrtMU, sqrtK, sqrtC, sqrtP = res.x

    mu_fit = np.square(sqrtMU)
    K_fit = np.square(sqrtK)
    c_fit = np.square(sqrtC)
    p_fit = np.square(sqrtP)

    hessian_ndt, info = nd.Hessian(funcOmori_nonSqr, method='complex', full_output=True)((K_fit, c_fit, p_fit), mu_fit, t_1, T1, T2)
    print(info)
    K_err, c_err, p_err = np.sqrt(np.diag(np.linalg.inv(hessian_ndt)))
    
    return mu_fit, K_fit, c_fit, p_fit, K_err, c_err, p_err

# Function to calculate Omori parameters
def calcOmori(t):
    MUin = 5.0
    Kin = 1.0
    Cin = 0.15
    Pin = 0.9
    mu, K, c, p, mu_err, K_err, c_err, p_err = [], [], [], [], [], [], [], []
    
    x = LLfit_omori(MUin, Kin, Cin, Pin, np.array(t))
    mu.append(x[0])
    K.append(x[1])
    c.append(x[2])
    p.append(x[3])
    K_err.append(x[4])
    c_err.append(x[5])
    p_err.append(x[6])

    return mu, K, c, p, K_err, c_err, p_err

def plotOmori(rate, t, mu, K, c, p):
    
    omoriR = omoriRate(t, mu, K, c, p)
    omoriR[0] = rate[0]
    plt.figure()
    plt.scatter(t, rate, marker='o', c='black', s=4, label='Observed rate')
    plt.plot(t, omoriR, color='red', linewidth=2, label="OU-law fit\n" + r'$\lambda(t)={%5.1f}/(t+%3.1fe-%02d)^{%4.2f}$'%(K[0], 5.4, 9, p[0]))
    # plt.xscale('log')
    # plt.yscale('log')
    plt.xlabel('Days')
    plt.ylabel('Rate ' + r'$(\lambda)$' + ' (N/day)')
    # plt.title('Omori law fit for %s_Avg = %6.2f\n mu = %5.2f  K = %03d  c = %4.2f  p = %4.2f' %(figPath.split('/')[-1], tagAvg, mu, K, c, p))
    plt.legend()
    plt.savefig('%s/omoriFit_(%s).png' %('./', 'ou_fit'), dpi=400, bbox_inches = 'tight')
    # plt.close()
    


def calcRate(t):
    t_bins = 100       # day    
    # calculate rate
    hist, edges = np.histogram(t, t_bins)
    rate = hist/(edges[1:]-edges[:-1])
    tmid = (edges[1:]-edges[:-1])/2.
    return rate, tmid



# MAINS

# Path
srcmodPath = '/home/rebhu-dev-l1/Work/NRC/raw_data/srcmod/srcmod_fsp_2019Mar'
srcmodCata = './srcmodCata.txt'
iscPkl = './../1_preProcess/outputs/isc_events.pkl'
McFigsPath = './'


# parameters
dT = 90          # 1 year
Hdist = 100     # km
dHdist = 5
Vdist = 50      # depth of volume (km)
dVdist = 5
binSize = 0.2
McBuff = 0.2
lbl = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)', '(g)', '(h)']
lbl1 = ['(a\')', '(b\')', '(c\')', '(d\')', '(e\')', '(f\')', '(g\')', '(h\')']

plt.rc('font', family='sans-serif')
plt.rc('font', size=14)
plt.rc('legend', fontsize=12)
font = font_manager.FontProperties(family='monospace',
                                   weight='normal',
                                   style='normal', size=14)
# load pkl file in memory
ISCdf = pd.read_pickle(iscPkl)
print(bcol.OKGREEN+"Pickle file loaded...\n" + bcol.ENDC)

# open mainshock catalog
srcmodFid = open(srcmodCata, 'r')


for ii,line in enumerate(srcmodFid):
    srcmodFlN = line.split()[12]
    Yr = int(line.split()[0])
    Mn = int(line.split()[2])
    Dy = int(line.split()[3])
    Hr = int(line.split()[4])
    Mi = int(line.split()[5])
    Se = float(line.split()[6])
    la = float(line.split()[7])
    lo = float(line.split()[8])
    Mw = float(line.split()[10])

    eq_label = '$M_w$ = %3.1f\nDatetime: %02d-%02d-%04d %02d:%02d:%02d\nLocation: %8.3f, %8.3f' %(Mw, Dy, Mn, Yr, Hr, Mi, Se, lo, la)
    
    print(bcol.OKBLUE + "Working on %s..." %(srcmodFlN.split(".")[0]) + bcol.ENDC)
   
    # get polygon buffer around the mainshock fault
    slpFile = srcmodPath + '/' + srcmodFlN
    xBuffer, yBuffer, polyBuffer = funcFile.getBuffer(slpFile, Hdist)

    # buffered list of aftershocks in the polygon region and within given time frame
    sDate = dt.datetime(Yr, Mn, Dy, Hr, Mi, int(Se)) + dt.timedelta(seconds=1)   # 1 second after the mainshock
    eDate = sDate + dt.timedelta(days=dT) - dt.timedelta(seconds=1)     # sTime + time duration (e.g. 
                                                                        # 365) - 1 second to be within 
                                                                        # time duration
    AScata, resp = funcFile.getISCcata(ISCdf, sDate, eDate, polyBuffer)
    print(resp)
    # check for the length of aftershock catalog
    if resp == 1:    
        #----------------------------------
        # calculate Mc
        #----------------------------------

        # get days distribution of aftershocks
        ASdays = funcFile.getDays(AScata)
        
        hist, edges = np.histogram(ASdays, 150)
        
        rate = hist/(edges[1:]-edges[:-1])
        tmid = (edges[1:]+edges[:-1])/2
        
        
        mu, K, c, p, K_err, c_err, p_err = calcOmori(ASdays)
        print(mu, K, c, p)
        plotOmori(rate, tmid, mu, K, c, p)
        
        
        
