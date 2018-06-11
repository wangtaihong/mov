#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-25 16:51:55
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    :
# @Version : $Id$

from sqlalchemy import Column, String, Integer, Text, SmallInteger
from sqlalchemy.dialects.mysql import \
    BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
    DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
    LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
    NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
    TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR, DECIMAL
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class NewVodData(Base):
    __tablename__ = 'new_vod_data'  # 表的名字  影视数据表
    ID = Column(BIGINT, primary_key=True)
    ACTION = Column(String(16), default=None)
    CONTENT_ID = Column(String(128), default=None)
    BIZDOMAIN = Column(Integer, default=None)
    DEFINITION = Column(String(128), default=None)
    RESOLUTION = Column(String(128), default=None)
    NAME = Column(String(384), default=None)
    TYPE = Column(Integer, default=None)
    STATUS = Column(String(128), default=None)
    CARRIER_CODE = Column(String(128), default=None)
    PROVIDER_CODE = Column(String(128), default=None)
    START_DATE_TIME = Column(String(100), default=None)
    END_DATE_TIME = Column(String(100), default=None)
    CREATE_DATE_TIME = Column(String(100), default=None)
    PRICE = Column(String(100), default=None)
    RATING = Column(Integer, default=None)
    RECOMMEND_LEVEL = Column(Integer, default=None)
    COPYRIGHT = Column(String(128), default=None)
    COPYRIGHT_END_TIME = Column(String(100), default=None)
    PRODUCE_DATE = Column(String(100), default=None)
    SUMMARY = Column(String(1536), default=None)
    LANGUAGE = Column(String(384), default=None)
    GENRES = Column(String(384), default=None)
    TAGS = Column(String(384), default=None)
    KEYWORDS = Column(String(384), default=None)
    STYLES = Column(String(100), default=None)
    COUNTRY = Column(String(100), default=None)
    AREA_IDS = Column(String(100), default=None)
    SERVICE_IDS = Column(String(255), default=None)
    ACTORS = Column(String(255), default=None)
    DIRECTORS = Column(String(255), default=None)
    DURATION = Column(TIME, default=None)
    SUPERCONTENT_ID = Column(String(128), default=None)
    MEDIA_ID = Column(String(128), default=None)
    UNKNOW_1 = Column(String(50), default=None)
    UNKNOW_2 = Column(String(50), default=None)
