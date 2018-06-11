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
from youku.parsers.parse_star_show import parse_star_show
from pymongo import MongoClient


home_url = 'https://www.youku.com/'

session = requests.Session()
session.adapters.DEFAULT_RETRIES = 5
timeout = 3
proxy = ''
task_wait = 5
max_step = 50  # 线程数越多，该值就尽量调小 40 / 线程数,,,减少youku block
youku_star = MongoClient(config.MONGO_HOST, config.MONGO_PORT).zydata.youku_star

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

def task_star():
    """
    明星数据，fetch
    """
    retry = 5
    i = 0
    while True:
        star = rd.spop(config.yk_star_task)
        if star is None:
            print(u"yk_star_task sleeping 20sec....")
            # time.sleep(task_wait)
            return True
        if rd.sismember(config.yk_star_done,star)==True and rd.sismember(config.yk_star_task_field,star)==True:
            continue
        r = requests_get(url=star, headers=youku_home_headers,session=session)
        print("star start:", star)
        data = parse_star_show(r, star)
        if data == None or data == False:  # 优酷数据缺失
            rd.sadd(config.yk_star_task_field, star)
            continue
        print("star done:", data)
        youku_star.insert(data, check_keys=False)  # save tv star
        rd.sadd(config.yk_star_done, star)
        # 每50步更新一次session
        # time.sleep(2)
        i += 1
        if i % max_step == 0:
            update_session()

