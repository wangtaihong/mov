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
from urlparse import urlparse
from pymongo import MongoClient

youku_category = MongoClient(config.MONGO_HOST, config.MONGO_PORT).zydata.youku_category

home_url = 'https://www.youku.com/'
category_url = 'http://list.youku.com/category/video'

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

def get_category():
    """获取分类,做种子"""
    start = 1
    retry = 5
    print('get_category')
    while retry > 0:
        try:
            r = requests_get(url=category_url,headers=youku_home_headers,timeout=timeout,session=session)
            page = etree.HTML(r)
            lis = page.xpath(
                u'//label[contains(text(),"分类：")]/following-sibling::ul/li')
            o = urlparse(category_url)
            host = o.scheme + '://' + o.netloc
            categories = []
            for x in xrange(1, len(lis)):
                categories.append({"name": lis[x].find(
                    'a').text, 'url': host + lis[x].find('a').get('href')})
                # categories[lis[x].find('a').text] = host + lis[x].find('a').get('href')
            print("categories:", json.dumps(categories))
            # categories = {lis[x].find('a').text : host + lis[x].find('a').get('href') for x in xrange(1,len(lis)) if lis[x].find('a')!=None}  #
            if len(categories) == 0:
                update_session(proxy)
                continue
            for x in categories:
                if rd.sismember(config.yk_category_task_done,x['url'])==False and rd.sismember(config.yk_category_task_failed,x['url'])==False:
                    task_sadd = rd.sadd(config.yk_category_task,json.dumps(x))  # 种子
                re_sadd = rd.sadd(config.yk_category_url, json.dumps(x))  # 种子
                if re_sadd != 0:  # 去重保存
                    youku_category.insert(x, check_keys=False)  # save categories
            return True
        except requests.exceptions.ProxyError as e:
            print("ttt", str(e))
            update_session(proxy)
            # retry = 5
        # except requests.exceptions.InvalidProxyURL as e:
        except requests.exceptions.RequestException as e:
            print("xxx", str(e))
            update_session(proxy)
            # retry = 5
        retry -= 1
    start += 1
    if start % 20 == 0:  # 每50步更新一次session
        update_session()