#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-06-25 15:43:44
# @Author  : Your Name (you@example.org)
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

path = u"E:/media/iptv_full2/"
file_name = u'C:/Users/Admin/Documents/Tencent Files/1985911781/FileRecv/img_increase_20180622.txt'


def process():
    path = u"E:/posters/"
    while True:
        p = rd.spop("posters")
        task = json.loads(p)
        r = requests_get(task['url'])
        print("r.status_code:",r.status_code)
        if r.status_code == 404 or r == False:
            rd.sadd("posters_failed",p)
            print("failed", p)
            continue
        im = Image.open(r.raw)
        file_name = "/".join([task.get("content_id"),"%s_%sx%s.jpg"%(task.get("content_id"),im.width,im.height)])
        try:
        	os.makedirs(re.search('(.*/)',path+file_name).group(1))
        except Exception as e:
        	print(str(e))
        	pass
        im.convert('RGB').save(path+file_name)
        result = mongo_conn.posters.update_one({"_id":ObjectId(task['_id'])},{"$set":{"file_path":file_name}})
        print("done--%s-%s"%(result.modified_count,path+file_name))


def readteak():
	posters = mongo_conn.posters.find()
	for p in posters:
		p['_id'] = str(p['_id'])
		print(p['_id'])
		rd.sadd("posters", json.dumps(p))


def requests_get(url):
    retry = 5
    while retry > 0:
        try:
            return requests.get(url,stream=True)
        except Exception as e:
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
    # readteak()
    gevent_threading()
