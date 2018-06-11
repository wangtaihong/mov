#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-11 15:36:59
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

import os
import re
import sys
import time
import threading
reload(sys)
sys.setdefaultencoding('utf8')
import json
sys.path.append('../')
import config
sys.path.append('./')
from pymongo import MongoClient
from bson.objectid import ObjectId
from DB.GSCmsStarsMetadata import GSCmsStarsMetadata
from DB.mysql_session import DBSession
# import Levenshtein as lst
from sqlalchemy.orm import scoped_session


def sync():
    mongo_stars = MongoClient(config.MONGO_HOST, config.MONGO_PORT).zydata.stars
    db_session = scoped_session(DBSession)
    contents = mongo_stars.find(no_cursor_timeout=True)
    for item in contents:
    	data = GSCmsStarsMetadata()
    	data.mongo_id = str(item.get("_id"))
 		data.birthplace = item.get("birthplace")
 		data.name = item.get("name")
 		data.area = item.get("area")
 		data.intro = item.get("intro")
 		data.gender = item.get("gender")
 		# data.star_poster = item.get("")
 		data.avatar = item.get("avatar_url") if item.get("avatar_url") else None
 		data.alias = item.get("alias")
 		data.birthday = item.get("birthday")
 		data.blood = item.get("blood")
 		data.constellation = item.get("constellation")
 		data.occupation = item.get("occupation")
 		data.mongo_create_time = item.get("created_at") if item.get("created_at") else int(time.time())
 		data.create_time = int(time.time())

if __name__ == '__main__':
    sync()
