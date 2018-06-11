#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-30 19:58:57
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$


from Utils.request import requests_get, requests_post
# import requests

import sys
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('../')
from Spiders.setting import headers
from Spiders.sohu.parsers.SohuParser import SohuParser
sys.path.append('./')

# 爱奇艺
class Sohu(object):
	"""docstring for ClassName"""
	def __init__(self, **args):
		# super(ClassName, self).__init__()
		# self.session = requests.Session()
		self.parser = SohuParser()
		self.playlist = u'https://pl.hd.sohu.com/videolist?playlistid={playlistid}&order=0&cnt=1&withLookPoint=1&preVideoRule=1&ssl=0&callback=__get_videolist'

	def vinfo(self,playlistid=None):
		r = requests_get(url=self.playlist.format(playlistid=playlistid),headers=headers)
		print(r)
		return self.parser.parser_vinfo(r)

	def crawl(self,urls):
		r = requests_get(url=urls["url"],headers=headers)
		playlistid = self.parser.playlistId_parser(r)
		if not playlistid:
			data = self.parser.vdetail_parser(r)
		info = self.vinfo(playlistid=playlistid)
		if not info:
			return None
		return self.parser.merge_content_fields(info)

	@staticmethod
	def crawl_star(self,url):
		r = requests_get(url=url,headers=headers)
		return self.parser.star_parser(r)

	def save(self,data):
		if data.get("starring_list"):
			for x in data.get("starring_list"):
				_id = mongo_conn.sohu_stars.insert(x,check_keys=False)
				del x['_id']
				_id = mongo_conn.stars.insert(x,check_keys=False)
				x['star_id'] = str(x['_id'])
				del x['_id']
		if data.get("screenwriter_list"):
			for x in data.get("screenwriter_list"):
				_id = mongo_conn.sohu_stars.insert(x,check_keys=False)
				del x['_id']
				_id = mongo_conn.stars.insert(x,check_keys=False)
				x['star_id'] = str(x['_id'])
				del x['_id']

		if data.get("directors_list"):
			for x in data.get("directors_list"):
				_id = mongo_conn.sohu_stars.insert(x,check_keys=False)
				del x['_id']
				_id = mongo_conn.stars.insert(x,check_keys=False)
				x['star_id'] = str(x['_id'])
				del x['_id']

		if data.get("peiyin_list"):
			for x in data.get("peiyin_list"):
				_id = mongo_conn.sohu_stars.insert(x,check_keys=False)
				del x['_id']
				_id = mongo_conn.stars.insert(x,check_keys=False)
				x['star_id'] = str(x['_id'])
				del x['_id']

		if data.get("actors_list"):
			for x in data.get("actors_list"):
				_id = mongo_conn.sohu_stars.insert(x,check_keys=False)
				del x['_id']
				_id = mongo_conn.stars.insert(x,check_keys=False)
				x['star_id'] = str(x['_id'])
				del x['_id']

		if data.get("guests_list"):
			for x in data.get("guests_list"):
				_id = mongo_conn.sohu_stars.insert(x,check_keys=False)
				del x['_id']
				_id = mongo_conn.stars.insert(x,check_keys=False)
				x['star_id'] = str(x['_id'])
				del x['_id']

		content_id = mongo_conn.contents.insert(data,check_keys=False)
		del data['_id']
		_id = mongo_conn.sohu_videos.insert(data,check_keys=False)
		del data['_id']
		if data.get("poster"):
			for x in data.get("poster"):
				x['content_id'] = str(content_id)
				_tempid = mongo_conn.poster.insert(x,check_keys=False)
				del x['_id']

		return data
