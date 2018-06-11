# coding:utf-8
import requests
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
import time
from lxml import etree
sys.path.append('../')
import config
sys.path.append('./')
from setting import youku_home_headers
from DB.RedisClient import rd, rpop
from Utils.proxy import get_proxy, delete_proxy
from Utils.request import requests_get
from youku.parsers.parse_tv_show import parse_tv_show

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

def get_detailurl_task():
    """
    get_detailurl_task yk_get_detailurl_task 解析到detail_list页面的url
    """
    retry = 5
    i = 0
    while True:
        q = rd.spop(config.yk_get_detailurl_task)
        if q is None:
            print(u"yk_get_detailurl_task sleeping 20 sec")
            # time.sleep(task_wait)
            return True
        to_detail_url = json.loads(q)
        headers = youku_home_headers
        headers['Referer'] = to_detail_url['Referer']
        # if rd.sismember(config.yk_get_detailurl_done,q)==True or rd.sismember(config.yk_get_detailurl_field,q)==True:
        if rd.sismember(config.yk_get_detailurl_done,q)==True:
            print("pass")
            continue
        r = requests_get(to_detail_url['url'], headers=headers)
        # headers = youku_home_headers
        # headers['Referer'] = to_detail_url['url']
        # try:
        #     session.get('http://cmstool.youku.com/cms/player/userinfo/user_info?specialTest=test&client=pc&callback=tuijsonp1',headers=headers)
        # except Exception as e:
        #     pass
        print("to_detail_url",to_detail_url['url'])
        detail_url = parse_tv_show(r, to_detail_url['url'])
        print("detail_url:",detail_url)
        if detail_url == False or detail_url==None:
            rd.sadd(config.yk_get_detailurl_field, q)
            continue
        # if rd.sismember(config.yk_video_detail_done,json.dumps({"url": detail_url, 'Referer': to_detail_url['url']}))==False:
        if rd.sismember(config.yk_video_detail_done,detail_url)==False:
            red = rd.sadd(config.yk_video_detail_task, json.dumps({"url": detail_url, 'Referer': to_detail_url['url']}))
            if red==1:
                print("yes")
        rd.sadd(config.yk_get_detailurl_done,q)
        # rd.sadd(config.yk_video_detail_task_, json.dumps({"url": detail_url, 'Referer': to_detail_url['url']}))
        # time.sleep(2)
        i += 1
        if i % max_step == 0:
            update_session()