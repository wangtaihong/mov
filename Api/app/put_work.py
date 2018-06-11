#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-23 15:05:42
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

import re
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')
import json
import demjson
import time
sys.path.append('../')
from DB.RedisClient import rd, rpop
sys.path.append('./')

sys.path.append('../../')
import config
sys.path.append('./')

def put(message=None):
	'''作业任务'''
	if message:
		rd.sadd(config.content_work_task,json.dumps(message))
		print(config.content_work_task)
		return {"status":"1","msg":u"success"}
	else:
		return {"status":"-1","msg":u"error,参数错误"}