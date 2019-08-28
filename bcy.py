import requests
from bs4 import BeautifulSoup
import random
import re
import os
import hashlib
import time
import threading
from multiprocessing import Pool #进程池
from concurrent.futures import ThreadPoolExecutor
import json
import pandas as pd
from datetime import datetime


STORAGE_DIR = r'C:\STORAGE\bcy'
USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
]

START_URL = r'https://bcy.net/apiv3/rank/list/itemInfo?p={}&ttype=illust&sub_type=week&date={}'
START_URL1 = r'https://bcy.net/apiv3/rank/list/itemInfo?p=1&ttype=illust&sub_type=week&date=20190828'


def get_datelist(beginDate, endDate):
    date_l=[datetime.strftime(x,'%Y%m%d') for x in list(pd.date_range(start=beginDate, end=endDate))]
    return date_l

DATES = get_datelist('20190720','20190820')

def get_content(url):
    '''
    返回url的html内容
    :param url:
    :return:
    '''
    headers = {
        'User-Agent':random.choice(USER_AGENT_LIST),
    }
    try:
        r = requests.get(url,headers=headers,timeout=2)
    except:
        return None
    if r.status_code == 200:
        return r.json()



def get_pic_url(dic):
    if not dic:
        return []
    item_infos = dic.get('data').get('top_list_item_info')
    urls = []
    for item in item_infos:
        url = item.get('item_detail').get('cover')
        urls.append(url)
    return urls

def get_md5(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()

def download_picture(future):
    '''
    根据url，下载图片，保存到指定位置
    :param url:
    :return:
    '''
    headers = {
        'User-Agent':random.choice(USER_AGENT_LIST),
    }
    urls = future.result()
    for url in urls:
        try:
            r  = requests.get(url,headers=headers,timeout=3)
        except:
            continue
        filepath = os.path.join(STORAGE_DIR,get_md5(url)+'.jpg')
        time.sleep(random.randint(1,4))
        if r.status_code == 200 and not os.path.exists(filepath):
            f = open(filepath,'wb')
            f.write(r.content)
            f.close()
            print('{} download success'.format(filepath))



def bcy(url):
    return get_pic_url(get_content(url))

if __name__ == '__main__':
    n = os.cpu_count()

    excutor = ThreadPoolExecutor(n)

    for date in DATES:
        for i in range(1,10):
            url = START_URL.format(i,date)
            excutor.submit(bcy,url).add_done_callback(download_picture)
    excutor.shutdown()

    print('----------------END----------------------')