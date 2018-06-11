#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-28 17:37:50
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    :
# @Version : $Id$

from Utils.request import requests_get, requests_post
# import requests

import sys, re
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('../')
from Spiders.setting import headers
from Spiders.youku.parsers.YoukuParser import YoukuParser
from DB.MongodbClient import mongo_conn
sys.path.append('./')

# 爱奇艺


class Youku(object):
    """docstring for ClassName"""

    def __init__(self, **args):
        # super(ClassName, self).__init__()
        self.parser = YoukuParser()

    def vinfo(self, tvId=None):
        r = requests_get(url=self.videos_url.format(
            tvId=tvId), headers=headers)
        return self.parser.parse_info(r)

    def user_profile(self, albumId=None):
        r = requests_get(url=self.get_user_profile_url.format(
            albumId=albumId), headers=headers)
        return self.parser.parse_user_profile(r)

    def playCountPCMobileCb(self, albumId=None):
        r = requests_get(url=self.playCountPCMobileCb_url.format(
            albumId=albumId), headers=headers)
        return self.parser.parse_playCountPCMobileCb(r)

    def recommend(self, uid=None, session=None):
        return requests_get(url=self.playCountPCMobileCb_url.format(uid=uid), headers=headers, session=session)

    def crawl_star(self, url):
        r = requests_get(url=url, headers=headers)
        return self.parser.parse_star_show(r, url)

    def crawl(self, urls):
        m = re.search(u'youku\.com/show/',urls['r_url'])
        url = urls["url"]
        if not m:
            # r = requests_get(url=url,headers=headers)
            # url = self.parsers.detail_url_parser(r)
            return None
        r = requests_get(url=url,headers=headers)
        # class="player_title"
        data = self.parser.parse_detail(r=r)
        data = self.check_crawl_star(data)
        if not data or not data.get("title"):
            return None
        data = self.save(data)
        return data


    def check_crawl_star(self,data):
    	if data==None:
    		return data
    	if data.get("directors_list"):
    		directors_list = []
    		for x in data.get("directors_list"):
    			if x.get("youku_url"):
    				s = self.crawl_star(url=self.star_url.format(id=x.get("youku_url")))
    				if s:
    					directors_list.append(s)
    				else:
    					directors_list.append(x)
    			else:
    				directors_list.append(x)
    		data['directors_list'] = directors_list
    	
    	if data.get("starring_list"):
    		starring_list = []
    		for x in data.get("starring_list"):
    			if x.get("youku_url"):
    				s = self.crawl_star(url=self.star_url.format(id=x.get("youku_url")))
    				if s:
    					starring_list.append(s)
    				else:
    					starring_list.append(x)
    			else:
    				starring_list.append(x)
    		data['starring_list'] = starring_list
    	
    	if data.get("screenwriter_list"):
    		screenwriter_list = []
    		for x in data.get("screenwriter_list"):
    			if x.get("youku_url"):
    				s = self.crawl_star(url=self.star_url.format(id=x.get("youku_url")))
    				if s:
    					screenwriter_list.append(s)
    				else:
    					screenwriter_list.append(x)
    			else:
    				screenwriter_list.append(x)
    		data['screenwriter_list'] = screenwriter_list
    	
    	if data.get("peiyin_list"):
    		peiyin_list = []
    		for x in data.get("peiyin_list"):
    			if x.get("youku_url"):
    				s = self.crawl_star(url=self.star_url.format(id=x.get("youku_url")))
    				if s:
    					peiyin_list.append(s)
    				else:
    					peiyin_list.append(x)
    			else:
    				peiyin_list.append(x)
    		data['peiyin_list'] = peiyin_list
    	
    	if data.get("actors_list"):
    		actors_list = []
    		for x in data.get("actors_list"):
    			if x.get("youku_url"):
    				s = self.crawl_star(url=self.star_url.format(id=x.get("youku_url")))
    				if s:
    					actors_list.append(s)
    				else:
    					actors_list.append(x)
    			else:
    				actors_list.append(x)
    		data['actors_list'] = actors_list
    	
    	if data.get("guests_list"):
    		guests_list = []
    		for x in data.get("guests_list"):
    			if x.get("youku_url"):
    				s = self.crawl_star(url=self.star_url.format(id=x.get("youku_url")))
    				if s:
    					guests_list.append(s)
    				else:
    					guests_list.append(x)
    			else:
    				guests_list.append(x)
    		data['guests_list'] = guests_list
    	return data

    def save(self, data):
        data['source'] = 'iqiyi'
        if data.get("starring_list"):
            for x in data.get("starring_list"):
                _id = self.save_youku_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']
        if data.get("screenwriter_list"):
            for x in data.get("screenwriter_list"):
                _id = self.save_youku_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("directors_list"):
            for x in data.get("directors_list"):
                _id = self.save_youku_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("peiyin_list"):
            for x in data.get("peiyin_list"):
                _id = self.save_youku_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("actors_list"):
            for x in data.get("actors_list"):
                _id = self.save_youku_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("guests_list"):
            for x in data.get("guests_list"):
                _id = self.save_youku_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        content_id = mongo_conn.contents.insert(data, check_keys=False)
        del data['_id']
        _id = mongo_conn.youku_videos.insert(data, check_keys=False)
        del data['_id']
        if data.get("poster"):
            for x in data.get("poster"):
                x['content_id'] = str(content_id)
                _tempid = mongo_conn.posters.insert(x, check_keys=False)
                if x.get("_id"):
                    del x['_id']

        data["_id"] = str(content_id)
        return data

    def save_star(self, star):
        try:
            query = {}
            query['name'] = star["name"]
            if star.get("date_birth"):
                query["date_birth"] = star["date_birth"]
            if star.get("gender"):
                query["gender"] = star["gender"]
            if star.get("birthplace"):
                query["birthplace"] = star["birthplace"]
            if star.get("occupation"):
                query["occupation"] = star["occupation"]
            if star.get("constellation"):
                query["constellation"] = star["constellation"]
            if star.get("area"):
                query["area"] = star["area"]
            if len(query) < 3:
                return str(mongo_conn.stars.insert(star, check_keys=False))
            r = mongo_conn.stars.find(query)
            if r.count() > 0:
                return str(r[0]["_id"])
            else:
                return str(mongo_conn.stars.insert(star, check_keys=False))
        except Exception as e:
            return str(mongo_conn.stars.insert(star, check_keys=False))

    def save_youku_star(self, star):
        try:
            query = {}
            query['name'] = star["name"]
            if star.get("date_birth"):
                query["date_birth"] = star["date_birth"]
            if star.get("gender"):
                query["gender"] = star["gender"]
            if star.get("birthplace"):
                query["birthplace"] = star["birthplace"]
            if star.get("occupation"):
                query["occupation"] = star["occupation"]
            if star.get("constellation"):
                query["constellation"] = star["constellation"]
            if star.get("area"):
                query["area"] = star["area"]
            if len(query) < 3:
                return str(mongo_conn.youku_stars.insert(star, check_keys=False))
            r = mongo_conn.youku_stars.find(query)
            if r.count() > 0:
                return str(r[0]["_id"])
            else:
                return str(mongo_conn.youku_stars.insert(star, check_keys=False))
        except Exception as e:
            return str(mongo_conn.youku_stars.insert(star, check_keys=False))
