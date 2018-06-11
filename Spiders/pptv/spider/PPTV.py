#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-30 19:58:57
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$


from Utils.request import requests_get, requests_post
# import requests

import sys
sys.path.append('../')
from Spiders.setting import headers
from Spiders.pptv.parsers.PPTVParser import PPTVParser
sys.path.append('./')

# qq
class PPTV(object):
	"""docstring for ClassName"""
	def __init__(self, **args):
		# super(ClassName, self).__init__()
		# self.session = requests.Session()
		self.parsers = PPTVParser()

	def crawl(self,url):
		r = requests_get(url=url,headers=headers)
		return self.parsers.vdetail_parser(r)

	@staticmethod
	def crawl_star(self,url):
		r = requests_get(url=url,headers=headers)
		return self.parsers.star_parser(r,url=url)
