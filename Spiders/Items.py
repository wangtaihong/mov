#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-30 09:44:45
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

class Contents(object):
    """docstring for ClassName"""

    def __init__(self, **arg):
        # super(ClassName, self).__init__()
        pass
    
    douban_rating = None
    douban_rating_sum = None

    letv_rating = None
    levid = None
    age = None
    starring = None

    youku_plays_num = None
    youku_rating = None
    
    screenwriter_list = None
    guests_list = None
    starring_list = None
    directors_list = None
    peiyin_list = None
    actors_list = None  #演员

    language = None
    title = None
    tags = None
    type = None
    all_episode = None
    category = None
    source = None

    # 出版时间
    release_date = None
    img_url = None

    # 编剧
    screenwriters = None
    summary = None
    alias = None
    directors = None
    year = None
    duration = None

    # 制片国家/地区
    producer_country = None
    doubanid = None

    # 季
    season = None

    # 外文名
    foreign_title = None

    # 出品公司
    production_company = None
    created_at = None
    poster = None
    sub_title = None
    peiyin = None
    banben = None

    iqiyi_play_url = None
    iqiyi_plays_num = None
    iqiyi_rating = None
    iqiyi_rating_num = None
    iqiyi_tvId = None
    iqiyi_vid = None
    iqiyi_albumId = None
    hosts = None
    
    pptv_play_url = None
    pptv_plays_num = None
    pptv_rating = None
    pptv_id = None
    
    sohu_play_url = None
    sohu_playlistid = None
    sohu_url = None
    sohu_plays_num = None
    sohu_rating = None
    sohu_id = None
    sohu_rating_sum = None

    qq_rating = None
    qq_id = None
    qq_play = None
    actors = None   #演员


class Star(object):
    """docstring for ClassName"""

    def __init__(self, **arg):
        # super(ClassName, self).__init__()
        # self.arg = arg
        pass
    '''出生地'''
    birthplace = None
    area = None

    # 出生日期
    date_birth = None
    name = None

    # 外文名
    foreign_names = None
    gender = None

    # 职业
    occupation = None
    intro = None

    family_member = None   # 家庭成员
    avatar = None
    doubanid = None
    douban_url = None
    qq_home_page = None
    qq_id = None
    iqiyi_id = None
    iqiyi_url = None
    baike_id = None
    baike_url = None
    sohu_id = None
    sohu_url = None

    # imdb id
    imdb = None

    # 星座
    constellation = None
    zh_names = None

    # 爱奇艺paopao id
    iqiyi_circleId = None

    # 体重
    body_weight = None

    # 身高
    body_height = None

    # 毕业院校
    graduated_school = None

    # 成名时间
    famous_times = None

    # 现居地
    current_residence = None

    # 经纪公司
    agency = None

    # 爱好
    hobbies = None

    created_at = None


class Poster(object):
    """docstring for Poster"""

    def __init__(self, **arg):
        # super(Poster, self).__init__()
        # self.arg = arg
        pass
    content_id = None
    name = None
    url = None
    photos_page = None
    doubanvid = None
    prop = None
    width = None
    doubanid = None
    levid = None
    qq_id = None
    letv_id = None
    height = None
