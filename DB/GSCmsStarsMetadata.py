#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-11 15:22:31
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

class GSCmsStarsMetadata(Base):
    __tablename__ = 'cms_stars_metadata'  # 表的名字  影视数据表
    ID = Column(BIGINT, primary_key=True)
 	mongo_id = Column(String(255), nullable=False)
 	birthplace = Column(String(255), default=None, comment='出生地')
 	name = Column(String(255), default=None,)
 	area = Column(String(255), default=None,)
 	intro = Column(Text, comment='简介')
 	gender = Column(String(5), default=None, comment='性别')
 	star_poster = Column(String(255), default=None, comment='明星海报')
 	avatar = Column(String(255), default=None, comment='头像')
 	alias = Column(String(255), default=None, comment='别名')
 	birthday = Column(String(255), default=None, comment='生日')
 	blood = Column(String(10), default=None, comment='血型')
 	constellation = Column(String(255), default=None, comment='星座')
 	occupation = Column(String(255), default=None, comment='职业')
 	mongo_create_time = Column(bigint(20), default=None, comment='MongoDB 创建时间')
 	create_time = Column(TIMESTAMP, nullable=False)
 	# create_time = Column(TIMESTAMP, nullable=False DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
 	update_time = Column(DATETIME, default=None,)
