#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-03 09:51:53
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    :
# @Version : $Id$
# TestCmscontent

from sqlalchemy import Column, String, Integer, Text, SmallInteger
from sqlalchemy.dialects.mysql import \
    BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
    DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
    LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
    NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
    TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR, DECIMAL
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class GDCmscontent(Base):
    __tablename__ = 'cms_content'  # 表的名字  影视数据表
    # code = Column(String(64), charset='utf8',
    id = Column(BIGINT, primary_key=True)
    code = Column(String(64), default=None, comment='内容code')
    type_name = Column(String(20), default=None, comment='内容分类名')
    user_id = Column(Integer, default=None, comment='操作用户id')
    code_cp_id = Column(String(100), default=None,
                        comment='内容所属平台id (南传 百事通 广信）')
    series_flag = Column(Integer, default=None,
                         comment='内容类型  100：普通点播 110：连续剧父集 120：连续剧子集')
    parent_code = Column(String(100), default=None,
                         comment='连续剧父集编号，如果不是连续剧子集则该字段为空')
    director = Column(String(255), default=None, comment='导演')
    name = Column(String(255), default=None,)
    actor = Column(String(455), default=None, comment='演员')
    image_v = Column(String(255), default=None, comment='竖版海报')
    image_h = Column(String(255), default=None, comment='横版海报')
    image_s = Column(String(255), default=None, comment='方海报')
    status = Column(Integer, default=None, comment='内容状态 0未激活 1激活')
    alias = Column(String(200), default=None, comment='别名')
    small_type = Column(String(100), default=None, comment='小分类')
    kind = Column(String(100), default=None, comment='种类')
    show_time = Column(DATE, default=None, comment='发布时间')
    create_time = Column(DATETIME, default=None,)
    update_time = Column(DATETIME, default=None,)
    language = Column(String(20), default=None, comment='语言')
    region = Column(String(100), default=None, comment='地区')
    duration = Column(String(20), default=None, comment='时长')
    all_episode = Column(BIGINT, default=None, comment='总集数')
    summary = Column(MEDIUMTEXT, default=None, comment='简介')
    source = Column(String(30), default=None, comment='来源')
    keyword = Column(String(255), default=None, comment='核心词')
    score = Column(Integer, default=None, comment='评分')
    attention_degree = Column(Integer, default=None, comment='关注度')
    search_volume = Column(BIGINT, default=0, comment='搜索量')
    comment_volume = Column(BIGINT, default=0, comment='评论量')
    playback_volume = Column(BIGINT, default=0, comment='播放量')
    weight = Column(Integer, default=None, comment='权重')
    year = Column(String(10), default=None, comment='年份')
    sequence = Column(Integer, default=None, comment='顺序')
    content_type = Column(Integer, default=None,
                          comment='内容类型 1：视频 2： 图片 3：图文 4：直播 5：WEB')
    thumbnail = Column(String(30), default=None, comment='缩略图')
    searchkey = Column(String(30), default=None, comment='搜索码')
    stills = Column(String(30), default=None, comment='剧照')
    check_time = Column(DATETIME, default=None, comment='审核时间')
    expire_time = Column(DATETIME, default=None, comment='过期时间')
    preview_start_time = Column(DATETIME, default=None, comment='预览开始时间')
    preview_stop_time = Column(DATETIME, default=None, comment='预览结束时间')
    episode = Column(Integer, default=None, comment='第几集')
    screen_writer = Column(String(255), default=None, comment='编剧')
    tag = Column(String(255), default=None, comment='标签')
    biz_domain = Column(Integer, default=None, comment='领域 无领域  单领域 双领域')
    definition = Column(String(128), default=None,
                        comment='码流大小列表 1：高清,2：标清, 默认,11：移动高清,15：移动清晰,20：移动流畅')
    resolution = Column(String(128), default=None, comment='分辨率列表，多值，逗号间隔')
    carrier_code = Column(String(128), default=None, comment='业务运营商CODE')
    start_date_time = Column(
        DATETIME, default=None, comment='内容开始时间（上线时间）')
    end_date_time = Column(DATETIME, default=None, comment='内容结束时间（下线时间）')
    price = Column(DOUBLE(50, 0), default=None, comment='价格')
    control_level = Column(Integer, default=None, comment='控制级别')
    recommend_level = Column(
        Integer, default=None, comment='推荐级别(0：不支持推荐1：热点推荐2：强档推荐)')
    copyright = Column(String(128), default=None, comment='版权号')
    copyright_end_time = Column(DATE, default=None, comment='版权到期时间')
    genres = Column(String(384), default=None, comment='主题')
    styles = Column(String(500), default=None, comment='风格')
    country = Column(String(500), default=None, comment='国家')
    area_ids = Column(String(500), default=None, comment='区域标识列表')
    service_ids = Column(String(500), default=None, comment='服务标识列表')
    media_id = Column(String(128), default=None,
                      comment='关联的媒体编号,如果不需要该字段')
    unknow_1 = Column(String(50), default=None,)
    unknow_2 = Column(String(50), default=None,)
    data_flag = Column(Integer, default=None,)
