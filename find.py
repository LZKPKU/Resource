import os
import pandas as pd
import numpy as np
import sys

pre = "data/"
repeatthres = 5
zerothres = 1
year = ["2011","2010"]
#year = ["2012","2013","2014","2015","2016","2017","2018"]
def repeat():
    dfff = []
    for i in year:
        PATH = pre + i + "/err/"
        for j in os.listdir(PATH):
            df = []
            with open(PATH+j,'r') as f:
                raw = f.readlines()
                for line in range(len(raw)):
                    raw[line] = raw[line].rstrip("\n")
                    raw[line] = raw[line].split(" ")
                for line in range(len(raw)):
                    if raw[line][0][:2] == "20":
                        date = int(raw[line][0])
                    if len(raw[line]) == 5:
                        df.append([raw[line][0],date,raw[line][1],raw[line][2],raw[line][4]])
                df = pd.DataFrame(df)
                df = df[df[4]!='2.0']
                dff = df.groupby([0,1])[2].count()
                dff = dff[dff>repeatthres]
                dff = dff.reset_index()
                dff = pd.merge(dff,df,on=[0,1])
                if len(dff) > 0:
                    for m in dff.values:
                        dfff.append(m)
    dfff = pd.DataFrame(dfff)
    date = pd.DataFrame(dfff[1].unique())
    date.columns = ["date"]
    # date.to_csv("repeat_date.csv",index=False)
    # dfff.to_csv("repeat"+str(repeatthres)+".csv",index=False)
    return date

def zero():
    dfff = []
    for i in year:
        PATH = pre + i + "/err/"
        for j in os.listdir(PATH):
            df = []
            with open(PATH+j,'r') as f:
                raw = f.readlines()
                for line in range(len(raw)):
                    raw[line] = raw[line].rstrip("\n")
                    raw[line] = raw[line].split(" ")
                for line in range(len(raw)):
                    if raw[line][0][:2] == "20":
                        date = int(raw[line][0])
                    if len(raw[line]) == 5:
                        df.append([raw[line][0],date,raw[line][1],raw[line][2],raw[line][4]])
                df = pd.DataFrame(df)
                df = df[df[4]=='2.0']
                dff = df.groupby([0,1])[2].count()
                dff = dff[dff>zerothres]
                dff = dff.reset_index()
                if len(df)>0:
                    dff = pd.merge(dff,df,on=[0,1])
                if len(dff) > 0:
                    for m in dff.values:
                        dfff.append(m)
    dfff = pd.DataFrame(dfff)
    date = pd.DataFrame(dfff[1].unique())
    date.columns = ["date"]
    # date.to_csv("zero_date.csv",index=False)
    # dfff.to_csv("zero"+str(zerothres)+".csv",index=False)
    return date

if __name__ == "__main__":
    repeatdf = repeat()
    repeatdf["type"] = "repeat"
    zerodf = zero()
    zerodf["type"] = "zero"
    # nobin = pd.read_csv(pre + "nobin.csv")
    final = pd.concat([repeatdf,zerodf],ignore_index=True).sort_values(by=["date"])
    final.to_csv("final_result2010.csv",index=False)