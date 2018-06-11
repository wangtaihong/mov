#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-28 09:19:06
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    :
# @Version : $Id$

import re
from lxml import etree
import json
import demjson
import time

import sys

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('../')
from Spiders.Items import Contents, Poster, Star
from Utils.utils import mictime_to_ymd, area_process, parse_simple, language_process, split_space

sys.path.append('./')


class YoukuParser(object):
    """docstring for ClassName"""

    def __init__(self, **arg):
        # super(ClassName, self).__init__()
        # self.arg = arg
        pass

    def parse_detail(self, r, url=None):
        try:
            page = etree.HTML(r)
        except Exception as e:
            return None
        data = Contents()
        sss = re.sub(u'\\n', '', r)
        v_show = page.xpath(u'//div[@class="p-post"]/div[@class="yk-pack p-list"]/div[@class="p-thumb"]/a')
        if len(v_show) > 0:
            data.youku_play = "http:" + v_show[0].get("href")
        # 海报:
        thumb = page.xpath(
            u'//div[@class="p-post"]/div[@class="yk-pack p-list"]/div[@class="p-thumb"]/img')
        if len(thumb) > 0:
            data.poster = [
                {"url": "http:" + thumb[0].get("src"), "title": thumb[0].get("alt"), "width": 200, "height": 300}]
            data.title = thumb[0].get("alt")
            data.img_url = "http:" + thumb[0].get("src")
        # category:
        category = page.xpath(
            '//div[@class="p-base"]/ul/li[@class="p-row p-title"]/a')
        if len(category) > 0:
            data.category = parse_simple(category[0].text)
        # 年份:可能没有
        year = page.xpath('//div[@class="p-base"]/ul/li[@class="p-row p-title"]/span[@class="sub-title"]')
        if len(year) > 0 and year[0].text:
            m = re.search(u'(\d{4})', year[0].text)
            if m:
                data.year = m.group(1)
        # 别名:可能没有
        alias = page.xpath('//div[@class="p-base"]/ul/li[@class="p-alias"]')
        if len(alias) > 0:
            data.alias = split_space(alias[0].get("title").replace('/', ','))
        # 上映:可能没有
        published_at = re.search(u'>上映：</label>(\w+-\d+-\d+)*</span>', sss)
        if published_at != None:
            data.release_date = published_at.group(1)
        # 优酷评分：可能没有
        youku_score = page.xpath('//div[@class="p-base"]/ul/li[@class="p-score"]/span[@class="star-num"]')
        if len(youku_score) > 0:
            data.youku_rating = parse_simple(youku_score[0].text)
        # 豆瓣评分:可能没有
        douban_score = re.search(u'<span class="db-bignum">(\d+\.\d*)</span>', sss)
        if douban_score != None:
            data.douban_rating = douban_score.group(1)
        # 豆瓣评价数量，可能没有
        douban_cm_num = re.search(u'<span class="db-cm-num">(\d*)评价</span>', sss)
        if douban_cm_num != None:
            data.douban_comment_sum = douban_cm_num.group(1)
        # 主演:可能没有
        actors = page.xpath('//div[@class="p-base"]/ul/li[@class="p-performer"]')
        if len(actors) > 0:
            data.starring = split_space(actors[0].get('title').replace("/", ","))
            data.starring_list = []
            for x in page.xpath('//div[@class="p-base"]/ul/li[@class="p-performer"]/a'):
                _temp = {}
                _temp["name"] = parse_simple(x.text)
                _temp["youkuid"] = re.search(u"//list\.youku\.com/star/show/(.*)\.html", etree.tostring(x)).group(1)
                if x.get("href"):
                    _temp["youku_url"] = "http:" + x.get("href")
                data.starring_list.append(_temp)

        # 集数
        renew = page.xpath(
            '//div[@class="p-base"]/ul/li[@class="p-row p-renew"]')
        if len(renew) > 0 and renew[0].text:
            m = re.search(u'(\d*)', renew[0].text)
            if m:
                data.all_episode = m.group(1)
        # 导演:循环出来
        directed = page.xpath(
            u'//div[@class="p-base"]/ul/li[contains(text(),"导演：")]/a')
        data['director_list'] = []
        if len(directed) > 0:
            data.directors = []
            for x in directed:
                data.directors.append(parse_simple(x.text))
                _temp = {}
                _temp["name"] = parse_simple(x.text)
                _temp["youkuid"] = re.search(u"//list\.youku\.com/star/show/(.*)\.html", etree.tostring(x)).group(1)
                if x.get("href"):
                    _temp["youku_url"] = x.get("href")
                data.directors_list.append(_temp)
                data.directors = ",".join(data.directors)
            data.directors = ",".join(data.directors)
        # 地区，可能没有
        area = re.search(
            u'>地区：<a href="//list\.youku\.com/category/show/([^\.html]+?)\.html" target="_blank">([^</a></li>]+?)</a>',
            sss)
        if area != None:
            data.producer_country = parse_simple(area.group(2))
        # 类型:循环出来
        types = page.xpath(u'//div[@class="p-base"]/ul/li[contains(text(),"类型")]/a')
        if len(types) > 0:
            data.tags = []
            for x in types:
                data.tags.append(parse_simple(x.text))
            data.tags = ",".join(data.tags)
        # 总播放数:可能为none
        plays_num = re.search(u'<li>总播放数：([^</li>]+?)</li>', sss)
        if plays_num != None:
            data.youku_plays_num = plays_num.group(1).replace(',', "")
        # 评论数量:可能为none
        youku_comments_num = re.search(u'<li>评论：([^</li>]+?)</li>', sss)
        if youku_comments_num:
            data.youku_comments_num = youku_comments_num.group(1)
        # 顶:可以空
        ding = re.search(u'<li>顶：([^</li>]+?)</li>', sss)
        if ding:
            data.ding = ding.group(1)
        # 简介:
        summary = page.xpath(u'.//span[contains(@class,"intro-more")]/text()')
        if summary:
            data.summary = parse_simple("".join(summary)).replace(u"简介：", "")
        # 适合年龄，可能为空
        age = re.search(u'>适用年龄：([^</li>]+?)</li>', sss)
        if age:
            data.age = age.group(1)
        peiyin = page.xpath(
            u'//div[@class="p-base"]/ul/li[contains(text(),"声优：")]/a')
        if len(peiyin) > 0:
            data.peiyin = []
            data.peiyin_list = []
            for x in peiyin:
                data.peiyin.append(parse_simple(x.text))
                _temp = {}
                _temp["name"] = parse_simple(x.text)
                _temp["youkuid"] = re.search(u"//list\.youku\.com/star/show/(.*)\.html", etree.tostring(x)).group(1)
                _temp['youku_url'] = "http:" + x.get("href")
                data['peiyin_list'].append(_temp)
            data.peiyin = ",".join(data.peiyin)
        # 综艺节目有
        presenters = page.xpath(
            u'//div[@class="p-base"]/ul/li[contains(text(),"主持人：")]/a')
        if len(presenters) > 0:
            data.presenters = []
            data.presenters_list = []
            for x in presenters:
                data.presenters.append(parse_simple(x.text))
                _temp["name"] = parse_simple(x.text)
                _temp["youkuid"] = re.search(u"//list\.youku\.com/star/show/(.*)\.html", etree.tostring(x)).group(1)
                _temp['youku_url'] = "http:" + x.get("href")
            data.presenters = ",".join(data.presenters)
        if data.title == None:
            return None
        data.created_at = time.time()

        return data.__dict__

    def parse_star_show(self, r, url):
        """
        解析明星主页
        return:dic
        """
        try:
            # r.decode('utf-8')
            page = etree.HTML(r)
        except Exception as e:
            return None
        info_el = page.xpath('//div[@id="starInfo"]/dl/dd[@class="info"]/span')
        sub_list = {u"别名": u'alias', u"性别": u'gender', u"地区": u'area', u"出生地": u'birthplace',
                    u'生日': u'birthday', u'星座': u'constellation', u"血型": u'blood', u"职业": u'occupation'}
        info_list = [re.split(u'：', parse_simple(x.text)) for x in info_el]
        for x in xrange(0, len(info_list)):
            info_list[x][0] = re.sub(info_list[x][0], sub_list[info_list[x][0]], info_list[x][0])
        info_data = {x[0]: x[1] for x in info_list}
        avatar = page.xpath(u'.//div[@class="box-avatar"]/img')
        if len(avatar) > 0:
            info_data['avatar'] = avatar[0].get("src")
        info_data.name = page.xpath('//div[@id="starInfo"]')[0].get('data-name')
        info_data.youku_starid = page.xpath('//div[@id="starInfo"]')[0].get('data-starid')
        m = re.search(u'\/(uid_\w*\d*=*)\.html', url)
        info_data['youku_uid'] = m.group(1) if m != None else None
        info_data['created_at'] = int(time.time() * 1000)
        intro = page.xpath('//dd[@class="intro"]/span[@class="long noshow"]')
        info_data['youku_url'] = url
        if len(intro) > 0:
            info_data['intro'] = intro[0].text

        return info_data

    def parse_tv_show(self, r):
            """
	    解析播放主页
	    r:网页内容
	    return tvs detail list page url
	    """
            data = Contents()
            try:
                page = etree.HTML(r)
            except Exception as e:
                return None
            a = page.xpath('//div[@class="tvinfo"]/h2/a')
            if len(a) > 0:
                data.detail_url = "http:" + a[0].get('href')
                return data.__dict__
            else:
                try:
                    data.detail_url = 'http:' + re.search(u'tvinfo.* *\n*(//list\.youku\.com/show/id_\w*\d*\.html)',
                                                          r).group(1)
                    return data.__dict__
                except Exception as e:
                    return None
            category = re.search(u"catName: '娱乐'", r)
