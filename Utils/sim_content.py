#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-06-07 19:07:43
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

import os,re
from DB.MongodbClient import mongo;db = mongo.zydata
from Utils.utils import process_actor, search_preprocess, parse_regx_char, area_process

def sim_content(data):
    sim_regx = {}
    if data.get("directors") and data.get("directors")!="":
        sim_regx["directors"] = re.compile(u"("+parse_regx_char(data["directors"])+")",re.IGNORECASE)
    # if data.get("starring") and data.get("starring")!="":
    #     sim_regx['starring'] = re.compile(u"("+data["starring"]+")",re.IGNORECASE)
    if len(sim_regx)==0:
        """如果主演导演都没有的话，就不去搜索了"""
        return None
    if data.get("area"):
        sim_regx['area'] = re.compile(u"("+ "|".join(area_process(data.get("area")))+")",re.IGNORECASE)
    regx_name = search_preprocess(data.get("title"))
    regx_name = parse_regx_char(regx_name)
    regx_name = u'.*' + regx_name.replace(u'-','.*') + ".*"
    regx_name = re.compile(regx_name, re.IGNORECASE)
    sim_regx['title'] = regx_name  #匹配标题以之开头的
    contents = db.contents.find(sim_regx)
    print('---%s------%s'%(regx_name,data.get("title")))
    if contents.count()>0:
        poster = db.posters.find({"content_id":str(contents[0]['_id'])})
        if poster.count()>0:
            p = []
            for x in poster:
                print(x['_id'],data['_id'])
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                del x['_id']
                x['content_id'] = data['_id']
                p.append(x)
            return p
    else:
        return None
