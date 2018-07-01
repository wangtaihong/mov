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
        save_to_path = u'E:/sx_posters/'
        posters_path = u'E:/posters/'
        contents = mongo_conn.contents.find({"category": {"$in": [
            u"电视剧", u"电影", u"综艺", u"少儿", u"动漫", u"动画片",u"剧集",u"连续剧"]}, 'relationship': {'$elemMatch': {"platform": platform}}})
        for c in contents:
        	posters = mongo_conn.posters.find({"content_id":str(c['_id']),"file_path":{"$exists":True}})
        	for p in posters:
				if not os.path.exists(posters_path+p['file_path']):
					print("file not exists:%s"%p['file_path'])
					p['_id'] = str(p['_id'])
					rd.sadd("filter_posterfailed",json.dumps(p))
					continue
        		try:
        			os.makedirs(re.search('(.*/)',save_to_path+p['file_path']).group(1))
        		except Exception as e:
        			#print(str(e))
        			pass
        		copyfile(posters_path+p['file_path'], save_to_path+p['file_path'])
        		print("done.   %s"%posters_path+p['file_path'])

if __name__ == '__main__':
	p_filter = PostersFilter()
	p_filter.filter_local("sx")
