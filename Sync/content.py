#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-25 10:48:26
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    :
# @Version : $Id$

import os
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
sys.path.append('../')
import config
sys.path.append('./')
from pymongo import MongoClient
from bson.objectid import ObjectId
from DB.CmsContent import CmsContent
from DB.mysql_session import DBSession
import Levenshtein as lst
from sqlalchemy.orm import scoped_session


def sync():
    tv_db = MongoClient(config.MONGO_HOST, config.MONGO_PORT).zydata.youku_tv
    test_db = MongoClient(config.MONGO_HOST, config.MONGO_PORT).zydata.test
    limit = 1000
    succ = 0
    db_session = scoped_session(DBSession)
    count = db_session.query(CmsContent).count()
    print(count)
    return True
    for step in xrange(0, count/limit):
        contens = db_session.query(CmsContent).offset(
            step*limit).limit(limit).all()
        for item in contens:
            if item.name == None or item.name == "":
                continue
            regx_name = item.name
            regx_name = regx_name.replace("(", "\(")
            regx_name = regx_name.replace(")", "\)")
            regx_name = regx_name.replace(".", "\.")
            regx_name = regx_name.replace("[", "\[")
            regx_name = regx_name.replace("]", "\]")
            try:
                regx = re.compile(".*"+regx_name+".*", re.IGNORECASE)
            except Exception as e:
                print("--------------error-------------")
                print(str(e))
                print(item.name)
                print("--------------error  ooooo-------------")
                continue
            mongo_rs = tv_db.find({"title": regx})
            nlts = [{"nlt": lst.ratio(item.name, mon['title']), "_id":mon["_id"], "title":mon["title"], "name":item.name}
                    for mon in mongo_rs if lst.ratio(item.name, mon['title']) >= 0.85]
            if len(nlts) > 0:
                succ += 1
                print(nlts)
    print(succ)


if __name__ == '__main__':
    sync()
