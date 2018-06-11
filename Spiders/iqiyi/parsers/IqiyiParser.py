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
from Utils.utils import mictime_to_ymd, area_process, parse_simple, language_process
sys.path.append('./')


class IqiyiParser(object):
    """docstring for ClassName"""

    def __init__(self, **arg):
        # super(ClassName, self).__init__()
        # self.arg = arg
        pass

    def vdetail_parser(self, r, url=None):
        """视频详情页面"""
        page = etree.HTML(r)
        L = Contents()
        result_div = page.xpath(u'//div[@class="mod_search_topic"]')
        if result_div:
            result_div = page.xpath(u'//div[@class="mod_reuslt"]')

        title = result_div.xpath(u'//h1[@class="main_title"]/a')
        if len(title) > 0:
            L.title = title[0].text

        sub_title = result_div.xpath(u'//span[@class="sub_title"]')
        if len(sub_title) > 0:
            L.sub_title = sub_title[0].text
            if re.search(u'(\d{4})', L.sub_title):
                L.year = re.search(u'(\d{4})', L.sub_title).group(1)

        category = page.xpath(u'//a[@class="channelTag"]')
        if len(category) > 0:
            L.category = category[0].text

        area = result_div.xpath(u'//em[contains(text(),"地区")]/a')
        if len(area) > 0:
            L.area = area[0].text

        L.iqiyi_tvId = self.get_vid_by_url(url)

        language = result_div.xpath(u'//em[contains(text(),"语言")]/a')
        if len(language) > 0:
            L.language = language[0].text

        tags = result_div.xpath(u'//em[contains(text(),"类型")]/a')
        if len(tags) > 0:
            _temp = [x.text for x in tags]
            L.tags = ",".join(set(_temp))

        banben = result_div.xpath(u'//em[contains(text(),"版本")]/a')
        if len(banben) > 0:
            L.banben = banben[0].text

        summary = result_div.xpath(u'//em[contains(text(),"简介")]')
        if len(summary) > 0:
            L.summary = result_div.xpath(
                u'//em[contains(text(),"简介")]/following::text()[1]')[0]
            L.summary = parse_simple(L.summary)

        all_episode = result_div.xpath(u'//em[contains(text(),"集数")]/a')
        if len(all_episode) > 0:
            L.all_episode = self.parse_all_episode(all_episode[0].text)

        iqiyi_play_url = result_div.xpath(u'//a[contains(text(),"立即播放")]')
        if len(iqiyi_play_url) > 0:
            L.iqiyi_play_url = iqiyi_play_url[0].get("href")

        iqiyi_plays_num = result_div.xpath(u'//i[@id="widget-playcount"]')
        if len(iqiyi_plays_num) > 0:
            L.iqiyi_plays_num = iqiyi_plays_num[0].text

        peiyin = result_div.xpath(u'//em[contains(text(),"配音")]/a')
        if len(peiyin) > 0:
            L.peiyin_list = []
            _temp = []
            for x in peiyin:
                _temp.append(peiyin[0].text)
                L.peiyin_list.append({"name": peiyin[0].text, "iqiyi_url": x.get(
                    "href"), "iqiyi_id": self.get_starId_by_url(x.get("href"))})
            L.peiyin = ",".join(set(_temp))

        iqiyi_rating = page.xpath(u'//span[@class="score_font"]')
        if len(iqiyi_rating) > 0:
            L.iqiyi_rating = iqiyi_rating[0].get("snsscore")

        poster = page.xpath(u'//div[@contains(@_stat,"result_pic"]/img')
        if len(poster) > 0:
            L.poster = {"url": poster[0].get("src"), "width": poster[0].get(
                "width"), "height": poster[0].get("height"), "name": poster[0].get("alt")}
            L.img_url = L.poster['url']

        # 导演演员
        # actor_list = page.xpath(u'//ul[@class="actor_list cf"]/li/')
        # starring_list = []
        # starring = []
        # directors_list = []
        # directors = []
        return L.__dict__

    def plays_parser(self, r):
        page = etree.HTML(r)
        el_actors = page.xpath(
            u'.//li[contains(@class,"widget-actorHideResp")]')
        starring_list = []
        starring = []
        data = {}
        if len(el_actors) > 0:
            for x in el_actors:
                _temp = {}
                _temp["iqiyi_id"] = x.get("data-avatar-id")
                _temp["name"] = x.get("data-tab-text")
                avatar = x.xpath(u'.//img')
                iqiyi_url = x.xpath(u'.//a')
                if len(avatar) > 0:
                    _temp['avatar'] = "http:"+avatar[0].get("src")
                if len(iqiyi_url) > 0:
                    if not iqiyi_url[0].get("href") or iqiyi_url[0].get("href") == "":
                        continue
                    _temp['iqiyi_url'] = "http:"+iqiyi_url[0].get("href")
                starring_list.append(_temp)
                starring.append(x.get("data-tab-text"))
            data["starring"] = ",".join(starring)
            data["starring_list"] = starring_list

        el_directors = page.xpath(u'.//a[@itemprop="director"]')
        if len(el_directors) > 0:
            directors = []
            directors_list = []
            for x in el_directors:
                directors.append(x.text)
                directors_list.append({"name": x.text, "iqiyi_url": "http:"+x.get(
                    "href"), "iqiyi_id": re.search(u'(\d*)', x.get("href")).group(1)})
            data['directors'] = ",".join(directors)
            data['directors_list'] = directors_list
        # data-qitancomment-tvyear="20110629"
        tvyear = page.xpath(u'.//div[@id="qitancommonarea"]')
        if len(tvyear)>0 and tvyear[0].get("data-qitancomment-tvyear"):
        	data['year'] = re.search(u'(\d{4})',tvyear[0].get("data-qitancomment-tvyear")).group(1)
        return data

    def start_detail(self, r, url=None):
        '''明星信息解析'''
        try:
            page = etree.HTML(r)
        except Exception as e:
            return None
        S = Star()
        S.iqiyi_url = url
        m = re.search(u'"circleId"\:(\d*)', r)  # paopao id
        if m:
            S.iqiyi_circleId = m.group(1)
        avatar = page.xpath(u'.//div[@class="result_pic"]/img')
        if len(avatar) > 0:
            S.avatar = avatar[0].get("src")
            S.name = avatar[0].get("alt")
        result_detail = page.xpath(u'.//div[@class="result_detail"]')
        if len(result_detail) > 0:
            name = result_detail[0].xpath(u'.//h1[@itemprop="name"]')
            if len(name) > 0:
                S.name = parse_simple(name[0].text)
        occupation = page.xpath(u'//span[contains(text(),"职业")]')
        if len(occupation) > 0:
            S.occupation = page.xpath(
                u'//span[contains(text(),"职业")]/following::text()[1]')[0]
            S.occupation = self.parse_occupation(S.occupation)

        date_birth = page.xpath(u'//span[contains(text(),"生日")]')
        if len(date_birth) > 0:
            S.date_birth = page.xpath(
                u'//span[contains(text(),"生日")]/following::text()[1]')[0]
            S.date_birth = parse_simple(self.parse_date_birth(S.date_birth))

        area = page.xpath(u'//span[contains(text(),"地区")]')
        if len(area) > 0:
            S.area = page.xpath(
                u'//span[contains(text(),"地区")]/following::text()[1]')[0]
            S.area = self.parse_area(S.area)

        body_weight = page.xpath(u'//span[contains(text(),"体重")]')
        if len(body_weight) > 0:
            S.body_weight = page.xpath(
                u'//span[contains(text(),"体重")]/following::text()[1]')[0]
            S.body_weight = self.parse_weight(S.body_weight)

        foreign_name = page.xpath(u'//dt[contains(text(),"外文名")]')
        if len(foreign_name) > 0:
            S.foreign_name = parse_simple(foreign_name[0].getnext().text)

        gender = page.xpath(u'//dt[contains(text(),"性别")]')
        if len(gender) > 0:
            S.gender = parse_simple(gender[0].getnext().text)

        body_height = page.xpath(u'//dt[contains(text(),"身高")]')
        if len(body_height) > 0:
            S.body_height = parse_simple(body_height[0].getnext().text)

        birthplace = page.xpath(u'//dt[contains(text(),"出生地")]')
        if len(birthplace) > 0:
            S.birthplace = parse_simple(birthplace[0].getnext().text)

        date_birth = page.xpath(u'//dt[contains(text(),"出生日期")]')
        if len(date_birth) > 0:
            S.date_birth = parse_simple(date_birth[0].getnext().text)

        graduated_school = page.xpath(u'//dt[contains(text(),"毕业院校")]')
        if len(graduated_school) > 0:
            S.graduated_school = parse_simple(
                graduated_school[0].getnext().text)

        famous_times = page.xpath(u'//dt[contains(text(),"成名年代")]')
        if len(famous_times) > 0:
            S.famous_times = parse_simple(famous_times[0].getnext().text)

        alias = page.xpath(u'//dt[contains(text(),"别名")]')
        if len(alias) > 0:
            S.alias = parse_simple(alias[0].getnext().text)

        blood = page.xpath(u'//dt[contains(text(),"血型")]')
        if len(blood) > 0:
            S.blood = parse_simple(blood[0].getnext().text)

        constellation = page.xpath(u'//dt[contains(text(),"星座")]')
        if len(constellation) > 0:
            S.constellation = parse_simple(constellation[0].getnext().text)

        current_residence = page.xpath(u'//dt[contains(text(),"现居地")]')
        if len(current_residence) > 0:
            S.current_residence = parse_simple(
                current_residence[0].getnext().text)

        agency = page.xpath(u'//dt[contains(text(),"经纪公司")]')
        if len(agency) > 0:
            S.agency = parse_simple(agency[0].getnext().text)

        hobbies = page.xpath(u'//dt[contains(text(),"爱好")]')
        if len(hobbies) > 0:
            S.hobbies = parse_simple(hobbies[0].getnext().text)

        intro = page.xpath(u'//p[@class="introduce-info"]')
        if len(intro):
            S.intro = "".join(page.xpath(u'//p[@class="introduce-info"]/text()'))
            S.intro = parse_simple(S.intro)

        S.created_at = time.time()
        return S.__dict__

    def parse_albumId_tvId(self, r, url=None):
        """
        albumId: 207771601,
		tvId: 1033851800,
        """
        albumId = re.search(u'albumId: *(\d*)', r)
        tvId = re.search(u'tvId: *(\d*)', r)
        page = etree.HTML(r)
        play = page.xpath(u'.//a[@class="albumPlayBtn"]')
        data = {}
        if not albumId:
            return None
        if albumId:
            data['albumId'] = albumId.group(1)
        if tvId:
            data['tvId'] = tvId.group(1)
        if len(play) > 0:
            data['play'] = play[0].get("href")
        else:
            data['play'] = url
        return data

    def parse_imgurl(self, url):
        if re.search(u'http:', url):
            return url
        else:
            return u'http:' + url

    def get_starId_by_url(self, url):
        # http://www.iqiyi.com/lib/s_213147505.html
        m = re.search(u'(s_([^\.]+?)\.)', url)
        if m:
            return m.group(1)
        else:
            return url

    def get_vid_by_url(self, url):
        # http://www.iqiyi.com/a_19rrjptx89.html
        # http://www.iqiyi.com/a_19rrjptx89.html?vfm=2008_aldbd
        m = re.search(u'(a_([^\.]+?)\.)', url)
        if m:
            return m.group(1)
        else:
            return url

    def parse_all_episode(self, all_episode):
        m = re.search(u'(\d*)', all_episode)
        if m:
            return m.group(1)
        else:
            all_episode

    def parse_occupation(self, occupation):
        return ",".join([x.replace(" ", '').replace("\n", "").replace("\t", "").replace("\r", "") for x in occupation.split('/')])

    def parse_date_birth(self, date_birth):
        return date_birth.replace(" ", '').replace("\n", "").replace("\t", "").replace("\r", "")

    def parse_area(self, area):
        return area.strip("\n").strip(" ").strip("\n").strip("\t").strip("\r")

    def parse_height(self, height):
        return height.strip("\n").strip(" ").strip("\n").strip("\t").strip("\r")

    def parse_weight(self, body_weight):
        return body_weight.strip("\n").strip(" ").strip("\n").strip("\t").strip("\r")

    def parse_info(self, r):
        m = re.search(u'([^\=]+?)=(.*)', r)
        try:
            return json.loads(m.group(2))
        except Exception as e:
            pass
        try:
            return demjson.decode(m.group(2))
        except Exception as e:
            return None

    def merge_fields(self, info):
        L = Contents()
        L.title = info.get("name")
        L.summary = info.get("description")
        L.iqiyi_tvId = info.get("tvId")
        L.iqiyi_vid = info.get("vid")
        L.iqiyi_plays_num = info.get("playCount")
        L.iqiyi_albumId = info.get("albumId")
        L.iqiyi_play_url = info.get("url")
        if info.get("duration") and info.get("duration") != "":
            L.duration = info.get("duration")/60
        L.poster = []
        if info.get("albumImageUrl"):
            L.img_url = info.get("albumImageUrl")
            L.poster.append({"url": info.get("albumImageUrl")})
        if info.get("imageUrl"):
            L.poster.append({"url": info.get("imageUrl")})
        if info.get("videoImageUrl"):
            L.poster.append({"url": info.get("videoImageUrl")})
        if info.get("posterUrl"):
            L.poster.append({"url": info.get("posterUrl")})
        if info.get("tvImageUrl"):
            L.poster.append({"url": info.get("tvImageUrl")})
        if info.get("qualityImageUrl"):
            L.poster.append({"url": info.get("qualityImageUrl")})
        if info["issueTime"]:
            L.release_date = mictime_to_ymd(info["issueTime"])
        if info.get("crumbList"):
            level2 = True
            for x in info.get("crumbList"):
            	if int(x["level"])==2 and x["title"]!=u'VIP会员':
            		L.category = x["title"]
            		level2 = False
            if level2:
            	for x in info.get("crumbList"):
            		if int(x["level"])==3:
            			L.category = x["title"]
            			level2 = False
        _temp = []
        for x in info.get("categories"):
            if u"地区" in x.get("subName"):
                L.area = area_process(x.get("name"))
            elif u"类型" in x.get("subName") or u'风格' in x.get("subName") or u'分类' in x.get("subName") or u'小学' in x.get("subName") or u'高中' in x.get("subName") or u'短片' in x.get("subName"):
                _temp.append(x.get("name"))
            elif u"语种" in x.get("subName"):
                L.language = language_process(x.get("name"))
            elif x.get("subName") == u"年龄段":
                L.age = x.get("name")
        L.tags = ",".join(_temp)
        L.all_episode = info.get("videoCount")
        L.sub_title = info.get("subtitle")
        L.iqiyi_rating_num = info.get("commentCount")
        L.iqiyi_qitanId = info.get("qitanId")
        if info.get("cast") and info.get("cast").get("directors"):
            L.directors = []
            L.directors_list = []
            for x in info.get("cast").get("directors"):
                L.directors.append(x.get("name"))
                L.directors_list.append({"name": x.get("name"), "iqiyi_id": x.get("id"), "avatar": x.get(
                    "imageUrl"), "iqiyi_userId": x.get("userId"), "iqiyi_circleId": x.get("circleId")})
            L.directors = ",".join(L.directors)

        if info.get("cast") and info.get("cast").get("speakers"):
            L.speakers = []
            L.speakers_list = []
            for x in info.get("cast").get("speakers"):
                L.speakers.append(x.get("name"))
                L.speakers_list.append({"name": x.get("name"), "iqiyi_id": x.get("id"), "avatar": x.get(
                    "imageUrl"), "iqiyi_userId": x.get("userId"), "iqiyi_circleId": x.get("circleId")})
            L.speakers = ",".join(L.speakers)

        if info.get("cast") and info.get("cast").get("publishers"):
            L.publishers = []
            L.publishers_list = []
            for x in info.get("cast").get("publishers"):
                L.publishers.append(x.get("name"))
                L.publishers_list.append({"name": x.get("name"), "iqiyi_id": x.get("id"), "avatar": x.get(
                    "imageUrl"), "iqiyi_userId": x.get("userId"), "iqiyi_circleId": x.get("circleId")})
            L.publishers = ",".join(L.publishers)

        if info.get("cast") and info.get("cast").get("singers"):
            L.singers = []
            L.singers_list = []
            for x in info.get("cast").get("singers"):
                L.singers.append(x.get("name"))
                L.singers_list.append({"name": x.get("name"), "iqiyi_id": x.get("id"), "avatar": x.get(
                    "imageUrl"), "iqiyi_userId": x.get("userId"), "iqiyi_circleId": x.get("circleId")})
            L.singers = ",".join(L.singers)

        if info.get("cast") and info.get("cast").get("mainActors"):
            L.starring = []
            L.starring_list = []
            for x in info.get("cast").get("mainActors"):
                L.starring.append(x.get("name"))
                L.starring_list.append({"name": x.get("name"), "iqiyi_id": x.get("id"), "avatar": x.get(
                    "imageUrl"), "iqiyi_userId": x.get("userId"), "iqiyi_circleId": x.get("circleId")})
            L.starring = ",".join(L.starring)

        """编剧"""
        if info.get("cast") and info.get("cast").get("writers"):
            L.screenwriters = []
            L.screenwriter_list = []
            for x in info.get("cast").get("writers"):
                L.screenwriters.append(x.get("name"))
                L.screenwriter_list.append({"name": x.get("name"), "iqiyi_id": x.get("id"), "avatar": x.get(
                    "imageUrl"), "iqiyi_userId": x.get("userId"), "iqiyi_circleId": x.get("circleId")})
            L.screenwriters = ",".join(L.screenwriters)

        if info.get("cast") and info.get("cast").get("actors"):
            L.actors = []
            L.actors_list = []
            for x in info.get("cast").get("actors"):
                L.actors.append(x.get("name"))
                L.actors_list.append({"name": x.get("name"), "iqiyi_id": x.get("id"), "avatar": x.get(
                    "imageUrl"), "iqiyi_userId": x.get("userId"), "iqiyi_circleId": x.get("circleId")})
            L.actors = ",".join(L.actors)

        """嘉宾"""
        if info.get("cast") and info.get("cast").get("guests"):
            L.guests = []
            L.guests_list = []
            for x in info.get("cast").get("guests"):
                L.guests.append(x.get("name"))
                L.guests_list.append({"name": x.get("name"), "iqiyi_id": x.get("id"), "avatar": x.get(
                    "imageUrl"), "iqiyi_userId": x.get("userId"), "iqiyi_circleId": x.get("circleId")})
            L.guests = ",".join(L.guests)

        if L.release_date and L.year==None:
        	m = re.search(u'(\d{4})',L.release_date)
        	if m:
        		L.year = m.group(1)

        L.focuses = info.get("focuses")
        L.iqiyi_rating = info.get("score")
        L.created_at = time.time()

        return L.__dict__

    def parse_playCountPCMobileCb(self, r):
        m = re.search(u'"p":(\d*),"f":(\d*),"m":(\d*)', r)
        if m:
            return {"p": m.group(1), "f": m.group(2), "m": m.group(3)}
        else:
            return m

    def parse_user_profile(self, r):
        m = re.search(u'/\(([^\);]+?)\);', r)
        if m:
            return m.group(1)
        return r
