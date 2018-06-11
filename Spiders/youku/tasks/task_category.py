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
from urlparse import urlparse
from youku.parsers.parse_category_show import parse_category_show

youku_video_types = MongoClient(config.MONGO_HOST, config.MONGO_PORT).zydata.youku_video_types

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

def task_category():
    """
    解析每一个category下的分类，
    并获取该category 每个分类下的全部资源的url任务, 
    这里要做url任务去重
    """
    retry = 5
    i = 0
    while True:
        category = rd.spop(config.yk_category_task)
        if category is None:
            print(u"task_category sleeping....20sec")
            # time.sleep(task_wait)
            return True
        category = json.loads(category)
        print(category)
        r = requests_get(url=category['url'], headers=youku_home_headers,session=session)
        if r is False or r == None:  # 获取详情失败
            print(u'filed task:%s' % category['url'])
            rd.sadd(config.yk_category_task_failed, category['url'])
            continue
        data = parse_category_show(r, category['url'])
        print("category and types:", json.dumps(data))
        if len(data['types']) == 0:  # category下没有type,
            re_sadd = rd.sadd(config.yk_types_task,category['url'])  # types url
        else:
            for ty in data['types']:
                if rd.sismember(config.yk_types_done,data['types'][ty]) == False and rd.sismember(config.yk_types_failed,data['types'][ty]) == False:
                    rd.sadd(config.yk_types_task,data['types'][ty])  # types fetch task
                re_sadd = rd.sadd(config.yk_types_done,data['types'][ty])  # types url　数据库去重
                if re_sadd == 0:  # 去重保存
                    continue
                youku_video_types.insert(
                    {"name": ty, "url": data['types'][ty], "category": category['name']}, check_keys=False)  # save tv types
        rd.sadd(config.yk_category_task_done, category['url'])
        # 每50步更新一次session
        i += 1
        if i % max_step == 0:
            update_session()