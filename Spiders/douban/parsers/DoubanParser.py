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
from Spiders.Items import Contents, Star, Poster
from Utils.utils import language_process
from Utils.utils import mictime_to_ymd, area_process, parse_simple, language_process, split_space
sys.path.append('./')
import time

class DoubanParser(object):
    """docstring for ClassName"""
    def __init__(self, **arg):
        # super(ClassName, self).__init__()
        # self.arg = arg
        pass

    def parse_imgurl(self,url):
        if re.search(u'http:',url):
            return url
        else:
            return u'http:' + url

    def vdetail_parser(self,r):
        data = Contents()
        try:
            page = etree.HTML(r)
        except Exception as e:
            return False
        year = re.search(u'<span class="year">\((\d{4})\)</span>', r)
        if year:
            data.year = year.group(1)
        title = re.search(u'<span property="v\:itemreviewed">(.*)</span>', r)
        if title:
            data.title = title.group(1)
        bianju = page.xpath(u'//span[contains(text(),"编剧")]')
        if len(bianju) > 0:
            bianju_a = bianju[0].getnext()
            if bianju_a is not None:
                bianju_a = bianju_a.findall('a')
                data.screenwriter_list = []
                screenwriters = ''
                for x in bianju_a:
                    screenwriters = screenwriters+parse_simple(x.text)+","
                    _temp = {}
                    if re.search(u'/celebrity/(\d*)/', x.get("href")):
                        _temp["doubanid"] = re.search(
                            u'/celebrity/(\d*)/', x.get("href")).group(1)
                    else:
                        # doubanid = x.get("href")
                        pass
                    if x.get("href"):
                        _temp["douban_url"] = "https://movie.douban.com"+x.get("href")
                    _temp["name"] = parse_simple(x.text)
                    data.screenwriter_list.append(_temp)
                data.screenwriters = screenwriters.strip(',')
    
        directors_el = page.xpath(u'//span[contains(text(),"导演")]')
        if len(directors_el) > 0:
            directors_a = directors_el[0].getnext()
            if directors_a is not None:
                directors_a = directors_a.findall('a')
                data.directors_list = []
                directors = ""
                for x in directors_a:
                    directors = directors+parse_simple(x.text)+","
                    _temp = {}
                    if re.search(u'/celebrity/(\d*)/', x.get("href")):
                        _temp["doubanid"] = re.search(
                            u'/celebrity/(\d*)/', x.get("href")).group(1)
                    else:
                        # doubanid = x.get("href")
                        pass
                    if x.get("href"):
                        _temp["douban_url"] = "https://movie.douban.com"+x.get("href")
                    _temp["name"] = parse_simple(x.text)
                    data.directors_list.append(_temp)
                data.directors = directors.strip(',')
    
        starring_el = page.xpath(u'//span[contains(text(),"主演")]')
        if len(starring_el) > 0:
            starring_a = starring_el[0].getnext()
            if starring_a is not None:
                starring_a = starring_a.findall('a')
                data.starring_list = []
                starring = ""
                for x in starring_a:
                    starring = starring+parse_simple(x.text)+","
                    _temp = {}
                    if re.search(u'/celebrity/(\d*)/', x.get("href")):
                        _temp["doubanid"] = re.search(
                            u'/celebrity/(\d*)/', x.get("href")).group(1)
                    else:
                        # doubanid = x.get("href")
                        pass
                    if x.get("href"):
                        _temp["douban_url"] = "https://movie.douban.com"+x.get("href")
                    _temp["name"] = parse_simple(x.text)
                    data.starring_list.append(_temp)
                starring = starring.strip(',')
                data.starring = starring
        type_el = page.xpath(u'//span[@property="v:genre"]')  # 类型
        mvtype = []
        if len(type_el) > 0:
            for x in type_el:
                mvtype.append(parse_simple(x.text))

        tags = page.xpath(u'//div[@class="tags-body"]/a')
        _temp = []
        for x in tags:
            _temp.append(parse_simple(x.text))
        _temp = _temp + mvtype
        data.tags = ",".join(set(_temp))
    
        producer_country_el = page.xpath(u'//span[contains(text(),"制片国家/地区:")]')
        if len(producer_country_el) > 0:
            producer_country = page.xpath(
                u'//span[contains(text(),"制片国家/地区:")]/following::text()[1]')[0]
            data.producer_country = area_process(split_space(producer_country.replace('/',',')))
    
        language_el = page.xpath(u'//span[contains(text(),"语言:")]')
        if len(language_el) > 0:
            language = page.xpath(
                u'//span[contains(text(),"语言:")]/following::text()[1]')[0]
            data.language = language_process(split_space(language.replace('/',',')))
    
        all_episode = page.xpath(u'//span[contains(text(),"集数:")]')
        if len(all_episode) > 0:
            all_episode = page.xpath(u'//span[contains(text(),"集数:")]/following::text()[1]')[0]
            m = re.search(u'(\d{1,})',all_episode.replace(" ",""))
            if m:
                data.all_episode = m.group(1)
    
        episode_time = page.xpath(u'//span[contains(text(),"单集片长:")]')
        if len(episode_time) > 0:
            episode = page.xpath(u'//span[contains(text(),"单集片长:")]/following::text()[1]')[0]
            m = re.search(u'(\d{1,})',episode.replace(" ",""))
            if m:
                data.duration = m.group(1)
    
        season = page.xpath(u'//select[@id="season"]/option[@selected="selected"]')   #season季数
        if len(season) > 0:
            data.season = season[0].text
    
        release_date_el = page.xpath(u'//span[@property="v:initialReleaseDate"]')#首播
        if len(release_date_el) > 0:
            release_date = ""
            for x in release_date_el:
                release_date = release_date+parse_simple(x.text)+"|"
            release_date = release_date.strip('|')
            m = re.search(u'(\d{4}-\d{2}-\d{2})',release_date.replace(" ",""))
            if m:
                data.release_date = m.group(1)
            else:
                data.release_date = release_date
        duration_el = page.xpath(u'//span[@property="v:runtime"]')
        if len(duration_el) > 0:
            m = re.search(u'(\d{1,})',duration_el[0].text.replace(" ",''))
            if m:
                data.duration = m.group(1)  # 片长
    
        alias_al = page.xpath(u'//span[contains(text(),"又名:")]')
        if len(alias_al) > 0:
            alias = page.xpath(
                u'//span[contains(text(),"又名:")]/following::text()[1]')[0]
            data.alias = split_space(alias.replace('/',','))
    
        IMDb_el = page.xpath(u'//span[contains(text(),"IMDb链接")]')
        if len(IMDb_el) > 0:
            data.IMDb = IMDb_el[0].getnext().get("href")
    
        rating = re.search(u'property="v\:average">(\d*\.\d*)</strong>', r)
        if rating:
            data.douban_rating = rating.group(1)
    
        rating_sum = page.xpath(u'//span[@property="v:votes"]')
        if len(rating_sum) > 0:
            data.douban_rating_sum = rating_sum[0].text
    
        summary_all = page.xpath(u'//span[@class="all hidden"]')
        summary = page.xpath(u'//span[@property="v:summary"]')
        if len(summary_all) > 0:
            data.summary = ''.join(page.xpath(
                u'//span[@class="all hidden"]/text()'))
            data.summary = parse_simple(data.summary)
        elif len(summary) > 0:
            data.summary = ''.join(page.xpath(
                u'//span[@property="v:summary"]/text()'))
            data.summary = parse_simple(data.summary)
    
        img_url = page.xpath(u'//img[@title="点击看更多海报"]')
        nbgnbg = page.xpath(u'//a[@title="点击看大图" and @class="nbgnbg"]')
        if len(img_url) > 0:
            data.img_url = page.xpath(u'//img[@title="点击看更多海报"]')[0].get("src")
        elif len(nbgnbg) > 0:
            data.img_url = nbgnbg[0].get("href")

        if data.all_episode>1 and (u"动漫" in data.tags or u"动画" in data.tags):
            data.category = u"动漫"
        elif data.all_episode>1 and (u"综艺" in data.tags or u'真人秀' in data.tags):
            data.category = u'综艺'
        elif data.all_episode>1:
            data.category = u"电视剧"
        elif u"动漫" in data.tags or u"动画" in data.tags:
            data.category = u'动漫'
        elif u"短片" in data.tags:
            data.category = u'短片'
        else:
            data.category = u'电影'

        m = re.search(u"SUBJECT_ID: *'(\d*)'",r)
        if m:
            data.doubanid = m.group(1)

        print("oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
        print(data.__dict__)
        print("oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
        return data.__dict__

    def parse_photos(self,r, id):
        data=[]
        page = etree.HTML(r)
        lis = page.xpath(
            u'//div[@class="article"]/ul[@class="poster-col3 clearfix"]/li')
        if len(lis) > 0:
            for x in lis:
                temp = {}
                temp['doubanvid'] = id
                temp['doubanid'] = x.get('data-id')
                name_el = x.find('div[@class="name"]')
                prop_el = x.find('div[@class="prop"]')
                cover = x.find('div[@class="cover"]/a')
                if name_el != None:
                    temp['name'] = name_el.text.replace(u'\n', '')
                    temp['name'] = parse_simple(temp['name'])
                if prop_el != None:
                    temp['prop'] = prop_el.text.replace(u'\n', '')
                    temp['prop'] = temp['prop'].strip(u' ')
                    m = re.search(u'(\d{1,})x(\d{1,})',temp['prop'].replace(" ",""))
                    if m:
                        temp['width'] = m.group(1)
                        temp['height'] = m.group(2)
                if cover != None:
                    temp['photos_page'] = cover.get("href")
                    temp['url'] = cover.find('img').get("src")
                    temp['url'] = re.sub(u'/photo/m/','/photo/l/',temp['url'])
                data.append(temp)
        nextpage = page.xpath(u'//a[contains(text(),"后页")]')
        if len(nextpage) > 0:
            return {"data": data, "next": nextpage[0].get("href")}
        return {"data": data}

    def parse_star(self,r):
        try:
            page = etree.HTML(r)
        except Exception as e:
            return False
        data = Star()
        name = page.xpath(u'//div[@id="content"]/h1')
        if len(name) > 0:
            data.name = parse_simple(name[0].text)
        else:
            return False
        imgUrl = page.xpath(u'//div[@class="pic"]/a[@class="nbg"]')
        if len(imgUrl) > 0:
            data.img_url = imgUrl[0].get("href")
        gender = page.xpath(u'//span[contains(text(),"性别")]/following::text()[1]')
        if len(gender):
            gender = re.sub('\n', '', gender[0])
            gender = gender.strip(':')
            data.gender = parse_simple(gender.strip(' '))
    
        constellation = page.xpath(
            u'//span[contains(text(),"星座")]/following::text()[1]')
        if len(constellation) > 0:
            constellation = re.sub('\n', '', constellation[0])
            constellation = constellation.strip(':')
            data.constellation = parse_simple(constellation.strip(' '))
    
        date_birth = page.xpath(
            u'//span[contains(text(),"出生日期")]/following::text()[1]')
        if len(date_birth) > 0:
            date_birth = re.sub('\n', '', date_birth[0])
            date_birth = date_birth.strip(':')
            date_birth = date_birth.strip(' ')
            data.date_birth = parse_simple(date_birth.strip(' '))
        
        birthplace = page.xpath(
            u'//span[contains(text(),"出生地")]/following::text()[1]')
        if len(birthplace) > 0:
            birthplace = re.sub(u'\n', "", birthplace[0])
            birthplace = birthplace.strip(':')
            data.birthplace = parse_simple(birthplace.strip(' '))
    
        occupation = page.xpath(
            u'//span[contains(text(),"职业")]/following::text()[1]')
        if len(occupation) > 0:
            occupation = re.sub('\n', '', occupation[0])
            occupation = occupation.strip(':')
            data.occupation = split_space(occupation.replace('/',","))
    
        foreign_names = page.xpath(
            u'//span[contains(text(),"更多外文名")]/following::text()[1]')
        if len(foreign_names) > 0:
            foreign_names = re.sub('\n', '', foreign_names[0])
            foreign_names = foreign_names.strip(':')
            data.foreign_names = split_space(foreign_names.replace("/",","))
    
        zh_names = page.xpath(u'//span[contains(text(),"更多中文名")]/following::text()[1]')
        if len(zh_names) > 0:
            zh_names = re.sub('\n', '', zh_names[0])
            zh_names = zh_names.strip('\n').strip(':')
            data.zh_names = split_space(zh_names.replace('/',','))
    
        family_member = page.xpath(
            u'//span[contains(text(),"家庭成员")]/following::text()[1]')
        if len(family_member) > 0:
            family_member = re.sub('\n', '', family_member[0])
            family_member = family_member.strip(u':')
            data.family_member = split_space(family_member.replace('/',','))
    
        imdb = page.xpath(u'//span[contains(text(),"imdb编号")]')
        if len(imdb) > 0:
            if imdb[0].getnext() is not None:
                data.IMDb = parse_simple(imdb[0].getnext().text)
    
        intro = page.xpath(u'//span[@class="all hidden"]/text()')
        _intro = page.xpath(u'//div[@id="intro"]/div[@class="bd"]/text()')
        if len(intro):
            data.intro = parse_simple("".join(intro))
        else:
            data.intro = parse_simple("".join(_intro))
        
        return data.__dict__
