#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-26 09:52:46
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

import re
from lxml import etree
import json
from Utils.utils import parse_simple, area_process, language_process

import sys
sys.path.append('../')
from Spiders.Items import Contents, Star, Poster
sys.path.append('./')
import  time

class PPTVParser(object):
	"""docstring for ClassName"""
	def __init__(self, **arg):
		# super(ClassName, self).__init__()
		# self.arg = arg
		pass

	def vdetail_parser(self, r):
		try:
			page = etree.HTML(r)
		except Exception as e:
			return None
		
		L = Contents()
		# area = page.xpath(u'//span[contains(text(),"地　区:")]')
		category = page.xpath(u'//span[contains(@class,"module-bread-nav")]/a')
		if len(category) > 0:
			L.category = category[0].text
		
		title = page.xpath(u'//div[@class="module-dpage-info"]/div[@class="hd"]/h1')
		if len(title) > 0:
			m = re.search(u'『(.*)』(.*)',parse_simple(title[0].text))
			if m:
				L.title = m.group(2)
				L.tags = m.group(1)
			else:
				L.title = title[0].text

		pptv_rating = page.xpath(u'//b[@class="score"]')
		if len(pptv_rating) > 0:
			L.pptv_rating = pptv_rating[0].text

		peiyin_list = page.xpath(u'//li[(@class="actor") and (contains(text(),"声优"))]/a')
		if len(peiyin_list) > 0:
			L.peiyin_list = [{"name":x.text,"pptv_url":x.get("href")} for x in peiyin_list]
			L.peiyin = ",".join([x.text for x in peiyin_list])

		starring_list = page.xpath(u'//li[(@class="actor") and (contains(text(),"主演"))]/a')
		if len(starring_list) > 0:
			L.starring_list = [{"name":x.text,"pptv_url":x.get("href")} for x in starring_list]
			L.starring = ",".join([x.text for x in starring_list])

		directors_list = page.xpath(u'//li[(@class="actor") and (contains(text(),"导演"))]/a')
		if len(directors_list) > 0:
			L.directors_list = [{"name":x.text,"pptv_url":x.get("href")} for x in directors_list]
			L.directors = ",".join([x.text for x in directors_list])

		area = page.xpath(u'//li[(@class="actor") and (contains(text(),"地区"))]/a')
		if len(area) > 0:
			L.area = area[0].text

		pptv_plays_num = page.xpath(u'//li[contains(text(),"播放：")]')
		if len(pptv_plays_num) > 0:
			L.pptv_plays_num = pptv_plays_num[0].text.replace("播放：","")

		duration = re.search(u'片长：(\d*)',r)
		if duration:
			L.duration = duration.group(1)

		release_date = page.xpath(u'//li[contains(text(),"上映")]/a')
		if len(release_date) > 0:
			L.release_date = parse_simple(release_date[0].text)
		all_episode = re.search(u'共(\d*)集',r)
		_temp = page.xpath(u'//span[@class="ba_jj"]')
		if all_episode:
			L.all_episode = all_episode.group(1)
		elif len(_temp) > 0:
			L.all_episode = parse_simple(_temp[0].text)

		img_url = page.xpath(u'//div[contains(@class,"coverpic")]/img')
		img = page.xpath(u'//div[@class="module-dpage-banner"]/a/img')
		if len(img_url) > 0:
			L.img_url = img_url[0].get("data-src2")
			L.poster = [{"url":img_url[0].get("data-src2")}]
		elif len(img) > 0:
			L.img_url = img[0].get("src")
			L.poster = [{"url":img[0].get("src")}]
		
		L.created_at = time.time()
		return L.__dict__

	
	def star_parser(self,r,url=None):
		try:
			page = etree.HTML(r)
		except Exception as e:
			return None
		S = Star()
		avatar = page.xpath(u'//div[contains(@class,"bpic"]/img')
		if len(avatar) > 0:
			S.avatar = avatar[0].get("src")

		dl = page.xpath(u'//dl[@class="tit"]')
		title = page.xpath(u'//dl[@class="tit"]/dt/a')
		if len(title) > 0:
			S.title = title[0].text

		occupation = page.xpath(u'//li[contains(text(),"职业"]/span')
		if len(occupation) > 0:
			S.occupation = parse_simple(occupation[0].text)

		gender = page.xpath(u'//li[contains(text(),"性别"]/span')
		if len(gender) > 0:
			S.gender = parse_simple(gender[0].text)

		date_birth = page.xpath(u'//li[contains(text(),"生日"]/span')
		if len(date_birth) > 0:
			S.date_birth = parse_simple(date_birth[0].text)

		area = page.xpath(u'//li[contains(text(),"国家/地区"]/span')
		if len(area) > 0:
			S.area = parse_simple(area[0].text)

		S.created_at = time.time()
		return S.__dict__
