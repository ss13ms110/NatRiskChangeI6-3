## Task manager for this project

| Sr.  	| Test  	| Itr  	| Dir  	            | Status  	| Figure    |
|---	|---	    |---	|---	            |---	    |---        |
| 1  	| GRTest  	| 100   | itr_100/bin_100  	| Done      | Done      |
| 2  	| GRTest  	| ''    | itr_100/bin_300  	| Done  	| Done      |
| 3  	| GRTest  	| ''    | itr_100/bin_500  	| Done      | Done      |
| 4  	| GRTest  	| 500   | itr_500/bin_100  	| Done  	| Done      |
| 5  	| GRTest  	| ''    | itr_500/bin_300  	| Done  	| Done      |
| 6  	| GRTest  	| ''    | itr_500/bin_500  	| Done      | Done      |
|_______|___________|_______|___________________|___________|___________|
| 7  	| binNum  	| 100   | itr_100/bin_200  	| Done      | Done      |
| 8  	| binNum  	| ''    | itr_100/bin_800  	| Done  	| Done      |
| 9  	| binNum  	| 500   | itr_500/bin_200  	| Done  	| Done      |
| 10  	| binNum  	| ''    | itr_500/bin_800  	| Done  	|           |
|_______|___________|_______|___________________|___________|___________|
| 11  	| All  	    | 1000 	| All/bin_100    	|   	    |           |
| 12  	| All     	| ''  	| All/bin_300	    |           |           |
| 13  	| All     	| ''  	| All/bin_500    	|           |           |
|_______|___________|_______|___________________|___________|___________|
| 14  	| distStrs 	| 500  	| RVsStress/bin_100 | Done      |    -      |
| 15  	| distStrs 	| ''  	| RVsStress/bin_300	| Done      |    -      |
| 16  	| distStrs 	| ''  	| RVsStress/bin_500	| Done      |    -      |


## Testing Plots
1. plot b-Val Vs R with MC examples with different colors
2. plot number of points Vs R (tag)

### Len Test and 3egTest  
| Sr.  	| Test  	| Itr  	| Dir  	            | Status  	| Figure    |
|---	|---	    |---	|---	            |---	    |---        |
| 1  	| lenTest  	| 500   | itr_500/bin_100  	| Done      | Done      |
| 2  	| lenTest  	| ''    | itr_500/bin_500  	| Done  	| Done      |
| 3  	| lenTest  	| 1000  | itr_1000/bin_100 	| DOne      | Done      |
| 4  	| lenTest  	| ''    | itr_1000/bin_500 	| Done      | DOne      |
|_______|___________|_______|___________________|___________|___________|

# Notes  
Error bars  
bootstraping  
log distance plots  
make GR map for bins  
make inset plot for stress vs distance  
make plots for larger binSize  
calculate difference to Mc vs # of events  
verify bath's law  
how many events in each stress bin  
correction for Mc and Mct  
equidistant bins  

Make different plots for b-Value Vs Stress  

NEW
Use maximum of Mmain - Mw

## working after 7-08-2020
1. CUmulative plots with Mm-Mmax to be max(cata)
2. output in ./outputs/MC/cummTest

# make plot by going through each sequence and look for largest aftershock with stress 
also plot non-cumulative values in background [DONE]

# for calculating new VM stress
VM_1 ---> std = (25, 25, 25, 0.1)    Nsample = 1500    
          CFSn = CFS[(CFS>0.0)]
          svm.append(np.sum(CFSn)/(len(CFSn)))
          combData_1.pkl


VM_2 ---> std = (20, 20, 20, 0.1)    Nsample = 1500    
          CFSn = CFS[(CFS>0.0)]
          svm.append(np.sum(CFSn)/(len(CFSn)))
          combData_2.pkl

VM_3 ---> std = (30, 30, 30, 0.1)    Nsample = 1500
          CFSn = CFS[(CFS>0.0)]
          svm.append(np.sum(CFSn)/(len(CFSn)))
          combData_3.pkl
        
VM_OLD ---> td = (25, 25, 25, 0.1)    Nsample = 1500    
            svm.append(np.sum(CFS[(CFS>0.0)])/(float(Nsample)))
            combData.pklOLD

VM_4 ---> std = (30, 30, 30, 0.1)    Nsample = 1500
          svm.append(np.sum(CFS[(CFS>0.0)])/(float(Nsample)))       Running
          combData_3.pkl

# DATE: 25-08-2020 [NEW TASK]
1. increment R with 100/500 bins and calculate b-value [MC_Rinc.py]
2. make mag vs stress vs distance plot [magVsStressVsR.py]

-----------------------------------------------------------------------------------------------
# MEETING 26-08-2020 [MINUTES]   [[[ 7_tests ]]]                                                           ----
1. try calculating R in different ways (5%, 10%, excluding 0 slips)                        ----
2. get freq-mag distribution before and after the kink (say <5k and >10 km)                ----
3. plot histograms for all-stress values and stress values of max mag aftershocks          ----
4. point 3 for distance                                                                    ----
-----------------------------------------------------------------------------------------------

# TO-DO
1. R calculation by excluding 0 slip patches [t1]
    combData_7_1.pkl
    binsize = 300
    mnths = 3 and 1 [3 mnth good]

2. freq-mag distribution before and after the kink
    MC_months.py with extracting data for GR plot
    * plots generated with events upto <0.7 - <3.3 [GRplot_1.png]   |
                                       <1.4 - <3.3 [GRplot_2.png]   | [obsolete]
                                       <2 - <3.3 [GRplot_3.png]     |
                                       <2.7 - <3.3 [GRplot_4.png]   |
    * plots for cuts: [GRplot_new.png] end-cut GR plots
                    mcL = [5, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
                    lcL = [0, -1.5, -2.5, -0.5, 0, 0, 0]
                    ucL = [120, 1.5, 2.0, 4.0, 1.2, 2.5, 4.2]

3. Histograms: a combined plot with separate histogram of all aftershocks and aftershocks with maximum stress.
4. RvS plots generated and found too high stress values for larger distances. So, moving on for next analysis
    to check which events are causing this

# Date - 15-90-2020
1. Generate Temp stress maps for mainshocks where stress > 0.5 MPa is found in a distance of 119 to 120 km [t2]

# PROBLEM
1. A problem has been found with the displacement of location arrays in CombData script. has been temporarily fixed
    * new combData output file name `combData_7_2.pkl`


# TRY [8_Single]
1. Calculate b-value vs stress, R only for one event [s2011TOHOKU02GUSM]

# uniqCombData [files stored in 7_tests/outputs/bVal]
1. only unique events are used

# newCombdata [newSrcmodCata.txt, newCombData_7_2.pkl]

# *************************************************************************************************************
#                                           NEW TEST
# *************************************************************************************************************
# ___Generate stress values only for aftershock lat-lons using PSCRN+PSCMP___
1. working directory [9_test]
