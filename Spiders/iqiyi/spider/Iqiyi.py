#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-28 17:37:50
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
from Spiders.iqiyi.parsers.IqiyiParser import IqiyiParser
# from Utils.sim_content import sim_content
from Api.app.content import merge_poster
from DB.MongodbClient import mongo_conn
sys.path.append('./')

# 爱奇艺

headers = None

class Iqiyi(object):
    """docstring for ClassName"""

    def __init__(self, **args):
        # super(ClassName, self).__init__()
        # self.session = requests.Session()
        # self.tvId = args['tvId']
        # self.albumId = args['albumId']
        self.parser = IqiyiParser()
        '''非常齐全的数据，包含影片主要信息和导演主演信息'''
        self.videos_url = u'http://mixer.video.iqiyi.com/jp/mixin/videos/{tvId}?select=user,credit,focus,star,cast&status=1'
        '''用户画像'''
        self.get_user_profile_url = u'https://uaa.if.iqiyi.com/video_index/v2/get_user_profile?album_id={albumId}&callback='
        '''pc和移动端播放数量'''
        self.playCountPCMobileCb_url = u'http://cache.video.iqiyi.com/pc/pr/{albumId}/playCountPCMobileCb?callback=playCountPCMobileCb'
        '''获取推荐 uid 在cookies里取'''
        self.recommend = u'http://qiyu.iqiyi.com/p13n20?area=rabbit&uid={uid}&ppuid=&cid_num=-1_10&rltfmt=json&play_platform=PC_QIYI'
        self.star_url = u'http://www.iqiyi.com/lib/s_{id}.html'

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
        return self.parser.start_detail(r, url)

    def crawl(self, urls):
        r = requests_get(url=urls['url'], headers=headers)
        albumId_tvId = self.parser.parse_albumId_tvId(r=r, url=urls['url'])
        print("albumId_tvId", albumId_tvId)
        if not albumId_tvId or not albumId_tvId.get("tvId"):
            return {"status": False, 'urls': urls}
        exists = self.before_crawl(albumId_tvId['tvId'])
        if exists:
            return exists
        info = self.vinfo(tvId=albumId_tvId.get("tvId"))
        if not info:
            return False
        data = self.parser.merge_fields(info)
        data = self.check_crawl_star(data)
        if albumId_tvId.get('play') and info.get("cast") and len(info.get("cast").get("directors")) == 0 and len(info.get("cast").get("mainActors")) == 0 and len(info.get("cast").get("singers")) == 0 and len(info.get("cast").get("actors")) == 0 and len(info.get("cast").get("guests")) == 0:
            play = requests_get(url=albumId_tvId["play"], headers=headers)
            _temp = self.parser.plays_parser(play)
            print(
                "////////////////////////////////////////////////////////////////_temp", _temp)
            data = dict(data.items()+_temp.items())
            if _temp.get("year"):
            	data['year'] = _temp.get("year")
            if data.get("directors_list"):
                directors_list = []
                # print(data.get("directors_list"))
                for x in data.get("directors_list"):
                    _temp = self.crawl_star(x["iqiyi_url"])
                    if _temp is not None:
                        directors_list.append(_temp)
                data['directors_list'] = directors_list

            if data.get("starring_list"):
                starring_list = []
                for x in data.get("starring_list"):
                    _temp = self.crawl_star(x["iqiyi_url"])
                    if _temp:
                        starring_list.append(_temp)
                data['starring_list'] = starring_list
            if data.get("actors_list"):
                actors_list = []
                for x in data.get("actors_list"):
                    _temp = self.crawl_star(x["iqiyi_url"])
                    if _temp:
                        actors_list.append(_temp)
                data['actors_list'] = actors_list

        data["user_profile"] = self.user_profile(
            albumId=albumId_tvId.get("albumId"))
        data['iqiyi_playCountPCMobileCb'] = self.playCountPCMobileCb(
            albumId=albumId_tvId.get("albumId"))

        if not data or not data.get("title"):
            return False
        data = self.save(data)
        self.after_save(data)
        return data

    def before_crawl(self,tvId):
        c = mongo_conn.contents.find({"iqiyi_tvId":tvId})
        if c.count() > 0:
            c['_id'] = str(c['_id'])
            return c
        else:
            return None

    def check_crawl_star(self,data):
    	if not data:
    		return False
    	if data.get("directors_list"):
    		directors_list = []
    		for x in data.get("directors_list"):
    			if x.get("iqiyi_id"):
    				s = self.crawl_star(url=self.star_url.format(id=x.get("iqiyi_id")))
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
                if x.get("iqiyi_id"):
                    s = self.crawl_star(url=self.star_url.format(id=x.get("iqiyi_id")))
                    if s:
                        starring_list.append(s)
                    else:
                        starring_list.append(x)
                else:
                    starring_list.append(x)
            data['starring_list'] = starring_list

        if data.get("speakers_list"):
    		speakers_list = []
    		for x in data.get("speakers_list"):
    			if x.get("iqiyi_id"):
    				s = self.crawl_star(url=self.star_url.format(id=x.get("iqiyi_id")))
    				if s:
    					speakers_list.append(s)
    				else:
    					speakers_list.append(x)
    			else:
    				speakers_list.append(x)
    		data['speakers_list'] = speakers_list
    	
    	if data.get("screenwriter_list"):
    		screenwriter_list = []
    		for x in data.get("screenwriter_list"):
    			if x.get("iqiyi_id"):
    				s = self.crawl_star(url=self.star_url.format(id=x.get("iqiyi_id")))
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
    			if x.get("iqiyi_id"):
    				s = self.crawl_star(url=self.star_url.format(id=x.get("iqiyi_id")))
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
                if x.get("iqiyi_id"):
                    s = self.crawl_star(url=self.star_url.format(id=x.get("iqiyi_id")))
                    if s:
                        actors_list.append(s)
                    else:
                        actors_list.append(x)
                else:
                    actors_list.append(x)
            data['actors_list'] = actors_list


        if data.get("hosts_list"):
            hosts_list = []
            for x in data.get("hosts_list"):
                if x.get("iqiyi_id"):
                    s = self.crawl_star(url=self.star_url.format(id=x.get("iqiyi_id")))
                    if s:
                        hosts_list.append(s)
                    else:
                        hosts_list.append(x)
                else:
                    hosts_list.append(x)
            data['hosts_list'] = hosts_list

        if data.get("publishers_list"):
            publishers_list = []
            for x in data.get("publishers_list"):
                if x.get("iqiyi_id"):
                    s = self.crawl_star(url=self.star_url.format(id=x.get("iqiyi_id")))
                    if s:
                        publishers_list.append(s)
                    else:
                        publishers_list.append(x)
                else:
                    publishers_list.append(x)
            data['publishers_list'] = publishers_list

        if data.get("singers_list"):
    		singers_list = []
    		for x in data.get("singers_list"):
    			if x.get("iqiyi_id"):
    				s = self.crawl_star(url=self.star_url.format(id=x.get("iqiyi_id")))
    				if s:
    					singers_list.append(s)
    				else:
    					singers_list.append(x)
    			else:
    				singers_list.append(x)
    		data['singers_list'] = singers_list
    	
    	if data.get("guests_list"):
    		guests_list = []
    		for x in data.get("guests_list"):
    			if x.get("iqiyi_id"):
    				s = self.crawl_star(url=self.star_url.format(id=x.get("iqiyi_id")))
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
                _id = self.save_iqiyi_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']
        if data.get("screenwriter_list"):
            for x in data.get("screenwriter_list"):
                _id = self.save_iqiyi_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("publishers_list"):
            for x in data.get("publishers_list"):
                _id = self.save_iqiyi_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("singers_list"):
            for x in data.get("singers_list"):
                _id = self.save_iqiyi_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("directors_list"):
            for x in data.get("directors_list"):
                _id = self.save_iqiyi_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("speakers_list"):
            for x in data.get("speakers_list"):
                _id = self.save_iqiyi_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("peiyin_list"):
            for x in data.get("peiyin_list"):
                _id = self.save_iqiyi_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("actors_list"):
            for x in data.get("actors_list"):
                _id = self.save_iqiyi_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("guests_list"):
            for x in data.get("guests_list"):
                _id = self.save_iqiyi_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']


        if data.get("hosts_list"):
            for x in data.get("hosts_list"):
                _id = self.save_iqiyi_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        
        return self.save_content_and_poster(data)
        # content_id = mongo_conn.contents.insert(data, check_keys=False)
        # del data['_id']
        # _id = mongo_conn.iqiyi_videos.insert(data, check_keys=False)
        # del data['_id']
        # if data.get("poster"):
        #     for x in data.get("poster"):
        #         x['content_id'] = str(content_id)
        #         _tempid = mongo_conn.posters.insert(x, check_keys=False)
        #         if x.get("_id"):
        #             del x['_id']

        # data["_id"] = str(content_id)
        # return data

    def save_content_and_poster(self,data):
        query = {}
        query['iqiyi_tvId'] = data['iqiyi_tvId']
        query['title'] = data['title']
        exists = mongo_conn.contents.find(query)
        if exists.count() > 0:
            data['_id'] = str(exists[0]['_id'])
            return data
        else:
            content_id = mongo_conn.contents.insert(data, check_keys=False)
            del data['_id']
            _id = mongo_conn.iqiyi_videos.insert(data, check_keys=False)
            del data['_id']
            data['_id'] = str(content_id)
            return self.save_poster(data)

    def save_poster(self,data):
        if data.get("poster"):
            for x in data.get("poster"):
                x['content_id'] = data['_id']
                _tempid = mongo_conn.posters.insert(x,check_keys=False)
                print(_tempid)
                if x.get("_id"):
                    del x['_id']
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
            if len(query)<3:
                return str(mongo_conn.stars.insert(star,check_keys=False))
            r = mongo_conn.stars.find(query)
            if r.count() > 0:
                return str(r[0]["_id"])
            else:
                return str(mongo_conn.stars.insert(star, check_keys=False))
        except Exception as e:
            return str(mongo_conn.stars.insert(star, check_keys=False))

    def save_iqiyi_star(self, star):
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
            if len(query)<3:
                return str(mongo_conn.iqiyi_stars.insert(star,check_keys=False))
            r = mongo_conn.stars.find(query)
            if r.count() > 0:
                return str(r[0]["_id"])
            else:
                return str(mongo_conn.iqiyi_stars.insert(star, check_keys=False))
        except Exception as e:
            return str(mongo_conn.iqiyi_stars.insert(star, check_keys=False))

    def after_save(self,data):
        merge_poster(data)
