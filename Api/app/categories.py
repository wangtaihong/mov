#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-26 09:24:26
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$


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
# from bson.objectid import ObjectId

# sys.path.append('../../')
# import config
# sys.path.append('./')

def get():
    return {"status":"1","msg":u"success","categories":_all_categories()}


def _all_categories():
    '''返回all categories  id,category'''
    categories = mongo_conn.categories.find()
    data = []
    for x in categories:
    	data.append({"id":str(x["_id"]),"category":x.get("category")})
    return data