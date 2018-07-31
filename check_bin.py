 #!/usr/bin/env python
# encoding: utf-8
"""
tools for checking and correcting the 1min-binary data
"""

import argparse
import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import autobase as ab
from util import tradingday

STYLE = "%Y%m%d"    #data format
TODAY = datetime.strftime(datetime.today(),STYLE) #date of today
ZERO_THRES = 0      # threshold for zero problem
REPEAT_THRES = 20   # threshold for repeat problem
REER_THRES = 0.05   # threshold for relative error
CSVPATH = "/data/stock/1min_csv/{yyyy}/{mm}/1min_{date}.csv"
OUTPATH = "/data/stock/1min_bin/{yyyy}/{mm}/"


## @brief check the bin data quality of some date
# @param csvpath the path of csv file
# @param correct whether to correct or not
# @return
# the result will be written into log file.
def check_function(csvpath, correct=0):

    def comp(a, b):
        '''
        calculate the relative error and compare it to the threshold.
        '''
        # if a is 0 while b isn't, rerr is 2.0
        avg = (a + b) / 2
        if avg != 0:
            rerr = abs(a - b) / avg
            if rerr > REER_THRES:
                return rerr
            else:
                return 0
        else:
            return 0
        
    date = csvpath[-12:-4]
    outpath = OUTPATH.format(
         yyyy = csvpath[-12:-8],
         mm = csvpath[-8:-6]
    )

    VV_FLAG = False        # value and volume error
    ZERO_REPEAT_FLAG = False      # zero error or repeat error
    
    binpath = csvpath.replace("csv", "bin")
    csvdf = pd.read_csv(csvpath)
    # test for the condition that bin file doesn't exist
    if os.path.getsize(binpath):
        bindf = pd.DataFrame(ab.objects.read_kline_from_file(binpath))
    else:
        log.write("Binary file doesn't exist.\n")
        if correct == 1:
            replace_function(csvpath)
            log.write("Use the csv file to make new binary file!")
        return
    
    bindf = bindf[["code", "time", "close", "open", "high", "low", "volume", "value", "vwap", "ret"]]
    csvdf = csvdf[["stkcd", "time", "close", "open", "high", "low", "volume", "value"]]   
    # deal with the condition that code starts with "IF", which mainly occured in 2010 and 2011
    end = len(bindf)
    for i in range(len(bindf)):
        if bindf["code"][i][0:2].decode("ascii")=="IF":
            end = i
            break
    bindf = bindf[:end]
    
    tmp = []
    tmpp = []
    # deal with the time incongruity between csv and bin 
    # deal with the illegal code in bin
    for i in range(len(bindf)):
        tmp.append(bindf["code"][i][:9].decode("ascii"))
        if(bindf["time"][i] == 145900):
            tmpp.append(150000)
        elif(bindf["time"][i] == 112900):
            tmpp.append(113000)
        else:
            tmpp.append(bindf["time"][i+1])
    
    # deal with the measure incongruity in volume and value between csv and bin
    bindf = bindf.drop(["code", "time"],axis=1)
    bindf["stkcd"] = tmp
    bindf["time"] = tmpp
    csvdf["volume"] = csvdf["volume"]/10000
    csvdf["value"] = csvdf["value"]/10000
  
    # code that csv has while bin doesn't
    csvcode = set(csvdf.stkcd.unique()) - set(bindf.stkcd.unique())
    bincode = set(bindf.stkcd.unique()) - set(csvdf.stkcd.unique())
    log.write("code that csv has while bin doesn't: \n")
    for code_ in csvcode:
        log.write("{code} \n".format(
                code = code_
            )
        )
        
    # calculate and record the summary of value and volume
    result = pd.merge(csvdf,bindf,on=["stkcd", "time"])
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
    # if summation > 1, there is problem
    if valuesum > 1 or volumesum > 1:
        VV_FLAG = True
        log.write("Have value and volume problem!\n")
    else:
        log.write("Don't have volume and value problem.\n")
    # calculate and record the error in open,close,high and low
    error = []
    replace_code = ()
    items = ["open", "high", "low", "close"]
    for i in range(len(result)):
        for item in items:
            x = item + "_x"
            y = item + "_y"
            _ = comp(result[x][i], result[y][i])
            if _:
                error.append([result["stkcd"][i], result["time"][i], item, str(_)])
                info = "{code} {time} {item} Err:{err}\n".format(
                        code = result["stkcd"][i],
                        time = result["time"][i],
                        item = item,
                        err = str(_)
                    )
                log.write(info)
    if error:            
        error = pd.DataFrame(error)
        zero = error[error[3] == "2.0"]
        repeat = error[error[3] != "2.0"]
        zero = zero.groupby([0])[1].count()
        repeat = repeat.groupby([0])[1].count()
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
        log.write("Don't have zero or repeat problem.\n")
    
    log.write("\n")
    
    if correct:
        if VV_FLAG or ZERO_REPEAT_FLAG:
            result = pd.merge(csvdf, bindf, on=["stkcd","time"], how="outer")
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

            for i in range(len(result)):
                if not result["time"][i] % 10000:
                    time = result["time"][i] - 4100
                else:
                    time = result["time"][i] - 100
                code = result["stkcd"][i].encode(encoding="ascii")
                if result["stkcd"][i] in csvcode:
                    tmp = (code, date, time,
                       result["open_x"][i], result["high_x"][i], result["low_x"][i], result["close_x"][i],
                       result["volume_x"][i], result["value_x"][i], result["vwap"][i], result["ret"][i])
                elif result["stkcd"][i] in bincode:
                    tmp = (code, date, time,
                       result["open_y"][i], result["high_y"][i], result["low_y"][i], result["close_y"][i],
                       result["volume_y"][i], result["value_y"][i], result["vwap"][i], result["ret"][i])
                elif result["stkcd"][i] in replace_code:
                    tmp = (code, date, time,
                       result["open_x"][i], result["high_x"][i], result["low_x"][i], result["close_x"][i],
                       result[volume_src][i], result[value_src][i], result["vwap"][i], result["ret"][i])
                else:
                    tmp = (code, date, time,
                       result["open_y"][i], result["high_y"][i], result["low_y"][i], result["close_y"][i],
                       result[volume_src][i], result[value_src][i], result["vwap"][i], result["ret"][i])
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
            if not os.path.exists(outpath):
                os.makedirs(outpath)
            output.tofile(outpath + "1min_" + date + ".bin")
            log.write("Correct successfully!\n\n")
        else:
            log.write("Don't need to correct!\n\n")


## @brief replace the binary file using csv file 
# @param csvpath path of csv file
# @return
def replace_function(csvpath):
    date = csvpath[-12:-4]
    binpath = csvpath.replace("csv", "bin")
    outpath = OUTPATH.format(
         yyyy = csvpath[-12:-8],
         mm = csvpath[-8:-6]
    )
    # test for the condition that bin file doesn't exist
    if os.path.getsize(binpath):
        ori_bindf = pd.DataFrame(ab.objects.read_kline_from_file(binpath))
    else:
        ori_bindf = pd.DataFrame()
    csvdf = pd.read_csv(csvpath)
    bindf = []
    # transform the csvdf to bindf
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
    
    if len(ori_bindf):
        ori_bindf = ori_bindf[["code", "date", "time", "close", "open", "high", "low", "volume", "value", "vwap", "ret"]]
         # deal with the condition that code starts with "IF", which mainly occured in 2010 and 2011
        end = len(ori_bindf)
        for i in range(len(ori_bindf)):
            if ori_bindf["code"][i][0:2].decode("ascii")=="IF":
                end = i
                break
        ori_bindf = ori_bindf[:end]
    
        tmp = []
        # deal with the time incongruity between csv and bin 
        # deal with the illegal code in bin
        for i in range(len(ori_bindf)):
            tmp.append(ori_bindf["code"][i][:9].decode("ascii"))
        # deal with the measure incongruity in volume and value between csv and bin
        ori_bindf = ori_bindf.drop(["code"],axis=1)
        ori_bindf["code"] = tmp
        bindf = pd.DataFrame(bindf,
                                 columns=["code", "date", "time", "open", "high", "low", "close", "volume", "value", "vwap",
                                 "ret"])
        bindf.sort_values(["code", "date", "time"], inplace=True)
        # copy the data that bin has while csv doesn't into newdf
        code = set(ori_bindf.code.unique()) - set(bindf.code.unique())
        
        for i in range(len(ori_bindf)):
            if ori_bindf["code"][i] in code:
                tmp = (ori_bindf["code"][i],
                           ori_bindf["date"][i],
                           ori_bindf["time"][i],
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
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    output.tofile(outpath + "1min_" + date + ".bin")
    log.write("Replace successfully!\n")


## @brief other operations before and after check or replace
# @param start start date(included)
# @param end   end date(included)
# @param mode  type of operation
# @return 
def index(start,end,mode):
    global log
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
    dates = daysbetween(start,end)
    for day in dates:
        csvpath = CSVPATH.format(
                date = day,
                yyyy = day[:4],
                mm = day[4:6]
        )
        if os.path.isfile(csvpath):
            logpath = OUTPATH.format(
                yyyy = day[:4],
                mm = day[4:6]
        )
            if not os.path.exists(logpath):
                os.makedirs(logpath)
            log = open(logpath + "1min_" + day + "log.txt",'a')
            log.write(day + "\n\n")
            log.write("Check date: " + TODAY + "\n")
            if mode == 0:
                check_function(csvpath, correct = 0)
            if mode == 1:
                check_function(csvpath, correct = 1)
            if mode == 2:
                replace_function(csvpath)
            log.close()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--begdate", default = TODAY, help = "8-digit start date(included)")
    parser.add_argument("-e", "--enddate", default = TODAY, help = "8-digit end date(included)")
    parser.add_argument("--check", action = "store_true", help="check")
    parser.add_argument("--check_and_correct", action = "store_true", help="check, then correct automatically")
    parser.add_argument("--replace", action = "store_true", help="replace")
    
    options = parser.parse_args()
    
    if options.check:
        index(options.begdate,options.enddate, 0)
    if options.check_and_correct:
        index(options.begdate,options.enddate, 1)
    if options.replace:
        index(options.begdate,options.enddate, 2)
