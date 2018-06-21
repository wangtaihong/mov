#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-26 09:52:46
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

import re
from lxml import etree
import json, demjson
from Utils.utils import parse_simple, area_process, language_process, split_space

import sys
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('../')
from Spiders.Items import Contents, Star, Poster
sys.path.append('./')
import time

class SohuParser(object):
	"""docstring for ClassName"""
	def __init__(self, **arg):
		# super(ClassName, self).__init__()
		# self.arg = arg
		pass

	
	def playlistId_parser(self,r):
		try:
			page = etree.HTML(r)
		except Exception as e:
			return False
		playlistId = re.search(u'playlistId *= *"(\d*)',r)
		__playlistId = re.search(u"playListId: *'(\d*)",r)
		_playlistId = re.search(u'PLAYLIST_ID="(\d*)',r)
		aid = page.xpath(u'//input[@id="aid"]')
		if playlistId:
			return playlistId.group(1)
		elif _playlistId:
			return _playlistId.group(1)
		elif __playlistId:
			return __playlistId.group(1)
		elif len(aid) > 0:
			return aid[0].get("value")
		else:
			return None

	
	def vdetail_parser(self, r):
		try:
			page = etree.HTML(r)
		except Exception as e:
			return False
		
		L = Contents()
		# area = page.xpath(u'//span[contains(text(),"地　区:")]')
		title = page.xpath(u'.//h2[contains(@class,"dbt")]')
		if len(title) > 0:
			L.title = parse_simple(title[0].text)

		sohu_rating = page.xpath(u'.//span[@class="socre"]')
		_rating = page.xpath(u'.//span[@class="movie_score"]')
		if len(sohu_rating) > 0:
			L.sohu_rating = parse_simple(sohu_rating[0].text)
		elif len(_rating) > 0:
			L.sohu_rating = parse_simple(_rating[0].text)

		sohu_plays_num = page.xpath(u'.//em[contains(@class,"acount")]')
		if len(sohu_plays_num) > 0:
			L.sohu_plays_num = parse_simple(sohu_rating_sum[0].text)

		sohu_rating_sum = page.xpath(u'span[@class="vssum"]')
		if len(sohu_rating_sum) > 0:
			L.sohu_rating_sum = parse_simple(sohu_rating_sum[0].text)

		starring = page.xpath(u".//p[contains(text(),'主演')]/a")
		s = page.xpath(u".//span[contains(text(),'主演')]")
		if len(starring) > 0:
			L.starring = ",".join(set([parse_simple(x.text) for x in starring]))
			L.starring_list = [{"name":parse_simple(x.text),"sohu_url":"https:"+x.get("href")} for x in starring]
		elif len(s)>0:
			L.starring = ",".join([parse_simple(x) for x in s[0].text.replace("主演：","").replace("/",",").split(',')])

		directors = page.xpath(u"//p[contains(text(),'导演')]/a")
		d = page.xpath(u"//span[contains(text(),'导演')]")
		if len(directors) > 0:
			L.directors = ",".join(set([parse_simple(x.text) for x in directors]))
			L.directors_list = [{"name":parse_simple(x.text),"sohu_url":"https:"+x.get("href")} for x in directors]
		elif len(d):
			L.directors = ",".join([parse_simple(x) for x in d[0].text.replace("导演：","").replace("/",",").split(',')])

		tags = page.xpath(u"//p[contains(text(),'类型')]/a")
		t = page.xpath(u"//span[contains(text(),'类型')]/em")
		if len(tags) > 0:
			L.tags = ",".join(set([parse_simple(x.text) for x in tags]))
		elif len(t) > 0:
			L.tags = ",".join(set([parse_simple(x.text) for x in t]))

		tags = page.xpath(u"//p[contains(text(),'类型')]/a")
		if len(tags) > 0:
			L.tags = ",".join(set([parse_simple(x.text) for x in tags]))

		year = page.xpath(u"//p[contains(text(),'年份')]/a")
		if len(year) > 0:
			L.year = ",".join(set([parse_simple(x.text) for x in year]))

		summary = page.xpath(u'//div[contains(@class,"J-fullintro")]')
		_summary = page.xpath(u'//p[contains(@class,"part_info")]')
		if len(summary) > 0:
			L.summary = parse_simple(summary[0].text).replace("简介：","")
		elif len(_summary) > 0:
			L.summary = parse_simple(summary[0].text).replace("简介：","")

		img_url = page.xpath(u'//a[contains(@class,"J-video-cover")]/img')
		_img = page.xpath(u'//div[contains(@class,"movie-info-img")]/img')
		L.poster = []
		if len(img_url) > 0:
			L.img_url = u"https:"+img_url[0].get("href")
			L.poster.append({"url":L.img_url,"width":img_url[0].get("width"),"height":img_url[0].get("height")})
		elif len(_img):
			L.img_url = u"https:"+_img[0].get("href")
			L.poster.append({"url":L._img,"width":_img[0].get("width"),"height":_img[0].get("height")})
		p = page.xpath(u'//img[@class="bg_img"]')
		# _p = 'background:url(//photocdn.tv.sohu.com/img/20180504/pic_compress_8e1253b4-077f-47b2-926d-81698fe02d8b_q_mini.jpg)'
		_p = re.search(u'background:url(\(//photocdn([^\)]+?)\))',r)
		if len(p)>0:
			L.poster.append({"url":p[0].get("src")})
		if _p:
			L.poster.append({"url":"https:"+_p.group(1)})

		duration = re.search(u'时长：(\d*)',r)
		if duration:
			L.duration = duration.group(1)

		area = page.xpath(u'//span[contains(text(),"地区")]')
		if area:
			L.area = parse_simple(area[0].text).replace("地区：","")

		L.created_at = time.time()
		return L.__dict__

	
	def star_parser(self,r,url=None):
		try:
			page = etree.HTML(r)
		except Exception as e:
			return False
		S = Star()
		avatar = page.xpath(u'//div[@class="colL"]/img')
		if len(avatar) > 0:
			S.avatar = "https:"+avatar[0].get("src")

		name = page.xpath(u'//div[contains(@class,"rowA")]/h2')
		if len(name)>0:
			S.name = parse_simple(name[0].text)
		star_id = re.search(u'star_id=(\d*)',r)
		if star_id:
			S.sohu_id = star_id.group(1)
		area = page.xpath(u'//li[contains(text(),"地区")]/em')
		if len(area)>0:
			S.area = area_process(parse_simple(area[0].text))

		birthplace = page.xpath(u'//li[contains(text(),"出生地")]/em')
		if len(birthplace)>0:
			S.birthplace = split_space(birthplace[0].text.replace("/",","))

		date_birth = page.xpath(u'//li[contains(text(),"生日")]/em')
		if len(date_birth)>0:
			S.date_birth = parse_simple(date_birth[0].text)

		intro = page.xpath(u'//p[contains(@class,"intro")]/text()')
		if intro:
			S.intro = parse_simple("".join(intro))

		body_height = page.xpath(u'//li[contains(text(),"身高")]/em')
		if len(body_height)>0:
			S.body_height = parse_simple(body_height[0].text)

		occupation = page.xpath(u'//li[contains(text(),"职业")]/em')
		if len(occupation)>0:
			S.occupation = split_space(occupation[0].text.replace("/",","))

		constellation = page.xpath(u'//li[contains(text(),"星座")]/em')
		if len(constellation)>0:
			S.constellation = parse_simple(constellation[0].text)

		alias = page.xpath(u'//li[contains(text(),"别名")]/em')
		if len(alias)>0:
			S.alias = ",".join([parse_simple(x) for x in alias[0].text.replace("/",",").split(',')])


		S.created_at = time.time()
		return S.__dict__

	
	def merge_content_fields(self,dic):
		L = Contents()
		if dic.get("directors"):
			L.directors = ",".join(dic.get("directors"))
		if dic.get("directorsMap"):
			L.directors_list = [{"name":x.get("starName"),"souhu_id":x.get("starId"),"sohu_url":"https:"+x.get("starUrl")}for x in dic.get("directorsMap")]
		if dic.get("mainActors"):
			L.starring = ",".join(dic.get("mainActors"))
		if dic.get("mainActorsMap"):
			L.starring_list = [{"name":x.get("starName"),"souhu_id":x.get("starId"),"sohu_url":"https:"+x.get("starUrl")}for x in dic.get("mainActorsMap")]
		if dic.get("albumDesc"):
			L.summary = dic.get("albumDesc")
		L.title = dic.get("albumName")
		if dic.get("albumPageUrl"):
			L.sohu_url = "https:"+dic.get("albumPageUrl")
		if dic.get("area"):
			L.producer_country = area_process(dic.get("area"))
		if dic.get("categories"):
			L.tags = ",".join(dic.get("categories"))
		if dic.get("defaultPageUrl"):
			L.sohu_play_url = "https:"+dic.get("defaultPageUrl")
		if dic.get("largeVerPicUrl"):
			L.img_url = "https:"+dic.get("largeVerPicUrl")
		L.poster = []
		if dic.get("largeVerPicUrl"):
			L.poster.append({"url":"https:"+dic.get("largeVerPicUrl")})
		if dic.get("largePicUrl"):
			L.poster.append({"url":"https:"+dic.get("largePicUrl")})
		if dic.get("largeHorPicUrl"):
			L.poster.append({"url":"https:"+dic.get("largeHorPicUrl")})
		if dic.get("pic144_144"):
			L.poster.append({"url":"https:"+dic.get("pic144_144")})
		if dic.get("pic170_110"):
			L.poster.append({"url":"https:"+dic.get("pic170_110")})
		if dic.get("pic170_225"):
			L.poster.append({"url":"https:"+dic.get("pic170_225")})
		if dic.get("pic240_330"):
			L.poster.append({"url":"https:"+dic.get("pic240_330")})
		if dic.get("pic50_50"):
			L.poster.append({"url":"https:"+dic.get("pic50_50")})
		if dic.get("smallHorPicUrl"):
			L.poster.append({"url":"https:"+dic.get("smallHorPicUrl")})
		if dic.get("smallPicUrl"):
			L.poster.append({"url":"https:"+dic.get("smallPicUrl")})
		if dic.get("smallVerPicUrl"):
			L.poster.append({"url":"https:"+dic.get("smallVerPicUrl")})
		# L.playlistid = dic.get("playlistid")
		L.year = dic.get("publishYear")
		L.all_episode = dic.get("totalSet")
		L.sohu_tvid = dic.get("tvId")
		L.sohu_vid = dic.get("vid")
		L.sohu_kissId = dic.get("kissId")
		L.sohu_playlistid = dic.get("playlistid")
		L.sohu_pid = dic.get("pid")
		L.sohu_pianhuaPid = dic.get("pianhuaPid")
		# L.videos = []
		# if dic.get("videos"):
		# 	L.videos = self.merge_videos(dic.get("videos"),L)
		# if dic.get("prevideos"):
		# 	L.videos += self.merge_videos(dic.get("prevideos"),L)

		L.created_at = time.time()

		return L.__dict__
	
	
	def merge_videos(self,videos,L):
		videos_list = []
		for x in videos:
			_temp = {}
			if x.get("videos") and x.get("videos").get("ep"):
				_temp["ep"] = x.get("videos").get("ep")
			_temp["name"] = x.get("name")
			if x.get("order"):
				_temp["episode"] = x.get("order")
			if x.get("playLength"):
				_temp['duration'] = x.get("playLength")/60
			if x.get("publishTime"):
				_temp['release_date'] = x.get("publishTime")
			if x.get("showName"):
				_temp['sub_title'] = x.get("showName")
			_temp["poster"] = []
			if x.get("smallVerPicUrl"):
				_temp["poster"].append({"url":"https:"+x.get("smallVerPicUrl"),"name":u"剧照"})
			if x.get("tvCropPic12090"):
				_temp["poster"].append({"url":"https:"+x.get("tvCropPic12090"),"name":u"剧照"})
			if x.get("tvCropPic160"):
				_temp["poster"].append({"url":"https:"+x.get("tvCropPic160"),"name":u"剧照"})
			if x.get("tvCropPic170"):
				_temp["poster"].append({"url":"https:"+x.get("tvCropPic170"),"name":u"剧照"})
			if x.get("tvCropPic170225"):
				_temp["poster"].append({"url":"https:"+x.get("tvCropPic170225"),"name":u"剧照"})
			if x.get("tvId"):
				_temp["sohu_tvid"] = x.get("tvId")
			if x.get("vid"):
				_temp["sohu_vid"] = x.get("vid")
			if x.get("videoDesc"):
				_temp["summary"] = x.get("videoDesc")
			_temp["sohu_playlistid"] = L.sohu_playlistid
			_temp["directors"] = L.directors
			_temp["directors_list"] = L.directors_list
			_temp["starring"] = L.starring
			_temp["starring_list"] = L.starring_list
			_temp["producer_country"] = L.producer_country
			_temp["tags"] = L.tags
			_temp["year"] = L.year
			videos_list.append(_temp)
		
		return videos_list

	# def parser_vinfo(self,r):
	# 	m = re.search(u'videolist\(([^\);]+?)\);',r)
	# 	try:
	# 		return json.loads(m.group(1))
	# 	except Exception as e:
	# 		pass
	# 	try:
	# 		return demjson.decode(m.group(1))
	# 	except Exception as e:
	# 		pass
	# 	return m

	def parser_vinfo(self,r):
		# r = r.replace(u"__get_videolist(","").replace(u');',"")
		try:
			return json.loads(r)
		except Exception as e:
			pass
		try:
			return demjson.decode(r)
		except Exception as e:
			pass
		return m