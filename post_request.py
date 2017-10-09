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
*****************
可改配置，酌情更改
*****************
"""
START_DATE = '2004-05-28'  # 首家中小板上市企业的日期
END_DATE = str(time.strftime('%Y-%m-%d'))  # 默认当前日期，可设置为制定值
OUT_DIR = 'D:/My Works/上市企业年报/2016中小板年报/'
OUTPUT_FILENAME = '2016中小板板首次上市信息'
# 板块类型：shmb（沪市主板）、szmb（深市主板）、szzx（中小板）、szcy（创业板）
PLATE = 'szzx;'
# 公告类型：category_scgkfx_szsh（首次公开发行及上市）、category_ndbg_szsh（年度报告）、category_bndbg_szsh（半年度报告）
CATEGORY = 'category_scgkfx_szsh;'

"""
*************
固定配置，勿改
*************
"""
URL = 'http://www.cninfo.com.cn/cninfo-new/announcement/query'
HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}
MAX_PAGESIZE = 50
MAX_RELOAD_TIMES = 5
RESPONSE_TIMEOUT = 10
if OUT_DIR[len(OUT_DIR) - 1] != '/':
    OUT_DIR += '/'
ERROR_LOG = OUT_DIR + 'error.log'
OUTPUT_CSV_FILE = OUT_DIR + OUTPUT_FILENAME.replace('/', '') + '_' + \
                  START_DATE.replace('-', '') + '-' + END_DATE.replace('-', '') + '.csv'


# 参数：页id（没页条目个数由MAX_PAGESIZE控制），是否返回总条目数（bool)
def get_response(page_num, return_total_count=False):
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
        'seDate': START_DATE + '~' + END_DATE,
    }
    result_list = []
    reloading = 0
    while True:
        reloading += 1
        if reloading > MAX_RELOAD_TIMES:
            return []
        elif reloading > 1:
            _sleeping(random.randint(5, 10))
            print('... reloading: the ' + str(reloading) + ' round ...')
        try:
            r = requests.post(URL, query, HEADER, timeout=RESPONSE_TIMEOUT)
        except Exception as e:
            print(e)
            continue
        if r.status_code == requests.codes.ok and r.text != '':
            break
    my_query = r.json()
    try:
        r.close()
    except Exception as e:
        print(e)
    if return_total_count:
        return my_query['totalRecordNum']
    else:
        for each in my_query['announcements']:
            file_link = 'http://www.cninfo.com.cn/' + str(each['adjunctUrl'])
            file_name = _filter_illegal_filename(
                str(each['secCode']) + str(each['secName']) + str(each['announcementTitle']) +
                file_link[-file_link[::-1].find('.') - 1:]  # 最后一项是获取文件类型后缀名
            )
            result_list.append([file_name, file_link])
        return result_list


def _log_error(err_msg):
    err_msg = str(err_msg)
    print(str(err_msg))
    with open(ERROR_LOG, 'a', encoding='gb18030') as err_writer:
        err_writer.write(err_msg + '\n')


def _sleeping(sec):
    if type(sec) == int:
        print('... sleeping ' + str(sec) + ' second ...')
        time.sleep(sec)


def _filter_illegal_filename(filename):
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
    assert (os.path.exists(OUT_DIR)), 'Such directory \"' + OUT_DIR + "\" does not exists!"
    item_count = get_response(1, True)
    assert (item_count != []), 'Please restart this script!'
    begin_pg = 1
    end_pg = int(math.ceil(item_count / MAX_PAGESIZE))
    print('Page count: ' + str(end_pg) + '; item count: ' + str(item_count) + '.')
    time.sleep(2)
    with open(OUTPUT_CSV_FILE, 'w', newline='', encoding='gb18030') as csv_out:
        writer = csv.writer(csv_out)
        for i in range(begin_pg, end_pg + 1):
            row = get_response(i)
            if not row:
                _log_error('Failed to fetch page #' + str(i) +
                           ': exceeding max reloading times (' + str(MAX_RELOAD_TIMES) + ').')
                continue
            else:
                writer.writerows(row)
                last_item = i * MAX_PAGESIZE if i < end_pg else item_count
                print('Page ' + str(i) + '/' + str(end_pg) + ' fetched, it contains items: (' +
                      str(1 + (i - 1) * MAX_PAGESIZE) + '-' + str(last_item) + ')/' + str(item_count) + '.')
