# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 15:04:42 2018

@author: Administrator
"""
import pandas as pd
import numpy as np
import autobase as ab
import os

def F(binpath):
    pre = "/data/stock/"
    original_binpath = pre + binpath
    
    if os.path.getsize(original_binpath):
        ori_bindf = pd.DataFrame(ab.objects.read_kline_from_file(original_binpath))
    else:
        return 
    bindf = pd.DataFrame(ab.objects.read_kline_from_file(binpath))
    
    code = set(ori_bindf.code.unique()) - set(bindf.code.unique())
    
    newdf = []
    
    for i in range(len(bindf)):
        tmp = (bindf["code"][i],
                   bindf["date"][i],
                   bindf["open"][i],
                   bindf["high"][i],
                   bindf["low"][i],
                   bindf["close"][i],
                   bindf["volume"][i],
                   bindf["value"][i],
                   bindf["vwap"][i],
                   bindf["ret"][i])
        newdf.append(tmp)
    for i in range(len(ori_bindf)):
        if ori_bindf["code"][i] in code:
            tmp = (ori_bindf["code"][i],
                       ori_bindf["date"][i],
                       ori_bindf["open"][i],
                       ori_bindf["high"][i],
                       ori_bindf["low"][i],
                       ori_bindf["close"][i],
                       ori_bindf["volume"][i],
                       ori_bindf["value"][i],
                       ori_bindf["vwap"][i],
                       ori_bindf["ret"][i])
            newdf.append(tmp)
    
    newdf = pd.DataFrame(newdf,
    columns=["code", "date", "time", "open", "high", "low", "close", "volume", "value", "vwap",
            "ret"])
    newdf.sort_values(["code", "date", "time"], inplace=True)

    output = list(map(lambda x: tuple(newdf.iloc[x]), range(len(newdf))))
    output = np.array(output,
                      dtype=[('code', 'S32'), ('date', '<i4'), ('time', '<i4'), ('open', '<f4'), ('high', '<f4'),
                             ('low', '<f4'), ('close', '<f4'), ('volume', '<f4'), ('value', '<f4'), ('vwap', '<f4'),
                             ('ret', '<f4')])
    output.tofile(binpath)

if __name__ == "__main__":
    year = ["2018"]
    month = ["01"]
    for i in year:
        for j in month:
            PATH = "1min_bin/" + year + "/" + month + "/"
            for m in os.listdir(PATH):
                csvpath = PATH + m
                F(csvpath)
                print(csvpath)