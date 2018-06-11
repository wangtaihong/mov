#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-01 18:49:55
# @Author  : taihong (wangtaihong1@gmail.com)
# @Link    : citybrain.top
# @Version : $Id$
import requests
import redis
import re
import threading
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')
import json
import demjson
from bson.objectid import ObjectId
import time
from lxml import etree
sys.path.append('../')
import config
sys.path.append('./')
from DB import mysql_session, Vod
from setting import douban_home_headers, douban_referer_tag_headers, douban_ajax_search_headers, douban_appjs_headers, ua
from DB.RedisClient import rd, rpop
from Utils.proxy import get_proxy, delete_proxy
from Utils.utils import random_str
from Utils.douban_ocr import recognize_url
from pymongo import MongoClient
from urlparse import urlparse
import user_agent

mongo_douban_tvs = MongoClient(
    config.MONGO_HOST, config.MONGO_PORT).zydata.douban_tvs  # 多线程下共享连接?????
mongo_douban_stars = MongoClient(
    config.MONGO_HOST, config.MONGO_PORT).zydata.douban_stars
mongo_douban_tags = MongoClient(
    config.MONGO_HOST, config.MONGO_PORT).zydata.douban_tags

home_url = u'https://movie.douban.com'
tag_url = u'https://movie.douban.com/tag/#/'
tv_url = u'https://movie.douban.com/subject/{id}/'
ajax_list_url = u'https://movie.douban.com/j/new_search_subjects?sort=T&range=0,10&tags={tags}&start=0&genres={genres}&countries={countries}'
verify_users_url = u'https://m.douban.com/rexxar/api/v2/movie/{id}/verify_users?start=0&count=2&ck='
star_url = u'https://movie.douban.com/celebrity/{id}/'

session = requests.Session()
session.adapters.DEFAULT_RETRIES = 5
session.get(url=home_url, headers=douban_home_headers, timeout=10)
timeout = 3
proxy = ''
task_wait = 20
max_step = 5  # 线程数越多，该值就尽量调小 40 / 线程数,,,减少 block
ll = 118318
bid = random_str(10)
session_time = int(time.time())

ad_url = u'https://erebor.douban.com/count/?ad=195767&bid={bid}&unit=dale_movie_tag_bottom_banner&type=impression'
def task_api():
    """
    """
    retry = 5
    i = 0
    while True:
        url = rd.spop(config.doubantv_ajax_task)
        origin_url = url
        if url is None:
            print(u"task_page sleeping....20sec")
            time.sleep(task_wait)
            continue
        # if rd.sismember(config.doubantv_ajax_task_done, url) == True or rd.sismember(config.doubantv_ajax_task_failed, url) == True:
        if rd.sismember(config.doubantv_ajax_task_done, url) == True:
            print(u"already done%s" % url)
            continue
        start = 0
        while True:
            url = re.sub(u'start=(\d*)', 'start=%s' % str(start*20), url)
            print(url)
            r = requests_get(url, headers=douban_referer_tag_headers)
            if r is False or r == None:  # 失败
                print(u'filed task:%s' % url)
                rd.sadd(config.doubantv_ajax_task_failed, url)
                continue
            try:
                r_data = json.loads(r)
            except Exception as e:
                rd.sadd(config.doubantv_ajax_task_failed, url)
                print(r)
                print(str(e))
                update_session()
                time.sleep(task_wait)
                print("-----spider  ben   sleep 10 sec....")
                continue
            if len(r_data['data']) == 0:
                rd.sadd(config.doubantv_ajax_task_done, origin_url)
                print("done%s" % origin_url)
                break
            for x in r_data['data']:
                if rd.sismember(config.douban_tv_done, x['id']) == False and rd.sismember(config.douban_tv_failed, x['id']) == False:
                    add_task = rd.sadd(config.douban_tv_task, x['id'])
                    if add_task == 1:
                        print(
                            "---------------join task.----%s--------------------" % x['id'])
                    else:
                        print(
                            '***********task repeat-******%s********************' % x['id'])
                    rd.sadd(config.douban_tvids, x['id'])
            rd.sadd(config.doubantv_ajax_task_done, origin_url)
            # 每50步更新一次session
            i += 1
            start += 1
            if i % max_step == 0:
                bid = random_str(10)
                session.cookies.set('bid', bid, domain='.douban.com', path='/')
                try:
                    session.get(url=ad_url.format(
                        bid=bid), headers=douban_referer_tag_headers, timeout=timeout)
                except Exception as e:
                    pass
