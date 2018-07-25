# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 13:50:22 2018

@author: Administrator
"""

import os
import numpy as np
import pandas as pd
import autobase as ab

def check(csvpath):
    binpath = csvpath.replace("csv","bin")
    csvdf = pd.read_csv(csvpath)
    if os.path.getsize(binpath):
        bindf = bindf = pd.DataFrame(ab.objects.read_kline_from_file(binpath))
    else:
        log.write("Binary file doesn't exist.\n")
        return
    
    bindf = bindf[["code","time","close","open","high","low","volume","value"]]
    csvdf = csvdf[["stkcd","time","close","open","high","low","volume","value"]]
    
    # deal with the IF code
    end = len(bindf)
    for i in range(len(bindf)):
        if bindf["code"][i][0:2].decode("ascii")=="IF":
            end = i
            break
    bindf = bindf[:end]
    
    tmp = []
    tmpp = []
    # csvdf.to_csv("csvdf.csv")
    # bindf.to_csv("bindf.csv")
    for i in range(len(bindf)):
        tmp.append(bindf["code"][i][:9].decode("ascii"))
        if(bindf["time"][i] == 145900):
            tmpp.append(150000)
        elif(bindf["time"][i] == 112900):
            tmpp.append(113000)
        else:
            tmpp.append(bindf["time"][i+1])

    bindf = bindf.drop(["code","time"],axis=1)
    bindf["stkcd"] = tmp
    bindf["time"] = tmpp
    csvdf["volume"] = csvdf["volume"]/10000
    csvdf["value"] = csvdf["value"]/10000
    
    result = pd.merge(csvdf,bindf,on=["stkcd","time"],how="right")
    #记录csv中没有而bin中有的stkcd
    result = result[np.isnan(result["close_x"])]
    result = result[result["value_y"]!=0]
    vacantright = result["stkcd"].unique()

    vac.write("bin has but cvs doesn't: \n")
    for j in vacantright:
        if j[0:3]!="399":
            log.write(j+"\n")
    result = pd.merge(csvdf,bindf,on=["stkcd","time"],how="left")
    #记录csv中没有而bin中有的stkcd

    result = result[np.isnan(result["close_y"])]
    result = result[result["value_x"]!=0]
    vacantleft = result["stkcd"].unique()

    vac.write("csv has but bin doesn't: \n")
    for j in vacantleft:
        log.write(j+"\n")

    result = pd.merge(csvdf,bindf,on=["stkcd","time"])
    valuesum = sum(result["value_x"])-sum(result["value_y"])
    volumesum = sum(result["volume_x"])-sum(result["volume_y"])

    log.write("value total error:"+str(valuesum)+"\n")
    log.write("volume total error:"+str(volumesum)+"\n")
    
    if valuesum > 1 & volumesum > 1:
        log.write("value and volume data isn't correct!")
    else:
        log.write("value and volume data doesn't have problem.")
        
    for i in range(len(result)):
        open = comp1(result["open_x"][i],result["open_y"][i])
        if open:
            log.write(result["stkcd"][i]+" "+result["time"][i].astype(str)+" open"+" Err: "+str(open)+"\n")
        close = comp1(result["close_x"][i], result["close_y"][i])
        if close:
            log.write(result["stkcd"][i]+" "+result["time"][i].astype(str)+" close"+" Err: "+str(close)+"\n")
        high = comp1(result["high_x"][i], result["high_y"][i])
        if high:
            log.write(result["stkcd"][i] + " " + result["time"][i].astype(str) + " high" + " Err: "+str(high)+"\n")
        low = comp1(result["low_x"][i], result["low_y"][i])
        if low:
            log.write(result["stkcd"][i] + " " + result["time"][i].astype(str) + " low" + " Err: "+str(low)+"\n")
    
    log.write("\n")
    
if __name__ == "__main__":
    '''
    determine the date that needs checking
    '''
    csvpath = "/data/stock/1min_csv/2018/01/1min_20180104.csv"
    log_file = "20180104.txt"
    with open(log_file,'w') as log:
        log.write(str(date)+"\n")
        check(csvpath)