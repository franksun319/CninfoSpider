# coding=utf-8
# __author__='Frank Sun'
# description: 下载CSV列出的年报

import csv
import time
import os

import requests

DST_DIR = 'D:/My Works/上市企业年报/2016中小板年报/'  # 目录格式，D:/dir/
LIST_FILE = 'D:/My Works/上市企业年报/2016中小板年报/招股说明书_002001-002901.csv'

if __name__ == '__main__':
    assert (os.path.exists(DST_DIR)), 'No such destination directory \"' + DST_DIR + '\"!'
    assert (os.path.exists(LIST_FILE)), 'No such list file \"' + LIST_FILE + '\"!'
    if DST_DIR[len(DST_DIR) - 1] != '/':
        DST_DIR += '/'
    # 读取待下载文件列表
    with open(LIST_FILE, 'r') as csv_in:
        reader = csv.reader(csv_in)
        for each in enumerate(reader):
            r = requests.get(each[1][1])
            # 下载成功则保存
            if r.ok:
                with open(DST_DIR + each[1][0], "wb") as file:
                    file.write(r.content)
                    print(str(each[0] + 1) + '/' + len(reader) + ': \"' + each[1][0] + '\" downloaded.')
            # 下载失败则记录日志
            else:
                with open(DST_DIR + 'error.log', 'a') as log_file:
                    log_file.write(time.strftime('[%Y/%m/%d %H:%M:%S] ',
                                                 time.localtime(time.time())) + 'Failed to download \"'
                                   + each[1][0] + '\"\n')
                    print(str(each[0] + 1) + ': \"' + each[1][0] + '\" failed!')
