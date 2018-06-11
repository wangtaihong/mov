#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-30 19:58:57
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$


from Utils.request import requests_get, requests_post
# import requests

import sys, re
sys.path.append('../')
from Spiders.setting import headers
from Spiders.qq.parsers.QQParser import QQParser
from DB.MongodbClient import mongo_conn
from Utils.sim_content import sim_content
sys.path.append('./')

headers = None
# qq
class QQ(object):
    """docstring for ClassName"""
    def __init__(self, **args):
        # super(ClassName, self).__init__()
        # self.session = requests.Session()
        self.parsers = QQParser()
        pass

    def crawl(self,urls):
        m = re.search(u'v\.qq\.com/x/cover/',urls['r_url'])
        url = urls["url"]
        if m:
            r = requests_get(url=url,headers=headers)
            url = self.parsers.detail_url_parser(r)
        r = requests_get(url=url,headers=headers)
        # class="player_title"
        data = self.parsers.vdetail_parser(r)
        data = self.check_crawl_star(data)
        if not data or not data.get("title"):
            return None
        self.after_save(data)
        return self.save(data)

    # @staticmethod
    def crawl_star(self,url):
        r = requests_get(url=url,headers=headers)
        return self.parsers.parse_star(r=r,url=url)

    def check_crawl_star(self,data):
    	if data==None:
    		return data
        if data.get("directors_list"):
            directors_list = []
            for x in data.get("directors_list"):
                if x.get("qq_home_page"):
                    s = self.crawl_star(url=x.get("qq_home_page"))
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
                if x.get("qq_home_page"):
                    s = self.crawl_star(url=x.get("qq_home_page"))
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
                if x.get("qq_home_page"):
                    s = self.crawl_star(url=x.get("qq_home_page"))
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
                if x.get("qq_home_page"):
                    s = self.crawl_star(url=x.get("qq_home_page"))
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
                if x.get("qq_home_page"):
                    s = self.crawl_star(url=x.get("qq_home_page"))
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
                if x.get("qq_home_page"):
                    s = self.crawl_star(url=x.get("qq_home_page"))
                    if s:
                        guests_list.append(s)
                    else:
                        guests_list.append(x)
                else:
                    guests_list.append(x)
            data['guests_list'] = guests_list
        return data

    def save(self,data):
        data["source"] = "qq"
        if data.get("starring_list"):
            for x in data.get("starring_list"):
                _id = self.save_qq_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']
        if data.get("screenwriter_list"):
            for x in data.get("screenwriter_list"):
                _id = self.save_qq_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("directors_list"):
            for x in data.get("directors_list"):
                _id = self.save_qq_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("peiyin_list"):
            for x in data.get("peiyin_list"):
                _id = self.save_qq_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("actors_list"):
            for x in data.get("actors_list"):
                _id = self.save_qq_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("guests_list"):
            for x in data.get("guests_list"):
                _id = self.save_qq_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        return self.save_content_and_poster(data)
        # content_id = mongo_conn.contents.insert(data,check_keys=False)
        # if data.get("_id"):
        #     del data['_id']
        # _id = mongo_conn.qq_videos.insert(data,check_keys=False)
        # if data.get("_id"):
        #     del data['_id']
        # if data.get("poster"):
        #     for x in data.get("poster"):
        #         x['content_id'] = str(content_id)
        #         _tempid = mongo_conn.posters.insert(x,check_keys=False)
        #         print(_tempid)
        #         if x.get("_id"):
        #             del x['_id']

        # data['_id'] = str(content_id)
        # return data

    def save_content_and_poster(self,data):
        query = {}
        query['source'] = 'qq'
        if data.get("qq_play"):
            query["qq_play"] = data['qq_play']
        if data.get("qq_id"):
            query['qq_id'] = data['qq_id']
        query['title'] = data['title']
        if len(query)>2:
            exists = mongo_conn.contents.find(query)
            if exists.count()>0:
                data['_id'] = str(exists[0]['_id'])
                return data
            else:
                content_id = mongo_conn.contents.insert(data,check_keys=False)
                if data.get("_id"):
                    del data['_id']
                _id = mongo_conn.qq_videos.insert(data,check_keys=False)
                if data.get("_id"):
                    del data['_id']
                data['_id'] = str(content_id)
                return self.save_poster(data)
        else:
            content_id = mongo_conn.contents.insert(data,check_keys=False)
            if data.get("_id"):
                del data['_id']
            _id = mongo_conn.qq_videos.insert(data,check_keys=False)
            if data.get("_id"):
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

    def save_star(self,star):
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
                return str(mongo_conn.stars.insert(star,check_keys=False))
            r = mongo_conn.stars.find(query)
            if r.count()>0:
                return str(r[0]["_id"])
            else:
                return str(mongo_conn.stars.insert(star,check_keys=False))
        except Exception as e:
            return str(mongo_conn.stars.insert(star,check_keys=False))

    def save_qq_star(self,star):
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
                return str(mongo_conn.qq_stars.insert(star,check_keys=False))
            r = mongo_conn.stars.find(query)
            if r.count()>0:
                return str(r[0]["_id"])
            else:
                return str(mongo_conn.qq_stars.insert(star,check_keys=False))
        except Exception as e:
            return str(mongo_conn.qq_stars.insert(star,check_keys=False))

    def after_save(self,data):
        p = sim_content(data)
        if p:
            for x in p:
                mongo_conn.posters.insert(x,check_keys=False)