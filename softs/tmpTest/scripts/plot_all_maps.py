import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

combDataFle = './../9_test/outputs/CombData_9-3.pkl'
polys = './../2_McCalc/outputs/polys'

# read file
combData = pd.read_pickle(combDataFle)
mainID = combData['MainshockID'].unique().tolist()

for id in mainID:
    print('working on ', id)
    poly = np.loadtxt(polys+'/'+id+'.poly')
    plt.figure(figsize=(8,8))
    data0 = combData[combData['MainshockID'] == id]
    data1 = data0[data0['R'] > 120]
    data120 = data0[data0['R'] <= 120]
    plt.plot(poly[:,0], poly[:,1], color='black')
    plt.scatter(data1['longitude'], data1['latitude'], color='green', s=2**4)
    plt.scatter(data120['longitude'], data120['latitude'], color='red', s=2**3)

    plt.savefig('./figs/maps/'+id+'.png')
    plt.close()