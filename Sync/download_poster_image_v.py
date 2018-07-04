#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-06-30 13:10:14
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

from gevent import monkey; monkey.patch_all()
import os
import threading
import redis,time
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
    path = u"E:/posters/"
    while True:
        p = rd.spop(config.image_v)
        if not p:
            print("done! sleep 6s")
            time.sleep(6)
            continue
        task = json.loads(p)
        # im = requests_get(u'http://meeting.itvfocus.com/'+task['image_v'])
        im = requests_get(u'http://183.59.160.50:8082/EPG/jsp/images/universal/film/poster/'+task['image_v'])
        if not im:
            rd.sadd("image_v_failed",p)
            print("failed", p)
            continue
        #im = Image.open(r.raw)
        if im.width < 180:
        	continue
        file_name = "/".join([task.get("content_id"),"%s_%sx%s.jpg"%(task.get("content_id"),im.width,im.height)])
        try:
        	os.makedirs(re.search('(.*/)',path+file_name).group(1))
        except Exception as e:
        	#print(str(e))
        	pass
        im.convert('RGB').save(path+file_name)
        ise = mongo_conn.posters.find({"file_path":file_name,"content_id":task['content_id']})
        if ise.count()!=0:
            continue
        task['file_name'] = file_name
        task['url'] = task['image_v']
        _id = mongo_conn.posters.insert(task,check_keys=False)
        print(task['content_id'],_id,file_name)


def readtask():
	posters = mongo_conn.posters.find({"file_path":{"$exists":False}},no_cursor_timeout=True)
	for p in posters:
		p['_id'] = str(p['_id'])
		print(p['_id'])
		rd.sadd("posters", json.dumps(p))


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
    for i in range(4):
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
    gevent_threading()