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
import Queue
import threading
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')
import json
import demjson
import time
from lxml import etree
sys.path.append('../')
import config
sys.path.append('./')
from DB import mysql_session, Vod
from setting import leshi_headers, leshi_ajax_headers, leso_headers
from DB.RedisClient import rd, rpop
from Utils.proxy import get_proxy, delete_proxy
from Utils.utils import random_str
from Utils.request import requests_get
from pymongo import MongoClient
from urlparse import urlparse

mongo_letv_tvs = MongoClient(config.MONGO_HOST, config.MONGO_PORT).zydata.letv_tvs    #多线程下共享连接?????
mongo_letv_stars = MongoClient(config.MONGO_HOST, config.MONGO_PORT).zydata.letv_stars

home_url = u'http://tv.le.com/'
category_url = u"http://list.le.com/listn/c2_t-1_a-1_y-1_s1_md_o20_d1_p.html"
list_url = u'http://list.le.com'
so_url = u'http://so.le.com/s?wd={wd}&from=list'

session = requests.Session()
session.adapters.DEFAULT_RETRIES = 5
timeout = 3
proxy = ''
task_wait = 5
max_step = 50  # 线程数越多，该值就尽量调小 40 / 线程数,,,减少youku block


def update_session(proxy=None):
    """
    更新session
    proxy:
    """
    if proxy != None:
        delete_proxy(proxy)
    proxy = get_proxy()
    print("proxy:", proxy)
    session = requests.Session()
    session.adapters.DEFAULT_RETRIES = 5
    session.proxies = {"http": "http://{}".format(proxy)}
    retry = 5
    while retry > 0:
        try:
            session.get(url=home_url, headers=leshi_headers, timeout=10)
            return True
            break
        except requests.exceptions.ProxyError as e:
            print('update_session:', str(e))
        except requests.exceptions.RequestException as e:
            print('update_session:', str(e))
        retry -= 1


def cleanup(*args):
    """
    清除指定的redis list数据
    """
    for x in args:
        rd.delete(x)


def spider_seed(category_url=category_url):
    """获取分类,做种子"""
    start = 1
    list_url = u'http://list.youku.com'
    retry = 5
    while retry > 0:
        try:
            r = requests_get(url=category_url,
                             headers=leshi_headers, timeout=timeout)
            page = etree.HTML(r)
            category_el = page.xpath(
                u'//div[@class="list_box"]/div[@class="column"]/ul[@class="list_cnt"]/li')
            # categories = [{"url":list_url + x.find("a").get("href"),"category":x.find("a").text.replace(" ","").replace("\n","")} for x in category_el if x.find("a") != None]
            categories = []
            for x in category_el:
                if x.find("a") != None:
                    categories.append({"url": list_url + x.find("a").get("href"),
                                       "title": x.find("a").text.replace(" ", "").replace("\n", "")})
                else:
                    categories.append(
                        {"url": category_url, "title": x.text.replace(" ", "").replace("\n", "")})
            print(json.dumps(categories))
            # return categories
            for x in categories:
                rd.sadd(config.le_page_task, x['url'])
                rd.sadd(config.le_page_urls, x['url'])
                urls = parse_all_url(x["url"])  # 获取该category下的urls
                if urls == False:
                    re.sadd(config.le_getpage_task, x["url"])  #获取该url下的urls失败
                    continue
                for xx in urls:  # 遍历每一个url,得到该页面的全部url
                    rd.sadd(config.le_page_task, xx['url'])
                    rd.sadd(config.le_page_urls, xx['url'])
                    print(xx['url'])
                    print(xx['title'])
                    r = requests_get(r=r,url=xx["url"])
                    rr_urls = parse_all_url(r)
                    if rr_urls == False:
                        re.sadd(config.le_getpage_task, x["url"])  #获取该url下的urls失败
                        continue
                    for xxx in rr_urls:
                    	if rd.sismember(config.le_page_failed,xxx['url']) == True:
                    		continue
                    	if rd.sismember(config.le_page_done,xxx['url']) == True:
                    		continue
                        rd.sadd(config.le_page_task, xxx['url'])
                        rd.sadd(config.le_page_urls, xxx['url'])
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
    if start % 20 == 0:  # 每50步更新一次session
        update_session()


def parse_all_url(r,url):
    """
        parse list_nav of .. url
        """
    try:
        r_page = etree.HTML(r)
    except Exception as e:
        print(r)
        print(str(e))
        return False
    menus_el = r_page.xpath('//div[@class="list_nav"]/ul/li')
    temp = []
    for x in menus_el:
        if x.find("a") != None:
            temp.append({"url": list_url + x.find("a").get("href"),
                         "title": x.find("a").text.replace(" ", "").replace("\n", "")})
        else:
            temp.append(
                {"url": url, "title": x.text.replace(" ", "").replace("\n", "")})
    new_le = r_page.xpath('//div[@class="column_tite"]/ul/li/a')
    if len(new_le) > 0:
        temp.append({"url": list_url + new_le[0].get(
            "href"), "title": new_le[0].text.replace(" ", "").replace("\n", "")})  # 最新
    return temp

def parse_types(r,url):
    """
        parse list_nav of .. url
        """
    try:
        r_page = etree.HTML(r)
    except Exception as e:
        print(r)
        print(str(e))
        return False
    menus_el = r_page.xpath('//div[@class="list_menu"]/div')
    temp = []
    for x in menus_el:
        if x.find("a") != None:
            temp.append({"url": list_url + x.find("a").get("href"),
                         "title": x.find("a").text.replace(" ", "").replace("\n", "")})
        else:
            temp.append(
                {"url": url, "title": x.text.replace(" ", "").replace("\n", "")})
    new_le = r_page.xpath('//div[@class="column_tite"]/ul/li/a')
    if len(new_le) > 0:
        temp.append({"url": list_url + new_le[0].get(
            "href"), "title": new_le[0].text.replace(" ", "").replace("\n", "")})  # 最新
    return temp


def task_page():
    """
    """
    retry = 5
    i = 0
    while True:
        url = rd.spop(config.le_page_task)
        # url = rd.spop(config.le_page_failed)
        if url is None:
            print(u"task_page sleeping....20sec")
            time.sleep(task_wait)
            continue
        if rd.sismember(config.le_page_done, url) == True:
            print(u"already done%s" % url)
            continue
        r = requests_get(url, headers=leshi_headers)
        if r is False or r == None:  # 失败
            print(u'filed task:%s' % url)
            rd.sadd(config.le_page_failed, url)
            continue
        m = re.search(
            u"frontUrl\: *'(http://list\.le\.com\/getLesoData([^',]+?))',", r)
        print("task_page:", url)
        if m:
            # http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn=1&ph=420001&dt=1&cg=2&or=4&stt=1&vt=180001
            ajax_url = m.group(1)
            pn = 1
            while True:
                ajax_url = re.sub(u"pn=\d*", 'pn=%s' % pn, ajax_url)
                print("ajax_url:", ajax_url)
                r = requests_get(url=ajax_url, headers=leshi_ajax_headers)
                if r == False or r == None:
                    rd.sadd(config.le_page_ajax_failed, ajax_url)
                    continue
                pn += 1
                # print(r)
                try:
                	list_data = json.loads(r)
                except Exception as e:
                	print(str(e))
                	print(r)
                	print(ajax_url)
                	rd.sadd(config.le_page_ajax_failed, ajax_url)
                	print("continue")
                	continue
                if list_data.get("data").get("more") == False:
                    print("this url page fetch done")
                    break
                for x in list_data.get("data").get("arr"):
                    is_done = rd.sismember(config.le_tv_done, x["unique_id"])
                    if is_done == True:
                        print("already done!")
                        print(x['name'])
                        # return False
                        continue
                    # 初步清洗
                    data = {}
                    data = x
                    data['created_at'] = time.time()
                    data['updated_at'] = time.time()
                    # print(json.dumps(x))
                    # data["summary"] = x['description']
                    # data["category"] = x['categoryName']
                    # data["title"] = x['name']
                    # data["alias"] = x['otherName']
                    # data["subname"] = x['subname']
                    # data["englishName"] = x['englishName']
                    # data["language"] = x['language']
                    # data["area"] = x['areaName']
                    # data["plays_num"] = x['playCount']
                    # data["le_score"] = x['rating']
                    # # data["isEnd"] = x['isEnd']
                    # data["subCategoryName"] = x['subCategoryName']
                    # data["videoTypeName"] = x['videoTypeName']
                    # data["duration"] = x['duration'] #时长 单集视频是秒，电视剧剧集资源是每集的分钟数
                    # data["doubanid"] = x['doubanid'] #doubanid
                    # data["urlLink"] = x['urlLink']
                    # data["copyright"] = x['copyright']
                    # data["imgUrl"] = x['imgUrl']
                    # data["tag"] = x['tag']
                    # data["vids"] = x['vids']  #子集ids
                    # data["shortDesc"] = x['shortDesc']
                    # data["monthCount"] = x['monthCount']
                    # data["intro"] = x['intro']
                    # data["publishCompany"] = x['publishCompany']
                    # data["fitAge"] = x['fitAge']
                    # data["weekCount"] = x['weekCount']
                    # data["style"] = x['style']
                    # data["letv_original_id"] = x['letv_original_id']
                    # data["global_id"] = x['global_id']
                    # data["tvTitle"] = x['tvTitle']
                    # data["videoBaseType"] = x['videoBaseType']
                    # data["pubName"] = x['pubName']
                    # data["nameQuanpin"] = x['nameQuanpin']
                    # data["nameJianpin"] = x['nameJianpin']
                    # data["allowforeign"] = x['allowforeign']
                    # data["subSrc"] = x['subSrc']
                    # data["updataInfo"] = x['updataInfo']
                    # data["downloadPlatform"] = x['downloadPlatform']
                    # data["pushFlag"] = x['pushFlag']
                    # data["payPlatform"] = x['payPlatform']
                    # data["vid"] = x['vid']
                    # data["episodes"] = x['episodes']  #集数
                    # data["nowEpisodes"] = x['nowEpisodes'] #当前更新到
                    # data["ispay"] = x['ispay']
                    # data["country"] = x['country']
                    # data["videoList"] = x['videoList']
                    # try:
                    # 	data["published_at"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(x['releaseDate'])/1000)) #乐视平台的发布时间
                    # except Exception as e:
                    # 	data["published_at"] = x['releaseDate']  #有-28800000,-126259200000此类值
                    data["ctime"] = time.strftime(
                        '%Y-%m-%d %H:%M:%S', time.localtime(int(x['ctime'])/1000))  # 乐视平台的ctime,待分析，不明意义
                    data["mtime"] = time.strftime(
                        '%Y-%m-%d %H:%M:%S', time.localtime(int(x['mtime'])/1000))  # 乐视平台的mtime,待分析，不明意义
                    data["images"] = [{"url": x['images'][k], "width":k.split(
                        '*')[0], "height":k.split('*')[1]} for k in x['images']]  # hai bao
                    data["actors"] = "".join(
                        [x['actor'][it] + "," for it in x['actor']])  # 演员
                    data["directors"] = "".join(
                        [x['directory'][it] + "," for it in x['directory']])  # 导演
                    starring_type = type(x['starring']).__name__
                    if starring_type != u'str':
                        for it in x['starring']:
                            if rd.sismember(config.le_star_done, json.dumps(it)) == True:
                                continue
                            if rd.sismember(config.le_star_failed, json.dumps(it)) == True:
                                continue
                            rd.sadd(config.le_star_task, json.dumps(it))
                        # 主演   坑啊，python 拷贝 可变类型.... x['starring']和data["starring"]的值在同一块内存地址
                        data["starring"] = "".join(
                            [starring[starring.keys()[0]] + "," for starring in x['starring']])
                    if type(x['actor']).__name__ != u'str':
                        for it in x['actor']:
                            if rd.sismember(config.le_star_done, json.dumps({it: x['actor'][it]})) == True:
                                continue
                            if rd.sismember(config.le_star_failed, json.dumps({it: x['actor'][it]})) == True:
                                continue
                            print(json.dumps({it: x['actor'][it]}))
                            rd.sadd(config.le_star_task,
                                    json.dumps({it: x['actor'][it]}))
                    if type(x['directory']).__name__ != u'str':
                        for it in x['directory']:
                            if rd.sismember(config.le_star_done, json.dumps({it: x['directory'][it]})) == True:
                                continue
                            if rd.sismember(config.le_star_failed, json.dumps({it: x['directory'][it]})) == True:
                                continue
                            json.dumps({it: x['directory'][it]})
                            rd.sadd(config.le_star_task, json.dumps(
                                {it: x['directory'][it]}))
                    # print(json.dumps(data))
                    print("done!")
                    mongo_letv_tvs.insert(data, check_keys=False)  #
                    rd.sadd(config.le_tv_done, x['unique_id'])
        else:
            print(u'filed task:%s' % url)
            rd.sadd(config.le_page_failed, url)
            continue
        # 每50步更新一次session
        i += 1
        if i % max_step == 0:
            update_session()


def task_star():
    """
    """
    retry = 5
    i = 0
    while True:
        task = rd.spop(config.le_star_task)
        # task = u'{"7088": "石田卓也"}'
        if task is None:
            print(u"task_page sleeping....20sec")
            time.sleep(task_wait)
            continue
        print(task)
        is_done = rd.sismember(config.le_star_done, task)
        if is_done == True:
            print("already done.")
            continue
        task_json = json.loads(task)
        url = so_url.format(wd=task_json[task_json.keys()[0]])
        r = requests_get(url=url, headers=leso_headers)
        if r is False or r == None:  # 失败
            print(u'filed task:%s' % url)
            rd.sadd(config.le_star_failed, task)
            continue
        data = parse_sostar(r, task_json)
        if data == False or data == None:
            rd.sadd(config.le_star_failed, task)
            continue
        mongo_id = mongo_letv_stars.insert(
            data, check_keys=False)  #
        if mongo_id:
            rd.sadd(config.le_star_done, task)
        else:
            print(mongo_id)
            rd.sadd(config.le_star_failed, task)
        print('done.')
        # 每50步更新一次session
        i += 1
        if i % max_step == 0:
            update_session()


def parse_sostar(r, task_json):
    try:
        page = etree.HTML(r)
    except Exception as e:
        print(str(e))
        return False
    data = {}
    star_so = page.xpath('//div[@class="So-detail Star-so"]')
    if len(star_so) > 0:
        data_info = demjson.decode(star_so[0].get("data-info"))
        # print(re.search(u'<u>(.*)<\/u>',data_info['name']).group(1))
        name = re.sub(u'<u>', "", data_info['name'])
        name = re.sub(u'</u>', "", name)
        if data_info['leId'] == task_json.keys()[0] and data_info['type'] == u'star' and name == task_json[task_json.keys()[0]]:
            data["name"] = name
            data["leId"] = data_info['leId']
            data["imgUrl"] = page.xpath(
                '//div[@class="So-detail Star-so"]/div[@class="so-cont"]/div[@class="star_top"]/div[@class="left"]/div/img')[0].get("src")
            con = page.xpath(
                '//div[@class="So-detail Star-so"]/div[@class="so-cont"]/div[@class="star_top"]/div[@class="con"]')
            constr = etree.tostring(con[0], encoding='unicode')
            print(constr)
            intro = page.xpath(
                '//div[@class="So-detail Star-so"]/div[@class="so-cont"]/div[@class="star_top"]/div[@class="con"]/div[@class="info-cnt"]')
            data['intro'] = None
            if len(intro):
                data['intro'] = intro[0].text
            # ([^"]+?)
            # title="职业：导演">导演</a>
            m_occupation = re.search(u'title="职业：([^">]+?)">', constr)
            m_area = re.search(u'<b>地区：<\/b><b>([^\<\/b\>]+?)<\/b>', constr)
            m_birth = re.search(
                u'出生日期：<\/b><b>(\d{4}-\d{2}-\d{2})\<\/b>', constr)
            # m_intro = re.search(u'简介：([^\<\/div]+?)\<\/div>',constr)
            if m_occupation:
                data['occupation'] = m_occupation.group(1)
            if m_area:
                data['area'] = m_area.group(1)
            if m_birth:
                data['birth'] = m_birth.group(1)
            return data
        return False


# def requests_get(url, headers=None, data=None, timeout=timeout):
#     retry = 5
#     while retry > 0:
#         try:
#             r = session.get(url=url, headers=headers, timeout=timeout)
#             return r.text
#             break
#         except requests.exceptions.ProxyError as e:
#             print('requests_get url:', url)
#             print('requests_get:', str(e))
#             update_session(proxy)
#             # retry = 5
#         except requests.exceptions.ConnectionError as e:
#             print('requests_get url:', url)
#             print('requests_get:', str(e))
#             print("Connection refused by the server..sleep 5 seconds")
#             time.sleep(5)
#             update_session(proxy)
#             # retry = 5
#         except requests.exceptions.RequestException as e:
#             print('requests_get url:', url)
#             print('requests_get:', str(e))
#             update_session(proxy)
#         retry -= 1
#     return False


def check_block(text):
    pass
    # page


def use_thread_with_queue():
    # cleanup((config.RD_MOVIES_LIST))
    # for i in range(1):
    #     t = threading.Thread(target=spider_seed)
    #     # t.setDaemon(True)
    #     t.start()

    time.sleep(1)
    for i in range(5):
        t = threading.Thread(target=task_page)
        # t.setDaemon(True)
        t.start()

    # time.sleep(1)
    # for i in range(5):
    #     t = threading.Thread(target=task_star)
    #     # t.setDaemon(True)
    #     t.start()


if __name__ == '__main__':
    # use_thread_with_queue2()
    print('ssss')
    update_session()
    use_thread_with_queue()
    # spider_seed()
    # task_page()
    # task_star()
