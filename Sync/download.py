# -*- coding: utf-8 -*-
# @Date    : 2018-04-25 15:45:17
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    :
# @Version : $Id$

import os
import threading
import redis
import requests
from gevent import monkey; monkey.patch_all()
import gevent, sys
sys.path.append('../')
import config
sys.path.append('./')
from DB.RedisClient import rd

path = u"E:/media/iptv_full2/"
file_name = r'E:/img_increase_20180615.txt'


def process():
    while True:
        p = rd.spop("imageTask")
        IM = p.replace('"', "")
        IM = IM.replace('\n', "")
        data = IM.split(',')
        url = 'http://183.59.160.50:8082/EPG/jsp/images/universal/film/poster/' + data[3]
        path = u"E:/posters_4/"+"/".join(data[3].split('/')[:-1])+"/"
        try:
        	os.makedirs(path)
        except Exception as e:
        	# print(str(e))
        	pass
        local_filename = path+url.split('/')[-1]
        r = requests_get(url)
        print("r.status_code:",r.status_code)
        if r.status_code == 404 or r == False:
            with open("E:/404.txt", "a") as myfile:
                myfile.write(p)
            rd.sadd("imageTaskFailed",p)
            print("failed", p)
            continue
        f = open(local_filename, 'wb')
        for chunk in r.iter_content(chunk_size=512 * 1024):
            if chunk:
            	f.write(chunk)
        f.close()
        print("done", local_filename)


def readfile():
    with open(file_name) as f:
        for line in f:
            rd.sadd("imageTask", line)
            print(line)


def requests_get(url):
    retry = 5
    while retry > 0:
        try:
            return requests.get(url)
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
    readfile()
    gevent_threading()
