# coding:utf-8
import requests
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
import time
sys.path.append('../')
import config
sys.path.append('./')
from setting import youku_home_headers
from DB.RedisClient import rd, rpop
from Utils.proxy import get_proxy, delete_proxy
from Utils.request import requests_get
from pymongo import MongoClient
from youku.parsers.parse_page_fetch import parse_page_fetch

home_url = 'https://www.youku.com/'

session = requests.Session()
session.adapters.DEFAULT_RETRIES = 5
timeout = 3
proxy = ''
task_wait = 5
max_step = 50  # 线程数越多，该值就尽量调小 40 / 线程数,,,减少youku block


def update_session(proxy=None):
    """
    更新session
    proxy:
    """
    if proxy != None:
        delete_proxy(proxy)
    proxy = get_proxy()
    print("proxy:", proxy)
    session = requests.Session()
    session.adapters.DEFAULT_RETRIES = 5
    session.proxies = {"http": "http://{}".format(proxy)}
    retry = 5
    while retry > 0:
        try:
            session.get(url=home_url, headers=youku_home_headers, timeout=10)
            return True
            break
        except requests.exceptions.ProxyError as e:
            print('update_session:', str(e))
        except requests.exceptions.RequestException as e:
            print('update_session:', str(e))
        retry -= 1


def task_page_fetch():
    """
    解析每一个category下每个分类下的每一页list数据中的所有tv url，
    这里要做url任务去重
    """
    retry = 5
    i = 0
    while True:
        page_url = rd.spop(config.yk_page_task)
        # page_url = rd.spop(config.yk_page_failed) #retry
        if page_url is None:
            print(u"task_page_fetch sleeping 20sec....")
            # time.sleep(task_wait)
            return True
        print("page_url",page_url)
        if rd.sismember(config.yk_page_failed,page_url)==True or rd.sismember(config.yk_page_done,page_url)==True:
            continue
        r = requests_get(url=page_url, headers=youku_home_headers,session=session)
        if r is False or r == None:  # 获取详情失败
            print(u'filed task:%s' % page_url)
            rd.sadd(config.yk_page_failed, page_url)
            continue
        print("done task_page_fetch:", page_url)
        data = parse_page_fetch(r, page_url)
        for x in data['yk_get_detailurl_task']:
            rd.sadd(config.yk_get_detailurl_task, json.dumps(x))  # 链接是直接到播放页面的V_show类型
        for x in data['yk_video_detail_task']:
            r_add = rd.sadd(config.yk_video_detail_task, json.dumps(x))  # detail_list_task
        rd.sadd(config.yk_page_done,page_url)
        # 每50步更新一次session
        i += 1
        if i % max_step == 0:
            update_session()

