#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-06-20 10:42:32
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import re
import pickle
import time
import sys
import os
from bson.objectid import ObjectId
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('../')
import config
sys.path.append('./')
from DB.GDCmscontent import GDCmscontent
from DB.GDCmscontent_Jon import GDCmscontent_Jon
from DB.mysql_session import DBSession
from sqlalchemy.orm import scoped_session
from sqlalchemy import desc, asc
from DB.RedisClient import rd, rpop
from DB.MongodbClient import mongo_conn

class ContentJob(object):
    """docstring for ClassName"""
    def __init__(self, **args):
    #   super(ClassName, self).__init__()
        pass

    def job(self):
        '''后台job'''
        while True:
            '''监听task'''
            p = rd.spop(config.gd_task_bkbk.encode('latin1'))
            if p==None:
                print("sleep 6s...")
                time.sleep(6)
                continue
            task = pickle.loads(p)
            print(task.get("name"))
            if task.get("name") == None:
                continue
            r = self.process(task)
            if not r:
                rd.sadd(config.gd_task_bkbk,p)
                pass

    def process(self,task=None):
        '''处理job task'''
        if task.get("name")==None or task.get("name")=="":
            pass

        #测试,先屏蔽了
        r_mongo = mongo_conn.contents.find({'relationship':{'$elemMatch':{'mediaId':task.get("code"),"platform":"gd"}}})
        if r_mongo.count() > 0:
            print(r_mongo[0])
            return self.after_mongo_succ(r_mongo[0]['_id'],task)
        else:
        	return True

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

    def callback(self,data,task):
        '''回掉给数据'''
        print("code",task['code'],data['_id'])
        db_session = scoped_session(DBSession)
        item = db_session.query(GDCmscontent).filter_by(code=task['code']).first()
        if not item:
            return None
        print(item)
        if item.summary == None and data.get("summary"):
            item.summary = data['summary'][0:4000]
            # pass
        if item.tag == None and data.get("tags"):
            item.tag = data['tags']
        if item.year == None and data.get("year"):
            item.year = data['year']
        if item.show_time == None and data.get("release_date"):
            item.show_time = re.search(u'(\d{4}-\d{2}-\d{2})',data['release_date']).group(1) if re.search(u'(\d{4}-\d{2}-\d{2})',data['release_date']) else None
        if item.alias == None and data.get("alias"):
            if len(data['alias'].split(',')) > 3:
                item.actor = ",".join(data['alias'].split(',')[0:3])
            else:
                item.alias = data['alias']
        if data.get("producer_country"):
            item.country = data['producer_country']
        if data.get("area"):
            item.region = data['area']
        elif data.get('producer_country'):
            item.region = data['producer_country']
        if item.actor == None and data.get("starring"):
            if len(data['starring'].split(',')) > 6:
                item.actor = ",".join(data['starring'].split(',')[0:6])
            else:
                item.actor = data['starring']
        if item.director == None and data.get("directors"):
            if len(data['directors'].split(',')) > 6:
                item.actor = ",".join(data['directors'].split(',')[0:6])
            else:
                item.director = data['directors']
        if item.language == None and data.get("language"):
            item.language = data['language']
        item.data_flag = 1
        db_session.add(item)
        db_session.commit()
        db_session.close()

        return True


def producer():
    db_session = scoped_session(DBSession)
    print(db_session)
    count = db_session.query(GDCmscontent).count()
    print(count)
    size = 500
    for x in xrange(1,count/size+2):
        contents = db_session.query(GDCmscontent).filter((GDCmscontent.series_flag.in_((100,110))) & (GDCmscontent.data_flag==None)&(GDCmscontent.id>=size*(x-1))&(GDCmscontent.id<=size*x)).all()
        for item in contents:
            rd.sadd(config.gd_task,pickle.dumps(item.__dict__))
            print(item.id)
    db_session.close()
    return True



if __name__ == '__main__':
    # producer()
    task_by_gevent()
    pass
