#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-23 17:01:59
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

import requests
import redis
import re
import demjson, pickle, json
import time
import sys
import os
from bson.objectid import ObjectId
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('../')
import config
from Spiders.baidu.spider.baidu import Baidu
sys.path.append('./')
import Levenshtein as lst
from DB.GDCmscontent import GDCmscontent
from DB.GDCmscontent_Jon import GDCmscontent_Jon
from DB.mysql_session import DBSession
from sqlalchemy.orm import scoped_session
from sqlalchemy import desc, asc
from Utils.request import requests_get, requests_post
from Utils.utils import parse_regx_char, area_process, title_preprocess, title_preprocess_seed, process_actor, search_preprocess, check_title
from DB.RedisClient import rd, rpop
from DB.MongodbClient import mongo_conn

class ContentJob(object):
    """docstring for ClassName"""
    def __init__(self, **args):
    # 	super(ClassName, self).__init__()
        pass

    def job(self):
        '''后台job'''
        total = 0
        while True:
            '''监听task'''
            # p = rd.spop(config.gd_task_bk.encode('latin1'))
            p = rd.spop(config.gd_task)
            if p==None:
                continue
            task = pickle.loads(p)
            if task.get("name") == None:
                continue
            print(task['name'])
            total += 1
            print('***********************%s************************'%total)
            # rd.sadd('gd_task_bkbk',p)
            r = self.process(task)
            if not r:
                rd.sadd(config.gd_task_failed,p)
            else:
                rd.sadd(config.gd_task_bk,p)
                pass

    def process(self,task=None):
        '''处理job task'''
        if task.get("name")==None or task.get("name")=="":
            pass

        #测试,先屏蔽了
        r_mongo = mongo_conn.contents.find({'relationship':{'$elemMatch':{'mediaId':task.get("code")}}})
        if r_mongo.count() > 0:
            return self.after_mongo_succ(r_mongo[0]['_id'],task)

        ct = check_title(task['name'])
        if ct:
            return self.after_search_failed(task,category=ct)

        if task.get("actor") and task.get("director"):
            #信息全的走mongodb匹配，mongo没有的接着走百度搜索引擎
            print("task:--name:%s------director:%s---actor:%s---area:%s-"%(task.get("name"),task.get("director"),task.get("actor"),task.get("region")))
            regx = {}
            if task.get("director") and task.get("director")!="":
                regx["directors"] = re.compile(u"("+ "|".join(process_actor(task.get("director")).split(','))+")",re.IGNORECASE)
            if task.get("actor") and task.get("actor")!="":
                regx['actors'] = re.compile(u"("+ "|".join(process_actor(task.get("actor")).split(','))+")",re.IGNORECASE)
            # if task.get("year"):
            #     regx['year'] = re.compile(u"("+ "|".join(process_actor(task.get("year")).split(','))+")",re.IGNORECASE)
            if task.get("region"):
                regx['area'] = re.compile(u"("+ "|".join(area_process(task.get("region")))+")",re.IGNORECASE)
            regx_name = title_preprocess_seed(task.get("name"))
            regx_name = parse_regx_char(regx_name)
            regx_name = u'.*' + regx_name.replace(u'-','.*') + ".*"
            print('---%s------%s'%(regx_name,task.get("name")))
            regx['title'] = re.compile(regx_name, re.IGNORECASE)
            contents = mongo_conn.contents.find(regx)
            '''在元数据仓库找不到的去百度搜索引擎'''
            if contents.count()==0:
                return self.baidu(task)
            else:
                ls = []
                lss = {}
                for mon in contents:
                    sim = lst.ratio(title_preprocess(task.get("name")), title_preprocess(mon['title']))
                    print("-sim:%s--title:%s--name:%s------director:%s---actor:%s---region:%s-"%(sim,mon['title'],task.get("name"),task.get("director"),task.get("actor"),task.get("region")))
                    if sim < 0.80:
                        continue
                    ls.append(sim)
                    lss[sim] = mon.get("_id")
                if len(ls) == 0:
                    return self.baidu(task)
                ls.sort()
                try:
                    _id = lss[ls[-1]]
                except Exception as e:
                    _id = lss[ls[0]]
                print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^%s"%regx_name)
                return self.after_mongo_succ(_id,task)
        else:
            self.baidu(task)

    def after_mongo_succ(self, _id, task):
        c = mongo_conn.contents.find({"_id": _id})
        # relationship
        if c[0].get("relationship"):
            f = True
            for x in c[0].get("relationship"):
                if x['platform']=="gd" and x['mediaId']==task.get("code"):
                    f = False
                    break
            if f==True:
                print({"relationship": {"platform": 'gd', "mediaId": task.get("code"), "CPID": task.get("code_cp_id")}})
                result = mongo_conn.contents.update_one({"_id": _id}, {"$push": {"relationship": {"platform": "gd", "mediaId": task.get("code"), "CPID": task.get("code_cp_id"),"mediaName":task.get("name")}}})
                print(result)
        else:
            result = mongo_conn.contents.update_one({"_id": _id}, {"$push": {"relationship": {"platform": "gd", "mediaId": task.get("code"), "CPID": task.get("code_cp_id"),"mediaName":task.get("name")}}})
            print(result)
        return self.callback(data=c[0],task=task)

    def after_search_failed(self,task,category=None):
        if not category:
            """测试阶段先返回，以后正式了要保存的"""
            task['category'] = None
            return None
        task['category'] = category
        print("((((((((((((((((((((((((((((((((((((((((")
        print(task['id'])
        return self.save_task_tocontents(task)
        # return self.callback(data=data,task=task)

    def baidu(self,task):
        baidu = Baidu(wd=search_preprocess(task['name']))
        data = baidu.v_search()
        print(json.dumps(data))
        print("-------------------------------------------------------------------------")
        print(not data)
        """搜索到结果"""
        if data and data.get("_id"):
            return self.after_mongo_succ(ObjectId(data['_id']),task)
        else:
            return self.after_search_failed(task)

    def callback(self,data,task):
        '''回掉给数据'''
        print("code",task['code'],data['_id'])
        return True
        db_session = scoped_session(DBSession)
        item = db_session.query(GDCmscontent).filter_by(code=task['code']).first()
        if not item:
            return None
        print(item)
        if item.summary == None and data.get("summary"):
            item.summary = data['summary']
            # pass
        if item.tag == None and data.get("tags"):
            item.tag = data['tags']
        if item.year == None and data.get("year"):
            item.year = data['year']
        if item.show_time == None and data.get("release_date"):
            item.show_time = re.search(u'(\d{4}-\d{2}-\d{2})',data['release_date']).group(1) if re.search(u'(\d{4}-\d{2}-\d{2})',data['release_date']) else None
        if item.alias == None and data.get("alias"):
            item.alias = data['alias']
        if data.get("producer_country"):
            item.country = data['producer_country']
        if data.get("area"):
            item.region = data['area']
        elif data.get('producer_country'):
            item.region = data['producer_country']
        if item.actor == None and data.get("starring"):
            item.actor = data['starring']
        if item.director == None and data.get("directors"):
            item.director = data['directors']
        if item.language == None and data.get("language"):
            item.language = data['language']
        item.data_flag = 1
        db_session.add(item)
        db_session.commit()
        db_session.close()

        return True

    def get_posters(self,content_id,width='300',height="400"):
        regx = {}
        regx['content_id'] = re.compile(str(content_id),re.IGNORECASE)
        regx['width'] = re.compile(width.replace('0',u"\d"),re.IGNORECASE)
        regx['height'] = re.compile(height.replace('0',u"\d"),re.IGNORECASE)
        posters = mongo_conn.posters.find(regx)
        if len(posters):
            pass

    def save_task_tocontents(self,task):
        data = dict()
        # data['mediaId'] = task.get("mediaId")
        data['category'] = task['category']
        data['title'] = task.get("name")
        data['summary'] = task.get("summary")
        data['directors'] = task.get("director")
        data['starring'] = task.get("actor")
        data['language'] = task.get("language")
        data['year'] = task.get("year")
        data['area'] = task.get("region")
        data['source'] = u'IPTV'
        data['created_at'] = time.time()
        _id = mongo_conn.contents.insert(data,check_keys=False)
        result = mongo_conn.contents.update_one({"_id": _id}, {"$push": {"relationship": {"platform": "gd", "mediaId": task.get("code"), "CPID": task.get("CPID"),"mediaName":task.get("name")}}})
        return data

def producer():
    db_session = scoped_session(DBSession)
    print(db_session)
    count = db_session.query(GDCmscontent).count()
    print(count)
    size = 1000
    for x in xrange(1,count/size+2):
        contents = db_session.query(GDCmscontent).filter((GDCmscontent.series_flag.in_((100,110))) & (GDCmscontent.data_flag==None)&(GDCmscontent.id>=size*(x-1))&(GDCmscontent.id<=size*x)).all()
        for item in contents:
            rd.sadd(config.gd_task,pickle.dumps(item.__dict__))
            print(item.id)
    db_session.close()
    return True



if __name__ == '__main__':
    # producer()
    # task_by_gevent()
    pass
