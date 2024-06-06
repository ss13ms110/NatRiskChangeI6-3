# Python code to calculate the percentage of 
# aftershocks occuring in negative stress region 
# of MAS and OOP

import pandas as pd
import numpy as np
import funcFileMC as funcFile
import timeit as ti

Stime = ti.default_timer()


#PATHS
combFile = './../9_test/outputs/CombData_9-3.pkl'
McValueFile = './../2_McCalc/outputs/Mc_MAXC_1Yr.txt'

# PARAM
metric = 'GF_OOP'

#  load combData
combDataload = pd.read_pickle(combFile)
print(funcFile.printLoad("Combined data loaded at", Stime))


# filter aftershocks above the Mc and Mct values [STEP 1]
combDataTmp = funcFile.filterMc(combDataload, McValueFile)
print(funcFile.printProcess("Mc filter applied at", Stime))

metric_data = combDataTmp[metric].to_numpy()

tot = len(metric_data)
neg_tot = len(metric_data[metric_data<0])
pos_tot = len(metric_data[metric_data>=0])
per_neg = (neg_tot/tot)*100

print('Metric: {}'.format(metric))
print('Total number of aftershocks: {:}\nNegative Stress \
region aftershocks: {:}\nPositive stress region aftershocks: {:}\n\
Percentage of aftershocks in negative region: {:6.3f}%'.format(tot, neg_tot, pos_tot, per_neg))
