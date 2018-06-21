#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-25 09:44:23
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

from Utils.request import requests_get
# import requests
import json
import sys
sys.path.append('../')
# from Spiders.setting import baidu_headers
from Spiders.baidu.parsers.BaiduParser import BaiduParser
from Spiders.douban.tasks.task_video import task_video
from Spiders.iqiyi.spider.Iqiyi import Iqiyi
from Spiders.douban.spider.Douban import Douban
from Spiders.youku.spider.Youku import Youku
# from Spiders.letv
from Spiders.pptv.spider.PPTV import PPTV
from Spiders.qq.spider.QQ import QQ
from Spiders.sohu.spider.Sohu import Sohu
# from Spiders.youku.tasks.go_detail_list_task import go_detail_list_task
sys.path.append('./')

headers = None

class Baidu(object):
	"""docstring for ClassName"""
	def __init__(self, **args):
		# super(ClassName, self).__init__()
		# self.session = requests.Session()
		self.host_map = {"baike.baidu.com" : Baidu,
			"movie.douban.com":Douban,
			"iqiyi.com" : Iqiyi,
			# "mgtv.com",
			"v.qq.com" : QQ,
			"v.pptv.com" : PPTV,
			"sohu.com": Sohu,
			# "le.com",
			"youku.com":Youku
			}
		self.host = [
					#"baike.baidu.com",
					"movie.douban.com",
					"v.qq.com",
					"sohu.com",
					"iqiyi.com",
					# "v.pptv.com",
					# "le.com",
					# "youku.com"
				]
		self.params = {"ie":"utf-8","f":"8","tn":"baidu","wd":args['wd'],"rqlang":"cn"}
		# self.url = u'https://www.baidu.com/s?ie=utf-8&f=8&tn=baidu&wd={wd}&rqlang=cn'.format(wd=args["wd"])
		self.url = u'https://www.baidu.com/s'

	def v_search(self):
		'''视频搜索   优酷 爱奇艺 腾讯 PP视频  ...'''
		from Spiders.setting import baidu_headers
		r = requests_get(url=self.url, headers=baidu_headers,data=self.params)
		result_map = BaiduParser.v_search_parser(r)
		print("result_map",result_map)
		if not result_map:
			return result_map
		for mid_url in result_map:
			print(mid_url)
			result_url = self.get_url_bymid(mid_url['url'])
			for x in self.host:
				if not result_url and mid_url.get("r_url") and x in mid_url.get("r_url"):
					data = self.host_map[x]().crawl(mid_url)
					if data and data.get("status")!=False:
						return data
				elif result_url and x in result_url:
					print(self.host_map[x])
					mid_url['url'] = result_url
					data = self.host_map[x]().crawl(mid_url)
					if data and data.get("status")!=False:
						return data
			

	def get_url_bymid(self,url):
		'''百度搜索结果页面的url是中间url，这里hui得到 目标page url'''
		from Spiders.setting import baidu_headers
		r = requests_get(url=url, headers=baidu_headers)
		return BaiduParser.parse_mid_tourl(r)

	@staticmethod
	def crawl(self,urls):
		from Spiders.setting import baidu_headers
		r = requests_get(url=urls["url"],headers=baidu_headers)
		return BaiduParser.baike_parser(r)