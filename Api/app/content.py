#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-25 10:56:29
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

# import re
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')
import json
# import demjson
import time

sys.path.append('../../../')
from DB.MongodbClient import mongo_conn
sys.path.append('./')
from bson.objectid import ObjectId

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
        posters = mongo_conn.posters.find({"content_id":str(r["id"])})
        if posters.count()!=0:
            r["posterList"] = []
            for p in posters:
                r["posterList"].append(parser_poster_fields(p))
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
    _temp['id'] = str(s.get("_id"))
    fields = ["content_id","name","prop","width","height","url"]
    for x in fields:
        if s.get(x):
            _temp[x] = s.get(x)
    return _temp

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