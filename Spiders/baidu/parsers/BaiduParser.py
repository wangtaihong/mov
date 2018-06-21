#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-25 09:21:28
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

import re
from lxml import etree
import json
from Utils.utils import parse_simple, area_process, language_process

import sys
sys.path.append('../')
from Spiders.Items import Contents
sys.path.append('./')
import time
class BaiduParser(object):
	"""docstring for ClassName"""
	def __init__(self, **arg):
		# super(ClassName, self).__init__()
		# self.arg = arg
		pass

	@staticmethod
	def v_search_parser(r):
		'''视频搜索 返回最相关的一个url'''
		try:
			page = etree.HTML(r)
		except Exception as e:
			return None
		container = page.xpath(u'.//div[contains(@class, "c-container")]')     #container
		re_data = []
		if len(container) > 0:
			"""优先给视频框"""
			for con in container:
				mvideo = con.xpath(u'.//div[@class="op-zx-new-mvideo-out"]')    #电影视频
				tvideo = con.xpath(u'.//div[@class="op-zx-new-tvideo-out"]')    #电视剧视频
				iqiyi = con.xpath(u'.//div[@data-site="iqiyi.com"]')
				iqiyi = con.xpath(u'.//div[@data-site="iqiyi.com"]')
				qq = con.xpath(u'.//div[@data-site="qq.com"]')
				if len(iqiyi)>0:
					a = iqiyi[0].xpath(u'.//li[contains(@class,"c-gap-top")]/a')
					data = {}
					if len(a):
						data["url"] = a[0].get("href")
						data['r_url'] = 'www.iqiyi.com'
						re_data.append(data)

				if len(qq)>0:
					data = {}
					a = qq[0].xpath(u'.//li[contains(@class,"c-gap-top")]/a')
					if len(a):
						data["url"] = a[0].get("href")
						data['r_url'] = 'www.v.qq.com'
						re_data.append(data)

			'''搜索结果没有视频框'''
			for con in container:
				strdiv = etree.tostring(con, encoding='unicode')
				# douban = re.search(u"豆瓣",strdiv)
				douban_url = re.search(u'movie\.douban\.com/subje',strdiv)
				_douban_url = re.search(u'douban\.com/doubana',strdiv)
				
				# baidu = re.search(u"百度视频",strdiv)
				baidu_url = re.search(u'v\.baidu\.com\/movie\/',strdiv)
				# qq = re.search(u"腾讯",strdiv)
				qq_url = re.search(u'v\.qq\.com/x/cover',strdiv)
				_qq_url = re.search(u'v\.qq\.com/',strdiv)

				# iqiyi = re.search(u"爱奇艺",strdiv)
				iqiyi_url = re.search(u'\.iqiyi\.com/',strdiv)
				youku = re.search(u'youku\.com',strdiv)
				sohu = re.search(u'tv\.sohu\.com',strdiv)

				if iqiyi_url:
					url = con.xpath(u'.//h3/a')
					r_url = con.xpath(u'.//*[@class="c-showurl"]')
					data = {}
					if len(url):
						data["url"] = url[0].get("href")
					if len(r_url):
						data["r_url"] = r_url[0].text
					else:
						data["r_url"] = u'www.iqiyi.com/'
					# return data
					re_data.append(data)

				"""腾讯优先级1"""
				if qq_url or _qq_url:
					url = con.xpath(u'.//h3/a')
					r_url = con.xpath(u'.//*[@class="c-showurl"]')
					_r_url = con.xpath(u'.//div[@class="g"]')
					data = {}
					if len(url):
						data["url"] = url[0].get("href")
					if len(r_url):
						data["r_url"] = r_url[0].text
						# return data
					elif len(_r_url)>0:
						data["r_url"] = _r_url[0].text
						# return data
					re_data.append(data)

				if sohu:
					url = con.xpath(u'.//h3/a')
					r_url = con.xpath(u'.//*[@class="c-showurl"]')
					_r_url = con.xpath(u'.//div[@class="g"]')
					data = {}
					if len(url):
						data["url"] = url[0].get("href")
					if len(r_url):
						data["r_url"] = r_url[0].text
					elif len(_r_url)>0:
						data["r_url"] = _r_url[0].text
					re_data.append(data)

				# if youku:
				# 	url = con.xpath(u'.//h3/a')
				# 	r_url = con.xpath(u'.//*[@class="c-showurl"]')
				# 	_r_url = con.xpath(u'.//div[@class="g"]')
				# 	data = {}
				# 	if len(url):
				# 		data["url"] = url[0].get("href")
				# 	if len(r_url):
				# 		data["r_url"] = "youku.com"
				# 	elif len(_r_url)>0:
				# 		data["r_url"] = "youku.com"
				# 	re_data.append(data)

				if douban_url:
					url = con.xpath(u'.//h3/a')
					r_url = con.xpath(u'.//*[@class="c-showurl"]')
					_r_url = con.xpath(u'.//div[@class="g"]')
					data = {}
					if len(url):
						data["url"] = url[0].get("href")
					if len(r_url):
						data["r_url"] = r_url[0].text
					elif len(_r_url)>0:
						data["r_url"] = _r_url[0].text
					re_data.insert(0,data)

				if _douban_url:
					url = con.xpath(u'.//h3/a')
					r_url = con.xpath(u'.//*[@class="c-showurl"]')
					_r_url = con.xpath(u'.//div[@class="g"]')
					data = {}
					if len(url):
						data["url"] = url[0].get("href")
					if len(r_url):
						data["r_url"] = r_url[0].text
					elif len(_r_url)>0:
						data["r_url"] = _r_url[0].text
					re_data.insert(0,data)


			# for con in container:
			# 	strdiv = etree.tostring(con, encoding='unicode')
			# 	baike = re.search(u"百度百科",strdiv)
			# 	baike_url = re.search(u'baike\.baidu\.com/',strdiv)
			# 	if baike and baike_url:
			# 		url = con.xpath(u'.//h3/a')
			# 		r_url = con.xpath(u'.//*[@class="c-showurl"]')
			# 		data = {}
			# 		if len(url):
			# 			data["url"] = url[0].get("href")
			# 		if len(r_url):
			# 			data["r_url"] = r_url[0].text
			# 			return data
			
		return re_data

	@staticmethod
	def parse_mid_tourl(r):
		# r = u'window.location.replace("http://www.iqiyi.com/a_19rrjptx89.html?vfm=2008_aldbd")}'
		"""中间跳转url"""
		try:
			page = etree.HTML(r)
		except Exception as e:
			return False
		referrer = page.xpath(u'.//meta[@name="referrer"]')
		m = re.search(u'window\.location\.replace\(\"([^\"\)\}]+?)\"\)\}',r)
		if m and len(referrer) > 0:
			return m.group(1)
		m1 = re.search(u'URL=\'([^\'\"]+?)\'\"',r)
		if m1:
			return m1.group(1)
		else:
			return None

	@staticmethod
	def baike_parser(r,url=None):
		try:
			r = re.sub(u'&nbsp;','',r)
			page = etree.HTML(r)
		except Exception as e:
			return False
		L = Contents()
		summary = page.xpath(u'//div[@class="lemmaWgt-lemmaSummary lemmaWgt-lemmaSummary-light"]')
		if len(summary) > 0:
			L.summary = summary[0].text

		title = page.xpath(u'//dt[contains(text(),"中文名")]')
		if len(title) > 0:
			L.title = parse_simple(title[0].getnext().text)

		foreign_title = page.xpath(u'//dt[contains(text(),"外文名")]')
		if len(foreign_title) > 0:
			L.foreign_title = parse_simple(foreign_title[0].getnext().text)

		production_company = page.xpath(u'//dt[contains(text(),"出品公司")]')
		if len(production_company) > 0:
			L.production_company = parse_simple(production_company[0].getnext().text)

		producer_country = page.xpath(u'//dt[contains(text(),"制片地区")]')
		if len(producer_country) > 0:
			L.producer_country = area_process(parse_simple(producer_country[0].getnext().text))

		directors_list = page.xpath(u'//dt[contains(text(),"导演")]')
		if len(directors_list) > 0:
			a_tag = directors_list[0].getnext().findall('a')
			if len(a_tag) > 0:
				L.directors_list = []
				directors = []
				for x in a_tag:
					L.directors_list.append({"name":parse_simple(x.text),"baike_id":x.get("data-lemmaid"),"baike_url":u'https://baike.baidu.com'+x.get("href")})
					directors.append(parse_simple(x.text))
				L.directors = ",".join(set(directors))
			else:
				L.directors = area_process(parse_simple(directors_list[0].getnext().text))

		screenwriter_list = page.xpath(u'//dt[contains(text(),"编剧")]')
		if len(screenwriter_list) > 0:
			a_tag = screenwriter_list[0].getnext().findall('a')
			if len(a_tag) > 0:
				L.screenwriter_list = []
				screenwriters = []
				for x in a_tag:
					L.screenwriter_list.append({"name":parse_simple(x.text),"baike_id":x.get("data-lemmaid"),"baike_url":u'https://baike.baidu.com'+x.get("href")})
					screenwriters.append(parse_simple(x.text))
				L.screenwriters = ",".join(set(screenwriters))
			else:
				L.screenwriters = area_process(parse_simple(screenwriter_list[0].getnext().text))

		starring_list = page.xpath(u'//dt[contains(text(),"主演")]')
		if len(starring_list) > 0:
			a_tag = starring_list[0].getnext().findall('a')
			if len(a_tag) > 0:
				L.starring_list = []
				starring = []
				for x in a_tag:
					L.starring_list.append({"name":parse_simple(x.text),"baike_id":x.get("data-lemmaid"),"baike_url":u'https://baike.baidu.com'+x.get("href")})
					starring.append(parse_simple(x.text))
				L.starring = ",".join(set(starring))
			else:
				L.starring = area_process(parse_simple(starring_list[0].getnext().text))

		alias = page.xpath(u'//dt[contains(text(),"其它译名")]')
		if len(alias) > 0:
			a_tag = alias[0].getnext().findall("a")
			if len(a_tag) > 0:
				L.alias = ",".join([parse_simple(x.text) for x in a_tag if parse_simple(x.text)])
			else:
				L.alias = parse_simple(alias[0].getnext().text)

		types = page.xpath(u'//dt[contains(text(),"类型")]')
		if len(types) > 0:
			L.type = area_process(parse_simple(types[0].getnext().text))

		duration = page.xpath(u'//dt[contains(text(),"片长")]')
		if len(duration) > 0:
			L.duration = area_process(parse_simple(duration[0].getnext().text))

		release_date = page.xpath(u'//dt[contains(text(),"上映时间")]')
		if len(release_date) > 0:
			L.release_date = area_process(parse_simple(release_date[0].getnext().text))

		release_date = page.xpath(u'//dt[contains(text(),"语言")]')
		if len(release_date) > 0:
			L.language = language_process(parse_simple(release_date[0].getnext().text))

		douban_rating = page.xpath(u'//span[contains(@class,"star-text")]')
		if len(douban_rating) > 0:
			L.douban_rating = douban_rating[0].text

		poster = page.xpath(u'//img[@alt="词条图片"]')
		if len(poster) > 0:
			L.poster = [{"url":poster[0].get("src"),"name":poster[0].get("alt")}]
			L.img_url = poster[0].get("src")

		actor_list = page.xpath(u'//ul[@class="actorList"]/li')
		if len(actor_list) > 0:
			starring = L.starring.split(',')
			L.actor_list = []
			starring_list = []
			for x in actor_list:
				_temp = {"avatar":x.find('img').get("src"),"name":x.xpath(u'//dl[@class="info"]/a')[0].text,"baike_id":x.xpath(u'//dl[@class="info"]/a')[0].get("data-lemmaid"),"baidu_url":"https://baike.baidu.com"+x.xpath(u'//dl[@class="info"]/a')[0].get("href")}
				if _temp['name'] in starring:
					starring_list.append(_temp)
				else:
					L.actor_list.append(_temp)
			if starring_list:
				L.starring_list = starring_list

		L.created_at = time.time()
		return L.__dict__
