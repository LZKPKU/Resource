# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 09:33:59 2018

@author: Administrator

substitute the volume and value of csv for those of bin
"""
import pandas as pd
import numpy as np
import autobase as ab
import os


def F(csvpath):
    date = csvpath[-12:-4]
    binpath = csvpath
    binpath = binpath.replace("csv","bin")
    outpath = "2010newbin/1min_" + date + ".bin"
    newbindf = []
    if os.path.getsize(binpath):
        bindf = pd.DataFrame(ab.objects.read_kline_from_file(binpath))
    else:
        return
    csvdf = pd.read_csv(csvpath)
    
    tmp = []
    tmpp = []
    tmppp = []
    for i in range(len(csvdf)):
        tmp.append(csvdf["stkcd"][i].encode("ascii"))
        if not csvdf["time"][i] % 10000:
            tmpp.append(csvdf["time"][i]-4100)
        else:
            tmpp.append(csvdf["time"][i]-100)
    csvdf = csvdf.drop(["stkcd","time"],axis=1)
    csvdf["stkcd"] = tmp
    csvdf["time"] = tmpp
    for i in range(len(bindf)):
        tmppp.append(bindf["code"][i][:9])
    bindf["stkcd"] = tmppp
    result = pd.merge(csvdf,bindf,on=["stkcd","time"],how = "right")
    result = result.drop(['date_x', 'close_x', 'open_x', 'high_x', 'low_x','buy_vol', 'buy_value',
                          'sale_vol', 'sale_value', 'w_buy', 'w_sale','stkcd',
                          'volume_y', 'value_y'],axis=1)
    column = ['code','date_y','time','open_y','high_y','low_y','close_y',
              'volume_x','value_x','vwap','ret']
    result = result[column]
    result.columns = ["code", "date", "time", "open", "high", "low",
                        "close", "volume", "value", "vwap","ret"]
    result.sort_values(["code", "date", "time"], inplace=True)
    result["volume"] = result["volume"]/10000
    result["value"] = result["value"]/10000
    output = list(map(lambda x: tuple(result.iloc[x]), range(len(result))))
    output = np.array(output,
                dtype=[('code', 'S32'), ('date', '<i4'), ('time', '<i4'), ('open', '<f4'), ('high', '<f4'),
                    ('low', '<f4'), ('close', '<f4'), ('volume', '<f4'), ('value', '<f4'), ('vwap', '<f4'),
                    ('ret', '<f4')])
    output.tofile(outpath)
    
if __name__ == "__main__":
    F("/data/stock/1min_csv/2010/01/1min_20100104.csv")