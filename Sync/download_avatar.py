#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-06-27 09:44:38
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : http://example.org
# @Version : $Id$

from gevent import monkey; monkey.patch_all()
import os
import threading
import redis
import requests, json, re
import gevent, sys
sys.path.append('../')
import config
sys.path.append('./')
from DB.RedisClient import rd
from DB.MongodbClient import mongo_conn
from bson.objectid import ObjectId
from PIL import Image


def process():
    path = u"E:/avatar/"
    while True:
        p = rd.spop("stars")
        if not p:
        	return True
        task = json.loads(p)
        if task.get("avatar") and not task.get("img_url"):
        	im = requests_get(task['avatar'])
        elif not task.get("avatar") and task.get("img_url"):
        	im = requests_get(task['img_url'])
        else:
        	print("----",p)
        	continue
        #print("r.status_code:",r.status_code)
        #if r.status_code == 404 or r == False:
        if not im:
            rd.sadd("avatar_failed",p)
            print("failed", p)
            continue
        #im = Image.open(r.raw)
        file_name = "/".join([task.get("_id"),"%s.jpg"%(task.get("_id"))])
        try:
        	os.makedirs(re.search('(.*/)',path+file_name).group(1))
        except Exception as e:
        	#print(str(e))
        	pass
        im.convert('RGB').save(path+file_name)
        result = mongo_conn.stars.update_one({"_id":ObjectId(task['_id'])},{"$set":{"file_path":file_name}})
        print("done-----%s-----%s"%(result.modified_count,path+file_name))
        return


def readtask():
	stars = mongo_conn.stars.find({"file_path":{"$exists":False}},no_cursor_timeout=True)
	for p in stars:
		p['_id'] = str(p['_id'])
		print(p['_id'])
		rd.sadd("stars", json.dumps(p))


def requests_get(url):
    retry = 5
    while retry > 0:
        try:
            # return requests.get(url,stream=True)
            return Image.open(requests.get(url,stream=True).raw)
        except Exception as e:
            print(str(e),url)
            retry -= 1
    return False

def gevent_threading():
    for i in range(8):
        t = threading.Thread(target=task_gevent)
        # t.setDaemon(True)
        t.start()

def task_gevent():
    gevent.joinall([
        gevent.spawn(process, ),
        gevent.spawn(process, ),
        gevent.spawn(process, ),
        gevent.spawn(process, ),
        gevent.spawn(process, ),
    ])


if __name__ == '__main__':
    # readtask()
    gevent_threading()
