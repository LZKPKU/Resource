import os
cwd = os.getcwd()
pre = "test/"
#pre = "/data/stock/1min_bin/"
for filename in os.listdir(cwd):
    year = filename[5:9]
    month = filename[9:11]
    dist = pre + year + "/" + month + "/"
    if not os.path.exists(dist):
        os.makedirs(dist)
    cmd = "cp "+filename+" "+dist
    os.system(cmd)