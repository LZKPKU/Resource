#!/usr/bin/env python
# encoding: utf-8

"""
tools for checking and correcting the 1min-binary data
"""
import argparse
import os
from datetime import datetime,timedelta
import numpy as np
import pandas as pd
import autobase as ab

STYLE = "%Y%m%d"    #日期格式
TODAY = datetime.strftime(datetime.today(),STYLE) #今天日期
LOGPATH = "log.txt" #日志文件路径
ZERO_THRES = 1      #数据点为0需要处理的阈值
REPEAT_THRES = 20    #数据点重复需要处理的阈值
REER_THRES = 0.05   #相对误差需要记录下来的阈值


# @brief 给定两个数，计算相对误差
# @param a
# @param b
# @return relative error
def comp(a, b):
    '''
    calculate the relative error and compare it to the threshold.
    '''
    # 阈值为 5%
    # 如果有一个为0但另一个不为0,则结果为2
    avg = (a + b) / 2
    if avg != 0:
        rerr = abs(a - b) / avg
        if rerr > REER_THRES:
            return rerr
        else:
            return 0
    else:
        return 0
# @brief 检查某一日期的bin数据质量
# @param csvpath csv文件的路径
# @return
# 将检查结果写入log文件中
def check_function(csvpath,correct=0):
    
    VV_FLAG = False        # value and volume error
    ZERO_REPEAT_FLAG = False      # zero error or repeat error
    
    binpath = csvpath.replace("csv","bin")
    csvdf = pd.read_csv(csvpath)
    #判断当天bin数据缺失的情况
    if os.path.getsize(binpath):
        bindf = bindf = pd.DataFrame(ab.objects.read_kline_from_file(binpath))
    else:
        log.write("Binary file doesn't exist.\n")
        return
    
    bindf = bindf[["code","time","close","open","high","low","volume","value","vwap","ret"]]
    csvdf = csvdf[["stkcd","time","close","open","high","low","volume","value"]]
    
    #处理代码为IF开头的情况，主要在2011年之前存在
    end = len(bindf)
    for i in range(len(bindf)):
        if bindf["code"][i][0:2].decode("ascii")=="IF":
            end = i
            break
    bindf = bindf[:end]
    
    tmp = []
    tmpp = []
    #处理bin数据和csv数据时间不一致
    #处理bin数据中code列有乱码的情况
    for i in range(len(bindf)):
        tmp.append(bindf["code"][i][:9].decode("ascii"))
        if(bindf["time"][i] == 145900):
            tmpp.append(150000)
        elif(bindf["time"][i] == 112900):
            tmpp.append(113000)
        else:
            tmpp.append(bindf["time"][i+1])
    
    #处理csv数据和bin数据中value和volume单位不一致
    bindf = bindf.drop(["code","time"],axis=1)
    bindf["stkcd"] = tmp
    bindf["time"] = tmpp
    csvdf["volume"] = csvdf["volume"]/10000
    csvdf["value"] = csvdf["value"]/10000
  
    # csv中有而bin中没有的股票代码
    csvcode = set(csvdf.code.unique()) - set(bindf.stkcd.unique())
    bincode = set(bindf.stkcd.unique()) - set(csvdf.code.unique())
    log.write("code that csv has but bin doesn't: \n")
    for code_ in csvcode:
        log.write("{code} \n".format(
                code = code_
            )
        )
        
    #计算并记录value和volume总和
    result = pd.merge(csvdf,bindf,on=["stkcd","time"])
    valuesum = sum(result["value_x"])-sum(result["value_y"])
    volumesum = sum(result["volume_x"])-sum(result["volume_y"])
    log.write("value total error(csv - bin): {valuesum}\n".format(
            valuesum = str(valuesum)
        )
    )
    log.write("volume total error(csv - bin): {volumesum}\n".format(
            volumesum = str(volumesum)
        )
    )
    #如果差值大于1就认为这两列数据有问题
    if valuesum > 1 or volumesum > 1:
        VV_FLAG = True
        log.write("value and volume data isn't correct!")
    else:
        log.write("value and volume data doesn't have problem.")
    # 记录open,low,high,close四列偏差过大的情况
    error = []
    items = ["open","high","low","close"]
    for i in range(len(result)):
        for item in items:
            x = item + "_x"
            y = item + "_y"
            _ = comp(result[x][i],result[y][i])
            if _:
                error.append(result["stkcd"][i],result["time"][i],item,_)
                info = "{code} {time} {item} Err:{err}\n".format(
                        code = result["stkcd"][i],
                        time = result["time"][i],
                        item = item,
                        err = str(_)
                    )
                log.write(info)
                
    error = pd.DataFrame(error)
    zero = error[error[4] == "2.0"]
    repeat = error[error[4] != "2.0"]
    zero.groupby([0])[1].count()
    repeat.groupby([0])[1].count()
    zerocode = set(zero[zero > ZERO_THRES].reset_index()[0].unique())
    repeatcode = set(repeat[repeat > REPEAT_THRES].reset_index()[0].unique())
    replace_code = zerocode | repeatcode
    if replace_code:
        ZERO_REPEAT_FLAG = True
        log.write("Have zero or repeat problem.\n")
        for code_ in replace_code:
            log.write("{code}\n".format(
                    code = code_
                )
            )
    else:
        log.write("Dont't have zero or repeat problem.\n")
    
    log.write("\n")
    
    if correct:
        outpath = "test.bin"
        '''
        correct
        '''
        result = pd.merge(csvdf,bindf,on=["stkcd","time"],how="outer")
        newdf = []
        value_src = "value_y"
        volume_src = "volume_y"
        open_src = "open_y"
        close_src = "close_y"
        high_src = "high_y"
        low_src = "low_y"
        
        if VV_FLAG:
            value_src = "value_x"
            volume_src = "volume_x"
            
        # need to replace the 
        for i in range(len(result)):
            if not result["time"][i]%10000:
                time = result["time"][i] - 4100
            else:
                time = result["time"][i] - 100
            code = result["stkcd"][i].encode(encoding="ascii")
            date = result["date"][i]
            if result["stkcd"][i] in csvcode:
                tmp = (code, date, time,
                   result["open_x"][i], result["high_x"][i], result["low_x"][i], result["close_x"][i], 
                   result["value_x"][i],result["volume_x"][i], result["vwap"][i], result["ret"][i])
            elif result["stkcd"][i] in bincode:
                tmp = (code, date, time,
                   result["open_y"][i], result["high_y"][i], result["low_y"][i], result["close_y"][i], 
                   result["value_y"][i],result["volume_y"][i], result["vwap"][i], result["ret"][i])
            elif result["stkcd"][i] in replace_code:   
                tmp = (code, date, time,
                   result["open_x"][i], result["high_x"][i], result["low_x"][i], result["close_x"][i], 
                   result[volume_src][i],result[value_src][i], result["vwap"][i], result["ret"][i])
            else:
                tmp = (code, date, time,
                   result["open_y"][i], result["high_y"][i], result["low_y"][i], result["close_y"][i], 
                   result[volume_src][i],result[value_src][i], result["vwap"][i], result["ret"][i])
            newdf.append(tmp)
        newdf = pd.DataFrame(newdf,
        columns=["code", "date", "time", "open", "high", "low", "close", "volume", "value", "vwap",
            "ret"])
        newdf.sort_values(["code", "date", "time"], inplace=True)
        # 将newdf输出成binary文件
        output = list(map(lambda x: tuple(newdf.iloc[x]), range(len(newdf))))
        output = np.array(output,
                          dtype=[('code', 'S32'), ('date', '<i4'), ('time', '<i4'), ('open', '<f4'), ('high', '<f4'),
                                 ('low', '<f4'), ('close', '<f4'), ('volume', '<f4'), ('value', '<f4'), ('vwap', '<f4'),
                                 ('ret', '<f4')])
        output.tofile(outpath)
        log.write("Correct successfully!\n\n")
            



# @brief 用csv数据替换掉某一日期的bin数据
# @param csvpath csv文件的路径
# @return
    
def replace_function(csvpath):
    binpath = csvpath.replace("csv","bin")
    #outpath = binpath
    # test
    outpath = "test.bin"
    #判断当天bin数据缺失的情况
    if os.path.getsize(binpath):
        ori_bindf = pd.DataFrame(ab.objects.read_kline_from_file(binpath))
    else:
        log.write("Binary file doesn't exist.\n")
        return 
    csvdf = pd.read_csv(csvpath)
    bindf = []
    #统一时间标准，将csvdf转换为bindf
    for i in range(len(csvdf)):
        if not csvdf["time"][i]%10000:
            time = csvdf["time"][i] - 4100
        else:
            time = csvdf["time"][i] - 100
        tmp = (csvdf["stkcd"][i].encode(encoding="ascii"), csvdf["date"][i], time,
               csvdf["open"][i], csvdf["high"][i], csvdf["low"][i], csvdf["close"][i], csvdf["volume"][i]/10000,
               csvdf["value"][i]/10000, np.nan, np.nan)
        bindf.append(tmp)
    newdf = bindf
    
    bindf = pd.DataFrame(bindf,
    columns=["code", "date", "time", "open", "high", "low", "close", "volume", "value", "vwap",
            "ret"])
    bindf.sort_values(["code", "date", "time"], inplace=True)
    #将bin中有而csv中没有的数据复制进newdf
    code = set(ori_bindf.code.unique()) - set(bindf.code.unique())
    
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
    # 将newdf输出成binary文件
    output = list(map(lambda x: tuple(newdf.iloc[x]), range(len(newdf))))
    output = np.array(output,
                      dtype=[('code', 'S32'), ('date', '<i4'), ('time', '<i4'), ('open', '<f4'), ('high', '<f4'),
                             ('low', '<f4'), ('close', '<f4'), ('volume', '<f4'), ('value', '<f4'), ('vwap', '<f4'),
                             ('ret', '<f4')])
    output.tofile(outpath)
    log.write("Replace successfully!\n")
    
# @brief 计算某两个日期中间的所有日期
# @param start 起始日期（包含）
# @param end 结束日期（包含）
# @return 日期的字符串列表
    
def daysbetween(start,end):
    start_ = datetime.strptime(start,STYLE)
    end_ = datetime.strptime(end,STYLE)
    day = timedelta(days=1)
    dates = []
    d = start_
    while d < end_ + day:
        dates.append(datetime.strftime(d,STYLE))
        d = d + day
    return dates

# @brief 处理主要功能前后的其他操作
# @param start 起始日期（包含）
# @param end 结束日期（包含）
# @return 
def index(start,end,mode):
    dates = daysbetween(start,end)
    log_mode = ["check","check_and_correct","replace"]
    with open(LOGPATH,"w") as log:
        log.write("log date: "+TODAY+"\n")
        log.write("Type: "+log_mode[mode]+"\n")
        log.write("Start: "+dates[0]+"\n")
        log.write("End: "+dates[-1]+"\n")
        for day in dates:
            csvpath = "/data/stock/1min_csv/{yyyy}/{mm}/1min_{date}.csv".format{
                    date = day,
                    yyyy = day[:4],
                    mm = day[4:6]
            }
            if os.path.isfile(csvpath):
*                log.write(csvpath + "\n\n")
                if mode == 0:
                    check_function(csvpath,correct = 0)
                if mode == 1:
                    check_function(csvpath,correct = 1)
                if mode == 2:
                    replace_function(csvpath)

            
    
 if __name__ == "__main__":
       
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--begdate",help = "八位起始日期")
    parser.add_argument("-e","--enddate",default = TODAY,help = "八位结束日期")
    parser.add_argument("--check",action = "store_true",help="检查")
    parser.add_argument("--check_and_correct",action = "store_true",help="检查并修改")
    parser.add_argument("--replace",action = "store_true",help="替换")
    
    options = parser.parse_args()
    
    if options.check:
        index(options.start,options.end,0)
    if options.check_and_correct:
        index(options.start,options.end,1)
    if options.replace:
        index(options.start,options.end,2)