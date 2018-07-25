import pandas as pd
import numpy as np
import os

pre = "data/"
year = ["2010","2011","2012","2013","2014","2015","2016","2017","2018"]
mid = "/vac/"

def vac():
    dfff = []
    for i in year:
        PATH = pre + i + mid
        for j in os.listdir(PATH):
            df = []
            with open(PATH + j, 'r') as f:
                raw = f.readlines()
                for line in range(len(raw)):
                    raw[line] = raw[line].rstrip("\n")
                    raw[line] = raw[line].split(" ")
                for line in range(len(raw)):
                    if raw[line][0][:2] == "20":
                        date = int(raw[line][0])
                    elif len(raw[line][0])>7 and raw[line][0][6] == '.':
                        df.append([raw[line][0], date])
                df = pd.DataFrame(df)
                if len(df) > 0:
                    for m in df.values:
                        dfff.append(m)
    dfff = pd.DataFrame(dfff).sort_values(by = [0,1])
    dfff.to_csv("vac.csv",index=False)

if __name__ == "__main__":
    vac()