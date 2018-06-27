#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-26 09:52:46
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

import re
from lxml import etree
import json

import sys
sys.path.append('../')
from Spiders.Items import Contents, Star
from Utils.utils import language_process
from Utils.utils import mictime_to_ymd, area_process, parse_simple, language_process
sys.path.append('./')
import time

class QQParser(object):
    """docstring for ClassName"""
    def __init__(self, **arg):
        # super(ClassName, self).__init__()
        # self.arg = arg
        pass

    def vdetail_parser(self,r):
        try:
            page = etree.HTML(r)
        except Exception as e:
            return False
        L = Contents()
        title = page.xpath(u'//a[@_stat="info:title"]')
        m = re.search(u'\{"id":"(\w*\d*)"',r)
        if m:
            L.qq_id = m.group(1)
        m = re.search(u'&vid=(\w*\d*)&',r)
        if m:
            L.qq_vid = m.group(1)
        if len(title) > 0:
            L.title = title[0].text

        category = page.xpath(u'//span[@class="type"]')
        if len(category) > 0:
            L.category = category[0].text

        area = page.xpath(u'.//span[contains(text(),"地　区:")]')
        if len(area) > 0:
            L.area = area_process(area[0].getnext().text)

        foreign_title = page.xpath(u'//span[@class="title_en"]')
        if len(foreign_title) > 0:
            L.foreign_title = foreign_title[0].text

        qq_play = page.xpath(u'.//a[@_stat="info:playbtn"]')
        if len(qq_play)>0:
            L.qq_play = qq_play[0].get("href")

        language = page.xpath(u'//span[contains(text(),"语　言:")]')
        if len(language) > 0:
            L.language = language_process(language[0].getnext().text)

        year = page.xpath(u'.//span[contains(text(),"上映时间")]')
        if len(year) > 0 and year[0].getnext().text:
            m = re.search(u'(\d{4})',year[0].getnext().text)
            if m:
                L.year = m.group(1)

        all_episode = page.xpath(u'//span[contains(text(),"总集数:")]')
        if len(all_episode) > 0:
            L.all_episode = all_episode[0].getnext().text

        release_date = page.xpath(u'//span[contains(text(),"出品时间:")]')
        if len(release_date) > 0:
            L.release_date = release_date[0].getnext().text
            if L.release_date and L.year==None:
                try:
                    m = re.search(u'(\d{4})',L.release_date)
                    if m:
                        L.year = m.group(1)
                except Exception as e:
                    pass
        year = page.xpath(u'.//span[contains(text(),"首播时间")]')
        if len(year) > 0 and L.year == None:
            m = re.search(u'(\d{4})',year[0].getnext().text)
            if m:
                L.year = m.group(1)

        alias = page.xpath(u'//span[contains(text(),"别　名")]')
        if len(alias) > 0:
            L.alias = alias[0].getnext().text

        tags = page.xpath(u'//a[@class="tag"]')
        if len(tags) > 0:
            _temp = [x.text for x in tags]
            L.tags = ",".join(set(_temp))

        summary = page.xpath(u'//span[@class="desc_txt"]/span[@class="txt _desc_txt_lineHight"]')
        if len(summary) > 0:
            L.summary = parse_simple(summary[0].text)

        qq_rating = page.xpath(u'//div[@class="score_v"]/span[@class="score"]')
        if len(qq_rating) > 0:
            L.qq_rating = qq_rating[0].text

        douban_rating = page.xpath(u'//a[@class="score_db"]/span[@class="score"]')
        if len(douban_rating) > 0:
            L.douban_rating = douban_rating[0].text

        poster = page.xpath(u'//img[@_stat="info:poster"]')
        if len(poster) > 0:
            L.poster = []
            if poster[0].get("src"):
            	L.poster.append({"url":self.parse_imgurl(poster[0].get("src")),"name":poster[0].get("alt")})
            	L.img_url = self.parse_imgurl(poster[0].get("src"))

        #导演演员
        actor_list = page.xpath(u'//ul[contains(@class,"actor_list")]/li')
        starring_list = []
        starring = []
        directors_list = []
        directors = []
        if len(actor_list) > 0:
            _temp = []
            for actor in actor_list:
                _dic = {}
                actor_avatar = actor.find(u'a')
                if actor_avatar is not None:
                    if actor_avatar.find('img') is not None:
                        _dic["avatar"] = self.parse_imgurl(actor_avatar.find('img').get("src"))
                    _dic["qq_id"] = actor.get("data-id")
                    if actor.find("span") is not None:
                        _dic["name"] = actor.find("span").text
                    _dic["qq_home_page"] = actor_avatar.get("href")
                    actor_detail = actor.xpath(u'.//div[@class="actor_detail"]')
                    if actor_detail:
                        # 职业
                        occupation = actor_detail[0].xpath(u'.//span[contains(text(),"职业")]')
                        if occupation:
                            _dic['occupation'] = occupation[0].getnext().text

                        # 地区
                        area = actor_detail[0].xpath(u'.//span[contains(text(),"地区")]')
                        if len(area) > 0:
                            _dic['area'] = area[0].getnext().text

                    # 简介
                    intro = actor.xpath(u'.//span[@itemprop="description"]')
                    if intro:
                        _dic["intro"] = intro[0].text
                    # 导演
                    if actor_avatar.xpath(u'.//span[@class="director"]'):
                        directors_list.append(_dic)
                        directors.append(_dic['name'])
                    else:
                        # 演员
                        starring_list.append(_dic)
                        starring.append(_dic['name'])
        if starring_list:
            L.starring = ','.join(starring)
            L.starring_list = starring_list
        if directors_list:
            L.directors = ','.join(directors)
            L.directors_list = directors_list

        if L.title==None:
            return False
        L.created_at = time.time()
        return L.__dict__


    def parse_imgurl(self,url):
        if re.search(u'http:',url):
            return url
        else:
            return u'http:' + url

    def detail_url_parser(self,r):
        try:
            page = etree.HTML(r)
        except Exception as e:
            return False
        m = page.xpath(u'//h2[@class="player_title"]/a')
        if len(m):
            return "https://v.qq.com"+m[0].get("href")
        else:
            return None

    def parse_star(self,r,url):
        data = Star()
        try:
            page = etree.HTML(r)
        except Exception as e:
            return False
        intro = page.xpath(u'.//div[@class="wiki_content"]/text()')
        if intro:
            data.intro = parse_simple("".join(intro))
        name = page.xpath(u'.//span[contains(text(),"中文名")]')
        if len(name)>0:
            data.name = parse_simple(name[0].getnext().text)

        date_birth = page.xpath(u'.//span[contains(text(),"出生日期")]')
        if len(date_birth)>0:
            data.date_birth = parse_simple(date_birth[0].getnext().text)
            m = re.search(u'(\d{4}).{1}(\d{2}).{1}(\d{2})',data.date_birth)
            if m:
                data.date_birth = "-".join(m.groups())

        foreign_names = page.xpath(u'.//span[contains(text(),"外文名")]')
        if len(foreign_names)>0:
            data.foreign_names = parse_simple(foreign_names[0].getnext().text)

        occupation = page.xpath(u'.//span[contains(text(),"职　　业")]')
        if len(occupation)>0:
            data.occupation = parse_simple(occupation[0].getnext().text)

        alias = page.xpath(u'.//span[contains(text(),"别　名")]')
        if len(alias)>0:
            data.alias = parse_simple(alias[0].getnext().text)

        hobbies = page.xpath(u'.//span[contains(text(),"爱　　好")]')
        if len(hobbies)>0:
            data.hobbies = parse_simple(hobbies[0].getnext().text)

        area = page.xpath(u'.//span[contains(text(),"地　区")]')
        if len(area)>0:
            data.area = parse_simple(area[0].getnext().text)

        area = page.xpath(u'.//span[contains(text(),"地　区")]')
        if len(area)>0:
            data.area = parse_simple(area[0].getnext().text)

        constellation = page.xpath(u'.//span[contains(text(),"星　座")]')
        if len(constellation)>0:
            data.constellation = parse_simple(constellation[0].getnext().text)

        blood = page.xpath(u'.//span[contains(text(),"血　型")]')
        if len(blood)>0:
            data.blood = parse_simple(blood[0].getnext().text)

        body_height = page.xpath(u'.//span[contains(text(),"身　高")]')
        if len(body_height)>0:
            data.body_height = parse_simple(body_height[0].getnext().text)

        body_height = page.xpath(u'.//span[contains(text(),"身　高")]')
        if len(body_height)>0:
            data.body_height = parse_simple(body_height[0].getnext().text)

        body_weight = page.xpath(u'.//span[contains(text(),"体　重")]')
        if len(body_weight)>0:
            data.body_weight = parse_simple(body_weight[0].getnext().text)

        birthplace = page.xpath(u'.//span[contains(text(),"出生地")]')
        if len(birthplace)>0:
            data.birthplace = parse_simple(birthplace[0].getnext().text)

        avatar = page.xpath(u'.//div[@class="star_pic"]/img')
        if len(avatar)>0:
            data.avatar = "http:"+avatar[0].get("src")

        data.qq_home_page = url
        if not data.name:
            return False
        data.created_at = time.time()
        return data.__dict__
