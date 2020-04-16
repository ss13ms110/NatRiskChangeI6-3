import numpy as np
import matplotlib.pyplot as plt
import funcFile




a=0.2
b=1

x1=np.linspace(-100,100,10000)
x2=np.linspace(0,200,10000)

sigval1 = funcFile.sigmoid(x1, a, 0)

sigval2 = funcFile.sigmoid(x2, a, 5)

plt.figure()
plt.scatter(x1, sigval1, label="11")
plt.scatter(x2,sigval2, label="22")
plt.legend()
plt.ylim(0,1)
plt.xlim(-100,200)
plt.show()