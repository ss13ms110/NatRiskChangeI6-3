# Date: 28.02.2020
# This script create mainshock-wise aftershock catalog files
# input: srcmodCata.txt, isc_eve.pkl
# variable: time duration 'td' [e.g. 365]
# output: aftershock catalog files named by unique IDs

import numpy as np
import pandas as pd

# functions

#mains
# paths
srcmodCata = './srcmodCata.txt'
iscEvents = './isc_eve.pkl'

# variables
td = 365
