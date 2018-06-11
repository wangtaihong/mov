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
from youku.parsers.parse_category_show import parse_category_show

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

def task_types_fetch():
    retry = 5
    i = 0
    while True:
        type_url = rd.spop(config.yk_types_task)
        if type_url is None:
            print(u"yk_types_task sleeping 20sec....")
            return True
        if rd.sismember(config.yk_types_failed,type_url)==True or rd.sismember(config.yk_types_done,type_url)==True:
            continue
        r = requests_get(url=type_url, headers=youku_home_headers,session=session)
        if r is False or r == None:
            print(u'filed task:%s' % type_url)
            rd.sadd(config.yk_types_failed, type_url)
            continue
        pages = parse_category_show(r, type_url)
        print("task_types_fetch data:", pages)
        for page in xrange(1, int(pages['pages'])):
            page_url = re.sub(
                '(\.html.*)', '_s_1_d_1_p_{page}.html'.format(page=page), type_url)
            print("task_types_fetch for :", page_url)
            if rd.sismember(config.yk_page_failed,page_url)==False and rd.sismember(config.yk_page_done,page_url)==False:
                rd.sadd(config.yk_page_task, page_url)
        rd.sadd(config.yk_types_done,type_url)
        # 每50步更新一次session
        i += 1
        if i % max_step == 0:
            update_session()