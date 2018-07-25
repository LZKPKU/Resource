import pandas as pd
import numpy as np
import autobase as ab
import os

year = ["2012"]
month = ["01"]

#, "04", "05", "06", "07", "08", "09", "10", "11", "12"]
#year = ["2018"]
#month = ["01", "02", "03", "04", "05","06","07"]
def comp1(a, b):
    thes = 0.05
    avg = (a + b) / 2
    if avg != 0:
        rerr = abs(a - b) / avg
        if rerr > thes:
            return rerr
        else:
            return 0
    else:
        return 0

def F(csvpath,mode):
    name = csvpath[-12:-4]
    year = csvpath[-12:-8]
    month = csvpath[-8:-6]
    print(name+"\n")
	
    if mode:
        binpath = csvpath
        binpath = binpath.replace("csv","bin")
    else:
        #binpath = "2017newbin/" + month + "/" + "1min_" + name + ".bin"
        binpath = "1min_bin/" + year + "/" + month + "/" + "1min_" + name + ".bin"
    if os.path.getsize(binpath):
        bindf = pd.DataFrame(ab.objects.read_kline_from_file(binpath))
    else:
        print("This file is empty!\n\n")
        return 
    csvdf = pd.read_csv(csvpath)

    bindf = bindf[["code","time","close","open","high","low","volume","value"]]
    csvdf = csvdf[["stkcd","time","close","open","high","low","volume","value"]]

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
            print(j+"\n")
    result = pd.merge(csvdf,bindf,on=["stkcd","time"],how="left")
    #记录csv中没有而bin中有的stkcd

    result = result[np.isnan(result["close_y"])]
    result = result[result["value_x"]!=0]
    vacantleft = result["stkcd"].unique()

    print("csv has but bin doesn't: \n")
    for j in vacantleft:
        vac.write(j+"\n")

    result = pd.merge(csvdf,bindf,on=["stkcd","time"])
    valuesum = sum(result["value_x"])-sum(result["value_y"])
    volumesum = sum(result["volume_x"])-sum(result["volume_y"])

    print("value total error:"+str(valuesum)+"\n")
    print("volume total error:"+str(volumesum)+"\n")

    for i in range(len(result)):
        open = comp1(result["open_x"][i],result["open_y"][i])
        if open:
            print(result["stkcd"][i]+" "+result["time"][i].astype(str)+" open"+" Err: "+str(open)+"\n")
        close = comp1(result["close_x"][i], result["close_y"][i])
        if close:
            print(result["stkcd"][i]+" "+result["time"][i].astype(str)+" close"+" Err: "+str(close)+"\n")
        high = comp1(result["high_x"][i], result["high_y"][i])
        if high:
            print(result["stkcd"][i] + " " + result["time"][i].astype(str) + " high" + " Err: "+str(high)+"\n")
        low = comp1(result["low_x"][i], result["low_y"][i])
        if low:
            print(result["stkcd"][i] + " " + result["time"][i].astype(str) + " low" + " Err: "+str(low)+"\n")
    print("\n")
	
if __name__ == "__main__":
    date = input("Please input the date:\n")
	year = date[:4]
	month = date[4:6]
    PATH = "/data/stock/1min_csv/"+year+"/"+month+"/1min_"+date+".csv"
    F(csvpath,0)
    print(csvpath+'\n')      
        