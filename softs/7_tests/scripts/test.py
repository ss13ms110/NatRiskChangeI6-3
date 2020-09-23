import numpy as np
import matplotlib.pyplot as plt
from math import ceil, log10

def Nmag(N0, b, M):
    # Nm = N0*10**(-b*M)
    Nm = N0 - b*M
    return Nm

M = np.arange(1, 10, 0.2)
N0 = 100000
b1 = 1
b2 = 0.9
b3 = 0.8

Nm1 = Nmag(N0, b1, M)
Nm2 = Nmag(N0, b2, M)
Nm3 = Nmag(N0, b3, M)

plt.figure()
plt.scatter(M, Nm1, label="%f" %(b1))
plt.scatter(M, Nm2, label="%f" %(b2))
plt.scatter(M, Nm3, label="%f" %(b3))
ylim = ceil(log10(100000))
# plt.yscale('log')
# plt.ylim(0.0001, 10**ylim)
plt.legend()
plt.show()