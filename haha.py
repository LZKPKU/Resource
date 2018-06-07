#!/usr/bin/env python
# encoding: utf-8

#
# @brief 获取msci ftp上的对应文件名称
#
# @param dataset 数据包名称
# @param date 日期，格式yyyymmdd
#
# @return
def get_ftp_file(dataset, date):
    return "/index/{date}_{date}d_{dataset}.zip".format(
        date = date
        dataset = dataset
    )

##
# @brief 原始文件的本地存储路径
#
# @param dataset
# @param date
#
# @return
def get_local_file(dataset, date):
    return "~/data/stock/msci/{dataset}/{yyyy}/".format(
        dataset = dataset,
        yyyy=date[0:4],
        date=date
    )
def get_local_raw_file(dataset, date):
    date = str(date)
    return "~/data/stock/msci/{dataset}/{yyyy}/{date}_{date}d_{dataset}".format(
        dataset=dataset,
        yyyy=date[0:4],
        date=date
    )

def get_index_weight_file(dataset, date):
    date = str(date)

def download_ftp_file(dataset, date):
        ftp_file = get_ftp_file(dataset, date)
        local_path = get_local_file(dataset, date)
        local_zip_file = local_file + dataset + "_" + date + ".zip"
        from ftplib import FTP
        import os
        import zipfile
        FTP_SERVER = ""
        USER = ""
        PWD = ""

        try:
            if os.path.exists(local_zip_file):
                print("--file exists!--")
            else:
                os.mkdirs(local__zip_file)
            return True
        except:
            return False

        ftp = FTP()
        ftp.connect(FTP_SERVER, 21)
        ftp.login(USER, PWD)

        ftp = ftpconnect()
        li = ftp.nlst(ftp_file)

        fp = open(local_zip_file, "wb+")
        bufsize = 1024
        ftp.retrbinary('RETR' + li[0], fp.write, bufsize)
        fp.flush()

        fp.close()
        ftp.quit()

        azip = zipfile.ZipFile(local_zip_file)
        azip.extractall()

    ───────────────────────────────────────────────────────────────────────────────────────────────

    Session
    stopped
    - Press <
    return > to
    exit
    tab
    - Press
    R
    to
    restart
    session
    - Press
    S
    to
    save
    terminal
    output
    to
    file


Network
error: Connection
timed
out

───────────────────────────────────────────────────────────────────────────────────────────────

Session
stopped
- Press <
return > to
exit
tab
- Press
R
to
restart
session
- Press
S
to
save
terminal
output
to
file

Network
error: Connection
timed
out
login as: lizekun
Access
denied
lizekun @ 10.24
.10
.235
's password:
┌────────────────────────────────────────────────────────────────────┐
│                        • MobaXterm
10.4 •                          │
│            (SSH client, X-server and networking tools)             │
│                                                                    │
│ ➤ SSH
session
to
lizekun @ 10.24
.10
.235                              │
│   • SSH
compression: ✔                                            │
│   • SSH - browser: ✔                                            │
│   • X11 - forwarding: ✔  (remote display is forwarded through SSH) │
│   • DISPLAY: ✔  (automatically set on remote server)      │
│                                                                    │
│ ➤ For
more
info, ctrl + click
on
help or visit
our
website           │
└────────────────────────────────────────────────────────────────────┘

Welcome
to
Ubuntu
16.04
.3
LTS(GNU / Linux
4.13
.0 - 38 - generic
x86_64)

*Documentation: https: // help.ubuntu.com
*Management: https: // landscape.canonical.com
*Support: https: // ubuntu.com / advantage

188
packages
can
be
updated.
8
updates
are
security
updates.

** *System
restart
required ** *
Last
login: Thu
Jun
7
10: 03:27
2018
from

10.24
.10
.61
➜  ~ fls
zsh: command
not found: fls
➜  ~ ls
examples.desktop
room
➜  ~ cd
room
➜  room
ls
alphaman.py
edstats.py
make
pnl
src
test_auto.py
auto.py
filter.py
Makefile
py
stats.py
update_room.py
csa.py
lib
one_by_one.py
room_config.py
summ.py
xml
➜  room. / update_room.py
cp / opt / room / *.-rf
room is updated.enjoy
it
➜  room
ls
alphaman.py
edstats.py
make
pnl
src
test_auto.py
auto.py
filter.py
Makefile
py
stats.py
update_room.py
csa.py
lib
one_by_one.py
room_config.py
summ.py
xml
➜  room
vim
py / util / mscic
➜  room. / update_room.py
cp / opt / room / *.-rf
room is updated.enjoy
it
➜  room
vim
py / util / msci_index.py

azip = zipfile.ZipFile(local_zip_file)
azip.extractall()


# try to download ftp_file, save to local_file
# will need to zip
# 注意目录可能不存在，要判断然后建立本地目录


##
# @brief raw_file是msci的原始数据文件，解析，从中抽取数据
#
# @param raw_file
#
# @return 一个数据表的dict
def parse_raw_file(raw_file):
    import pandas as pd
    import numpy as np
    import re

    """
    返回值类似于这样：
    return {
        "table1": table1,
        "table2": table2,
    }
    """


##
# @brief 以CSV文件保存指数权重数据
#
# 文件格式为：逗号为分隔符，第一列为指数日期，第二列为指数代码，第三列为成份股代码，第四列为成份股权重（初始权重），第五列
为收盘权重
#
# @param raw_file 原始数据文件地址
# @param index_weight_file 指数权重的文件地址
#

# @brief 以CSV文件保存指数权重数据
#
# 文件格式为：逗号为分隔符，第一列为指数日期，第二列为指数代码，第三列为成份股代码，第四列为成份股权重（初始权重），第五列
为收盘权重
#
# @param raw_file 原始数据文件地址
# @param index_weight_file 指数权重的文件地址
#
# @return 无
def parse_raw_file_and_save(raw_file, index_weight_file):
    tables = parse_raw_file(raw_file)
    # join tables and save to index_weight_file


if __name__ == "__main__":
    import argparse
    #  from util import tradingday

    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="7941R", help="数据集")
    parser.add_argument("-d", "--date", help="数据日期")
    #  parser.add_argument("-d", "--date", default=tradingday.today(), help="数据日期")
    parser.add_argument("--download", action="store_true", help="设置后下载数据")
    parser.add_argument("--parse_and_save", action="store_true", help="设置后下载数据")

    options = parser.parse_args()

    if options.download:
        download_ftp_file(options.dataset, options.date)

    if options.parse_and_save:
        raw_file = get_local_raw_file(options.dataset, options.date)
        index_weight_file = get_index_weight_file(options.dateset, options.date)
        parse_raw_file_and_save(raw_file, index_weight_file)
-- VISUAL LINE --                                                                                       145,9         Bot
