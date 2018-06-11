#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-28 08:28:47
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

import sys
import threading
reload(sys)
sys.setdefaultencoding('utf8')

def task():
	# do something
	pass
if __name__ == '__main__':
	for i in range(1):
        # t = threading.Thread(target = use_queue,args = (in_queue,))
        t = threading.Thread(target = task)
        # t.setDaemon(True)
        t.start()