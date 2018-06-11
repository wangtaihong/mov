#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-25 16:59:37
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
from DB.GDCmscontent import GDCmscontent
from DB.mysql_session import DBSession
from Utils.utils import parse_regx_char, area_process, title_preprocess, title_preprocess_seed
import Levenshtein as lst
from sqlalchemy.orm import scoped_session
from sqlalchemy import desc, asc
from gevent import monkey; monkey.patch_all()
import gevent
import threading

def sync(arges):
    print("haha")
    offset = arges["offset"]
    size = arges['size']
    mongo = MongoClient(config.MONGO_HOST, config.MONGO_PORT).zydata
    mongo_contents = mongo.contents
    mongo_stars = mongo.stars
    succ = 0
    total = 0
    #db_session = scoped_session(DBSession)
    # contents = db_session.query(GDCmscontent).filter((GDCmscontent.series_flag=='100') | (GDCmscontent.series_flag=='110')).offset(offset).limit(limit).all()
    # count = db_session.query(GDCmscontent).filter().offset(offset).limit(limit).count()
    # print("count:",count)
    this_limit = 3000
    this_offset = offset
    step = (size-offset)/this_limit
    print('this_offset:',this_offset,size,size/this_limit)
    for x in xrange(1,step+1):
        print("offset:",offset+x*this_limit,this_limit)
        db_session = scoped_session(DBSession)
        print(offset + (x-1)*this_limit,x*this_limit + offset)
        contents = dict()
        contents = db_session.query(GDCmscontent).filter(
            (
                (GDCmscontent.series_flag=='100') | (GDCmscontent.series_flag=='110')
            ) & (GDCmscontent.id >= offset + (x-1)*this_limit) & (GDCmscontent.id <= x*this_limit + offset) & (GDCmscontent.data_flag==None)).order_by(asc(GDCmscontent.id)).all()
        # contents = db_session.query(GDCmscontent).filter(GDCmscontent.id == "4200").order_by(asc(GDCmscontent.id)).all()
        for item in contents:
            print(dict(item))
            return True
            if item.name == None or item.name == "":
                continue
            total+=1
            regx_name = title_preprocess_seed(item.name)
            regx_name = parse_regx_char(regx_name)
            regx_name = u'.*' + regx_name.replace(u'-','.*') + ".*"
            print("-----%s---------%s-----"%(item.name,regx_name))
            regx = re.compile(regx_name, re.IGNORECASE)
            mongo_rs = mongo_contents.find({"title": regx})
            ls = []
            lss = {}
            # 100：普通点播 110：连续剧父集 110：连续剧子集
            for mon in mongo_rs:
                sim = lst.ratio(title_preprocess(item.name), title_preprocess(mon['title']))
                print("-sim:----%s----%s---%s----regx_name:%s----"%(sim,item.name,mon['title'],regx_name))
                if sim < 0.80:
                    continue
                ls.append(sim)
                lss[sim] = mon.get("_id")
                if sim==1.0:
                    break
            if len(ls) == 0:
                item.data_flag = '2'
                db_session.add(item)
                db_session.commit()
                continue
            ls.sort()
            try:
                _id = lss[ls[-1]]
            except Exception as e:
                _id = lss[ls[0]]
            c = dict()
            c = mongo_contents.find({"_id":_id})
            print(_id)
            print("after--%s---succ:%s---total:%s---%s---%s----%s----%s---%s-----%s-------%s-------%s------%s--"%(item.id,succ,total,item.name,item.country,item.alias,item.actor,item.director,item.language,item.show_time,item.tag,item.summary))
            # if item.PRODUCE_DATE == None and mon.get("published_at"):
            # 	item.PRODUCE_DATE = mon['published_at']
            if item.summary == None and c[0].get("summary"):
            	item.summary = c[0]['summary']
                # pass
            if item.tag == None and c[0].get("tags"):
            	item.tag = c[0]['tags']
            if item.year == None and c[0].get("year"):
            	item.year = c[0]['year']
            if item.show_time == None and c[0].get("release_date"):
            	item.show_time = re.search(u'(\d{4}-\d{2}-\d{2})',c[0]['release_date']).group(1) if re.search(u'(\d{4}-\d{2}-\d{2})',c[0]['release_date']) else None
            if item.alias == None and c[0].get("alias"):
            	item.alias = c[0]['alias']
            # if item.country == None and c[0].get("producer_country"):
            if c[0].get("producer_country"):
            	item.country = c[0]['producer_country']
            if c[0].get("area"):
                item.region = c[0]['area']
            elif c[0].get('producer_country'):
                item.region = c[0]['producer_country']
            if item.actor == None and c[0].get("starring"):
            	item.actor = c[0]['starring']
            if item.director == None and c[0].get("directors"):
                item.director = c[0]['directors']
            if item.language == None and c[0].get("language"):
            	item.language = c[0]['language']
            succ+=1
            print("after---%s---succ:%s---total:%s---%s---%s----%s----%s---%s-----%s-------%s-------%s------%s--"%(item.id,succ,total,item.name,item.country,item.alias,item.actor,item.director,item.language,item.show_time,item.tag,item.summary))
            # print("---%s--------%s----"%(item.name,c[0]['title']))
            print("-------done--------")
            # return True
            item.data_flag = '1'
            db_session.add(item)
            db_session.commit()
        db_session.close()
    #db_session.commit()
    db_session.close()
    print(size,succ)


def task_by_gevent():
    print("go")
    db_session = scoped_session(DBSession)
    count = db_session.query(GDCmscontent).count()
    db_session.close()
    print("count:",count)
    thr = 6
    block_len = count/thr
    ge = [gevent.spawn(sync, {"offset":x*block_len,"size":x*block_len+block_len}) for x in xrange(0,thr)]
    gevent.joinall(ge)

def task_by_threading():
    print("go")
    db_session = scoped_session(DBSession)
    count = db_session.query(GDCmscontent).count()
    db_session.close()
    print("count:",count)
    thr = 1
    block_len = count/thr
    for x in range(thr):
        t = threading.Thread(target = sync, args = ({"offset":x*block_len,"size":x*block_len+block_len},))
        # t.setDaemon(True)   #True:设置当主线程退出时候补等待子线程执行完毕,表明该线程"不重要"
        t.start()

if __name__ == '__main__':
    task_by_threading()
    # task_by_gevent()