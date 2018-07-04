#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-07-01 20:37:45
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    :
# @Version : $Id$

import os, os.path
from shutil import copyfile
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
from DB.RedisClient import rd, rpop
from DB.MongodbClient import mongo_conn
from Utils.utils import parse_regx_char, area_process, split_space, parse_simple


class PostersFilter(object):
    """docstring for PostersFilter"""

    def __init__(self, **args):
        # super(PostersFilter, self).__init__()
        # self.arg = arg
        pass

    def filter_local(self, platform):
        save_to_path = u'E:/gs/gs_posters_f1/'
        filter_path = u'E:/gs/gs_posters/'
        posters_path = u'E:/data/v0703/'
        contents = mongo_conn.contents.find({"category": {"$in": [
            u"电视剧", u"电影", u"综艺", u"少儿", u"动漫", u"动画片",u"剧集",u"连续剧"]}, 'relationship': {'$elemMatch': {"platform": platform}}},no_cursor_timeout=True)
        print(contents.count())
        i = 0
        for c in contents:
            posters = mongo_conn.posters.find({"content_id":str(c['_id'])},no_cursor_timeout=True)
            if posters.count()>0:
                i +=1
            for p in posters:
                if not p.get("file_path"):
                    # p['_id'] = str(p["_id"])
                    # rd.sadd("image_v",json.dumps(p))
                    # print(p)
                    exists = mongo_conn.posters.find({"content_id":str(c['_id']),"url":p['url'],"file_path":{"$exists":True}})
                    if exists.count()>0:
                        # rr = mongo_conn.posters.remove({"_id":p['_id']})
                        print(p)
                    continue
                if not os.path.exists(posters_path+p['file_path']):
                    print("failed     file not exists:       %s"%p['file_path'])
                    # mongo_conn.posters.update({'_id': p['_id']}, {'$unset': {'file_path':1}}, multi=True)
                    continue
                if os.path.exists(save_to_path+p['file_path']) or os.path.exists(filter_path+p['file_path']):
                    print("alredy      exists.      %s"%p['file_path'])
                    continue
                try:
                    os.makedirs(re.search('(.*/)',save_to_path+p['file_path']).group(1))
                except Exception as e:
                    #print(str(e))
                    pass
                copyfile(posters_path+p['file_path'], save_to_path+p['file_path'])
                print("done.        %s"%save_to_path+p['file_path'])
        print(i,contents.count())

    def filter_dbposter(self):
        posters = mongo_conn.posters.find({"file_path":{"$exists":False},"hide":{"$exists":False}},no_cursor_timeout=True)
        for p in posters:
            exists = mongo_conn.posters.find({"content_id":p['content_id'],"url":p['url'],"file_path":{"$exists":True}},no_cursor_timeout=True)
            if exists.count()>0:
                rr = mongo_conn.posters.update({'_id': p['_id']}, {'$set': {'hide':"1"}})
                print(rr,p)
            else:
                __exists = mongo_conn.posters.find({"content_id":p['content_id'],"url":p['url'],"file_path":{"$exists":False}},no_cursor_timeout=True)
                if __exists.count()>0:
                    rr = mongo_conn.posters.update({'_id': p['_id']}, {'$set': {'hide':"1"}})
                    print(rr,p)

if __name__ == '__main__':
    p_filter = PostersFilter()
    p_filter.filter_local("gs")
