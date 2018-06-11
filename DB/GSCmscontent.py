#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-11 15:06:35
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


class GSCmscontent(Base):
    __tablename__ = 'cms_content'  # 表的名字  影视数据表
    # code = Column(String(64), charset='utf8',
    ID = Column(BIGINT, primary_key=True)  
	MediaId = Column(String(128), nullable=False, comment ='内容code')
	ContentType = Column(String(128), default=None, comment ='内容类型：电影 电视剧')
	ContentName = Column(String(128), default=None, comment ='内容名称')
	OriginalName = Column(String(128), default=None, comment ='原名或别名')
	ContentDetail = Column(Text, comment ='内容详情')
	ContentNum = Column(int(11), default='0', comment ='集数')
	Director = Column(String(256), default=None, comment ='主演/主讲')
	Actor = Column(String(256), default=None, comment ='演员')
	SearchKey = Column(String(256), default=None, comment ='搜索码')
	LicensingWindowStart = Column(String(32), default=None, comment ='开始时间')
	LicensingWindowEnd = Column(String(32), default=None, comment ='结束时间')
	Duration = Column(String(64), default=None, comment ='时长：分钟')
	Thumbnail = Column(String(1024), default=None, comment ='缩略图')
	Stills = Column(String(1024), default=None, comment ='剧照')
	PosterURL = Column(String(1024), default=None, comment ='海报')
	CPID = Column(String(255), default=None, comment ='cpid')
	Status = Column(int(4), default=None, comment ='状态1:生效,0:未生效')
	Language = Column(String(255), default=None, comment ='语言')
	Area = Column(String(255), default=None, comment ='地区')
	Year = Column(String(255), default=None, comment ='年代')
	Grade = Column(DECIMAL(4,1), default='6.0', comment ='评分')
	SeriesFlag = Column(int(11), default='0', comment ='多集单集标志,0:单集1:多集')
	MetaId = Column(String(64), default=None, comment ='元数据的Mongodb的id')
	CreateTime = Column(TIMESTAMP, nullable=False, comment ='创建时间')
	# CreateTime = Column(TIMESTAMP, nullable=False, DEFAULT CURRENT_TIMESTAMP comment ='创建时间')
	UpdateTime = Column(DATETIME, default=None,)