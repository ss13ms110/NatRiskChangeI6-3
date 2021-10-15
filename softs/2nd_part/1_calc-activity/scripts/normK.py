import numpy as np
import matplotlib.pyplot as plt
def normalizeK(K, tagAvg, tag, dR, dS, sDF):
    K = np.array(K)
    
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
    kk = []
    for tag1, tag2 in zip(tagRange[:-1], tagRange[1:]):
        indx = (tagAvg>=tag1) & (tagAvg<tag2)
        if indx.any():
            # y.append(hist[i])
            kk = np.append(kk, K[indx]/hist[i])
        i+=1

    return list(kk)

def normalizeK_binned(K, tagAvg, tag, dR, dS, sDF, BINSIZE, incFactor, combDat):
    K = np.array(K)
    
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
            
            tagRange1 = np.append(tagRange1, combDat[tag].iloc[i+BINSIZE])

        i += BINSIZE
        BINSIZE = int(BINSIZE*incFactor)
    tagRange1 = np.append(tagRange1, combDat[tag].iloc[-1])

    
    hist, _ = np.histogram(list(sDF[tagS]), tagRange1)
    
    i = 0
    kk = []
    for tag1, tag2 in zip(tagRange1[:-1], tagRange1[1:]):
        indx = (tagAvg>=tag1) & (tagAvg<tag2)
        if indx.any():
            kk = np.append(kk, K[indx]/hist[i])
        i+=1

    return list(kk)


# function to calculate expected N using Knorm, p, c and T
def expectedN(Knorm, p, c, T):
    return (Knorm/(p-1))*(c**(1-p) - (c + T)**(1-p))