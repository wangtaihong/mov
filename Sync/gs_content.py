#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-14 08:37:01
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

import os
import re
import sys
import threading
reload(sys)
sys.setdefaultencoding('utf8')
import json
sys.path.append('../')
import config
sys.path.append('./')
from pymongo import MongoClient
from bson.objectid import ObjectId
from DB.NewVodData import NewVodData
from DB.GSCmscontent import GSCmscontent
from DB.mysql_session import DBSession
import Levenshtein as lst
from sqlalchemy.orm import scoped_session


def sync(offset,size):
    mongo = MongoClient(config.MONGO_HOST, config.MONGO_PORT).zydata
    mongo_contents = mongo.contents
    mongo_stars = mongo.stars
    succ = 0
    db_session = scoped_session(DBSession)
    print(offset,size,db_session,mongo_contents)
    # contents = db_session.query(GSCmscontent).filter((GSCmscontent.series_flag=='100') | (GSCmscontent.series_flag=='110')).offset(offset).limit(limit).all()
    # count = db_session.query(GSCmscontent).filter().offset(offset).limit(limit).count()
    # print("count:",count)
    this_limit = 10000
    this_offset = offset
    step = size/this_limit
    for x in xrange(1,step+1):
        contents = db_session.query(GSCmscontent).filter((GSCmscontent.series_flag=='100') | (GSCmscontent.series_flag=='110') & GSCmscontent.unknow_1==None).offset(x*this_offset).limit(this_limit).all()
        for item in contents:
            if item.name == None or item.name == "":
                continue
            regx_name = item.name.replace("(","\(").replace(")","\)").replace(".","\.").replace("[","\[").replace("]","\]").replace("*","\*").replace("?","\?").replace("+","\+")
            regx = re.compile(u"^"+regx_name+".*", re.IGNORECASE)
            mongo_rs = mongo_contents.find({"title": regx})
            # nlts = [{"nlt": lst.ratio(item.name, mon['title']), "_id":mon["_id"], "title":mon["title"],"name":item.name}
            #         for mon in mongo_rs if lst.ratio(item.name, mon['title']) >= 0.80]
            ls = []
            lss = {}
            # 100：普通点播 110：连续剧父集 120：连续剧子集
            for mon in mongo_rs:
                sim = lst.ratio(item.name, mon['title'])
                print("-sim:----%s------------"%sim)
                # if sim < 0.7 and item.series_flag=='120':
                if sim < 0.65:
                    # print("-sim:%s----%s--------%s----"%(sim,item.name,mon['title']))
                    # print("-sim:----%s------------"%sim)
                    continue
                ls.append(sim)
                lss[sim] = mon.get("_id")
            if len(ls) == 0:
                continue
            ls.sort()
            try:
                _id = lss[ls[-1]]
            except Exception as e:
                _id = lss[ls[0]]
            c = mongo_contents.find({"_id":_id})
            # if item.PRODUCE_DATE == None and mon.get("published_at"):
            # 	item.PRODUCE_DATE = mon['published_at']
            if item.summary == None and c[0].get("summary"):
            	# item.summary = c[0]['summary']
                pass
            if item.tag == None and c[0].get("tags"):
            	item.tag = c[0]['tags']
            if item.year == None and c[0].get("year"):
            	item.year = c[0]['year']
            if item.show_time == None and c[0].get("release_date"):
            	item.show_time = re.search(u'(\d{4}-\d{2}-\d{2})',c[0]['release_date']).group(1) if re.search(u'(\d{4}-\d{2}-\d{2})',c[0]['release_date']) else None
            if item.alias == None and c[0].get("alias"):
            	item.alias = c[0]['alias']
            if item.country == None and c[0].get("producer_country"):
            	item.country = c[0]['producer_country']
            elif c[0].get("area"):
                item.country = c[0]['area']
            if item.actor == None and c[0].get("starring"):
            	item.actor = c[0]['starring']
            if item.director == None and c[0].get("directors"):
                item.director = c[0]['directors']
            if item.language == None and c[0].get("language"):
            	item.language = c[0]['language']
            item.unknow_1 = 'yes'
            # print("---%s--------%s----"%(item.name,c[0]['title']))
            print("-------done--------")
            succ+=1
            db_session.add(item)
            db_session.commit()
    db_session.commit()
    db_session.close()
    print(size,succ)


def task():
    succ = 0
    db_session = scoped_session(DBSession)
    print(db_session)
    # count = db_session.query(GSCmscontent).filter((GSCmscontent.series_flag=='100') | (GSCmscontent.series_flag=='110')).count()
    # count = db_session.query(GSCmscontent).filter().count()
    count = db_session.query(GSCmscontent).count()
    print("count:",count)
    thr = 5
    block_len = count/thr
    print(block_len,count)
    for x in xrange(0,thr+1):
        offset = x*block_len
        print(offset,block_len)
        t = threading.Thread(target=sync,args=(offset,block_len))
        # t.setDaemon(True)
        t.start()

if __name__ == '__main__':
    task()