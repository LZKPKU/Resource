#!/usr/bin/env python
# encoding: utf-8

#
# @brief 获取msci ftp上的对应文件名称
#
# @param dataset 数据包名称
# @param date 日期，格式yyyymmdd
# 注意当天下载文件第二天使用，文件夹名称应相符
# @return
def get_ftp_file(dataset, date):
    # 用今天日期
    # 注意，在msci的ftp上文件名全部为小写
    date = str(date)
    
    return "{date}_{date}d_{dataset}.zip".format(
        date = date,
        dataset = dataset.lower()
    )

##
# @brief 原始文件的本地存储路径
#
# @param dataset
# @param date
#
# @return
def get_local_raw_file(dataset, date):
    # 存在今天的文件夹里
    date = str(date)
    
    #return "D:/test/{dataset}/{yyyy}/{date}_{date}_D_{dataset}".format(
    dataset = dataset,
    yyyy = date[0:4],
    date = date
    )


def get_index_weight_file(dataset, date):
    # 存在下一个交易日的文件夹里（因为权值在下一个交易日使用）
    date = tradingday.next(date)
    
    #return "D:/test/{dataset}/{yyyy}/{mm}/{dataset}_{date}.csv".format(
        dataset=dataset,
        yyyy=date[0:4],
        mm=date[4:6],
        date=date
    )
# @brief 从远程下载原始文件
# @param dataset
# @param date
# @return
def download_ftp_file(dataset, date):
    # get ftp path
    ftp_file = get_ftp_file(dataset, date)

    # get zip file path
    local_path = get_local_raw_file(dataset, date)
    local_zip_file = local_path + '.zip'
    local_path = os.path.dirname(local_path)

    # get weight csv path
    local_weight_path = os.path.dirname(get_index_weight_file(dataset, date))

    # set login information
    FTP_SERVER = "ftp2.msci.com"
    USER = "hiflsbwq"
    PWD = "G1xkxfgudpxzk-"

    # test for save paths and create them if necessary
    if not os.path.exists(local_path):
        os.makedirs(local_path)
        print("Create new path: ",local_path)

    if not os.path.exists(local_weight_path):
        os.makedirs(local_weight_path)
        print("Create new path: ",local_weight_path)
    
    # test for zip file path, remind user and terminate if existed
    if os.path.exists(local_zip_file):
        print("--file exists!--")
        return False

    # ftp connection
    ftp = FTP()
    ftp.connect(FTP_SERVER, 21)
    ftp.login(USER, PWD)
    
    # download and write
    fp = open(local_zip_file, "wb+")
    ftp.retrbinary('RETR ' + ftp_file, fp.write, 1024)
    fp.flush()
    
    # close file and connection
    fp.close()
    ftp.quit()

    # zip file
    azip = zipfile.ZipFile(local_zip_file)
    azip.extractall(local_path)
    azip.close()
    print("Download Successfully!\n")

# @brief raw_file是msci的原始数据文件，解析，从中抽取数据表

# @param raw_file

#
# @return 一个数据表的dict，
# 主要是'SECURITY CONSTITUENTS FUTURE','SECURITY CODE MAP'
# 供parse_raw_file_and_save函数使用
def parse_raw_file(raw_file):

    # 将数据部分按列分割开
    def parse_line(line):
        df = []
        tmp = ""
        for i in range(len(line)):
            if line[i].isdigit() or line[i] == ".":
                tmp = tmp + line[i]
            if (line[i].isdigit() or line[i] == " ") \
                    and (i + 1 == len(line) or line[i + 1] == "|"):
                df.append(tmp)
                tmp = ""
        return df

    # 打开文件，按行读取
    def extract(tname):
        with open(raw_file) as f:
            data = pd.DataFrame()
            raw = f.readlines()
            for line in range(len(raw)):
                raw[line] = raw[line].rstrip("\n")
                pattern = tname
                if re.search(pattern, raw[line]):
                    pos = line

        # find # to get position of the start of a table
        pattern = r"^# (\d{1,2}) ((\w*\b\s)*)\s*"
        result = re.match(pattern, raw[pos])
        rows = int(result.group(1))

        table_name = result.group(2)
        column = []
        for j in range(rows):
            line = raw[j + pos + 1]
            pattern = r'^#\s*\d{1,2}\s*(\w*\b\s)*\s*(\w*)'
            name = re.match(pattern, line).group(2)
            column.append(name)
        # 表的数据部分
        while not re.match(r"\|", raw[pos]):
            pos += 1
        # #EOD为表的结尾
        while raw[pos] != "#EOD":
            a = np.array(parse_line(raw[pos]))
            pos += 1
            for _ in range(len(a)):
                if a[_] != "":
                    a[_] = a[_]
                else:
                    a[_] = np.nan
            j += 1
            data = data.append(pd.Series(a), ignore_index=True)
        # 将列名赋予Dataframe并返回
        data.columns = column
        return data
 
    all_table_name = ['SECURITY CONSTITUENTS FUTURE',
                      'SECURITY CODE MAP']
    all_table = {x:extract(x) for x in all_table_name}
    return all_table

# @brief 以CSV文件保存指数权重数据
#
# 文件格式为：逗号为分隔符，第一列为指数日期，第二列为指数代码，第三列为成份股代码，第
# 四列为成份股权重（初始权重），第五列为收盘权重
#
# @param raw_file 原始数据文件地址
# @param index_weight_file 指数权重的文件地址
#
# @return 无

def parse_raw_file_and_save(raw_file, index_weight_file):
    tables = parse_raw_file(raw_file)
    
    # get two useful tables
    wgt = tables["SECURITY CONSTITUENTS FUTURE"]
    wgt.to_csv("haha.csv")
    map = tables["SECURITY CODE MAP"]
    wgt["code"] = 0

    msci_code = map.msci_security_code.unique()
    ticker = map.bb_ticker.unique()
    wgt_code = wgt.msci_security_code
    
    # extract the code of each stock
    code = []
    for i in ticker:
        code.append(re.match(r"(\d*)", i).group(1))
    
    # join
    for i in range(len(msci_code)):
        wgt.loc[wgt_code == msci_code[i], "code"] = str(code[i]).zfill(6)

    # get the date of next trading day and select data of that day
    pattern = "(\d{8,8}).csv"
    date = re.findall(pattern,index_weight_file)[0]
    wgt = wgt[wgt["as_of_date"] == date]
    
    # choose the useful columns
    df = pd.DataFrame(wgt[["calc_date", "msci_index_code"
        , "code", "initial_weight"]])
    
    df.to_csv(index_weight_file, index=False)
    print("Complete!\n")


if __name__ == "__main__":
    import re
    import os
    import pandas as pd
    import numpy as np
    from ftplib import FTP
    import argparse
    import tradingday
    import zipfile

    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="7941R", help="数据集")
    parser.add_argument("-d", "--date", help="数据日期")
    # parser.add_argument("-d", "--date", default=tradingday.today(), help="数据日期")
    parser.add_argument("--download", action="store_true", help="设置后下载数据")
    parser.add_argument("--parse_and_save", action="store_true", help="设置后下载数据")

    options = parser.parse_args()

    if options.download:
        download_ftp_file(options.dataset, options.date)

    if options.parse_and_save:
        raw_file = get_local_raw_file(options.dataset, options.date)
        index_weight_file = get_index_weight_file(options.dataset, options.date)
        parse_raw_file_and_save(raw_file, index_weight_file)
