#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-23 17:01:59
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

import requests
import redis
import re
import json
import demjson
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
from DB import mysql_session, Vod
from Utils.request import requests_get, requests_post
from Utils.utils import parse_regx_char, area_process, title_preprocess, title_preprocess_seed, process_actor, search_preprocess, check_title
from DB.RedisClient import rd, rpop
from DB.MongodbClient import mongo_conn
from Api.app.content import merge_poster
# from pymongo import MongoClient

class ContentJob(object):
    """docstring for ClassName"""
    def __init__(self, **args):
    # 	super(ClassName, self).__init__()
        pass

    def job(self):
        '''后台job'''
        print("go job")
        while True:
            '''监听task'''
            p = rd.spop(config.content_work_task)
            if p==None:
                self.failed_job()
                print("sleep 6s...")
                time.sleep(6)
                continue
            task = json.loads(p)
            if task.get("contentName") == None:
                continue
            r = self.process(task)
            if not r:
                rd.sadd(config.content_work_task_failed,p)

    def failed_job(self):
        print("go failed_job")
        while True:
            '''监听task'''
            p = rd.spop(config.content_work_task_failed)
            if p==None:
                return True
            task = json.loads(p)
            if task.get("contentName") == None:
                continue
            r = self.process(task)
            if not r:
                rd.sadd(config.content_work_task_failed,p)

    def process(self,task=None):
        '''处理job task'''
        if task.get("contentName")==None or task.get("contentName")=="":
            pass

        #测试,先屏蔽了
        r_mongo = mongo_conn.contents.find({'relationship':{'$elemMatch':{'mediaId':task.get("mediaId"),"platform":task.get("platform")}}})
        if r_mongo.count() > 0:
            return self.after_mongo_succ(r_mongo[0]["_id"],task)

        """过滤新闻等短视频"""
        ct = check_title(task['contentName'])
        if ct:
            return self.after_search_failed(task,category=ct)

        if task.get("actor") and task.get("director"):
            #信息全的走mongodb匹配，mongo没有的接着走百度搜索引擎
            print("task:--contentName:%s---contentType:%s---director:%s---actor:%s---area:%s-"%(task.get("contentName"),task.get("contentType"),task.get("director"),task.get("actor"),task.get("area")))
            regx = {}
            if task.get("director") and task.get("director")!="":
                regx["directors"] = re.compile(u"("+ "|".join(process_actor(task.get("director")).split(','))+")",re.IGNORECASE)  #匹配至少有一个directors相交的
            if task.get("actor") and task.get("actor")!="":
                regx['actors'] = re.compile(u"("+ "|".join(process_actor(task.get("actor")).split(','))+")",re.IGNORECASE)    #匹配至少有一个starring相交的
            if task.get("year"):
                regx['year'] = re.compile(u"("+ "|".join(process_actor(task.get("year")).split(','))+")",re.IGNORECASE)    #匹配至少有一个year
            if task.get("area"):
                regx['area'] = re.compile(u"("+ "|".join(area_process(task.get("area")))+")",re.IGNORECASE)    #匹配至少有一个year
            regx_name = title_preprocess_seed(task.get("contentName"))
            regx_name = parse_regx_char(regx_name)
            regx_name = u'.*' + regx_name.replace(u'-','.*') + ".*"
            regx_name = re.compile(regx_name, re.IGNORECASE)
            regx['title'] = regx_name  #匹配标题以之开头的
            contents = mongo_conn.contents.find(regx)
            '''在元数据仓库找不到的去百度搜索引擎'''
            if contents.count()==0:
                return self.baidu(task)
            else:
                # mongo_rs = mongo_conn.contents.find({"title": regx_name})
                ls = []
                lss = {}
                # 100：普通点播 110：连续剧父集 110：连续剧子集
                for mon in contents:
                    sim = lst.ratio(title_preprocess(task.get("contentName")), title_preprocess(mon['title']))
                    print("-sim:%s--title:%s--contentName:%s---contentType:%s---director:%s---actor:%s---area:%s-"%(sim,mon['title'],task.get("contentName"),task.get("contentType"),task.get("director"),task.get("actor"),task.get("area")))
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
            return self.baidu(task)

    def after_mongo_succ(self, _id, task):
        c = mongo_conn.contents.find({"_id": _id})
        # relationship
        if c[0].get("relationship"):
            f = True
            for x in c[0].get("relationship"):
                if x['platform']==task.get("platform") and x['mediaId']==task.get("mediaId"):
                    f = False
                    break
            if f==True:
                print({"relationship": {"platform": task.get(
                "platform"), "mediaId": task.get("mediaId"), "CPID": task.get("CPID")}})
                result = mongo_conn.contents.update_one({"_id": _id}, {"$push": {"relationship": {"platform": task.get(
                "platform"), "mediaId": task.get("mediaId"), "CPID": task.get("CPID"),"mediaName":task.get("contentName")}}})
                print(result)
        else:
            result = mongo_conn.contents.update_one({"_id": _id}, {"$push": {"relationship": {"platform": task.get(
                "platform"), "mediaId": task.get("mediaId"), "CPID": task.get("CPID"),"mediaName":task.get("contentName")}}})
            print(result)
        return self.callback(data=c[0],task=task)

    def after_search_failed(self,task,category=None):
        task['contentType'] = category
        data = self.save_task_tocontents(task)
        return self.callback(data=data,task=task)

    def baidu(self,task):
        _temp = []
        _temp.append(task['contentName'])
        k = "".join(_temp)
        print(k)
        baidu = Baidu(wd=search_preprocess(k))
        data = baidu.v_search()
        print("-------------------------------------------------------------------------")
        # print(json.dumps(data))
        """搜索到结果"""
        if data and data.get("_id"):
            """成功爬到数据"""
            merge_poster(data)
            return self.after_mongo_succ(ObjectId(data['_id']),task)
        elif data==False:
            """百度已经搜索到影视结果，但是由于其他原因数据没有爬去完整"""
            return data
        elif not data:
            """百度搜索没有影视结果 未None或为[]"""
            return self.after_search_failed(task)

    def callback(self,data,task):
        '''回掉给数据'''
        r = self.parse_cmscontent_field(dic=data,task=task)
        m = re.search(u"(meta.*)",task.get("redirectURL"))
        url = "http://192.168.2.133:8010/"+m.group(1)
        rc = requests_post(url=url,data=json.dumps(r),headers={"Content-Type":"application/json"})
        print("rcrcrcrcrcrcrcrcrcrcrcrcrcrcrcrcrcrcrc",rc)
        if rc != '0':
        	return None
        else:
            return rc

    def parse_cmscontent_field(self,dic,task):
        data = dict()
        data['mediaId'] = task.get("mediaId")
        data['contentType'] = dic.get("category")
        data['contentName'] = dic.get("title")
        data['originalName'] = dic.get("title")
        data['contentDetail'] = dic.get("summary")
        if dic.get("directors_list"):
            data['directorId'] = ','.join([x["star_id"] for x in dic.get("directors_list") if x.get("star_id")])
        if dic.get("starring_list"):
            data['actorId'] = ','.join([x["star_id"] for x in dic.get("starring_list") if x.get("star_id")])
        data['director'] = dic.get("directors")
        data['actor'] = dic.get("starring")
        data['duration'] = dic.get("duration")
        # data['thumbnail'] = dic.get("img_url")
        # data['posterURL'] = dic.get("img_url")
        data['language'] = dic.get("language")
        data['year'] = dic.get("year")
        data['area'] = dic.get("area")
        if data['area']==None and dic.get("producer_country"):
            data['area'] = dic.get("producer_country")
        if dic.get("douban_rating"):
            data['grade'] = dic.get("douban_rating")
        elif dic.get("youku_rating"):
            data['grade'] = dic.get("youku_rating")
        elif dic.get("letv_rating"):
            data['grade'] = dic.get("letv_rating")
        elif dic.get("iqiyi_rating"):
            data['grade'] = dic.get("iqiyi_rating")
        elif dic.get("qq_rating"):
            data['grade'] = dic.get("qq_rating")
        elif dic.get("pptv_rating"):
            data['grade'] = dic.get("pptv_rating")
        elif dic.get("sohu_rating"):
            data['grade'] = dic.get("sohu_rating")
        else:
            pass
        data['metaId'] = str(dic.get("_id"))
        tags = []
        if dic.get("tags"):
            tags = tags + dic.get("tags").split(',')
        if dic.get("type"):
            tags = tags + dic.get("type").split(',')
        data['tags'] = ",".join(tags)
        return data

    def save_task_tocontents(self,task):
        data = dict()
        # data['mediaId'] = task.get("mediaId")
        data['category'] = task.get("contentType")
        data['title'] = task.get("contentName")
        data['summary'] = task.get("contentDetail")
        data['directors'] = process_actor(task.get("director"))
        data['starring'] = process_actor(task.get("actor"))
        data['language'] = task.get("language")
        data['year'] = task.get("year")
        data['area'] = task.get("area")
        data['source'] = u'IPTV'
        data['created_at'] = time.time()
        _id = mongo_conn.contents.insert(data,check_keys=False)
        result = mongo_conn.contents.update_one({"_id": _id}, {"$push": {"relationship": {"platform": task.get(
                "platform"), "mediaId": task.get("mediaId"), "CPID": task.get("CPID"),"mediaName":task.get("contentName")}}})
        return data