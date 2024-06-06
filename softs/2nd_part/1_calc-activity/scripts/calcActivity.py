# script to calculate aftershock activity
# by calculating aftershock density in a distance range.
# The distance is calculated from the mainshock.

import numpy as np
import pandas as pd
from astropy.io import ascii
import funcFile
import timeit as ti
from pickle import dump
import normK

Stime = ti.default_timer()

# PATHS ----------------------------------------------------------
combFile = './outputs/new1CombData.pkl'
srcCataFile = './../../1_preProcess/outputs/srcmodCata-less-than-50.txt'
omoriPramFile = './outputs/less-than-50/omoriPrams_err.pkl'
stressDF = './outputs/stressDF'
figDir = './figs/less-than-50'


# PARAMS ---------------------------------------------------------
t_inc = 0.01       # day
T_INC_FACTOR = 1.5
MONTHS = 1
BINSIZE = 7200
dR = 5.0
dS = 0.2
TAGS = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']
models = ['R', 'MAS0', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
MUL_FACTOR = 1e-6    # convert Pa to MPa
L_CUT = [0, -3, -3, -2, 0, 0, 0]
U_CUT = [0, 3, 3, 6, 2, 6, 6]
R_CUT = 200
# initialize parameters
MUin = 5.0
Kin = 1.0
Cin = 0.15
Pin = 0.9

# MAINS ----------------------------------------------------------
# load combData
combDataload = pd.read_pickle(combFile)
combDataload = combDataload.dropna()
print(funcFile.printLoad("Combined data loaded at", Stime))

# load data from srcCata.txt
srcDat = ascii.read(srcCataFile)
print(funcFile.printLoad("SRCMOD catalog loaded in", Stime))

trimmedIds = [x['srcmodId'][:17] for x in srcDat]

srcDat['srcmodId'][:] = trimmedIds

# filter aftershocks above the Mc and Mct values [STEP 1]
combDataTmp = funcFile.filterMc(combDataload, srcDat['srcmodId'])
print(funcFile.printProcess("Mc filter applied at", Stime))

# filter aftershocks for months
combDataTmp2 = funcFile.filterMnths(combDataTmp, MONTHS, srcDat)
print(funcFile.printProcess("Aftershock filtered for %s months at" %(MONTHS), Stime))

# filter under limits
# for i, tag in enumerate(TAGS):
#     if tag == 'R':
#         combDataTmp2 = combDataTmp2[combDataTmp2[tag] <= R_CUT]
#     if tag in TAGS[1:4]:
#         combDataTmp2[tag] = combDataTmp2[tag] * MUL_FACTOR
#     if tag in TAGS[1:]:
#         combDataTmp2 = combDataTmp2[(combDataTmp2[tag] >= L_CUT[i]) & (combDataTmp2[tag] <= U_CUT[i])]

omoriDict = dict()

for i, tag in enumerate(TAGS):
    combData = combDataTmp2.copy()
    
    print(funcFile.printProcess("Working on %s at" %(tag), Stime))
    figPath = '%s/%s' %(figDir, models[i])
    if tag == 'R':
        combData = combData[combData[tag] <= R_CUT]
    if tag in TAGS[1:4]:
        combData[tag] = combData[tag] * MUL_FACTOR
    if tag in TAGS[1:]:
        combData = combData[(combData[tag] >= L_CUT[i]) & (combData[tag] <= U_CUT[i])]
    
    
    # sort data in ascending order
    sortedDat = combData.sort_values(by=[tag], kind='quicksort')

    # calculate event rates
    if tag == 'GF_MAS':
        R_t, t, omoriT, tagAvg, Nobs = funcFile.calcRate1(combData, t_inc, T_INC_FACTOR, dR, dS, tag)
    else:
        R_t, t, omoriT, tagAvg, incFactor, Nobs = funcFile.calcRate(sortedDat, t_inc, T_INC_FACTOR, BINSIZE, tag)
    # R_t, t, omoriT, tagAvg = funcFile.calcRate1(combData, t_inc, T_INC_FACTOR, dR, dS, tag)
    # R_t, t, omoriT, tagAvg = funcFile.calcRateCumm(sortedDat, t_inc, T_INC_FACTOR, dR, dS, tag)
    np.save('./for_SH/omori_times_%s.npy' %(models[i]), omoriT)
    np.save('./for_SH/%s_binned_avg.npy' %(models[i]), tagAvg)
    
    # calculate Omori parameters
    mu, K1, c, p, K1_err, c_err, p_err = funcFile.calcOmori(MUin, Kin, Cin, Pin, omoriT)
    
    omoriDict[models[i]+'R_t'] = R_t
    omoriDict[models[i]+'t'] = t
    omoriDict[models[i]+'omoriT'] = omoriT
    omoriDict[models[i]+'tagAvg'] = tagAvg
    omoriDict[models[i]+'mu'] = mu
    omoriDict[models[i]+'K1'] = K1
    omoriDict[models[i]+'c'] = c
    omoriDict[models[i]+'p'] = p
    # omoriDict[models[i]+'mu_err'] = mu_err
    omoriDict[models[i]+'K1_err'] = K1_err
    omoriDict[models[i]+'c_err'] = c_err
    omoriDict[models[i]+'p_err'] = p_err
    
    # normalize K
    sDF = pd.read_pickle(stressDF+'/stressDF_'+models[i]+'.pkl')

    if tag == 'GF_MAS':
        muu, K, K_err, Nobs_norm = normK.normalizeK(mu, K1, K1_err, tagAvg, tag, dR, dS, sDF, Nobs)
    else:
        muu, K, K_err, Nobs_norm = normK.normalizeK_binned(mu, K1, K1_err, tagAvg, tag, sDF, BINSIZE, incFactor, sortedDat, Nobs)
    omoriDict[models[i]+'K'] = K
    omoriDict[models[i]+'K_err'] = K_err

    # calculate omori time period (max days in each omori times)
    
    T = [max(np.array(tlist)) for tlist in omoriT]
    
    Nexp = normK.expectedN(np.array(muu), np.array(K), np.array(p), np.array(c), np.array(T))
    omoriDict[models[i]+'Nexp'] = Nexp
    omoriDict[models[i]+'Nobs'] = Nobs_norm
    
    # plot one omori
    for j in range(len(t)):
        funcFile.plotOmori(R_t[j], t[j], omoriT[j], mu[j], K1[j], c[j], p[j], tagAvg[j], figPath)

fout = open(omoriPramFile, 'wb')
dump(omoriDict, fout)
fout.close()