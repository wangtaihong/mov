#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-06-25 15:43:44
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : http://example.org
# @Version : $Id$

from gevent import monkey; monkey.patch_all()
import os, time
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

requests.packages.urllib3.disable_warnings()

def process():
    path = u"E:/data/posters_07_02/"
    while True:
        p = rd.spop("posters")
        if not p:
            readtask()
            time.sleep(90)
            print("sleep 90s...")
            continue
        task = json.loads(p)
        im = requests_get(task['url'])
        #print("r.status_code:",r.status_code)
        #if r.status_code == 404 or r == False:
        if not im:
            rd.sadd("posters_failed",p)
            print("failed", p)
            continue
        #im = Image.open(r.raw)
        if im.width < 190:
            print(im.width,im.height,task)
            mongo_conn.posters.remove({"_id":ObjectId(task['_id'])})
            continue
        file_name = "/".join([task.get("content_id"),"%s_%sx%s.jpg"%(task.get("content_id"),im.width,im.height)])
        try:
            os.makedirs(re.search('(.*/)',path+file_name).group(1))
        except Exception as e:
            #print(str(e))
            pass
        im.convert('RGB').save(path+file_name)
        result = mongo_conn.posters.update_one({"_id":ObjectId(task['_id'])},{"$set":{"file_path":file_name}})
        print("done--%s-%s"%(result.modified_count,path+file_name))


def readtask():
    posters = mongo_conn.posters.find({"file_path":{"$exists":False},"image_v":{"$exists":False}},no_cursor_timeout=True)
    for p in posters:
        p['_id'] = str(p['_id'])
        print(p['_id'])
        rd.sadd("posters", json.dumps(p))


def requests_get(url):
    retry = 5
    while retry > 0:
        try:
            # return requests.get(url,stream=True)
            return Image.open(requests.get(url,stream=True,verify=False).raw)
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
    gevent_threading()
