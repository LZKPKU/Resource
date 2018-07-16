import pandas as pd
import numpy as np
import autobase as ab
import os
'''
find the dates where there is a csv file while isn't a bin file
'''

def F(csvpath):
    name = csvpath[-12:-4]

    binpath = csvpath
    binpath = binpath.replace("csv","bin")
    if os.path.getsize(binpath):
        bindf = pd.DataFrame(ab.objects.read_kline_from_file(binpath))
    else:
        result.write(name + "This file is empty!\n\n")
        return
    csvdf = pd.read_csv(csvpath)
    end = 0
    for i in range(len(bindf)):
        if bindf["code"][i][0:2].decode("ascii") == "IF":
            end = i
            break
    bindf = bindf[:end]

    binrow1 = bindf.shape[0]/240
    binrow2 = bindf["code"].unique().shape[0]
    if not binrow1==binrow2:
        result.write(name+"bin "+str(binrow1)+" "+str(binrow2)+"\n\n")
    csvrow1 = csvdf.shape[0]/240
    csvrow2 = csvdf["stkcd"].unique().shape[0]
    if not csvrow1==csvrow2:
        result.write(name+"csv "+str(csvrow1)+" "+str(csvrow2)+"\n\n")
        
if __name__ == "__main__":
    year = ["2010","2011","2012"]
    month = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    for i in year:
        resultpath = "result"+i+".txt"
        result = open(resultpath,'w')
        for j in month:
            PATH = "/data/stock/1min_csv/" + i + "/" + j + "/"
            for m in sorted(os.listdir(PATH)):
                csvpath = PATH + m
                F(csvpath)
                print(csvpath+"\n")
        result.close()
