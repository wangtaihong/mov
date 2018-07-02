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
from Spiders.douban.parsers.DoubanParser import DoubanParser
from DB.MongodbClient import mongo_conn
sys.path.append('./')

# 
class Douban(object):
    """docstring for ClassName"""
    def __init__(self, **args):
        # super(ClassName, self).__init__()
        # self.session = requests.Session()
        self.parsers = DoubanParser()
        self.poster_url = u'https://movie.douban.com/subject/{id}/photos?type=R'
        self.detail_url = u'https://movie.douban.com/subject/{id}/'
        self.star_url = u'https://movie.douban.com/celebrity/{id}/'

    def crawl(self,urls):
        # m = re.search(u'movie\.douban\.com/subje',urls['r_url'])
        m = re.search(u'douban\.com/subje',urls['url'])
        url = urls["url"]
        if not m:
            iid = re.search(u'(\d{5,})',urls['url'])
            if iid:
                url = u'https://movie.douban.com/subject/{}/'.format(iid.group(1))
        m = re.search(u'(\d*)',url)
        if m:
            exists = self.crawl_before(doubanid=m.group(1))
            if exists:
                return exists
        r = requests_get(url=url,headers=headers)
        data = self.parsers.vdetail_parser(r)
        if not data or not data.get("doubanid"):
            return False
        poster = self.crawl_poster(data.get("doubanid"))
        if poster==None or poster==False:
            return False
        data['poster'] = poster
        data = self.check_crawl_star(data)
        if not data or not data.get("title"):
            return False
        return self.save(data)

    def crawl_before(self,doubanid):
        c = mongo_conn.contents.find({"doubanid":doubanid})
        if c.count() > 0:
            c['_id'] = str(c['_id'])
            return c
        return None

    def crawl_star(self,url):
        print(url)
        r = requests_get(url=url)
        return self.parsers.parse_star(r,url)

    def check_crawl_star(self,data):
        if data==None:
            return False
        if data.get("directors_list"):
            directors_list = []
            for x in data.get("directors_list"):
                if x.get("douban_url"):
                    s = self.crawl_star(url=x.get("douban_url"))
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
                if x.get("douban_url"):
                    s = self.crawl_star(url=x.get("douban_url"))
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
                if x.get("douban_url"):
                    s = self.crawl_star(url=x.get("douban_url"))
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
                if x.get("douban_url"):
                    s = self.crawl_star(url=x.get("douban_url"))
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
                if x.get("douban_url"):
                    s = self.crawl_star(url=x.get("douban_url"))
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
                if x.get("douban_url"):
                    s = self.crawl_star(url=x.get("douban_url"))
                    if s:
                        guests_list.append(s)
                    else:
                        guests_list.append(x)
                else:
                    guests_list.append(x)
            data['guests_list'] = guests_list
        return data


    def crawl_poster(self, id, data=[], result={}):
        url = self.poster_url.format(id=id)
        h = headers
        h["Referer"] = self.detail_url.format(id=id)
        data = []
        if len(result) == 0:
            result = {"next": url}
        url = url
        while url:
            print(url)
            r = requests_get(url=url, headers=h)
            if r == False or r == None:
                # yield False
                data = False
                url = False
                break
            if u'检测到有异常请求从你的 IP 发出' in r:
                print("------spider ben block... break......")
                url = False
                data = False
                break
            result = self.parsers.parse_photos(r,id)
            data += result.get('data')
            if result.get("next"):
                url = result.get("next")
            else:
                url = False
        return data

    def save(self,data):
        if data.get("starring_list"):
            for x in data.get("starring_list"):
                _id = self.save_douban_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']
        if data.get("screenwriter_list"):
            for x in data.get("screenwriter_list"):
                _id = self.save_douban_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("directors_list"):
            for x in data.get("directors_list"):
                _id = self.save_douban_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("peiyin_list"):
            for x in data.get("peiyin_list"):
                _id = self.save_douban_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("actors_list"):
            for x in data.get("actors_list"):
                _id = self.save_douban_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        if data.get("guests_list"):
            for x in data.get("guests_list"):
                _id = self.save_douban_star(x)
                if x.get("_id"):
                    del x['_id']
                x['star_id'] = self.save_star(x)
                if x.get("_id"):
                    del x['_id']

        return self.save_content_and_poster(data)
        # data['source'] = 'douban'
        # content_id = mongo_conn.contents.insert(data,check_keys=False)
        # if data.get("_id"):
        #     del data['_id']
        # _id = mongo_conn.douban_tvs.insert(data,check_keys=False)
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
        query["doubanid"] = data['doubanid']
        query['title'] = data['title']
        exists = mongo_conn.contents.find(query)
        if exists.count()>0:
            data['_id'] = str(exists[0]['_id'])
            return data
        else:
            data['source'] = 'douban'
            content_id = mongo_conn.contents.insert(data,check_keys=False)
            if data.get("_id"):
                del data['_id']
            _id = mongo_conn.douban_tvs.insert(data,check_keys=False)
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
            if len(query)<3:
                return str(mongo_conn.stars.insert(star,check_keys=False))
            r = mongo_conn.stars.find(query)
            if r.count()>0:
                return str(r[0]["_id"])
            else:
                return str(mongo_conn.stars.insert(star,check_keys=False))
        except Exception as e:
            return str(mongo_conn.stars.insert(star,check_keys=False))

    def save_douban_star(self,star):
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
                return str(mongo_conn.douban_stars.insert(star,check_keys=False))
            r = mongo_conn.stars.find(query)
            if r.count()>0:
                return str(r[0]["_id"])
            else:
                return str(mongo_conn.douban_stars.insert(star,check_keys=False))
        except Exception as e:
            return str(mongo_conn.douban_stars.insert(star,check_keys=False))
