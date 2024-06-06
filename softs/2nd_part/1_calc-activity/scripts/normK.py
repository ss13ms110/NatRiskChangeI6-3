import numpy as np
# import matplotlib.pyplot as plt

def normalizeK(mu, K, K_err, tagAvg, tag, dR, dS, sDF, Nobs):
    mu = np.array(mu)
    K = np.array(K)
    K_err = np.array(K_err)
    Nobs = np.array(Nobs)
    
    dd = dS
    tagS = 'stress'
    if tag == 'R':
        dd = dR
        tagS = 'R'

    if tag in ['homo_MAS', 'GF_MAS', 'GF_OOP']:
        sDF[tagS] = sDF[tagS] * 1e-6

    tgMin, tgMax = min(sDF[tagS]), max(sDF[tagS])
    tagRange = np.arange(tgMin, tgMax, dd)

    hist, _ = np.histogram(list(sDF[tagS]), tagRange)

    i = 0
    muu = []
    kk = []
    kk_err = []
    Nobs_norm = []
    for tag1, tag2 in zip(tagRange[:-1], tagRange[1:]):
        indx = (tagAvg>=tag1) & (tagAvg<tag2)
        if indx.any():
            # y.append(hist[i])
            muu = np.append(muu, mu[indx]/hist[i])
            kk = np.append(kk, K[indx]/hist[i])
            kk_err = np.append(kk_err, K_err[indx]/hist[i])
            Nobs_norm = np.append(Nobs_norm, Nobs[indx]/np.float(hist[i]))
        i+=1

    return list(muu), list(kk), list(kk_err), list(Nobs_norm)


def normalizeK_cumm(K, K_err, tagAvg, tag, dR, dS, sDF, Nobs, tagRange):
    K = np.array(K)
    K_err = np.array(K_err)
    Nobs = np.array(Nobs)
    
    dd = dS
    tagS = 'stress'
    if tag == 'R':
        dd = dR
        tagS = 'R'

    if tag in ['homo_MAS', 'GF_MAS', 'GF_OOP']:
        sDF[tagS] = sDF[tagS] * 1e-6

    # tgMin, tgMax = min(sDF[tagS]), max(sDF[tagS])
    
    # tagRange = np.arange(tgMin, tgMax, dd)
    hist, _ = np.histogram(list(sDF[tagS]), tagRange)
    
    j = 0
    kk = []
    kk_err = []
    Nobs_norm = []
    if tag in ['homo_MAS', 'GF_MAS', 'GF_OOP']:
        histL = np.cumsum(hist[hist<0])
        histR = np.cumsum(hist[hist>=0])[::-1]
        histLR = np.concatenate((histL,histR))
        for i in tagRange[:-1]:
            if i < 0:
                indx = (tagAvg<=i)
            else:
                indx = (tagAvg>=i)
            if indx.any():
                kk = np.append(kk, K[indx][-1]/histLR[j])
                kk_err = np.append(kk_err, K_err[indx][-1]/histLR[j])
                Nobs_norm = np.append(Nobs_norm, Nobs[indx][-1]/np.float(histLR[j]))
            j+=1

    else:
        if tag == 'R':
            histR = np.cumsum(hist)
            
        else:
            histR = np.cumsum(hist)[::-1]
        
        for i in tagRange[:-1]:
            if tag == 'R':
                indx = (tagAvg<=i)
                
            else:
                indx = (tagAvg>=i)
            if indx.any():
                
                kk = np.append(kk, K[indx][-1]/histR[j])
                kk_err = np.append(kk_err, K_err[indx][-1]/histR[j])
                Nobs_norm = np.append(Nobs_norm, Nobs[indx][-1]/np.float(histR[j]))
            j+=1   
    
    return list(kk), list(kk_err), list(Nobs_norm)


def normalizeK_binned(mu, K, K_err, tagAvg, tag, sDF, BINSIZE, incFactor, combDat, Nobs):
    mu = np.array(mu)
    K = np.array(K)
    K_err = np.array(K_err)
    Nobs = np.array(Nobs)
    
    tagS = 'stress'
    if tag == 'R':
        tagS = 'R'

    if tag in ['homo_MAS', 'GF_MAS', 'GF_OOP']:
        sDF[tagS] = sDF[tagS] * 1e-6

    tgLen = len(combDat)
    tagRange1 = combDat[tag].iloc[0]

    i = 0
    while i < tgLen:
        
        if i+BINSIZE < tgLen:
            
            tagRange1 = np.append(tagRange1, combDat[tag].iloc[i+BINSIZE-1])
        
        i += BINSIZE
        BINSIZE = int(BINSIZE*incFactor)
        
    tagRange1 = np.append(tagRange1, combDat[tag].iloc[-1])

    
    hist, _ = np.histogram(list(sDF[tagS]), tagRange1)
    
    i = 0
    muu = []
    kk = []
    kk_err = []
    Nobs_norm = []
    for tag1, tag2 in zip(tagRange1[:-1], tagRange1[1:]):
        indx = (tagAvg>=tag1) & (tagAvg<tag2)
        if indx.any():
            muu = np.append(muu, mu[indx]/hist[i])
            kk = np.append(kk, K[indx]/hist[i])
            kk_err = np.append(kk_err, K_err[indx]/hist[i])
            Nobs_norm = np.append(Nobs_norm, Nobs[indx]/np.float(hist[i]))
        i+=1

    return list(muu), list(kk), list(kk_err), list(Nobs_norm)


# function to calculate expected N using Knorm, p, c and T
def expectedN(mu, Knorm, p, c, T):
    return mu*T + (Knorm/(p-1))*(c**(1-p) - (c + T)**(1-p))