#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-25 10:56:29
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

# import re
import sys,re
import os
reload(sys)
sys.setdefaultencoding('utf8')
import json
# import demjson
import time
import uuid

sys.path.append('../../../')
from DB.MongodbClient import mongo_conn, mongo_zydata
sys.path.append('./')
from bson.objectid import ObjectId
from Utils.utils import parse_regx_char, area_process, title_preprocess, title_preprocess_seed, process_actor, search_preprocess, check_title,split_space,title_preprocess_mongosearch

# sys.path.append('../../')
# import config
# sys.path.append('./')

def get(_id=None):
    '''作业任务'''
    if _id:
        r = _get_content(_id)
        return {"status":"1","msg":u"success","data":r}
    else:
        return {"status":"-1","msg":u"error,参数错误"}

def _get_content(_id):
    '''根据content _id 返回content的海报，导演，主演,编剧'''
    try:
        ObjectId(_id)
    except Exception as e:
        return None
    if _id:
        c = mongo_conn.contents.find({"_id":ObjectId(_id)})
        if c.count()==0:
            return None
        r = {}
        r = parser_contents_fields(c[0])
        tags = []
        if c[0].get("tags"):
            tags = tags + c[0].get("tags").split(',')
        if c[0].get("type"):
            tags = tags + c[0].get("type").split(',')
        r['tags'] = ",".join(tags)
        # print(r['title'])
        p = get_posters(c[0])
        if p:
            r["posterList"] = p
        if c[0].get("directors_list"):
            r["directorsList"] = []
            for x in c[0].get("directors_list"):
                if x.get("star_id")==None:
                    continue
                d = mongo_conn.stars.find({"_id":ObjectId(x["star_id"])})
                if d.count()>0:
                    r["directorsList"].append(parser_starring_fields(d[0]))

        if c[0].get("starring_list"):
            r["starringList"] = []
            for x in c[0].get("starring_list"):
                if x.get("star_id")==None:
                    continue
                s = mongo_conn.stars.find({"_id":ObjectId(x["star_id"])})
                if s.count()>0:
                    r["starringList"].append(parser_starring_fields(s[0]))

        if c[0].get("screenwriter_list"):
            r["screenwriterList"] = []
            for x in c[0].get("screenwriter_list"):
                if x.get("star_id")==None:
                    continue
                sc = mongo_conn.stars.find({"_id":ObjectId(x["star_id"])})
                if sc.count()>0:
                    r["screenwriterList"].append(parser_starring_fields(sc[0]))
        # print(r['title'])
        return r
    else:
        return None

def parser_starring_fields(s):
    _temp = {}
    _temp['id'] = str(s.get("_id"))
    fields = ["name","foreign_names","zh_names","birthplace","area","date_birth","birthday","intro","gender","avatar","alias","blood","constellation","occupation"]
    for x in fields:
        if s.get(x):
            _temp[x] = s.get(x)
    return _temp

def parser_poster_fields(s):
    _temp = {}
    if s.get("_id"):
        _temp['id'] = str(s.get("_id"))
    else:
        _temp['id'] = uuid.uuid4().hex
    fields = ["content_id","name","prop","width","height","url"]
    for x in fields:
        if s.get(x):
            if s.get(x):
                _temp[x] = s.get(x)
    return _temp

def get_posters(c):
    posterList = []
    if c.get("iqiyi_tvId") and c.get("starring") and c.get("directors"):
        regx = {}
        regx["directors"] = re.compile(u"("+ "|".join(process_actor(c.get("directors")).split(','))+")",re.IGNORECASE)
        regx['starring'] = re.compile(u"("+ "|".join(process_actor(c.get("starring")).split(','))+")",re.IGNORECASE)
        # regx['area'] = re.compile(u"("+ "|".join(area_process(c.get("region")))+")",re.IGNORECASE)
        regx_name = title_preprocess_mongosearch(c.get("title"))
        regx_name = parse_regx_char(regx_name)
        regx_name = u'.*' + regx_name.replace(u'-','.*') + ".*"
        print('---%s------%s'%(regx_name,c.get("title")))
        regx['title'] = re.compile(regx_name, re.IGNORECASE)
        regx["doubanid"] = {"$exists":True}
        contents = mongo_zydata.douban_tvs.find(regx)
        if contents.count() > 0:
            for x in contents:
                r1 = len(set(split_space(x['starring'].replace('|',",").replace("/",",")).split(',')).intersection(set(c['starring'].split(','))))
                r2 = len(set(split_space(x['directors'].replace('|',",").replace("/",",")).split(',')).intersection(set(c['directors'].split(','))))
                print(r1)
                print(r2)
                if r1 and r2:
                    if x.get("poster"):
                        for p in x.get("poster"):
                            p['url'] = re.sub(u'photo/m/public/',u'photo/l/public/',p['url'])
                            p['content_id'] = str(c['_id'])
                            posterList.append(parser_poster_fields(p))
        
        regx["doubanid"] = {"$exists":False}
        regx['name'] = regx['title']
        del regx['title']
        del regx['doubanid']
        contents = mongo_zydata.letv_tvs.find(regx)
        if contents.count() > 0:
            for x in contents:
                r1 = len(set(split_space(x['starring'].replace('|',",").replace("/",",")).split(',')).intersection(set(c['starring'].split(','))))
                r2 = len(set(split_space(x['directors'].replace('|',",").replace("/",",")).split(',')).intersection(set(c['directors'].split(','))))
                print(r1)
                print(r2)
                if r1 and r2:
                    if x.get("images"):
                        for p in x.get("images"):
                            p['content_id'] = str(c['_id'])
                            posterList.append(parser_poster_fields(p))

        regx['actors'] = regx['starring']
        del regx['starring']
        regx['title'] = regx['name']
        del regx['name']
        contents = mongo_zydata.youku_tv.find(regx)
        if contents.count() > 0:
            for x in contents:
                r1 = len(set(split_space(x['actors'].replace('|',",").replace("/",",")).split(',')).intersection(set(c['starring'].split(','))))
                r2 = len(set(split_space(x['directors'].replace('|',",").replace("/",",")).split(',')).intersection(set(c['directors'].split(','))))
                print(r1)
                print(r2)
                if r1 and r2:
                    if x.get("thumb"):
                        for p in x.get("thumb"):
                            p['content_id'] = str(c['_id'])
                            posterList.append(parser_poster_fields(p))

        if posterList:
            # return posterList
            pass
    posters = mongo_conn.posters.find({"content_id":str(c["_id"])})
    if posters.count()!=0:
        for p in posters:
            posterList.append(parser_poster_fields(p))
    return posterList


def parser_contents_fields(s):
    _temp = {}
    _temp['id'] = str(s.get("_id"))
    fields = ["douban_rating","youku_rating","letv_rating","douban_rating_sum","youku_plays_num","language","title","alias","subname","tags","category","category_id","screenwriters","directors","starring","producer_country","summary","year","release_date","duration","created_at"]
    for x in fields:
        if s.get(x):
            _temp[x] = s.get(x)
    if s.get("area") and not _temp.get("producer_country"):
        _temp["producer_country"] = s.get("area")
    return _temp