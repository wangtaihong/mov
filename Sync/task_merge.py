#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-10 20:09:00
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

import os
import time
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
sys.path.append('../')
import config
sys.path.append('./')
from pymongo import MongoClient
from bson.objectid import ObjectId
from DB.NewVodData import NewVodData
from DB.TestCmscontent import TestCmscontent
from DB.mysql_session import DBSession
import Levenshtein as lst
from sqlalchemy.orm import scoped_session
import hashlib
import jieba
from DB.RedisClient import rd, rpop
from DB.MongodbClient import mongo_conn
import threading
from merge import Merge

mongo_youku_videos = mongo_conn.youku_videos
mongo_youku_star = mongo_conn.youku_star
mongo_letv_tvs = mongo_conn.letv_tvs
mongo_letv_stars = mongo_conn.letv_stars
mongo_douban_tvs = mongo_conn.douban_tvs
mongo_douban_stars = mongo_conn.douban_stars
mongo_stars = mongo_conn.stars
mongo_contents = mongo_conn.contents
mongo_posters = mongo_conn.posters
mongo_categories = mongo_conn.categories

"""清洗豆瓣明星"""
def merge_star():
    m = Merge()
    m.merge_star()

"""清洗优酷明星"""
def task_merge_youkustar():
    m = Merge()
    while True:
        task = rd.spop("task_merge_youkustar")
        if task:
            m.merge_youkustar(query={"_id":ObjectId(task)})
        else:
            break

def merge_youkustar():
    stars = mongo_youku_star.find()
    for item in stars:
        print("put task",item.get("_id"))
        rd.sadd("task_merge_youkustar",str(item.get("_id")))

    for i in range(20):
        t = threading.Thread(target=task_merge_youkustar,)
        # t.setDaemon(True)
        t.start()

"""清洗乐视明星"""
def task_merge_letvstar():
    m = Merge()
    while True:
        task = rd.spop("task_merge_letvstar")
        if task:
            m.merge_letvstar(query={"_id":ObjectId(task)})
        else:
            break

def merge_letvstar():
    stars = mongo_letv_stars.find()
    for item in stars:
        print("put task",item.get("_id"))
        rd.sadd("task_merge_letvstar",str(item.get("_id")))

    for i in range(20):
        t = threading.Thread(target=task_merge_letvstar,)
        # t.setDaemon(True)
        t.start()

"""清洗豆瓣shipin"""
def merge_doubanvideo():
    douban = mongo_douban_tvs.find(no_cursor_timeout=True)
    for item in douban:
        print("put task",item.get("_id"))
        rd.sadd("task_merge_doubanvideo",str(item.get("_id")))

    for i in range(20):
        t = threading.Thread(target=task_merge_doubanvideo,)
        # t.setDaemon(True)
        t.start()

def task_merge_doubanvideo():
    m = Merge()
    while True:
        task = rd.spop("task_merge_doubanvideo")
        if task:
            m.merge_doubanvideo(query={"_id":ObjectId(task)})
        else:
            break

"""清洗乐视视频"""
def task_merge_letvvideo():
    m = Merge()
    while True:
        task = rd.spop("task_merge_letvvideo")
        if task:
            m.merge_letvvideo(query={"_id":ObjectId(task)})
        else:
            break

def merge_letvvideo():
    stars = mongo_letv_tvs.find()
    for item in stars:
        print("put task",item.get("_id"))
        rd.sadd("task_merge_letvvideo",str(item.get("_id")))

    for i in range(20):
        t = threading.Thread(target=task_merge_letvvideo,)
        # t.setDaemon(True)
        t.start()

"""清洗优酷视频"""
def task_merge_youku_videos():
    m = Merge()
    while True:
        task = rd.spop("task_merge_youku_videos")
        if task:
            m.merge_youku_videos(query={"_id":ObjectId(task)})
        else:
            break

def merge_youku_videos():
    stars = mongo_youku_videos.find()
    for item in stars:
        print("put task",item.get("_id"))
        rd.sadd("task_merge_youku_videos",str(item.get("_id")))

    for i in range(30):
        t = threading.Thread(target=task_merge_youku_videos,)
        # t.setDaemon(True)
        t.start()

def groupCategories():
    for i in range(1):
        t = threading.Thread(target=task_categories,)
        # t.setDaemon(True)
        t.start()

def task_categories():
    m = Merge()
    m.groupCategories(query={})

def rm_unknown():
    for i in range(10):
        t = threading.Thread(target=task_rm_unknown,)
        # t.setDaemon(True)
        t.start()

def task_rm_unknown():
    m = Merge()
    m.rm_unknown(query={})


def clean_category():
    for i in range(10):
        t = threading.Thread(target=task_clean_category,)
        # t.setDaemon(True)
        t.start()

def task_clean_category():
    m = Merge()
    m.clean_category(query={})


def task_groupLanguageAndProducer_country():
    m = Merge()
    m.groupLanguageAndProducer_country(query={})

def download_starts_avtar():
    for i in range(1):
        t = threading.Thread(target=task_download_starts_avtar,)
        # t.setDaemon(True)
        t.start()

def task_download_starts_avtar():
    m = Merge()
    m.download_starts_avtar(query={})

if __name__ == '__main__':
    '''
    数据带上目标网站来源id.

    1,明星数据清洗:
    第一步，清洗豆瓣明星
    第二步，清洗优酷
    第三步，清洗乐视
    '''

    '''
    2,影视数据清洗:每一条数据清洗过程都把明星与明星库关联，海报单独抽出来存到海报库，形成关联关系
    第一步，清洗豆瓣
    第二部，清洗乐视
    第四部，清洗优酷
    '''

    '''
    3,category信息:
    从清洗好的内容库抽出来存到category库,偶caozuo
    
    '''

    t = time.time()
    # merge()
    # fixyoukuid()
    # fixletv()

    # merge_star()
    # merge_youkustar()
    # merge_letvstar()
    
    #merge_doubanvideo()
    # merge_letvvideo()
    # merge_youku_videos()

    # groupCategories()   #偶操作....

    # task_download_starts_avtar()
    # rm_unknown()
    # clean_category()
    # task_groupLanguageAndProducer_country()
    m = Merge()
    m.fix_youku_starId()
    print(time.time()-t)
