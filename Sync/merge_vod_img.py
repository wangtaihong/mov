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
from DB.mysql_session import DBSession
from DB.MongodbClient import mongo_conn
from Utils.utils import parse_regx_char, area_process, title_preprocess, title_preprocess_seed, process_actor
import Levenshtein as lst
from sqlalchemy.orm import scoped_session
from sqlalchemy import desc, asc
from gevent import monkey; monkey.patch_all()
import gevent
import threading
from DB.Vod import Vod

def sync(arges):
    print("haha")
    offset = arges["offset"]
    size = arges['size']
    mongo_contents = mongo_conn.contents
    mongo_posters = mongo_conn.posters
    succ = 0
    total = 0
    this_limit = 3000
    this_offset = offset
    step = (size-offset)/this_limit
    print('this_offset:',this_offset,size,size/this_limit)
    for x in xrange(1,step+1):
        print("offset:",offset+x*this_limit,this_limit)
        db_session = scoped_session(DBSession)
        print(offset + (x-1)*this_limit,x*this_limit + offset)
        contents = dict()
        contents = db_session.query(Vod).filter(Vod.d_downfrom!="1").order_by(asc(Vod.id)).all()
        for item in contents:
            if item.d_name == None or item.d_name == "" or item.d_pic==None or item.d_pic=="":
                item.d_downfrom = '1'
                db_session.add(item)
                db_session.commit()
                continue
            total+=1
            """没有地区或者导演主演都没有就pass"""
            if not item.d_area or (not item.d_directed and not item.d_starring):
                item.d_downfrom = '1'
                db_session.add(item)
                db_session.commit()
                continue
            regx_name = title_preprocess_seed(item.d_name)
            regx_name = parse_regx_char(regx_name)
            regx_name = u'.*' + regx_name.replace(u'-','.*') + ".*"
            print("-----%s-----%s----%s--%s----%s---"%(item.d_name,regx_name,item.d_area,item.d_directed,item.d_starring))
            regx = {}
            # regx["title"] = re.compile(regx_name, re.IGNORECASE)
            regx["title"] = regx_name
            if item.d_directed and item.d_directed!="":
                # regx["directors"] = re.compile(u"("+ "|".join(process_actor(item.d_directed).split(','))+")",re.IGNORECASE)  #匹配至少有一个directors相交的
                regx["directors"] = u"("+ "|".join(process_actor(item.d_directed).split(','))+")"  #匹配至少有一个directors相交的
            if item.d_starring and item.d_starring!="":
                regx['actors'] = re.compile(u"("+ "|".join(process_actor(item.d_starring).split(','))+")",re.IGNORECASE)    #匹配至少有一个starring相交的
                regx['actors'] = u"("+ "|".join(process_actor(item.d_starring).split(','))+")"    #匹配至少有一个starring相交的
            if item.d_area:
                # regx['area'] = re.compile(u"("+ "|".join(area_process(item.d_area))+")",re.IGNORECASE)
                regx['area'] = u"("+ "|".join(area_process(item.d_area))+")"
            print(json.dumps(regx))
            mongo_rs = mongo_contents.find(regx)
            ls = []
            lss = {}
            # 100：普通点播 110：连续剧父集 110：连续剧子集
            print("mongo_rs",mongo_rs.count())
            for mon in mongo_rs:
                sim = lst.ratio(title_preprocess(item.d_name), title_preprocess(mon['title']))
                print("-sim:----%s----%s---%s----regx_name:%s----"%(sim,item.d_name,mon['title'],regx_name))
                if sim < 0.80:
                    continue
                ls.append(sim)
                lss[sim] = mon.get("_id")
                if sim==1.0:
                    break
            if len(ls) == 0:
                item.d_downfrom = '1'
                db_session.add(item)
                db_session.commit()
                continue
            ls.sort()
            try:
                _id = lss[ls[-1]]
            except Exception as e:
                _id = lss[ls[0]]
            _id = mongo_posters.insert({"url":item.d_pic,"content_id":str(_id)},check_keys=False)
            print(_id)
            # print("---%s--------%s----"%(item.d_name,c[0]['title']))
            print("-------done--------")
            # return True
            item.d_downfrom = '1'
            db_session.add(item)
            db_session.commit()
        db_session.close()
    #db_session.commit()
    db_session.close()
    print(size,succ)


def task_by_gevent():
    print("go")
    db_session = scoped_session(DBSession)
    # count = db_session.query(Vod).filter((Vod.series_flag=='100') | (Vod.series_flag=='110')).count()
    # count = db_session.query(Vod).filter().count()
    count = db_session.query(Vod).count()
    db_session.close()
    print("count:",count)
    thr = 6
    block_len = count/thr
    ge = [gevent.spawn(sync, {"offset":x*block_len,"size":x*block_len+block_len}) for x in xrange(0,thr)]
    gevent.joinall(ge)

def task_by_threading():
    print("go")
    db_session = scoped_session(DBSession)
    count = db_session.query(Vod).count()
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
