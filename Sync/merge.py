#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-04 14:51:17
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    :
# @Version : $Id$

import os
import time
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
sys.path.append('../')
import config
sys.path.append('./')
from pymongo import MongoClient
from bson.objectid import ObjectId
from DB.NewVodData import NewVodData
from DB.TestCmscontent import TestCmscontent
from DB.mysql_session import DBSession
import Levenshtein as lst
from sqlalchemy.orm import scoped_session
import hashlib
import jieba
from DB.RedisClient import rd, rpop
from Utils.download_file import DownloadFile
from Utils.utils import parse_regx_char, area_process

# md5 = hashlib.md5()
# md5.update('how to use md5 in python hashlib?')
# md5.hexdigest()

class Merge(object):
    """数据汇总"""

    def __init__(self, **arg):
        # super(Merge, self).__init__()
        # self.arg = arg
        self.mongo_conn = MongoClient(config.MONGO_HOST, config.MONGO_PORT).zydata
        self.mongo_youku_videos = self.mongo_conn.youku_videos
        self.mongo_youku_star = self.mongo_conn.youku_star
        self.mongo_letv_tvs = self.mongo_conn.letv_tvs
        self.mongo_letv_stars = self.mongo_conn.letv_stars
        self.mongo_douban_tvs = self.mongo_conn.douban_tvs
        self.mongo_douban_stars = self.mongo_conn.douban_stars
        self.mongo_stars = self.mongo_conn.stars
        self.mongo_contents = self.mongo_conn.contents
        self.mongo_posters = self.mongo_conn.posters
        self.mongo_categories = self.mongo_conn.categories
        self.able_rating = 0.9
        self.letv_language = {"70001":"国语","70002":"粤语","70003":"英语","70006":"法语","70010":"泰语","70009":"德语","70007":"意大利语","70008":"西班牙语","70004":"日语","70008":"韩语","70000":"其他","70005":"韩语"}
        self.categories = set(["剧集","电影","综艺","动漫","少儿","音乐","教育","纪实","体育","文化","娱乐","游戏","资讯","搞笑","生活","汽车","科技","时尚","亲子","旅游","微电影","网剧","拍客","创意视频","自拍","广告","VR","纪录片","短片","电影","动漫","综艺","纪录片","娱乐","亲子","体育","音乐","风尚","财经","汽车","旅游","热点","教育",'资讯',"全景"])

    # def merge_video(self):
    #     t1 = time.time()
    #     contens = self.mongo_douban_tvs.find().limit(10).skip(10)
    #     self.mongo_posters.create_index("content_id")
    #     for item in contens:
    #         doc1 = ",".join([item.get("title").strip(" "),item.get("starring") if item.get("starring") else "",item.get("year").strip(" ") if item.get("year")else"",item.get("directors")if item.get("directors")else""])
    #         print(doc1)
    #         print(item.get("title"))
    #         regx = re.compile(".*"+parse_regx_char(item.get("title"))+".*", re.IGNORECASE)
    #         youku_data = self.mongo_youku_videos.find({"title": regx})
    #         ls = []
    #         for youku in youku_data:
    #             youku_doc = ",".join([youku.get("title").strip(" "),youku.get("actors") if youku.get("actors") else "",youku.get("year").strip(" ") if youku.get("year")else"",youku.get("directors")if youku.get("directors")else""])
    #             print(youku_doc)
    #             if lst.ratio(doc1, youku_doc) >= self.able_rating:
    #                 ls.append({"lst":lst.ratio(doc1, youku_doc),"doc1":str(item.get("_id")),"to":"youku","toid":str(youku.get("_id"))})

    #         letv_data = self.mongo_letv_tvs.find({"name": regx})
    #         for letv in letv_data:
    #             letv_doc = ",".join([letv.get("name").strip(" "),letv.get("starring").strip(',') if letv.get("starring") else "",letv.get("year").strip(" ") if letv.get("year")else"",youku.get("directors").strip(',') if youku.get("directors")else""])
    #             print(letv_doc)
    #             if lst.ratio(doc1, letv_doc) >= self.able_rating:
    #                 ls.append({"lst":lst.ratio(doc1, letv_doc),"doc1":str(item.get("_id")),"to":"letv","toid":str(letv.get("_id"))})
    #         if len(ls)==1:
    #             if ls[0]['to']=="letv":
    #                 pass
    #         if len(ls)==0:
    #             pass
    #         if len(ls)>1:
    #             pass
    #         print(youku_data.count())
    #         print(letv_data.count())
    #         print(json.dumps(ls))
    #         return True
    #         # nlt = lst.ratio(doc1, doc2)
    #         # result = mongo_douban_tvs.update_one({'_id': ObjectId()}, {'$set': {'merged': '1'}})
    
    def photos_task(self):
        data = self.mongo_douban_tvs.find(no_cursor_timeout=True)
        for item in data:
            rd.sadd(config.douban_photos_task,json.dumps({"mongoTVID": str(item["_id"]), "id": item['doubanid']}))
            print(item["doubanid"])
        print("done")

    def merge_doubanvideo(self,query={}):
        t1 = time.time()
        #contens = self.mongo_douban_tvs.find().limit(10).skip(10)
        contents = self.mongo_douban_tvs.find(query,no_cursor_timeout=True)
        print(contents.count())
        self.mongo_posters.create_index("doubanid")
        self.mongo_posters.create_index("title")
        for item in contents:
            exists = self.mongo_contents.find({"doubanid":item.get("doubanid")},no_cursor_timeout=True)
            if exists.count()!=0:
                print("exists----%s"%item.get("title"))
                continue
            data = self.parse_doubanfield(item)
            _id = self.mongo_contents.insert(data,check_keys=False)
            print("add done %s------%s"%(_id,item.get("title")))
            #豆瓣的category和type不易匹配，豆瓣标签化管理
            # self.update_category(category=data.get("category"),types=item.get("type"))
            # 豆瓣海报数据有问题，先暂时注释
            if item.get("poster") and item.get("poster")!="":
                for x in item.get("poster"):
                    size = x['prop'].split('x')
                    x['width'] = size[0]
                    x['height'] = size[1]
                    x['content_id'] = str(_id)
                    r = self.mongo_posters.insert(x,check_keys=False)
                    print("poster saved! %s----%s"%(r,item.get("title")))

    def update_category(self,category,types=None):
        categories = self.mongo_categories.find({"name":category})
        if categories.count()!=0:
            types = categories[0].get("types")
        else:
            pass
    # def parse_regx_char(self,doc):
    #     return doc.replace(".",'\.').replace("+","\+").replace("(","\(").replace(")","\)").replace("[","\[").replace("]",'\]').replace('|','\|').replace("?","\?").replace("*","\*")
    
    def merge_letvvideo(self,query={}):
        t1 = time.time()
        #contens = self.mongo_douban_tvs.find().limit(10).skip(10)
        contents = self.mongo_letv_tvs.find(query,no_cursor_timeout=True)
        print(contents.count())
        self.mongo_posters.create_index("doubanid")
        self.mongo_posters.create_index("levid")
        self.mongo_posters.create_index("content_id")
        # letv_tvs的名称是name不是title..f..k
        for item in contents:
            if item.get("name")==None or item.get("name") == "":
                print("error:None name:%s"%item['_id'])
                continue
            if self.mongo_contents.find({"letv_vid":item.get("vid")}).count()!=0:
                print("--exists---%s-"%item.get("name"))
                continue
            regx = {}
            #一部视频，片名，主演，导演，年份，可以确定
            if item.get("directors") and item.get("directors")!="":
                regx["directors"] = re.compile(u"("+ "|".join(item.get("directors").strip(",").split(','))+")",re.IGNORECASE)  #匹配至少有一个directors相交的
            if item.get("starring") and item.get("starring")!="":
                regx['starring'] = re.compile(u"("+ "|".join(item.get("starring").strip(",").split(','))+")",re.IGNORECASE)    #匹配至少有一个starring相交的
            # _name = item.get("name").replace(".",'\.').replace("+","\+").replace("(","\(").replace(")","\)").replace("[","\[").replace("]",'\]').replace('|','\|').replace("?","\?").replace("*","\*")
            _name = u"^"+parse_regx_char(item.get("name"))
            regx['title'] = re.compile(_name,re.IGNORECASE)  #匹配标题以之开头的
            exists = self.mongo_contents.find(regx)
            print("%s---%s-"%(item.get("name"),exists.count()))
            if exists.count() == 0:
                data = self.parse_letvfield(item)
                _id = self.mongo_contents.insert(data,check_keys=False)
                print("add done-%s--%s--"%(item.get("name"),_id))
                if item.get("images") and item.get("images")!="":
                    for im in item.get("images"):
                        im['content_id'] = str(_id)
                        _po_id = self.mongo_posters.insert(im,check_keys=False)
                        print("posters saved%s"%_po_id)
            elif exists.count() == 1:
                setdata = {}
                setdata = self.parse_letv_join(item,exists[0])
                result = self.mongo_contents.update_one({"_id":exists[0]['_id']},{"$set":setdata})
                print("--%s--%s---%s"%(result.modified_count,item.get("name"),exists[0]['title']))
            else:
                #相似度判断
                # doc1 = "|".join([item.get("name"),str(item.get("starring")),str(item.get("directors")),str(item.get("intro"))])
                doc1 = "|".join([item.get("name"),str(item.get("starring")),str(item.get("directors"))])
                ls = []
                lss = {}
                exists_one = exists[0]
                for x in exists:
                    # doc2 = "|".join([x['title'],str(x.get("starring")),str(x.get("directors")),str(x.get("intro"))])
                    doc2 = "|".join([x['title'],str(x.get("starring")),str(x.get("directors"))])
                    sim = lst.ratio(doc1,doc2)
                    if sim > 0.8:
                        lss[sim] = x['_id']
                        ls.append(sim)
                if len(ls)>=1:
                    ls.sort()
                    setdata = {}
                    setdata = self.parse_letv_join(item,exists_one)
                    result = self.mongo_contents.update_one({"_id":lss[ls[-1]]},{"$set":setdata})
                    print("--%s--%s---%s----%s"%(result.modified_count,item.get("name"),exists_one['title'],lss[ls[-1]]))
                else:
                    # 相似度达不到的视为不同的数据
                    data = self.parse_letvfield(item)
                    _id = self.mongo_contents.insert(data,check_keys=False)
                    print("add done-%s--%s--"%(item.get("name"),_id))
                    if item.get("images") and item.get("images")!="":
                        for im in item.get("images"):
                            im['content_id'] = str(_id)
                            im['levid'] = item.get("vid")
                            _po_id = self.mongo_posters.insert(im,check_keys=False)
                            #_po_id = self.mongo_posters.insert(im,check_keys=False)
                            print("posters saved%s"%_po_id)
        return True

    def merge_youku_videos(self,query={}):
        t1 = time.time()
        contents = self.mongo_youku_videos.find(query,no_cursor_timeout=True)
        print(contents.count())
        self.mongo_posters.create_index("doubanid")
        self.mongo_posters.create_index("levid")
        self.mongo_posters.create_index("content_id")
        for item in contents:
            if item.get("title")==None or item.get("title") == "":
                print("error:None title:%s"%item['_id'])
                continue
            regx = {}
            #一部视频，片名，主演，导演，年份，可以确    name
            if item.get("directors") and item.get("directors")!="":
                regx["directors"] = re.compile(u"("+ "|".join(item.get("directors").strip(",").split(','))+")",re.IGNORECASE)  #匹配至少有一个directors相交的
            if item.get("actors") and item.get("actors")!="":   #主演：优酷的主演字段actors
                regx['actors'] = re.compile(u"("+ "|".join(item.get("actors").strip(",").split(','))+")",re.IGNORECASE)    #匹配至少有一个starring相交的
            # if item.get("year"):
                # regx['year'] = re.compile(u"("+ "|".join(item.get("year").strip(",").split(','))+")",re.IGNORECASE)    #匹配至少有一个year
            _title = parse_regx_char(item.get("title"))
            regx['title'] = re.compile(_title,re.IGNORECASE)  #匹配标题以之开头的
            exists = self.mongo_contents.find(regx)
            print("%s---%s-"%(item.get("title"),exists.count()))
            if exists.count() == 0:
                data = self.parse_youkufield(item)
                _id = self.mongo_contents.insert(data,check_keys=False)
                print("add done-%s--%s--"%(item.get("title"),_id))
                if item.get("thumb") and item.get("thumb")!="":
                    for im in item.get("thumb"):
                        im['content_id'] = str(_id)
                        _po_id = self.mongo_posters.insert(im,check_keys=False)
                        print("posters saved%s"%_po_id)
            elif exists.count() == 1:
                setdata = {}
                setdata = self.parse_youku_join(youku_item=item, contents_item=exists[0])
                result = self.mongo_contents.update_one({"_id":exists[0]['_id']},{"$set":setdata})
                print("-update_one ----%s--%s---%s"%(result.modified_count,item.get("title"),exists[0]['title']))
            else:
                #相似度判断title + starring + directors + summery
                # doc1 = "|".join([item.get("title"),str(item.get("starring")),str(item.get("directors")),str(item.get("summary"))])
                doc1 = "|".join([item.get("title"),str(item.get("starring")),str(item.get("directors"))])
                ls = []
                lss = {}
                exists_one = exists[0]
                for x in exists:
                    # title + starring + directors + summery
                    # doc2 = "|".join([x['title'],str(x.get("starring")),str(x.get("directors")),str(x.get("summary"))])
                    doc2 = "|".join([x['title'],str(x.get("starring")),str(x.get("directors"))])
                    sim = lst.ratio(doc1,doc2)
                    if sim > 0.8:
                        lss[sim] = x['_id']
                        ls.append(sim)
                if len(ls)>=1:
                    ls.sort()
                    setdata = {}
                    setdata = self.parse_youku_join(item,x)
                    result = self.mongo_contents.update_one({"_id":lss[ls[-1]]},{"$set":setdata})
                    print("-update_one -----%s--%s---%s"%(result.modified_count,item.get("title"),exists_one['title']))
                else:
                    # 相似度达不到的视为不同的数据
                    data = self.parse_youkufield(item)
                    _id = self.mongo_contents.insert(data,check_keys=False)
                    print("add done-%s--%s--"%(item.get("title"),_id))
                    if item.get("thumb") and item.get("thumb")!="":
                        for im in item.get("thumb"):
                            im['content_id'] = str(_id)
                            # self.mongo_posters.insert(im,check_keys=False)
                            _po_id = self.mongo_posters.insert(im,check_keys=False)
                            print("posters saved%s"%_po_id)
        return True

    def parse_youku_join(self,youku_item,contents_item):
        setdata = {}
        if youku_item.get("tag") and contents_item.get("tags"):
            setdata['tags'] = ",".join(set(contents_item.get("tags").split(',')+youku_item.get("tag").split(',')))
        elif youku_item.get("tag") and contents_item.get("tags")==None:
            setdata['tags'] = youku_item.get("tag")
        if youku_item.get("year") and contents_item.get("year")==None:
            setdata['year'] = youku_item.get("year")
        if youku_item.get("category") and youku_item.get("category")!="":
            setdata['category'] = youku_item.get("category")  #youku 的category比较精准
        if youku_item.get("types") and youku_item.get("types")!="":
            setdata['type'] = ",".join(set(contents_item.get("type").split(',')+youku_item.get("types").split(','))) if contents_item.get("type") else ",".join(set(youku_item.get("types").split(',')))
        if youku_item.get("presenters") and youku_item.get("presenters")!="":
            setdata['presenters'] = youku_item.get("presenters").replace("|",",").strip(',')
        if youku_item.get("alias") and contents_item.get("alias")==None:
            setdata['alias'] = youku_item.get("alias")
        if youku_item.get("youku_score") and youku_item.get("youku_score")!="":
            setdata["youku_rating"] = youku_item.get("youku_score") if youku_item.get("youku_score")else None #优酷评分  可能没有
        summary = self.clean_summary(youku_item.get("summary"))
        if contents_item.get("summary"):
            if len(summary)-len(contents_item.get("summary")) > 10:
                setdata['summary'] = summary
        if youku_item.get("ding"):
            setdata['youku_ding'] = youku_item.get("ding")
        if youku_item.get("plays_num"):
            setdata["youku_plays_num"] = youku_item["plays_num"]
        if youku_item.get("youku_comments_num"):
            setdata['youku_comments_num'] = youku_item.get("youku_comments_num")
        return setdata

    def parse_letv_join(self,letv_item,contents_item):
        setdata = {}
        setdata['letv_vid'] = letv_item.get("vid")
        if letv_item.get("tag") and contents_item.get("tags"):
            setdata['tags'] = ",".join(set(contents_item.get("tags").split(',')+letv_item.get("tag").split(',')))
        elif letv_item.get("tag") and contents_item.get("tags")==None:
            setdata['tags'] = letv_item.get("tag")
        if letv_item.get("categoryName") and contents_item.get("category")!="":
            setdata['category'] = letv_item.get("categoryName")
        if letv_item.get("playCount"):
            setdata['letv_playCount'] = letv_item.get("playCount")
        if letv_item.get("subname"):
            setdata['subname'] = letv_item.get("subname")
        if letv_item.get("rating"):
            setdata['letv_rating'] = letv_item.get("rating")
        return setdata

    def clean_summary(self,summary):
        return summary.strip('\n').strip(" ").strip('\t').strip('\r').strip(" ")


    def parse_douban_star_list(self,star_list):
        for item in star_list:
            star = self.mongo_stars.find({"doubanid":item.get("doubanid")})
            if star.count()!=0:
                item["star_id"] = str(star[0].get("_id"))
            else:
                _name = u"^"+parse_regx_char(item.get("name"))+u" *"
                regx = re.compile(_name, re.IGNORECASE)
                _star = self.mongo_stars.find({"name":regx})
                if _star.count()>0:
                    item["star_id"] = str(_star[0].get("_id"))
                else:
                    pass
        return star_list

    def parse_doubanfield(self,item):
        data = {}
        # "_id" : ObjectId("5ae8943a48bc891827764577"),
        # data["starring_list"] = item.get("starring_list") if item.get("starring_list")else None
        data["starring_list"] = self.parse_douban_star_list(item.get("starring_list")) if item.get("starring_list")else None
        data["douban_rating"] = item["rating"] if item.get("rating") else None #豆瓣评分  可能没有
        # "youku_rating" : "6.2",#优酷评分  可能没有
        # "letv_rating" : "6.2",#乐视评分   可能没有
        data["age"] = item.get("age") if item.get("age")else None
        # "youku_plays_num" : "7,713,334",#优酷播放量 可能没有
        # data["screenwriter_list"] = item.get("screenwriter_list")if item.get("screenwriter_list")else None
        data["screenwriter_list"] = self.parse_douban_star_list(item.get("screenwriter_list"))if item.get("screenwriter_list")else None
        data["language"] = item.get('language').replace("/",',').strip(" ") if item.get('language') else None
        data["title"] = item.get("title")
        data["tags"] = item.get("tags")if item.get("tags")else None
        data["type"] = item.get("type") if item.get("type") else None
        data["all_episode"] = item.get("all_episode") if item.get("all_episode") else None
        if data["all_episode"]!= None:
            data["category"] = "电视剧"
        # else:
        # 	for x in self.categories:
        # 		if x in data['type']:
        # 			pass
        # "category_id" : "a48bc891827764577", #关联到category表
        data["release_date"] = item.get("release_date")if item.get("release_date") else None
        data["img_url"] = item.get("img_url")if item.get("img_url") else None
        data["screenwriters"] = item.get("screenwriters") if item.get("screenwriters") else None  #编剧,逗号分隔
        data["summary"] = self.clean_summary(item.get("summary"))if item.get("summary") else None
        data["alias"] = item.get("alias").replace("/",',').strip(" ") if item.get("alias")else None
        data["directors"] = item.get("directors")if item.get("directors") else None #导演逗号分隔
        data["douban_rating_sum"] = item.get("rating_sum") if item.get("rating_sum")else None #豆瓣评论数
        data["starring"] = item.get("starring")if item.get("starring") else None #主演逗号分隔
        data["year"] = item.get("year") if item.get("year")else None
        data["duration"] = re.search(u"(\d*)",item.get("duration")).group(1) if item.get("duration") and re.search(u"(\d*)",item.get("duration")) else None #时长
        # data["directors_list"] = item.get("directors_list") if item.get("directors_list") else None
        data["directors_list"] = self.parse_douban_star_list(item.get("directors_list")) if item.get("directors_list") else None
        data["producer_country"] = item.get("producer_country").replace("/",",").strip(' ') if item.get("producer_country") else None #制片国家/地区
        data['doubanid'] = item.get("doubanid") if item.get("doubanid")else None
        data['season'] = item.get("season") if item.get("season")else None   #季
        data['created_at'] = int(time.time())
        for key, v in data.copy().items():
            if v==None:
                del data[key]
        # md5 = hashlib.md5()
        # md5.update(data['title'])
        # data['id'] = md5.hexdigest()
        return data

    def parse_youkufield(self,item):
        data = {}
        # "_id" : ObjectId("5ae8943a48bc891827764577"),
        # data["starring_list"] = [{"youkuid":x["youkuid"],"name":x['name']}for x in item['actor_list']]if item.get("actor_list")else None
        data["starring_list"] = self.parse_youku_starring_list(item['actor_list']) if item.get("actor_list") else None
        data["douban_rating"] = item.get("douban_score") if item.get("douban_score") else None #豆瓣评分  可能没有
        data["youku_rating"] = item.get("youku_score") if item.get("youku_score")else None #优酷评分  可能没有
        # "letv_rating" : "6.2",#乐视评分   可能没有
        data["age"] = item.get("age") if item.get("age")else None
        data["youku_plays_num"] = item.get("plays_num").replace(',',"") if item.get("plays_num") else None #优酷播放量 可能没有
        data["youku_comments_num"] = item.get("youku_comments_num") if item.get("youku_comments_num") else None #优酷播放量 可能没有
        data["screenwriter_list"] = self.parse_youku_starring_list(item['screenwriter_list']) if item.get('screenwriter_list') else None
        data["producer_country"] = item.get("area").replace("/",",").strip(' ') if item.get("area") else None #制片国家/地区
        data["language"] = item.get('language').replace("/",',').strip(" ") if item.get('language') else None
        if data['language']==None and data['producer_country']:
            if u"中国" in data['producer_country'] or u'大陆' in data['producer_country']:
                data["language"] = "国语"
        data["title"] = item.get("title")
        data["tags"] = item.get("tags")if item.get("tags")else None
        data["type"] = item.get("types") if item.get("types") else None
        data["all_episode"] = item.get("all_episode") if item.get("all_episode") else None
        data['category'] = item.get("category")if item.get("category")else None
        # "category_id" : "a48bc891827764577", #关联到category表
        data["release_date"] = item.get("release_date")if item.get("release_date") else None
        data["screenwriters"] = item.get("screenwriters")if item.get("screenwriters") else None  #编剧,逗号分隔
        data["summary"] = self.clean_summary(item.get("summary"))if item.get("summary") else None
        data["alias"] = item.get("alias").replace("/",',').strip(" ") if item.get("alias")else None
        data["directors"] = item.get("directors") if item.get("directors") else None #导演逗号分隔
        # data["douban_rating_sum"] = item.get("rating_sum") if item.get("rating_sum")else None #豆瓣评论数
        data["starring"] = item.get("actors") if item.get("actors") else None #主演逗号分隔
        data["year"] = item.get("year") if item.get("year")else None
        data["duration"] = item.get("duration") if item.get("duration") else None #时长
        # data["directors_list"] = [{"youkuid":x["youkuid"],"name":x['name']}for x in item['director_list']]if item.get("director_list")else None
        data["directors_list"] = self.parse_youku_starring_list(item['director_list']) if item.get("director_list")else None
        data['doubanid'] = item.get("doubanid") if item.get("doubanid")else None
        data['season'] = item.get("season") if item.get("season")else None   #季
        data['img_url'] = item.get("thumb")[0]['url'] if item.get("thumb")else None   #季
        data['presenters'] = item.get("presenters").replace('|',",").strip(',') if item.get("presenters")else None   #季
        data['created_at'] = int(time.time())
        for key, v in data.copy().items():
                if v==None:
                    del data[key]
                if key==u"star_id":
                    del data[key]
        # md5 = hashlib.md5()
        # md5.update(data['title'])
        # data['id'] = md5.hexdigest()
        return data

    def parse_letv_starring_list(self,starring_list):
        # keng:letv的star_list
        data = []
        for item in starring_list[0]:
            star = self.mongo_stars.find({"leId":item.get("leId")})
            if star.count()!=0:
                item["star_id"] = str(star[0].get("_id"))
                data.append(item)
            else:
                regx = re.compile(u"^"+parse_regx_char(item.get("name"))+u" *", re.IGNORECASE)
                _star = self.mongo_stars.find({"name":regx})
                if _star.count()>0:
                    item["star_id"] = str(_star[0].get("_id"))
                    data.append(item)
                else:
                    data.append(item)
        return data

    def parse_youku_starring_list(self,star_list):
        # keng:letv的star_list
        data = []
        for item in star_list:
            if item.get("youkuid_bac"):
            	del item['youkuid_bac']
            star = self.mongo_stars.find({"youkuid":item.get("youkuid")})
            if star.count()!=0:
                item["star_id"] = str(star[0].get("_id"))
                data.append(item)
            else:
                regx = re.compile(u"^"+parse_regx_char(item.get("name"))+u" *", re.IGNORECASE)
                _star = self.mongo_stars.find({"name":regx})
                if _star.count()>0:
                    item["star_id"] = str(_star[0].get("_id"))
                    data.append(item)
                else:
                    data.append(item)
        return data

    def parse_letv_directors_list(self,directors_list):
        # keng:letv的star_list
        data = []
        for key in directors_list.keys():
            star = self.mongo_stars.find({"leId":key})
            if star.count()!=0:
                temp = {}
                temp["star_id"] = str(star[0].get("_id"))
                temp['leId'] = key
                temp['name'] = directors_list[key]
                data.append(temp)
            else:
                regx = re.compile(u"^"+parse_regx_char(directors_list[key])+u" *", re.IGNORECASE)
                _star = self.mongo_stars.find({"name":regx})
                if _star.count()>0:
                    temp = {}
                    temp["star_id"] = str(star[0].get("_id"))
                    temp['leId'] = key
                    temp['name'] = directors_list[key]
                    data.append(temp)
                else:
                    temp = {}
                    temp['leId'] = key
                    temp['name'] = directors_list[key]
                    data.append(temp)
        return data
 
    def parse_letvfield(self,item):
        data = {}
        # "_id" : ObjectId("5ae8943a48bc891827764577")
        data['letvtbID'] = str(item.get("_id"))
        # data["starring_list"] = item.get(starring_list)if item.get("starring_list") else None
        data["starring_list"] = self.parse_letv_starring_list(item.get("starring_list"))if item.get("starring_list") else None
        data["doubanid"] = item.get("doubanid") if item.get("doubanid") else None #豆瓣评分  可能没有
        data["letv_rating"] = item.get("rating") if item.get("rating")else None #优酷评分  可能没有
        data["age"] = item.get("age") if item.get("age")else None
        data["letv_vid"] = item.get("vid") if item.get("vid")else None
        # data["youku_plays_num"] = item.get("plays_num") if item.get("plays_num") else None #优酷播放量 可能没有
        # data["youku_comments_num"] = item.get("youku_comments_num") if item.get("youku_comments_num") else None #优酷播放量 可能没有
        # data["screenwriter_list"] = item['screenwriter_list'] if item.get('screenwriter_list') else None
        data["producer_country"] = item.get("areaName").replace("/",",").strip(' ').strip(',') if item.get("areaName") else None #制片国家/地区
        try:
            data["language"] = self.letv_language[item.get('language').split(',')[0]] if item.get('language') else None  #70004,70044
        except Exception as e:
            data["language"] = u"未知"
        data["title"] = item.get("title")
        data["tags"] = item.get("tag")if item.get("tag")else None
        data["type"] = item.get("subCategoryName") if item.get("subCategoryName") else None
        data["all_episode"] = item.get("episodes") if item.get("episodes") else None
        data['category'] = item.get("categoryName")if item.get("categoryName")else None
        # "category_id" : "a48bc891827764577", #关联到category表
        try:
            data["release_date"] = time.strftime('%Y-%m-%d', time.localtime(int(item['releaseDate'])/1000))if item.get("releaseDate") else None
        except Exception as e:
            pass
        data["screenwriters"] = item.get("screenwriter")if item.get("screenwriter") else None  #编剧,逗号分隔
        data["summary"] = self.clean_summary(item.get("description")) if item.get("description") else None
        data["alias"] = item.get("otherName").replace("/",',').strip(" ") if item.get("otherName")else None
        data["directors"] = item.get("directors").strip(',').strip(" ") if item.get("directors") else None #导演逗号分隔
        # data["douban_rating_sum"] = item.get("rating_sum") if item.get("rating_sum")else None #豆瓣评论数
        data["starring"] = item.get("actors").strip(',').strip(" ") if item.get("actors") else None #主演逗号分隔
        data["year"] = item.get("year") if item.get("year")else None
        data["duration"] = item.get("duration") if item.get("duration") else None #时长
        # data["directors_list"] = [{"youkuid":x["youkuid"],"name":x['name']}for x in item['director_list']]if item.get("director_list")else None
        data["directors_list"] = self.parse_letv_directors_list(item['director_list']) if item.get("director_list") and item.get("director_list")!="" else None
        data['doubanid'] = item.get("doubanid") if item.get("doubanid")else None
        data['season'] = item.get("season") if item.get("season")else None   #季
        data['subname'] = item.get("subname") if item.get("subname")else None   #
        data['letv_playCount'] = item.get("playCount") if item.get("playCount")else None   #
        data['img_url'] = item.get("imgUrl") if item.get("imgUrl")else None   #
        data['created_at'] = int(time.time())
        for key, v in data.copy().items():
            if v==None:
                del data[key]
            if key==u"star_id":
                del data[key]
        #md5 = hashlib.md5()
        #md5.update(data['title'])
        #data['id'] = md5.hexdigest()
        return data

    def merge_star(self):
        t1 = time.time()
        contens = self.mongo_douban_stars.find(no_cursor_timeout=True)
        self.mongo_stars.create_index("name")
        self.mongo_stars.create_index("doubanid")
        self.mongo_stars.create_index("leId")
        self.mongo_stars.create_index("youkuid")
        for item in contens:
            item_id = item.get("_id")
            data = {}
            data = item
            data['zh_names'] = data['zh_names'].strip(":").strip(" ") if data.get("zh_names") else None
            data['occupation'] = data['occupation'].replace(" / ",',').strip(" ") if data.get("occupation") else None
            data['avatar'] = data['imgUrl']
            del data['imgUrl']
            for key, v in data.copy().items():
                if v==None:
                    del data[key]
                if key==u"star_id":
                    del data[key]
            del(data['_id'])
            data['created_at'] = int(time.time())
            _id = self.mongo_stars.insert(data, check_keys=False)  #
            print("done stars,%s"%_id)
            print(data.get("name"))

    def merge_youkustar(self,query={}):
        t1 = time.time()
        contents = self.mongo_youku_star.find(query,no_cursor_timeout=True)
        print(contents.count())
        # self.mongo_stars.create_index("name")
        for item in contents:
            if item.get("name")==None or item.get("name")=="":
                continue
            item_id = item.get("_id")
            data = {}
            data = item
            doc1 = ",".join([item.get("name"),item.get("gender")if item.get("gender") else ""])
            regx = {}
            # name
            regx["name"] = re.compile(u'^'+parse_regx_char(item.get("name"))+u" *", re.IGNORECASE)
            # occupation
            if item.get(item.get("occupation")):
                regx['occupation'] = re.compile(u"("+ "|".join(item.get("occupation").replace(" / ",",").strip(" ").strip(",").split(','))+")",re.IGNORECASE)
            # birthplace
            if item.get(item.get("birthplace")):
                # regx['birthplace'] = re.compile(u"("+ "|".join(item.get("birthplace").replace(" / ",",").replace(" ","").strip(" ").strip(",").split(','))+")",re.IGNORECASE)
                #使用分词来
                # seglist = '|'.join(jieba.cut(item.get("birthplace"), cut_all=True))
                regx['birthplace'] = re.compile(u"("+ '|'.join(jieba.cut(item.get("birthplace"), cut_all=True)) +")",re.IGNORECASE)
            # gender
            if item.get("gender"):
                regx["gender"] = re.compile(parse_regx_char(item.get("gender")), re.IGNORECASE)
            stars = {}
            stars = self.mongo_stars.find(regx)
            if stars.count()==1:
                update_data = {}
                update_data = {"youku_starid":item.get("youku_starid"),
                                "youku_uid":item.get("youku_uid"),
                                "birthday":item.get("birthday"),
                                "blood":item.get("blood"),
                                "alias":item.get("alias"),
                                "avatar":item.get("avatar"),
                                "area":item.get("area")
                            }
                if stars[0].get("intro") and len(stars[0].get("intro").replace("\n","").strip(" "))<20:
                    update_data['intro'] = item.get("intro")
                result = self.mongo_stars.update_one({"_id":stars[0]["_id"]},{"$set":update_data})
                print("update done.%s---%s----%s-"%(result.modified_count,item['name'],stars[0]['name']))
                continue
            elif stars.count()>1:
                for x in stars:
                    if x.get("birthplace")!=None and item.get("birthplace")!=None:
                        if lst.ratio(x['birthplace'].replace(',',""),item.get("birthplace"))>=0.85:
                            update_data = {}
                            update_data = {"youku_starid":item.get("youku_starid"),
                                    "youku_uid":item.get("youku_uid"),
                                    "birthday":item.get("birthday"),
                                    "blood":item.get("blood"),
                                    "alias":item.get("alias"),
                                    "avatar":item.get("avatar"),
                                    "area":item.get("area")
                                }
                            if len(x.get("intro").replace("\n","").strip(" "))<20:
                                update_data['intro'] = item.get("intro")
                            result = self.mongo_stars.update_one({"_id":x['_id']},{"$set":update_data})
                            print("update done.%s---%s----%s-"%(result.modified_count,item['name'],x['name']))
                            continue
                    else:
                        if lst.ratio(x.get("intro").replace('\n',"").strip(" "),item.get("intro").replace("\n","").strip(" "))>=0.29:
                            update_data = {}
                            update_data = {"youku_starid":item.get("youku_starid"),
                                    "youku_uid":item.get("youku_uid"),
                                    "birthday":item.get("birthday"),
                                    "blood":item.get("blood"),
                                    "alias":item.get("alias"),
                                    "avatar":item.get("avatar"),
                                    "area":item.get("area")
                                }
                            if item.get("birthplace"):
                                update_data['birthplace'] = item.get("birthplace")
                            if len(x.get("intro").replace("\n","").strip(" "))<20:
                                update_data['intro'] = item.get("intro")
                            result = self.mongo_stars.update_one({"_id":x['_id']},{"$set":update_data})
                            print("update done.%s---%s----%s-"%(result.modified_count,item['name'],x['name']))
                            continue
            else:
                for key, v in data.copy().items():
                    if v==None:
                        del data[key]
                del(data['_id'])
                data['created_at'] = int(time.time())
                _id = self.mongo_stars.insert(data, check_keys=False)  #
                print("add done stars,%s----%s"%(_id,item['name']))
        # print("finished")

    def download_starts_avtar(self,query={}):
    	stars = self.mongo_stars.find(query, no_cursor_timeout=True)
    	size = 10000
    	i = 1
    	for item in stars:
    		path = "".join([u'E:/',u'stars_avatar/',str((i/size+1)*size),'/'])
    		filename = path+"".join([str(item.get("_id")),'.',item.get("avatar").split('.')[-1]])
    		if item.get("avatar") and item.get("avatar_url")==None:
    			avatar_url = DownloadFile(url=item.get("avatar"), path=path,filename=filename)
    			print(avatar_url)
    			break
    			# result = self.mongo_stars.update_one({"_id":item.get("_id")},{"$set":{"avatar_url":avatar_url}})
    			# print(result.modified_count)
    		i+=1

    def merge_letvstar(self,query={}):
        '''乐视明星数据汇总'''
        t1 = time.time()
        succ = 0
        contens = self.mongo_letv_stars.find(query,no_cursor_timeout=True)
        self.mongo_stars.create_index("name")
        for item in contens:
            item_id = item.get("_id")
            #date_birth     area
            #birth area
            # doc1 = ",".join([item.get("name"),item.get("gender")])
            regx = {}
            regx["name"] = re.compile(u"^"+parse_regx_char(item.get("name"))+u" *", re.IGNORECASE)    #按名字匹配
            if item.get("birth"):
                regx["date_birth"] = re.compile(item.get("birth"), re.IGNORECASE)    #出生年月
            stars = {}
            stars = self.mongo_stars.find(regx)
            print(stars.count())
            if stars.count()>0:
                for x in stars:
                    if x.get("leId") and item.get("leId")==x['leId']:   #乐视id 已存在的就跳过
                        continue
                    if item.get("birth") and x.get("date_birth") and item.get("birth") == x.get("date_birth"):   #按照名字+出生日期匹配
                        update_data = {}
                        update_data['leId'] = item.get("leId")
                        result = self.mongo_stars.update_one({"_id":x['_id']},{"$set":update_data})
                        print("update done--%s--%s----%s-----%s"%(result.modified_count,x['_id'],item.get("name"),x['name']))
                        continue
                    elif item.get("area") and x.get("area"):   #按照名字和地区相似度
                        if lst.ratio(item.get("name")+item.get("area"),x.get("name")+x.get("area"))>=0.75:
                            update_data = {}
                            update_data['leId'] = item.get("leId")
                            result = self.mongo_stars.update_one({"_id":x['_id']},{"$set":update_data})
                            print("update done--%s--%s----%s-----%s"%(result.modified_count,x['_id'],item.get("name"),x['name']))
                        continue
                    elif item.get("birth") and x.get("birthday"):    #生日和出生日期 + 名字
                        m = re.search(u'\d{4}-(\d{2})-(\d{2})',item.get("birth"))
                        m2 = re.search(u'(\d{2})月(\d{2})日',x.get("birthday"))
                        if m and m2 and "".join(m.groups())=="".join(m2.groups()):
                            update_data = {}
                            update_data['leId'] = item.get("leId")
                            result = self.mongo_stars.update_one({"_id":x['_id']},{"$set":update_data})
                            print("update done--%s--%s----%s-----%s"%(result.modified_count,x['_id'],item.get("name"),x['name']))
                        continue
                    elif item.get("intro") and x.get("intro"):    #名字+简介相似度
                        if lst.ratio(item.get("intro"),x.get("intro")) >=0.7:
                            update_data = {}
                            update_data['leId'] = item.get("leId")
                            result = self.mongo_stars.update_one({"_id":x['_id']},{"$set":update_data})
                            print("update done--%s--%s----%s-----%s"%(result.modified_count,x['_id'],item.get("name"),x['name']))
                        continue
                    else:
                        """以上维度达不到相似度的，就写入吧"""
                        data = {}
                        data = item
                        data['avatar'] = item['imgUrl'] if item.get("imgUrl") else None
                        for key, v in data.copy().items():
                            if v==None or key=="imgUrl":
                                del data[key]
                        del(data['_id'])
                        data['created_at'] = int(time.time())
                        _id = self.mongo_stars.insert(data, check_keys=False)  #
                        print("add done stars,%s----%s--"%(_id,item['name']))
            else:
                '''名字匹配无果'''
                data = {}
                data = item
                data['avatar'] = item['imgUrl'] if item.get("imgUrl") else None
                for key, v in data.copy().items():
                    if v==None or key=="imgUrl":
                        del data[key]
                del(data['_id'])
                data['created_at'] = int(time.time())
                _id = self.mongo_stars.insert(data, check_keys=False)  #
                print("add done stars,%s----%s--"%(_id,item['name']))
        print(succ)

    def groupCategories(self,query={}):
        """清洗categories和subcategory,在影视数据清洗完成后执行"""
        contents = self.mongo_contents.find(query,no_cursor_timeout=True)
        print("go")
        data = {}
        for item in contents:
            if item.get("category")==None or item.get("type")==None:
                continue
            if data.get(item["category"])==None:
                data[item["category"]] = set([])
            for x in item.get("type").strip(" ").strip(",").split(','):
                print("---%s-------%s-"%(item['category'],x))
                data[item.get("category")].add(x)
        for key in data:
            print(key)
            self.mongo_categories.insert({"category" : key,"subCategory" : ",".join(data[key])})
        print("categories done")

    def groupLanguageAndProducer_country(self,query={}):
        """"""
        contents = self.mongo_contents.find(query,no_cursor_timeout=True)
        print("go")
        language = set([])
        standar = ['汉语','中文','国语','普通话']
        producer_country = set([])
        for item in contents:
            # if item.get("language")!=None:    #已处理
                # language.add(item.get("language"))
                # _temp = item.get("language").split(',')
                # for st in standar:
                #     for x in xrange(0,len(_temp)):
                #         if st in _temp[x]:
                #             _temp[x] = u"汉语"
                # result = self.mongo_contents.update_one({'_id': item.get("_id")}, {'$set': {'language': ",".join(set(_temp))}})
                # print(",".join(set(_temp)))
            if item.get("producer_country")!=None:
                # _temp = item.get("producer_country").split(',')
                # print("be"+",".join(set(_temp)))
                # for x in xrange(0,len(_temp)):
                #     if u'大陆' in _temp[x] or _temp[x] == u"中国":
                #         _temp[x] = u"中国"
                # result = self.mongo_contents.update_one({'_id': item.get("_id")}, {'$set': {'producer_country': ",".join(set(_temp))}})
                producer_country = area_process(item.get("producer_country"))
                result = self.mongo_contents.update_one({'_id': item.get("_id")}, {'$set': {'producer_country': producer_country}})
                print("af"+producer_country)

            if item.get("area")!=None:
                area = area_process(item.get("area"))
                result = self.mongo_contents.update_one({'_id': item.get("_id")}, {'$set': {'producer_country': area}})
                print("af"+area)

    def rm_unknown(self,query={}):
        '''清除cointents中的四无数据 screenwriters  presenters  starring  directors'''
        contents = self.mongo_contents.find({
                'screenwriters': {'$exists': False},
                'presenters': {'$exists': False},
                'starring': {'$exists': False},
                'directors': {'$exists': False}
                })
        print(contents.count())
        for x in contents:
            print(x.get("_id"),x.get("screenwriters"),x.get("presenters"),x.get("starring"),x.get("directors"))
            r = self.mongo_posters.remove({"content_id":str(x.get("_id"))})
            r1 = self.mongo_contents.remove({"_id":x.get("_id")})
            print(r,r1)

    def clean_category(self,query={}):
        '''清洗内容中的category ‘剧集’改为"电视剧"'''
        contents = self.mongo_contents.find({"category":"剧集"})
        for item in contents:
            result = self.mongo_contents.update({'_id': item['_id']}, {'$set': {"category": "电视剧"}}, False, True)
            print(result,item.get("_id"))
            # return True

    def fix_youku_starId(self,query={}):
        contents = self.mongo_contents.find(query,no_cursor_timeout=True)
        for item in contents:
            if item.get("starring_list"):
                for x in item.get("starring_list"):
                    if x.get("youkuid"):
                        starring_list = self.parse_youku_starring_list(item.get("starring_list"))
                        result = self.mongo_contents.update({'_id': item['_id']}, {'$set': {"starring_list":starring_list}}, False, True)
                        print(result,item.get("_id"))
                        break
            if item.get("directors_list"):
                for x in item.get("directors_list"):
                    if x.get("youkuid"):
                        directors_list = self.parse_youku_starring_list(item.get("directors_list"))
                        result = self.mongo_contents.update({'_id': item['_id']}, {'$set': {"directors_list":directors_list}}, False, True)
                        print(result,item.get("_id"))
                        break
            if item.get("screenwriter_list"):
                for x in item.get("screenwriter_list"):
                    if x.get("youkuid"):
                        screenwriter_list = self.parse_youku_starring_list(item.get("screenwriter_list"))
                        result = self.mongo_contents.update({'_id': item['_id']}, {'$set': {"screenwriter_list":screenwriter_list}}, False, True)
                        print(result,item.get("_id"))
                        break
        print("done")

def fixyoukuid():
    mongo_youku_videos = MongoClient(
        config.MONGO_HOST, config.MONGO_PORT).zydata.youku_videos
    count = mongo_youku_videos.count()
    limit = 1000
    for step in xrange(0, count/limit):
        contens = mongo_youku_videos.find(no_cursor_timeout=True).skip(step*limit).limit(limit)
        for item in contens:
            print("id:", item['_id'])
            if item.get("types"):
                types = item.get("types").replace("|",",")
                types = types.strip(",")
                types = types.strip(" ")
                result = mongo_youku_videos.update({'_id': item['_id']}, {'$set': {"types": types}}, False, True)

            if item.get("actors"):
                actors = item.get("actors").replace("|",",")
                actors = item.get("actors").replace("/",",")
                actors = actors.strip(",")
                actors = actors.strip(" ")
                result = mongo_youku_videos.update({'_id': item['_id']}, {'$set': {"actors": actors}}, False, True)

            if item.get("directors"):
                directors = item.get("directors").replace("|",",")
                directors = directors.strip(",")
                directors = directors.strip(" ")
                result = mongo_youku_videos.update({'_id': item['_id']}, {'$set': {"directors": directors}}, False, True)
            if item.get("actor_list"):
                for x in item.get("actor_list"):
                    m = re.search(
                        u'<a href=\"//list\.youku\.com/star/show/(uid_*\w*\d*=*)\.html\"( *target=\"_blank\")*>' + x['name'] + '</a>', x['youkuid'])
                    if m:
                        youkuid = m.group(1)
                        print("actor_list:", youkuid)
                        result = mongo_youku_videos.update({'_id': item['_id'], "actor_list.name": x['name']}, {'$set': {"actor_list.$.youkuid": youkuid}}, False, True)
                        print(result)
                        print(dir(result))

            if item.get("director_list"):
                directors = ''
                for x in item.get("director_list"):
                    directors = directors + x['name'] + ","
                    M = re.search(u'<a href=\"//list\.youku\.com/star/show/(uid_*\w*\d*=*)\.html\"( *title=\"' +x['name'] + '\" *target=\"_blank\")?>' + x['name'] + '</a>', x['youkuid'])
                    M1 = re.search(u'<a href=\"//list\.youku\.com/star/show/(uid_*\w*\d*=*)\.html\" title=\"' +x['name'] + '\" target=\"_blank\">' +x['name'] + '</a>', x['youkuid'])
                    if M:
                        directorid = M.group(1)
                        print("director_list:", directorid)
                        # result = mongo_youku_videos.update({'_id': item['_id'], "director_list.name": x['name']}, {'$set': {"director_list.$.youkuid": directorid, "director_list.$.youkuid_bac": x['youkuid']}}, False, True)
                        result = mongo_youku_videos.update({'_id': item['_id'], "director_list.name": x['name']}, {'$set': {"director_list.$.youkuid": directorid}}, False, True)
                        print(result)
                        print(dir(result))
                    elif M1:
                        directorid = M1.group(1)
                        print("director_list:", directorid)
                        result = mongo_youku_videos.update({'_id': item['_id'], "director_list.name": x['name']}, {'$set': {"director_list.$.youkuid": directorid}}, False, True)
                        print(result)
                        print(dir(result))
                if item.get("directors")==None:
                    result = mongo_youku_videos.update({'_id': item['_id']}, {'$set': {"directors": directors.strip(',')}}, False, True)
def clean():
    mongo_contents = MongoClient(
        config.MONGO_HOST, config.MONGO_PORT).zydata.contents
    count = mongo_contents.count()
    contens = mongo_contents.find(no_cursor_timeout=True)
    for item in contens:
        print("id:", item['_id'])
        if item.get("type"):
            types = item.get("type").replace(u"|",",").replace(u'/',',').replace(u" ","")
            types = types.strip(",")
            types = types.strip(" ")
            result = mongo_contents.update({'_id': item['_id']}, {'$set': {"type": types}}, False, True)
        if item.get("tags"):
            tags = item.get("tags").replace(u"|",",").replace(u'/',',').replace(u" ","")
            tags = tags.strip(",")
            tags = tags.strip(" ")
            result = mongo_contents.update({'_id': item['_id']}, {'$set': {"tags": tags}}, False, True)
        if item.get("starring"):
            starring = item.get("starring").replace("|",",").replace("/",",")
            starring = starring.strip(",")
            starring = starring.strip(" ")
            result = mongo_contents.update({'_id': item['_id']}, {'$set': {"starring": starring}}, False, True)
        if item.get("directors"):
            directors = item.get("directors").replace("|",",").replace('/',',')
            directors = directors.strip(",")
            directors = directors.strip(" ")
            result = mongo_contents.update({'_id': item['_id']}, {'$set': {"directors": directors}}, False, True)
        if item.get("screenwriters"):
            screenwriters = item.get("screenwriters").replace("|",",").replace('/',',')
            screenwriters = screenwriters.strip(",")
            screenwriters = screenwriters.strip(" ")
            result = mongo_contents.update({'_id': item['_id']}, {'$set': {"screenwriters": screenwriters}}, False, True)
        # return True

def fixletv():
    mongo_letv_tvs = MongoClient(config.MONGO_HOST, config.MONGO_PORT).zydata.letv_tvs
    mongo_letv_stars = MongoClient(config.MONGO_HOST, config.MONGO_PORT).zydata.letv_stars
    contens = mongo_letv_tvs.find({'starring_list': {'$exists': False}})
    for item in contens:
        if item.get("starring")!="":
            starring_list = []
            for x in item.get("starring").strip(",").strip(" ").split(','):
                regx = re.compile(u"^"+parse_regx_char(x), re.IGNORECASE)
                stars = mongo_letv_stars.find({"name": regx})
                print(x)
                print(stars.count())
                if stars.count()>0:
                    starring_list.append({"name":stars[0]['name'],"leId":stars[0]['leId']})
            result = mongo_letv_tvs.update_one({'_id': item.get("_id")}, {'$push': {'starring_list': starring_list}})
            print("done ",result.modified_count,starring_list)
            print(item.get("name"))

if __name__ == '__main__':
    '''
    数据带上目标网站来源id.

    1,明星数据清洗:
    第一步，清洗豆瓣明星
    第二步，清洗优酷
    第三步，清洗乐视
    '''

    '''
    2,影视数据清洗:每一条数据清洗过程都把明星与明星库关联，海报单独抽出来存到海报库，形成关联关系
    第一步，清洗豆瓣
    第二部，清洗乐视
    第四部，清洗优酷
    '''

    '''
    3,category信息:
    从清洗好的内容库抽出来存到category库
    
    '''
    t = time.time()
    # merge()
    # fixyoukuid()
    # fixletv()
    clean()
    # m = Merge()
    # m.merge_star()
    # m.merge_youkustar()
    # m.merge_letvstar()

    # m.merge_doubanvideo()
    # m.merge_letvvideo()
    # m.merge_youku_videos()


    # m.categories()  #清洗categories
    print(time.time()-t)
