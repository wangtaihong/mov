#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-01 18:43:38
# @Author  : taihong (wangtaihong1@gmail.com)
# @Link    : citybrain.top
# @Version : $Id$
import requests
import re
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')
import json
import demjson
import time
from lxml import etree
from setting import douban_home_headers, douban_referer_tag_headers, douban_ajax_search_headers, douban_appjs_headers, ua
from Utils.proxy import get_proxy, delete_proxy
from Utils.utils import random_str
from urlparse import urlparse
import user_agent

home_url = u'https://movie.douban.com'
tag_url = u'https://movie.douban.com/tag/#/'
tv_url = u'https://movie.douban.com/subject/{id}/'
ajax_list_url = u'https://movie.douban.com/j/new_search_subjects?sort=T&range=0,10&tags={tags}&start=0&genres={genres}&countries={countries}'
verify_users_url = u'https://m.douban.com/rexxar/api/v2/movie/{id}/verify_users?start=0&count=2&ck='
star_url = u'https://movie.douban.com/celebrity/{id}/'


ad_url = u'https://erebor.douban.com/count/?ad=195767&bid={bid}&unit=dale_movie_tag_bottom_banner&type=impression'

def parse_video(r):
    data = {}
    page = etree.HTML(r)
    year = re.search(u'<span class="year">\((\d{4})\)</span>', r)
    if year:
        data['year'] = year.group(1)
    title = re.search(u'<span property="v\:itemreviewed">(.*)</span>', r)
    if title:
        data['title'] = title.group(1)
    bianju = page.xpath(u'//span[contains(text(),"编剧")]')
    if len(bianju) > 0:
        bianju_a = bianju[0].getnext()
        if bianju_a:
            bianju_a = bianju_a.findall('a')
            data['screenwriter_list'] = []
            screenwriters = ''
            for x in bianju_a:
                screenwriters = screenwriters+x.text+","
                # doubanid = re.search(u'/celebrity/(\d*)/',x.get("href")).group(1) if re.search(u'/celebrity/(\d*)/',x.get("href")) else x.get("href")
                if re.search(u'/celebrity/(\d*)/', x.get("href")):
                    doubanid = re.search(
                        u'/celebrity/(\d*)/', x.get("href")).group(1)
                    if rd.sismember(config.douban_star_done, doubanid) == False and rd.sismember(config.douban_star_failed, doubanid) == False:
                        rd.sadd(config.douban_star_task, doubanid)
                else:
                    doubanid = x.get("href")
                data['screenwriter_list'].append(
                    {"name": x.text, "doubanid": doubanid})
            screenwriters = screenwriters.strip(',')
            data['screenwriters'] = screenwriters

    directors_el = page.xpath(u'//span[contains(text(),"导演")]')
    if len(directors_el) > 0:
        directors_a = directors_el[0].getnext()
        if directors_a:
            directors_a = directors_a.findall('a')
            data['directors_list'] = []
            directors = ""
            for x in directors_a:
                directors = directors+x.text+","
                # doubanid = re.search(u'/celebrity/(\d*)/',x.get("href")).group(1) if re.search(u'/celebrity/(\d*)/',x.get("href")) else x.get("href")
                if re.search(u'/celebrity/(\d*)/', x.get("href")):
                    doubanid = re.search(
                        u'/celebrity/(\d*)/', x.get("href")).group(1)
                    if rd.sismember(config.douban_star_done, doubanid) == False and rd.sismember(config.douban_star_failed, doubanid) == False:
                        rd.sadd(config.douban_star_task, doubanid)
                else:
                    doubanid = x.get("href")
                data["directors_list"].append(
                    {"name": x.text, "doubanid": doubanid})
            directors = directors.strip(',')
            data['directors'] = directors

    starring_el = page.xpath(u'//span[contains(text(),"主演")]')
    if len(starring_el) > 0:
        starring_a = starring_el[0].getnext()
        if starring_a:
            starring_a = starring_a.findall('a')
            data['starring_list'] = []
            starring = ""
            for x in starring_a:
                starring = starring+x.text+","
                # doubanid = re.search(u'/celebrity/(\d*)/',x.get("href")).group(1) if re.search(u'/celebrity/(\d*)/',x.get("href")) else x.get("href")
                if re.search(u'/celebrity/(\d*)/', x.get("href")):
                    doubanid = re.search(
                        u'/celebrity/(\d*)/', x.get("href")).group(1)
                    if rd.sismember(config.douban_star_done, doubanid) == False and rd.sismember(config.douban_star_failed, doubanid) == False:
                        rd.sadd(config.douban_star_task, doubanid)
                else:
                    doubanid = x.get("href")
                data["starring_list"].append(
                    {"name": x.text, "doubanid": doubanid})
            starring = starring.strip(',')
            data['starring'] = starring
    type_el = page.xpath(u'//span[@property="v:genre"]')  # 类型
    if len(type_el) > 0:
        mvtype = ""
        for x in type_el:
            mvtype = mvtype+x.text+","
        mvtype = mvtype.strip(',')
        data['type'] = mvtype

    producer_country_el = page.xpath(u'//span[contains(text(),"制片国家/地区:")]')
    if len(producer_country_el) > 0:
        data['producer_country'] = page.xpath(
            u'//span[contains(text(),"制片国家/地区:")]/following::text()[1]')[0]

    language_el = page.xpath(u'//span[contains(text(),"语言:")]')
    if len(language_el) > 0:
        data['language'] = page.xpath(
            u'//span[contains(text(),"语言:")]/following::text()[1]')[0]

    release_date_el = page.xpath(u'//span[@property="v:initialReleaseDate"]')
    if len(release_date_el) > 0:
        release_date = ""
        for x in release_date_el:
            release_date = release_date+x.text+"|"
        release_date = release_date.strip('|')
        data['release_date'] = release_date
    duration_el = page.xpath(u'//span[@property="v:runtime"]')
    if len(duration_el) > 0:
        data['duration'] = duration_el[0].text  # 片长

    alias_al = page.xpath(u'//span[contains(text(),"又名:")]')
    if len(alias_al) > 0:
        data["alias"] = page.xpath(
            u'//span[contains(text(),"又名:")]/following::text()[1]')[0]

    IMDb_el = page.xpath(u'//span[contains(text(),"IMDb链接")]')
    if len(IMDb_el) > 0:
        data["IMDb"] = IMDb_el[0].getnext().get("href")

    rating = re.search(u'property="v\:average">(\d*\.\d*)</strong>', r)
    if rating:
        data['rating'] = rating.group(1)

    rating_sum = page.xpath(u'//span[@property="v:votes"]')
    if len(rating_sum) > 0:
        data['rating_sum'] = rating_sum[0].text

    summary_all = page.xpath(u'//span[@class="all hidden"]')
    summary = page.xpath(u'//span[@property="v:summary"]')
    if len(summary_all) > 0:
        data['summary'] = ''.join(page.xpath(
            u'//span[@class="all hidden"]/text()'))
    elif len(summary) > 0:
        data['summary'] = ''.join(page.xpath(
            u'//span[@property="v:summary"]/text()'))

    img_url = page.xpath(u'//img[@title="点击看更多海报"]')
    nbgnbg = page.xpath(u'//a[@title="点击看大图" and @class="nbgnbg"]')
    if len(img_url) > 0:
        data["img_url"] = page.xpath(u'//img[@title="点击看更多海报"]')[0].get("src")
    elif len(nbgnbg) > 0:
        data["img_url"] = nbgnbg[0].get("href")
    if len(data) == 0:
        print(r)
        update_session()
    return data