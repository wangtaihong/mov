#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-24 17:26:26
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

from gevent import monkey; monkey.patch_all()
from Work.gd_work import ContentJob
import gevent

import threading
def work():
    job = ContentJob()
    job.job()

def by_gevent():
    gevent.joinall([
        gevent.spawn(work, ),
        gevent.spawn(work, ),
        gevent.spawn(work, ),
        gevent.spawn(work, ),
        gevent.spawn(work, ),
    ])

def by_threading_gevent(thr=2):
    for i in range(thr):
        # t = threading.Thread(target = use_queue,args = (in_queue,))
        t = threading.Thread(target = by_gevent)
        # t.setDaemon(True)   #True:设置当主线程退出时候补等待子线程执行完毕,表明该线程"不重要"
        t.start()

if __name__ == '__main__':
    by_threading_gevent()
