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
from lxml import etree
from setting import youku_home_headers
from DB.RedisClient import rd, rpop
from Utils.proxy import get_proxy, delete_proxy
from Utils.request import requests_get
from youku.parsers.parse_all_url import parse_all_url

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


def cleanup(*args):
    """
    清除指定的redis list数据
    """
    for x in args:
        rd.delete(x)

def spider_seed(category_url=category_url):
    """获取分类,做种子"""
    start = 1
    retry = 5
    while retry > 0:
        try:
            r = requests_get(url=category_url,
                             headers=youku_home_headers, timeout=timeout,session=session)
            page = etree.HTML(r)
            category_el = page.xpath(u'//div[@id="filterPanel"]/div[1]/ul/li')
            categories = []
            for x in category_el:
                if x.find("a") != None:
                    categories.append({"url": list_url + x.find("a").get("href"),"title": x.find("a").text.replace(" ", "").replace("\n", "")})
                else:
                    categories.append({"url": category_url, "title": x.find("span").text.replace(" ", "").replace("\n", "")})
            print(json.dumps(categories))
            # return categories
            for x in categories:
                if rd.sismember(config.yk_types_done,x['url']) == False and rd.sismember(config.yk_types_failed,x['url']) == False:
                    rd.sadd(config.yk_types_task, x['url'])
                print(x['url'])
                rr = requests_get(url=x["url"], headers=youku_home_headers, timeout=timeout)
                urls = parse_all_url(x["url"],r=rr)  # 获取该category下的urls
                if urls == False:
                    re.sadd(config.yk_getpage_task, x["url"])  #获取该url下的urls失败
                    continue
                for xx in urls:  # 遍历每一个url,得到该页面的全部url
                    if rd.sismember(config.yk_types_done,xx['url']) == False and rd.sismember(config.yk_types_failed,xx['url']) == False:
                        rd.sadd(config.yk_types_task, xx['url'])
                    print(xx['url'])
                    rr = requests_get(url=x["url"], headers=youku_home_headers, timeout=timeout)
                    rr_urls = parse_all_url(xx["url"],r=rr)
                    if rr_urls == False:
                        re.sadd(config.yk_getpage_task, x["url"])  #获取该url下的urls失败
                        continue
                    for xxx in rr_urls:
                        print(xxx['url'])
                        if rd.sismember(config.yk_types_done,xxx['url']) == False and rd.sismember(config.yk_types_failed,xxx['url']) == False:
                            rd.sadd(config.yk_types_task, xxx['url'])
            return True
        except requests.exceptions.ProxyError as e:
            print("ttt", str(e))
            update_session(proxy)
        except requests.exceptions.RequestException as e:
            print("xxx", str(e))
            update_session(proxy)
            # retry = 5
        retry -= 1
    start += 1
    if start % 20 == 0:  # 每50步更新一次session
        update_session()
