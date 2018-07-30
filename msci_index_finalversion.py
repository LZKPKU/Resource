#!/usr/bin/env python
# encoding: utf-8

import re
import os, sys
import numpy as np
import pandas as pd
import zipfile
from util import ftp

if __name__ == "__main__":
    sys.path.append(os.path.realpath(__file__ + "/../../"))

import tradingday
from util.Log import log


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
        date=date,
        dataset=dataset.lower()
    )


def get_local_raw_file(dataset, date):
    # 存在今天的文件夹里
    date = str(date)
    path = "/data/stock/msci_raw_{dataset}/{yyyy}/{date}_{date}_D_{dataset}".format(
        dataset=dataset,
        yyyy=date[0:4],
        date=date
    )
    return os.path.expanduser(path)


def get_index_weight_file(dataset, date):
    # 存在下一个交易日的文件夹里（因为权值在下一个交易日使用）
    path = "/data/stock/msci_{dataset}/{yyyy}/{mm}/{dataset}_{date}.csv".format(
        dataset=dataset,
        yyyy=date[0:4],
        mm=date[4:6],
        date=date
    )
    return os.path.expanduser(path)


# @brief 从远程下载原始文件
# @param dataset
# @param date
# @return
def download_ftp_file(dataset, date):
    # get ftp path
    ftp_file = get_ftp_file(dataset, date)

    # get zip file path
    local_zip_file = get_local_raw_file(dataset, date) + '.zip'
    local_path = os.path.dirname(local_zip_file)

    # set login information
    FTP_SERVER = "ftp2.msci.com"
    USER = "hiflsbwq"
    PWD = "G1xkxfgudpxzk-"

    try:
        # ftp connection
        ftp.download_ftp(ftp_file, local_zip_file, FTP_SERVER, USER, PWD)
        log.info("已下载{}到{}".format(ftp_file, local_zip_file))

        # zip file
        azip = zipfile.ZipFile(local_zip_file)
        azip.extractall(local_path)
        azip.close()
        log.info("已解压{}".format(local_zip_file))
    except Exception as e:
        log.warn("无法下载{}，错误信息：{}".format(ftp_file, e))


# @brief raw_file是msci的原始数据文件，解析，从中抽取数据表
#
# 供parse_raw_file_and_save函数使用, mode默认返回所有表
# 但考虑到速度因素，当获取weight数据时只返回有用的两张表
# 'SECURITY CONSTITUENTS FUTURE','SECURITY CODE MAP'
#
# @param raw_file
# @mode 为0时返回所有表，其它值只返回指数权重相关的两张表
#
# @return 一个数据表的dict，
def parse_raw_file(raw_file, mode=0):
    # 将数据部分按列分割开
    def parse_line(line):
        df = []
        tmp = ""
        for i in range(len(line)):
            if line[i] != "|":
                tmp = tmp + line[i]
            if (line[i].isalnum() or line[i] == " ") \
                    and (i + 1 == len(line) or line[i + 1] == "|"):
                df.append(tmp.strip())
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

        pattern = r"^# (\d{1,2}) ((\w*\b\s)*)\s*"
        result = re.match(pattern, raw[pos])
        rows = int(result.group(1))

        column = []
        for j in range(rows):
            name = raw[j + pos + 1][39:70].rstrip()
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

    all_table_name = ['INDEX SAME DAY',
                      'INDEX FUTURE',
                      'SECURITY SAME DAY',
                      'SECURITY FUTURE',
                      'SECURITY CONSTITUENTS SAME DAY',
                      'SECURITY CONSTITUENTS FUTURE',
                      'SECURITY CODE MAP',
                      'DIVIDENDS SAME DAY',
                      'DIVIDENDS FUTURE'
                      ]
    part_table_name = ['SECURITY CONSTITUENTS FUTURE',
                       'SECURITY CODE MAP']
    if mode == 0:
        print("Extract all table!")
        all_table = {x: extract(x) for x in all_table_name}
    else:
        all_table = {x: extract(x) for x in part_table_name}
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
    dirname = os.path.dirname(index_weight_file)
    if os.path.isdir(dirname) is False:
        log.info("Create new path: " + dirname)
        os.makedirs(dirname)

    tables = parse_raw_file(raw_file, 1)
    # get two useful tables
    wgt = tables["SECURITY CONSTITUENTS FUTURE"]
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
    date = re.findall(pattern, index_weight_file)[0]
    # 这里不copy一下，会出来一个
    # A value is trying to be set on a copy of a slice from a DataFrame
    # 的警告
    wgt = wgt.loc[wgt["as_of_date"] == date].copy()
    wgt.loc[:, ("msci_index_code")] = wgt["msci_index_code"] + ".IX"

    # choose the useful columns
    df = pd.DataFrame(wgt[[
        "as_of_date", "msci_index_code",
        "code", "initial_weight"
    ]])

    df.to_csv(index_weight_file, index=False)
    log.info("已保存指数成分信息到{}".format(index_weight_file))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="7941R", help="数据集")
    parser.add_argument("-d", "--date", default=tradingday.today(), help="数据日期")
    parser.add_argument("--download", action="store_true", help="设置后下载数据")
    parser.add_argument("--parse_and_save", action="store_true", help="设置后下载数据")

    options = parser.parse_args()
    options.date = tradingday.yesterday(options.date, days_shift=1)
    options.yesterday = tradingday.yesterday(options.date)

    if options.download:
        download_ftp_file(options.dataset, options.yesterday)

    if options.parse_and_save:
        raw_file = get_local_raw_file(options.dataset, options.yesterday)
        index_weight_file = get_index_weight_file(options.dataset, options.date)
        parse_raw_file_and_save(raw_file, index_weight_file)