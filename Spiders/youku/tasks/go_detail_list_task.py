# coding:utf-8
import requests
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
from youku.parsers.parse_detail_list_page import parse_detail_list_page

youku_videos = MongoClient(config.MONGO_HOST, config.MONGO_PORT).zydata.youku_videos
# youku_videos.create_index("title")
home_url = 'https://www.youku.com/'
category_url = 'http://list.youku.com/category/video'
list_url = 'http://list.youku.com'

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

def go_detail_list_task():
    retry = 5
    i = 0
    while True:
        q = rd.spop(config.yk_video_detail_task)
        if q is None:
            print(u"yk_video_detail_task sleeping 20 sec....")
            # time.sleep(task_wait)
            return True
        detail_url = json.loads(q)
        #if rd.sismember(config.yk_video_detail_failed,q)==True or rd.sismember(config.yk_video_detail_done,detail_url['url'])==True:
        if rd.sismember(config.yk_video_detail_done,detail_url['url'])==True:
            print("pass",detail_url['url'])
            continue
        # r = go_detail_list_page(detail_url)
        r = requests_get(detail_url['url'], headers=youku_home_headers)
        d = parse_detail_list_page(r, detail_url['url'])
        data = d['data']
        if data is False or data == None:
            rd.sadd(config.yk_video_detail_failed, q)
            continue
        for x in d['stars']:
            rd.sadd(config.yk_star_task, x)  # 明星采集队列,redis set特性去重
        print('detail_url done:', detail_url['url'], data)
        done = rd.sadd(config.yk_video_detail_done, detail_url['url'])  # finished
        #if done == 1:
        youku_videos.insert(data, check_keys=False)  # save tv data
        # 每50步更新一次session
        # time.sleep(2)
        i += 1
        if i % max_step == 0:
            update_session()


def url_format(url):
    """
    //v.youku.com/v_show/id_XMzA5NTA1ODg2MA==.html?s=bc2a0ca1a64b11e6b9bb
    http://v.youku.com/v_show/id_XMzA5NTA1ODg2MA==.html
    """
    url = re.sub('http:', '', url)
    return "http:" + re.sub('(\.html.*)', '.html', url)