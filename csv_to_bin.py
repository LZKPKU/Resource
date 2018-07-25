import pandas as pd
import numpy as np
import autobase as ab
import os

def F(csvpath):
    binpath = csvpath
    binpath = binpath.replace("csv", "bin")
    date = csvpath[-12:-4]
    outpath = "newbin/1min_" + date + ".bin"
    csvdf = pd.read_csv(csvpath)
    bindf = []

    for i in range(len(csvdf)):
        if not csvdf["time"][i]%10000:
            time = csvdf["time"][i] - 4100
        else:
            time = csvdf["time"][i] - 100
        tmp = (csvdf["stkcd"][i].encode(encoding="ascii"), csvdf["date"][i], time,
               csvdf["open"][i], csvdf["high"][i], csvdf["low"][i], csvdf["close"][i], csvdf["volume"][i]/10000,
               csvdf["value"][i]/10000, np.nan, np.nan)
        bindf.append(tmp)

    bindf = pd.DataFrame(bindf,
    columns=["code", "date", "time", "open", "high", "low", "close", "volume", "value", "vwap",
            "ret"])
    bindf.sort_values(["code", "date", "time"], inplace=True)

    output = list(map(lambda x: tuple(bindf.iloc[x]), range(len(bindf))))
    output = np.array(output,
                      dtype=[('code', 'S32'), ('date', '<i4'), ('time', '<i4'), ('open', '<f4'), ('high', '<f4'),
                             ('low', '<f4'), ('close', '<f4'), ('volume', '<f4'), ('value', '<f4'), ('vwap', '<f4'),
                             ('ret', '<f4')])
    output.tofile(outpath)

if __name__ == "__main__":
    # dateset = ["20120712",
    #             "20120717",
    #             "20121026",
    #             "20130122",
    #             "20130222",
    #             "20130410",
    #             "20130508",
    #             "20140224",
    #             "20140314",
    #             "20140918",
    #             "20141223",
    #             "20150202",
    #             "20150518",
    #             "20150528",
    #             "20150716"]

    dateset = pd.read_csv("final_result.csv")["date"].unique()
    for i in dateset:
        i = str(i)
        year = i[:4]
        month = i[4:6]
        csvpath = "/data/stock/1min_csv/"+year+"/"+month+"/"+"1min_"+i+".csv"
        F(csvpath)
        print(csvpath+"\n")
