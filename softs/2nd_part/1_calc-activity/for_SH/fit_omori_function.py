import numpy as np
from scipy.optimize import minimize
import numdifftools as nd

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
    K_err, c_err, p_err = np.sqrt(np.diag(np.linalg.inv(hessian_ndt)))
    
   
    return mu_fit, K_fit, c_fit, p_fit, K_err, c_err, p_err

# Function to calculate Omori parameters
def calcOmori(MUin, Kin, Cin, Pin, t):
    mu, K, c, p, mu_err, K_err, c_err, p_err = [], [], [], [], [], [], [], []
    
    for i in range(len(t)):
        x = LLfit_omori(MUin, Kin, Cin, Pin, np.array(t[i]))
        mu.append(x[0])
        K.append(x[1])
        c.append(x[2])
        p.append(x[3])
        K_err.append(x[4])
        c_err.append(x[5])
        p_err.append(x[6])

    return mu, K, c, p, K_err, c_err, p_err


# MAIN
models = ['R', 'MAS0', 'MAS', 'OOP', 'VM', 'MS', 'VMS']
# initialize parameters
MUin = 5.0
Kin = 1.0
Cin = 0.15
Pin = 0.9

# loop for all models
for model in models:
    omoriT = np.load('omori_times_%s.npy' %(model), allow_pickle=True)
    binned_avg = np.load('%s_binned_avg.npy' %(model), allow_pickle=True)
    
    # fit parameters for
    mu, K1, c, p, K1_err, c_err, p_err = calcOmori(MUin, Kin, Cin, Pin, omoriT)
    
    # columnwise data [binned_average, mu, K, c, p, K_err, c_err, p_err] for R and stress
    columnwise_data = np.column_stack((binned_avg, mu, K1, c, p, K1_err, c_err, p_err))
    
    print(columnwise_data[0])
    

