#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-26 11:58:38
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    :
# @Version : $Id$

# coding:utf-8
import requests
import redis
import re
import threading
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')
import json
import demjson
from bson.objectid import ObjectId
import time
from lxml import etree
sys.path.append('../')
import config
sys.path.append('./')
from DB import mysql_session, Vod
from setting import douban_home_headers, douban_referer_tag_headers, douban_ajax_search_headers, douban_appjs_headers, ua
from DB.RedisClient import rd, rpop
from Utils.proxy import get_proxy, delete_proxy
from Utils.utils import random_str, delay
from Utils.request import requests_get
from Utils.douban_ocr import recognize_url
from pymongo import MongoClient
from urlparse import urlparse
import user_agent

mongo_douban_tvs = MongoClient(
    config.MONGO_HOST, config.MONGO_PORT).zydata.douban_tvs  # 多线程下共享连接?????
mongo_douban_stars = MongoClient(
    config.MONGO_HOST, config.MONGO_PORT).zydata.douban_stars
mongo_douban_tags = MongoClient(
    config.MONGO_HOST, config.MONGO_PORT).zydata.douban_tags

home_url = u'https://movie.douban.com'
tag_url = u'https://movie.douban.com/tag/#/'
tv_tag_url = u'https://movie.douban.com/tv/'
tv_url = u'https://movie.douban.com/subject/{id}/'
ajax_list_url = u'https://movie.douban.com/j/new_search_subjects?sort=T&range=0,10&tags={tags}&start=0&genres={genres}&countries={countries}'
verify_users_url = u'https://m.douban.com/rexxar/api/v2/movie/{id}/verify_users?start=0&count=2&ck='
star_url = u'https://movie.douban.com/celebrity/{id}/'

session = requests.Session()
session.adapters.DEFAULT_RETRIES = 5
# session.cookies[] = u'll="118318"; bid=JMjve9nh9Ug; __yadk_uid=rma3RP9OuF1JDekWWGEQLIVRGDlSc5wR; _vwo_uuid_v2=D4BE7289F6AA483D6B792C38D0EC9C2F1|992a80a86f70b1cd20ef12e7e7959793; ap=1; dbcl2="154152988:v2gmo0C6RvA"; push_noty_num=0; push_doumail_num=0; __utmv=30149280.15415; ck=sy5V; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1525319368%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_id.100001.4cf6=74d116d143255fe8.1525244970.3.1525319368.1525256304.; _pk_ses.100001.4cf6=*; __utma=30149280.487994295.1525244966.1525256302.1525319370.3; __utmc=30149280; __utmz=30149280.1525319370.3.2.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utma=223695111.310121982.1525244970.1525256304.1525319370.3; __utmb=223695111.0.10.1525319370; __utmc=223695111; __utmz=223695111.1525319370.3.3.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmt=1; __utmb=30149280.2.10.1525319370'
# session.get(url=home_url, headers=douban_home_headers, timeout=10)
timeout = 3
proxy = ''
task_wait = 0
block_wait = 10
max_step = 2  # 线程数越多，该值就尽量调小 40 / 线程数,,,减少 block
ll = 118318
bid = random_str(10)
session_time = int(time.time())

ad_url = u'https://erebor.douban.com/count/?ad=195767&bid={bid}&unit=dale_movie_tag_bottom_banner&type=impression'

def delay(wait=0):
    time.sleep(wait)

def update_session(proxy=None):
    """
    更新session
    proxy:
    """
    # if proxy != None:
    #     delete_proxy(proxy)
    # proxy = get_proxy()
    # print("proxy:", proxy)
    # session = requests.Session()
    # session.cookies['bid'] = random_str(10)
    bid = random_str(10)
    session.cookies.set('bid', bid, domain='.douban.com', path='/')
    # session.cookies['ll'] = '218319'
    session.adapters.DEFAULT_RETRIES = 5
    session_time = int(time.time())
    # session.proxies = {"http": "http://{}".format(proxy)}
    
    # retry = 5
    # while retry > 0:
    #     try:
    #         ua = user_agent.generate_navigator(
    #             os=None, navigator=None, platform=None, device_type=None)
    #         douban_home_headers['User-Agent'] = ua['user_agent']
    #         session.get(url=home_url, headers=douban_home_headers, timeout=10)
    #         break
    #     except requests.exceptions.ProxyError as e:
    #         print('update_session:', str(e))
    #     except requests.exceptions.RequestException as e:
    #         print('update_session:', str(e))
    #     retry -= 1
    # print(session.cookies)


def cleanup(*args):
    """
    清除指定的redis list数据
    """
    for x in args:
        rd.delete(x)


def spider_seed(tag_url=tag_url):
    """获取分类,做种子"""
    start = 1
    retry = 5
    while retry > 0:
        try:
            r = requests_get(url=tag_url,
                             headers=douban_home_headers, timeout=timeout)
            # page = etree.HTML(r)
            appjs_url = re.search(
                u'<script type="text/javascript" src="((.*)app\.js)"></script>', r).group(1)
            print(appjs_url)
            appjs = requests_get(url=appjs_url, headers=douban_appjs_headers)
            jsdata = re.search(
                u'mixins\:\[f\.mixin\],data\:function\(\)\{return(.*)\},ready\:function\(\)\{window', appjs).group(1)
            print(jsdata)
            jsdata = re.sub(u'!', '', jsdata)
            jsdata = re.sub(
                u'browserHeight:document.documentElement.clientHeight', '', jsdata)
            jsdata = demjson.decode(jsdata)
            save_tags = rd.sadd(config.doubantv_tags,
                                json.dumps(jsdata['tag_categories']))
            if save_tags == 1:
                # mongo_douban_tags.insert(json.dumps(jsdata["tag_categories"]), check_keys=False)  #
                mongo_douban_tags.insert(
                    {"tag_categories": jsdata["tag_categories"]}, check_keys=False)  #
            ajax_list_url = u'https://movie.douban.com/j/new_search_subjects?sort=T&range=0,10&tags={tags}&start=0&genres={genres}&countries={countries}'
            print(len(jsdata["tag_categories"][0]))
            print(len(jsdata["tag_categories"][1]))
            print(len(jsdata["tag_categories"][2]))
            print(len(jsdata["tag_categories"][3]))
            jsdata["tag_categories"][1][0] = ""
            jsdata["tag_categories"][2][0] = ""
            jsdata["tag_categories"][3][0] = ""
            jsdata["tag_categories"][0][0] = ""
            for x in xrange(0, len(jsdata["tag_categories"][1])):  # "全部类型"
                c1 = jsdata["tag_categories"][1][x]
                for xx in xrange(0, len(jsdata["tag_categories"][2])):  # "全部地区"
                    c2 = jsdata["tag_categories"][2][xx]
                    # "全部特色"  tag2
                    for xx in xrange(0, len(jsdata["tag_categories"][3])):
                        c3 = jsdata["tag_categories"][3][xx]
                        url = ajax_list_url.format(
                            tags=c3, genres=c1, countries=c2)
                        if rd.sismember(config.doubantv_ajax_task_failed, url) == False and rd.sismember(config.doubantv_ajax_task_done, url) == False:
                            rd.sadd(config.doubantv_ajax_task, url)
                        # rd.sadd(config.doubantv_ajax_url,url)
                        print(url)
                        # "全部形式" tag1
                        for xx in xrange(0, len(jsdata["tag_categories"][0])):
                            c0 = jsdata["tag_categories"][0][xx]
                            c3c0 = c3+','+c0
                            c3c0 = re.sub(u',$', "", c3c0)
                            c3c0 = re.sub(u'^,', "", c3c0)
                            url = ajax_list_url.format(
                                tags=c3c0, genres=c1, countries=c2)
                            if rd.sismember(config.doubantv_ajax_task_failed, url) == False and rd.sismember(config.doubantv_ajax_task_done, url) == False:
                                rd.sadd(config.doubantv_ajax_task, url)
                            # rd.sadd(config.doubantv_ajax_url,url)
                            url = ajax_list_url.format(
                                tags=c0, genres=c1, countries=c2)
                            if rd.sismember(config.doubantv_ajax_task_failed, url) == False and rd.sismember(config.doubantv_ajax_task_done, url) == False:
                                rd.sadd(config.doubantv_ajax_task, url)
                            # rd.sadd(config.doubantv_ajax_url,url)
                            print(url)

            return True
        except requests.exceptions.ProxyError as e:
            print("ttt", str(e))
            update_session(proxy)
            # retry = 5
        # except requests.exceptions.InvalidProxyURL as e:
        except requests.exceptions.RequestException as e:
            print("xxx", str(e))
            update_session(proxy)
            # retry = 5
        retry -= 1
    start += 1
    if start % max_step == 0:  # 每50步更新一次session
        update_session()


def task_api():
    """
    """
    retry = 5
    i = 0
    while True:
        url = rd.spop(config.doubantv_ajax_task)
        origin_url = url
        if url is None:
            print(u"task_page sleeping....20sec")
            time.sleep(task_wait)
            continue
        # if rd.sismember(config.doubantv_ajax_task_done, url) == True or rd.sismember(config.doubantv_ajax_task_failed, url) == True:
        if rd.sismember(config.doubantv_ajax_task_done, url) == True:
            print(u"already done%s" % url)
            continue
        start = 0
        while True:
            url = re.sub(u'start=(\d*)', 'start=%s' % str(start*20), url)
            print(url)
            r = requests_get(url, headers=douban_referer_tag_headers)
            if r is False or r == None:  # 失败
                print(u'filed task:%s' % url)
                rd.sadd(config.doubantv_ajax_task_failed, url)
                continue
            try:
                r_data = json.loads(r)
            except Exception as e:
                rd.sadd(config.doubantv_ajax_task_failed, url)
                print(r)
                print(str(e))
                update_session()
                time.sleep(task_wait)
                print("-----spider  ben   sleep 10 sec....")
                continue
            if len(r_data['data']) == 0:
                rd.sadd(config.doubantv_ajax_task_done, origin_url)
                print("done%s" % origin_url)
                break
            for x in r_data['data']:
                if rd.sismember(config.douban_tv_done, x['id']) == False and rd.sismember(config.douban_tv_failed, x['id']) == False:
                    add_task = rd.sadd(config.douban_tv_task, x['id'])
                    if add_task == 1:
                        print(
                            "---------------join task.----%s--------------------" % x['id'])
                    else:
                        print(
                            '***********task repeat-******%s********************' % x['id'])
                    rd.sadd(config.douban_tvids, x['id'])
            rd.sadd(config.doubantv_ajax_task_done, origin_url)
            print("sleep 2 seconds")
            delay()
            i += 1
            start += 1
            if i % max_step == 0:
                bid = random_str(10)
                session.cookies.set('bid', bid, domain='.douban.com', path='/')
                try:
                    session.get(url=ad_url.format(
                        bid=bid), headers=douban_referer_tag_headers, timeout=timeout)
                except Exception as e:
                    pass


def task_video():
    """
    """
    retry = 5
    i = 0
    while True:
        id = rd.spop(config.douban_tv_task)
        # id = rd.spop(config.douban_tv_failed)
        if id is None:
            print(u"task_page sleeping....20sec")
            return True
        if rd.sismember(config.doubantv_ajax_task_done, id) == True:
            print(u"already done%s" % id)
            continue
        url = tv_url.format(id=id)
        r = requests_get(url=url, headers=douban_home_headers)
        if r == False or r == None:
            rd.sadd(config.douban_tv_failed, id)
            continue
        try:
            cb = check_block(r)
        except Exception as e:
            print("check_block:",str(e))
        if u'检测到有异常请求从你的 IP 发出' in r:
            print("------spider ben block... break......")
            delay(block_wait)
            continue
        data = parse_video(r)
        piw = piwik(page_title=page_title(r), session_time=session_time, origin_url=url,urlref='')
        print("piw",piw)
        if data.get("title") == None:
            rd.sadd(config.douban_tv_failed, id)
            time.sleep(task_wait)
            # update_session()
            print("------spider ben block...")
            continue
        data['doubanid'] = id
        print(json.dumps(data))
        mongo_r = mongo_douban_tvs.insert(data, check_keys=False)  #
        photostask = json.dumps({"id": id, "mongoTVID": str(mongo_r)})
        if rd.sismember(config.douban_star_done, photostask) == False and rd.sismember(config.douban_photos_failed, photostask) == False:
            rd.sadd(config.douban_photos_task, photostask)
        print(photostask)
        # return True
        rd.sadd(config.douban_tv_done, id)
        # tv_after(id=id, url=url)
        print("done.. sleep %s seconds."%task_wait)
        delay()
        i += 1
        if i % max_step == 0:
            bid = random_str(10)
            session.cookies.set('bid', bid, domain='.douban.com', path='/')


def tv_after(id, url):
    headers = douban_home_headers
    headers['Referer'] = url
    headers['Accept'] = u'application/json, text/javascript, */*; q=0.01'
    return requests_get(url=verify_users_url.format(id=id), headers=headers)


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

    all_episode = page.xpath(u'//span[contains(text(),"集数:")]')
    if len(all_episode) > 0:
        data['all_episode'] = page.xpath(
            u'//span[contains(text(),"集数:")]/following::text()[1]')[0]

    episode_time = page.xpath(u'//span[contains(text(),"单集片长:")]')
    if len(episode_time) > 0:
        data['episode_time'] = page.xpath(u'//span[contains(text(),"单集片长:")]')[0].text

    season = page.xpath(u'//select[@id="season"]/option[@selected="selected"]')   #season季数
    if len(season) > 0:
        data['season'] = season[0].text

    release_date_el = page.xpath(u'//span[@property="v:initialReleaseDate"]')#首播
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
    tags = page.xpath(u'//div[@class="tags-body"]/a')
    data['tags'] = ''
    for x in tags:
        data['tags']+= "".join([x.text,','])
    data['tags'] = data['tags'].strip(',')
    if len(data) == 0:
        print(r)
    return data


def task_photos():
    """
    """
    retry = 5
    i = 0
    photos_url = u'https://movie.douban.com/subject/{id}/photos?type=R'
    while True:
        #线程锁,必须加这里.
        #with threading.Lock():
        # task = rd.spop(config.douban_photos_task)
        task = rd.spop(config.douban_photos_failed)
        if task is None:
           print(u"task_page sleeping....20sec")
           return True
        # if rd.sismember(config.douban_photos_failed, task) == True or rd.sismember(config.douban_photos_done, task) == True:
        if rd.sismember(config.douban_photos_done, task) == True:
           print(u"already done%s" % task)
           continue
        T = json.loads(task)
        # T = {}
        # task = ""
        # T['id'] = "25827963"
        url = photos_url.format(id=T['id'])
        print(url)
        # data = []
        data = get_photos(url=url, id=T['id'])
        # for x in get_photos(url=url, id=T['id']):
        #     #if x == False or len(x) == 0 or x == None:
        #     if x == False or x == None:
        #         # rd.sadd(config.douban_photos_failed, task)
        #         rd.sadd(config.douban_photos_task, task)
        #         print("------spider ben sleep 20 sec...")
        #         update_session()
        #         break
        #     print(json.dumps(x))
        #     print(len(x))
        #     data += x
        print("++++++++++++++++%s+++++++++++++%s++++++++++++"%(task,len(data)))
        if len(data)==0:
            #rd.sadd(config.douban_photos_failed, task)
            #rd.sadd(config.douban_photos_task, task)
            continue
        print(json.dumps(data))
        # return
        '''这是后面的骚操作.....'''
        mongo_douban_tvs.update({'_id': ObjectId(T['mongoTVID'])}, {'$unset': {'poster':1}}, multi=True)
        result = mongo_douban_tvs.update_one({'_id': ObjectId(T['mongoTVID'])}, {'$set': {'poster': data}})
        if result.modified_count == 0:
            rd.sadd(config.douban_photos_failed, task)
            #rd.sadd(config.douban_photos_task, task)
        rd.sadd(config.douban_photos_done, task)
        delay()
        print("done.%s. sleep 3 seconds."%result.modified_count)
        i += 1
        if i % max_step == 0:
            bid = random_str(10)
            session.cookies.set('bid', bid, domain='.douban.com', path='/')


def task_star():
    """
    """
    retry = 5
    i = 0
    while True:
        # task = rd.spop(config.douban_star_task)
        task = rd.spop(config.douban_star_failed)
        if task is None:
            print(u"task_page sleeping....20sec")
            break
            continue
        # if rd.sismember(config.douban_star_failed, task) == True or rd.sismember(config.douban_star_done, task) == True:
        if rd.sismember(config.douban_star_done, task) == True:
            print(u"already done%s" % task)
            continue
        url = star_url.format(id=task)
        print(url)
        r = requests_get(url=url)
        if u'检测到有异常请求从你的 IP 发出' in r:
            print("------spider ben block... break......")
            delay(block_wait)
            continue
        data = parse_star(r)
        if data == False or data == None or data.get("name") == None:
            rd.sadd(config.douban_star_failed, task)
            update_session()
            time.sleep(20)
            print("------spider ben sleep 20 sec...")
            continue
        data['doubanid'] = task
        print(json.dumps(data))
        result = mongo_douban_stars.insert(data, check_keys=False)
        rd.sadd(config.douban_star_done, task)
        delay()
        print("done.%s. sleep 3 seconds."%result)
        i += 1
        if i % max_step == 0:
            bid = random_str(10)
            session.cookies.set('bid', bid, domain='.douban.com', path='/')


def parse_star(r):
    if r == False or r == None:
        return False
    page = etree.HTML(r)
    data = {}
    name = page.xpath(u'//div[@id="content"]/h1')
    if len(name) > 0:
        data['name'] = name[0].text
    imgUrl = page.xpath(u'//div[@class="pic"]/a[@class="nbg"]')
    if len(imgUrl) > 0:
        data['imgUrl'] = imgUrl[0].get("href")
    gender = page.xpath(u'//span[contains(text(),"性别")]/following::text()[1]')
    if len(gender):
        gender = re.sub('\n', '', gender[0])
        gender = gender.strip(':')
        data['gender'] = gender.strip(' ')

    constellation = page.xpath(
        u'//span[contains(text(),"星座")]/following::text()[1]')
    if len(constellation) > 0:
        constellation = re.sub('\n', '', constellation[0])
        constellation = constellation.strip(':')
        data['constellation'] = constellation.strip(' ')

    date_birth = page.xpath(
        u'//span[contains(text(),"出生日期")]/following::text()[1]')
    if len(date_birth) > 0:
        date_birth = re.sub('\n', '', date_birth[0])
        date_birth = date_birth.strip(':')
        date_birth = date_birth.strip(' ')
        data['date_birth'] = date_birth.strip(' ')
    birthplace = page.xpath(
        u'//span[contains(text(),"出生地")]/following::text()[1]')
    if len(birthplace) > 0:
        birthplace = re.sub(u'\n', "", birthplace[0])
        birthplace = birthplace.strip(':')
        data['birthplace'] = birthplace.strip(' ')

    occupation = page.xpath(
        u'//span[contains(text(),"职业")]/following::text()[1]')
    if len(occupation) > 0:
        occupation = re.sub('\n', '', occupation[0])
        occupation = occupation.strip(':')
        data['occupation'] = occupation.strip(' ')

    foreign_names = page.xpath(
        u'//span[contains(text(),"更多外文名")]/following::text()[1]')
    if len(foreign_names) > 0:
        foreign_names = re.sub('\n', '', foreign_names[0])
        foreign_names = foreign_names.strip(':')
        data['foreign_names'] = foreign_names.strip(' ')

    zh_names = page.xpath(
        u'//span[contains(text(),"更多中文名")]/following::text()[1]')
    if len(zh_names) > 0:
        zh_names = re.sub('\n', '', zh_names[0])
        zh_names = zh_names.strip('\n')
        data['zh_names'] = zh_names.strip(' ')

    family_member = page.xpath(
        u'//span[contains(text(),"家庭成员")]/following::text()[1]')
    if len(family_member) > 0:
        family_member = re.sub('\n', '', family_member[0])
        family_member = family_member.strip(':')
        data['family_member'] = family_member.strip(' ')

    imdb = page.xpath(u'//span[contains(text(),"imdb编号")]')
    if len(imdb) > 0:
        if imdb[0].getnext() is not None:
            data['imdb'] = imdb[0].getnext().text

    intro = page.xpath(u'//span[@class="all hidden"]/text()')
    _intro = page.xpath(u'//div[@id="intro"]/div[@class="bd"]/text()')
    if len(intro):
        data['intro'] = "".join(intro)
    else:
        data['intro'] = "".join(_intro)
    return data


def piwik(page_title, session_time, origin_url,urlref=''):
    '''用户行为数据上报'''
    # https://fundin.douban.com/piwik?action_name=脱单告急 (豆瓣)&idsite=100001&rec=1&r=579246&h=20&m=14&s=21&url=https%3A%2F%2Fmovie.douban.com%2Fsubject%2F26661189%2F&_id=7a36e03deb79996b&_idts=1525176862&_idvc=1&_idn=1&_refts=0&_viewts=1525176862&pdf=1&qt=0&realp=0&wma=0&dir=0&fla=0&java=0&gears=0&ag=0&cookie=1&res=1366x768&gt_ms=1143
    url = u'https://fundin.douban.com/piwik?action_name={page_title}&idsite=100001&rec=1&r=579246&h=20&m=14&s=21&url={origin_url}&urlref={urlref}&_id={_id}&_idts={_idts}&_idvc=1&_idn=1&_refts=0&_viewts={_viests}&pdf=1&qt=0&realp=0&wma=0&dir=0&fla=0&java=0&gears=0&ag=0&cookie=1&res=1366x768&gt_ms=1143'
    url = url.format(page_title=page_title,origin_url=origin_url,_id=random_str(16,True),_idts=session_time,_viests=int(time.time())+3,urlref=urlref)
    headers = douban_home_headers
    headers['Referer'] = origin_url
    return requests_get(url=url,headers=headers)

def get_photos(url, id, data=[], result={}):
    data = []
    if len(result) == 0:
        result = {"next": url}
    # while result.get("next") != None:
    url = url
    while url:
        # print('get_photos:', result.get("next"))
        print('get_photos:', url)
        headers = douban_home_headers
        headers['Referer'] = tv_url.format(id=id)
        # r = requests_get(url=result.get("next"), headers=headers)
        r = requests_get(url=url, headers=headers)
        cb = check_block(r)
        # if cb==None:
        #     # yield False
        #     url = False
        #     break
        piwik(page_title=page_title(r),session_time=session_time,origin_url=url,urlref=headers['Referer'])
        if r == False or r == None:
            # yield False
            data = False
            url = False
            break
        if u'检测到有异常请求从你的 IP 发出' in r:
            print("------spider ben block... break......")
            delay(block_wait)
            # yield False
            url = False
            data = False
            break
        result = parse_photos(r,id)
        # yield result.get('data')
        data += result.get('data')
        if result.get("next"):
            url = result.get("next")
        else:
            url = False
    return data

def page_title(r):
    try:
        page = etree.HTML(r)
        page_title = page.xpath(u'//title')[0].text
        page_title = re.sub(u'\n','',page_title)
        return page_title.strip(' ')
    except Exception as e:
        return ''

def parse_photos(r, id):
    data=[]
    page = etree.HTML(r)
    lis = page.xpath(
        u'//div[@class="article"]/ul[@class="poster-col3 clearfix"]/li')
    print("lis",lis)
    # <a href="https://movie.douban.com/subject/1292052/photos?type=R&amp;start=30&amp;sortby=like&amp;size=a&amp;subtype=a">后页&gt;</a>
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
                temp['name'] = temp['name'].strip(u' ')
            if prop_el != None:
                temp['prop'] = prop_el.text.replace(u'\n', '')
                temp['prop'] = temp['prop'].strip(u' ')
            if cover != None:
                temp['photos_page'] = cover.get("href")
                temp['url'] = cover.find('img').get("src")
            data.append(temp)
    nextpage = page.xpath(u'//a[contains(text(),"后页")]')
    if len(nextpage) > 0:
        return {"data": data, "next": nextpage[0].get("href")}
    return {"data": data}


# def requests_get(url, cookies = None,headers=None, data=None, timeout=timeout):
#     retry = 5
#     while retry > 0:
#         try:
#             r = session.get(url=url, headers=headers, timeout=timeout)
#             # print("cookies:",session.cookies)
#             # print('response url:%s' % r.url)
#             # print('request headers:%s' % r.request.headers)
#             # print('-----------------------------history-----------------------------')
#             # for x in r.history:
#             #     # print(x.status_code, x.url)
#             #     print(x.status_code)
#             return r.text
#             break
#         except requests.exceptions.ProxyError as e:
#             print('requests_get url:', url)
#             print('requests_get ProxyError:', str(e))
#             update_session(proxy)
#             # retry = 5
#         except requests.exceptions.ConnectionError as e:
#             print('requests_get url:', url)
#             print('requests_get ConnectionError:', str(e))
#             print("Connection refused by the server..sleep 5 seconds")
#             time.sleep(5)
#             update_session(proxy)
#         except requests.exceptions.TooManyRedirects as e:
#             print('requests_get url:', url)
#             print('requests_get:', str(e))
#             print("TooManyRedirects by the server..sleep 5 seconds")
#             time.sleep(5)
#             update_session(proxy)
#         except requests.exceptions.Timeout as e:
#             print('requests_get url:', url)
#             print('requests_get:', str(e))
#             print("Timeout by the server..sleep 5 seconds")
#             time.sleep(5)
#             # update_session(proxy)
#             # retry = 5
#         except requests.exceptions.RequestException as e:
#             print('requests_get url:', url)
#             print('requests_get RequestException:', str(e))
#             update_session(proxy)
#         except Exception as e:
#             print('requests_get url:', url)
#             print('requests_get Exception:', str(e))
#             # update_session(proxy)
#         retry -= 1
#     return False


def check_block(text):
    if text == None or text == False:
        return None
    if re.search(u'userAgent\,navigator\.vendor\]\.join\("\|"\)\;window\.location\.href="(.*)"\;</script>', text):
        url = re.search(
            u'window\.location\.href="(.*)"\;</script>', text).group(1)
        # https://sec.douban.com/a?c=7fe5a9&d="+d+"&r=https%3A%2F%2Fmovie.douban.com%2Fsubject%2F27025785%2F&k=dxPw8V4vdmfvvr4HxBIdfU3GtgRmjrJt80PY0sZQQHE
        # [navigator.platform,navigator.userAgent,navigator.vendor].join("|")
        navigator = "|".join([ua["platform"], ua["user_agent"], ua['vendor']])
        url = re.sub('"\+d\+"', navigator, url)
        print("sec url:",url)
        print(douban_home_headers)
        sec = session.get(url=url, headers=douban_home_headers)
        print("----sec:", sec.text)
        return sec.text
    page = etree.HTML(text)
    captcha = page.xpath(u'//img[@alt="captcha"]')
    if len(captcha) == 0:
        return None
    original_url = page.xpath(u'//input[@name="original-url"]')
    if len(original_url) == 0:
        return None
    original_url = original_url[0].get("value")
    post_url = re.search(u'(\w*://.*\.com)', original_url).group(1)
    captcha_url = page.xpath(u'//img[@alt="captcha"]')[0].get("src")
    action = page.xpath(u'//form')[0].get("action")
    # captcha-solution
    data = {}
    data['captcha-id'] = page.xpath(u'//input[@name="captcha-id"]')[
        0].get("value")
    data['captcha-solution'] = recognize_url(captcha_url)
    data['original-url'] = original_url
    print("robbot:...",data)
    print('https://www.douban.com'+action)
    r = session.post(url='https://www.douban.com'+action, headers={
                      "Content-Type": "application/x-www-form-urlencoded", "User-Agent": ua["user_agent"]}, data=data)
    print("check block.:%s" % r.text)
    if u'你访问豆瓣的方式有点像机器人程序' in r.text:
        check_block(r.text)
    elif re.search(u'userAgent\,navigator\.vendor\]\.join\("\|"\)\;window\.location\.href="(.*)"\;</script>', r.text):
        url = re.search(
            u'window\.location\.href="(.*)"\;</script>', r.text).group(1)
        # https://sec.douban.com/a?c=7fe5a9&d="+d+"&r=https%3A%2F%2Fmovie.douban.com%2Fsubject%2F27025785%2F&k=dxPw8V4vdmfvvr4HxBIdfU3GtgRmjrJt80PY0sZQQHE
        # [navigator.platform,navigator.userAgent,navigator.vendor].join("|")
        navigator = "".join([ua["platform"], ua["user_agent"], ua['vendor']])
        url = re.sub('"\+d\+"', navigator, url)
        print("sec url:",url)
        sec = session.get(url=url, headers=douban_home_headers)
        print("----sec:", sec.text)
        return sec.text
    return r.text


def use_thread():
    pass
    # cleanup((config.RD_MOVIES_LIST))
    # for i in range(1):
    #     t = threading.Thread(target=spider_seed)
    #     # t.setDaemon(True)
    #     t.start()

    # time.sleep(1)
    # for i in range(10):
    #     t = threading.Thread(target=task_api)
    #     # t.setDaemon(True)
    #     t.start()

    # time.sleep(1)
    # for i in range(20):
    #     t = threading.Thread(target=task_video)
    #     # t.setDaemon(True)
    #     t.start()

    time.sleep(10)
    for i in range(10):
        t = threading.Thread(target=task_photos)
        # t.setDaemon(True)
        t.start()

    # time.sleep(10)
    # for i in range(10):
    #     t = threading.Thread(target=task_star)
    #     # t.setDaemon(True)
    #     t.start()


if __name__ == '__main__':
    # use_thread2()
    print('ssss')
    update_session()
    use_thread()
    # spider_seed()
    # task_api()
    # task_video()
    # task_photos()
    # task_star()