#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-30 19:58:57
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$


from Utils.request import requests_get, requests_post
# import requests

import sys, json
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('../')
from Spiders.setting import headers
from Spiders.sohu.parsers.SohuParser import SohuParser
from Utils.sim_content import sim_content
from DB.MongodbClient import mongo_conn
sys.path.append('./')

# 
class Sohu(object):
    """docstring for ClassName"""
    def __init__(self, **args):
        # super(ClassName, self).__init__()
        # self.session = requests.Session()
        self.parser = SohuParser()
        # self.playlist = u'https://pl.hd.sohu.com/videolist?playlistid={playlistid}&order=0&cnt=1&withLookPoint=1&preVideoRule=1&ssl=0&callback=__get_videolist'
        self.playlist = u'https://pl.hd.sohu.com/videolist?playlistid={playlistid}&order=0&cnt=1&withLookPoint=1&preVideoRule=1&ssl=0&callback='

    def vinfo(self,playlistid=None):
        r = requests_get(url=self.playlist.format(playlistid=playlistid),headers=headers)
        return self.parser.parser_vinfo(r)

    def crawl(self,urls):
        r = requests_get(url=urls["url"],headers=headers)
        playlistid = self.parser.playlistId_parser(r)
        if not playlistid:
            data = self.parser.vdetail_parser(r)
        info = self.vinfo(playlistid=playlistid)
        if not info:
            return False
        data = self.parser.merge_content_fields(info)
        data = self.check_crawl_star(data)
        if data==False:
            return False
        data = self.save(data)
        self.after_save(data)
        return data

    def crawl_star(self,url):
        r = requests_get(url=url,headers=headers)
        return self.parser.star_parser(r)

    def check_crawl_star(self,data):
        if not data:
            return data
        if data.get("directors_list"):
            directors_list = []
            for x in data.get("directors_list"):
                if x.get("sohu_url"):
                    s = self.crawl_star(url=x.get("sohu_url"))
                    if s:
                        directors_list.append(s)
                    else:
                        return False
                else:
                    directors_list.append(x)
            data['directors_list'] = directors_list

        if data.get("starring_list"):
            starring_list = []
            for x in data.get("starring_list"):
                if x.get("sohu_url"):
                    s = self.crawl_star(url=x.get("sohu_url"))
                    if s:
                        starring_list.append(s)
                    else:
                        return False
                else:
                    starring_list.append(x)
            data['starring_list'] = starring_list

        if data.get("speakers_list"):
            speakers_list = []
            for x in data.get("speakers_list"):
                if x.get("sohu_url"):
                    s = self.crawl_star(url=x.get("sohu_url"))
                    if s:
                        speakers_list.append(s)
                    else:
                        return False
                else:
                    speakers_list.append(x)
            data['speakers_list'] = speakers_list

        if data.get("screenwriter_list"):
            screenwriter_list = []
            for x in data.get("screenwriter_list"):
                if x.get("sohu_url"):
                    s = self.crawl_star(url=x.get("sohu_url"))
                    if s:
                        screenwriter_list.append(s)
                    else:
                        return False
                else:
                    screenwriter_list.append(x)
            data['screenwriter_list'] = screenwriter_list

        if data.get("peiyin_list"):
            peiyin_list = []
            for x in data.get("peiyin_list"):
                if x.get("sohu_url"):
                    s = self.crawl_star(url=x.get("sohu_url"))
                    if s:
                        peiyin_list.append(s)
                    else:
                        return False
                else:
                    peiyin_list.append(x)
            data['peiyin_list'] = peiyin_list

        if data.get("actors_list"):
            actors_list = []
            for x in data.get("actors_list"):
                if x.get("sohu_url"):
                    s = self.crawl_star(url=x.get("sohu_url"))
                    if s:
                        actors_list.append(s)
                    else:
                        return False
                else:
                    actors_list.append(x)
            data['actors_list'] = actors_list

        if data.get("publishers_list"):
            publishers_list = []
            for x in data.get("publishers_list"):
                if x.get("sohu_url"):
                    s = self.crawl_star(url=x.get("sohu_url"))
                    if s:
                        publishers_list.append(s)
                    else:
                        return False
                else:
                    publishers_list.append(x)
            data['publishers_list'] = publishers_list

        if data.get("singers_list"):
            singers_list = []
            for x in data.get("singers_list"):
                if x.get("sohu_url"):
                    s = self.crawl_star(url=x.get("sohu_url"))
                    if s:
                        singers_list.append(s)
                    else:
                        return False
                else:
                    singers_list.append(x)
            data['singers_list'] = singers_list

        if data.get("guests_list"):
            guests_list = []
            for x in data.get("guests_list"):
                if x.get("sohu_url"):
                    s = self.crawl_star(url=x.get("sohu_url"))
                    if s:
                        guests_list.append(s)
                    else:
                        return False
                else:
                    guests_list.append(x)
            data['guests_list'] = guests_list
        return data

    def save(self, data):
        data['source'] = 'sohu'
        if data.get("starring_list"):
            for x in data.get("starring_list"):
                _id = self.save_sohu_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']
        if data.get("screenwriter_list"):
            for x in data.get("screenwriter_list"):
                _id = self.save_sohu_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("publishers_list"):
            for x in data.get("publishers_list"):
                _id = self.save_sohu_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("singers_list"):
            for x in data.get("singers_list"):
                _id = self.save_sohu_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("directors_list"):
            for x in data.get("directors_list"):
                _id = self.save_sohu_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("speakers_list"):
            for x in data.get("speakers_list"):
                _id = self.save_sohu_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("peiyin_list"):
            for x in data.get("peiyin_list"):
                _id = self.save_sohu_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("actors_list"):
            for x in data.get("actors_list"):
                _id = self.save_sohu_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("guests_list"):
            for x in data.get("guests_list"):
                _id = self.save_sohu_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        
        return self.save_content_and_poster(data)
        # content_id = mongo_conn.contents.insert(data, check_keys=False)
        # del data['_id']
        # _id = mongo_conn.sohu_videos.insert(data, check_keys=False)
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
        query['sohu_vid'] = data['sohu_vid']
        # query['title'] = data['title']
        exists = mongo_conn.contents.find(query)
        if exists.count() > 0:
            data['_id'] = str(exists[0]['_id'])
            return data
        else:
            content_id = mongo_conn.contents.insert(data, check_keys=False)
            del data['_id']
            _id = mongo_conn.sohu_videos.insert(data, check_keys=False)
            del data['_id']
            data['_id'] = str(content_id)
            return self.save_poster(data)

    def save_poster(self,data):
        if data.get("poster"):
            for x in data.get("poster"):
                x['content_id'] = data['_id']
                _tempid = mongo_conn.posters.insert(x,check_keys=False)
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

    def save_sohu_star(self, star):
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
                return str(mongo_conn.sohu_stars.insert(star,check_keys=False))
            r = mongo_conn.stars.find(query)
            if r.count() > 0:
                return str(r[0]["_id"])
            else:
                return str(mongo_conn.sohu_stars.insert(star, check_keys=False))
        except Exception as e:
            return str(mongo_conn.sohu_stars.insert(star, check_keys=False))

    def after_save(self,data):
        p = sim_content(data)
        if p:
            for x in p:
                mongo_conn.posters.insert(x,check_keys=False)
