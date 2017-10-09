# coding=utf-8
# __author__='Frank Sun'
# description: 指定年份、板块、公告类型，生成公告文件列表

import csv
import math
import os
import random
import time

import requests

"""
#################
可改配置，酌情更改
#################
"""
START_DATE = '2004-05-28'  # 首家中小板上市企业的日期
END_DATE = str(time.strftime('%Y-%m-%d'))  # 当前日期，可设置为制定值
OUTPUT_CSV_FILE = 'D:/My Works/上市企业年报/2016中小板年报/2016中小板板首次上市信息' + \
                  '_' + START_DATE.replace('-', '') + '-' + END_DATE.replace('-', '') + '.csv'
# 板块类型：shmb（沪市主板）、szmb（深市主板）、szzx（中小板）、szcy（创业板）
PLATE = 'szzx' + ';'
# 公告类型：category_scgkfx_szsh（首次公开发行及上市）、category_ndbg_szsh（年度报告）、category_bndbg_szsh（半年度报告）
CATEGORY = 'category_scgkfx_szsh' + ';'

##### 固定配置，勿改 #####
URL = 'http://www.cninfo.com.cn/cninfo-new/announcement/query'
HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}
MAX_PAGESIZE = 50
RELOAD_TIMES = 5
SLEEP_COUNT = random.randint(40, 50)


# 参数：页id（没页条目个数由MAX_PAGESIZE控制），是否返回总条目数（bool)
def get_response(page_num, return_total_count=False):
    time_stamp = START_DATE + '~' + END_DATE
    query = {
        'stock': '',
        'searchkey': '',
        'plate': PLATE,
        'category': CATEGORY,
        'trade': '',
        'column': 'szse_sme',
        'columnTitle': '历史公告查询',
        'pageNum': page_num,
        'pageSize': MAX_PAGESIZE,
        'tabName': 'fulltext',
        'sortName': '',
        'sortType': '',
        'limit': '',
        'showTitle': '',
        'seDate': time_stamp,
    }
    result_list = []
    reloading = 0
    while True:
        reloading += 1
        if reloading > RELOAD_TIMES:
            print('Can\'t download data! QUIT!')
            exit(-1)
        r = requests.post(URL, query, HEADER)
        if r.status_code == requests.codes.ok and r.text != '':
            break
    my_query = r.json()
    if return_total_count:
        return my_query['totalRecordNum']
    else:
        for each in my_query['announcements']:
            file_link = 'http://www.cninfo.com.cn/' + str(each['adjunctUrl'])
            file_name = filter_illegal_filename(
                str(each['secCode']) + str(each['secName']) + str(each['announcementTitle']) +
                file_link[-file_link[::-1].find('.') - 1:]  # 最后一项是获取文件类型后缀名
            )
            result_list.append([file_name, file_link])
        return result_list


def filter_illegal_filename(filename):
    illegal_char = {
        ' ': '',
        '*': '',
        '/': '-',
        '\\': '-',
        ':': '-',
        '?': '-',
        '"': '',
        '<': '',
        '>': '',
        '|': '',
        '－': '-',
        '—': '-',
        '（': '(',
        '）': ')',
        'Ａ': 'A',
        'Ｂ': 'B',
        'Ｈ': 'H',
        '，': ',',
        '。': '.',
        '：': '-',
        '！': '_',
        '？': '-',
        '“': '"',
        '”': '"',
        '‘': '',
        '’': ''
    }
    for item in illegal_char.items():
        filename = filename.replace(item[0], item[1])
    return filename


if __name__ == '__main__':
    if os.path.exists(OUTPUT_CSV_FILE):
        os.remove(OUTPUT_CSV_FILE)
    item_count = get_response(1, True)
    begin_pg = 1
    end_pg = int(math.ceil(item_count / MAX_PAGESIZE))
    with open(OUTPUT_CSV_FILE, 'a', newline='', encoding='gb18030') as csv_out:
        writer = csv.writer(csv_out)
        for i in range(begin_pg, end_pg):
            if i % SLEEP_COUNT == 0:
                s = random.randint(8, 15)
                print('Sleeping ' + str(s) + ' seconds ...')
                time.sleep(s)
            writer.writerows(get_response(i))
            print('Page ' + str(i) + '/' + str(end_pg) + ' fetched, it contains items: (' +
                  str(1 + (i - 1) * MAX_PAGESIZE) + '-' + str(i * MAX_PAGESIZE) + ')/' + str(item_count) + '.'
                  )
