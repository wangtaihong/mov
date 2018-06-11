# coding: utf-8

from sqlalchemy import Column, String, Integer, Text, SmallInteger
from sqlalchemy.dialects.mysql import \
    BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
    DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
    LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
    NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
    TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR, DECIMAL
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Vod(Base):
    __tablename__ = 'baiyug_vod'  # 表的名字  影视数据表

    # 表的结构:
    id = Column(Integer, primary_key=True)
    d_name = Column(String(255), nullable=False, default='')
    d_subname = Column(String(255), nullable=False, default='')
    d_enname = Column(String(255), nullable=False, default='')
    d_letter = Column(String(1), nullable=False, default='')
    d_color = Column(String(6), nullable=False, default='')
    d_pic = Column(String(255), nullable=False, default='')
    d_picthumb = Column(String(255), nullable=False, default='')
    d_picslide = Column(String(255), nullable=False, default='')
    d_starring = Column(String(255), nullable=False, default='')
    d_directed = Column(String(255), nullable=False, default='')
    d_tag = Column(String(64), nullable=False, default='')
    d_remarks = Column(String(64), nullable=False, default='')
    d_area = Column(String(16), nullable=False, default='')
    d_lang = Column(String(16), nullable=False, default='')
    d_year = Column(SmallInteger, nullable=False, default=0)
    d_type = Column(SmallInteger, nullable=False, default=0)
    d_type_expand = Column(String(255), nullable=False, default='')
    d_class = Column(String(255), nullable=False, default='')
    d_topic = Column(String(255), nullable=False, default='0')
    d_hide = Column(Integer, nullable=False, default=0)
    d_lock = Column(Integer, nullable=False, default=0)
    d_state = Column(Integer, nullable=False, default=0)
    d_level = Column(Integer, nullable=False, default=0)
    d_usergroup = Column(SmallInteger, nullable=False, default=0)
    d_stint = Column(SmallInteger, nullable=False, default=0)
    d_stintdown = Column(SmallInteger, nullable=False, default=0)
    d_hits = Column(Integer, nullable=False, default=0)
    d_dayhits = Column(Integer, nullable=False, default=0)
    d_weekhits = Column(Integer, nullable=False, default=0)
    d_monthhits = Column(Integer, nullable=False, default=0)
    # merged = Column(Integer, nullable=False, default=0)
    d_duration = Column(SmallInteger, nullable=False, default=0)
    d_up = Column(Integer, nullable=False, default=0)
    d_down = Column(Integer, nullable=False, default=0)
    d_score = Column(DECIMAL(3, 1), nullable=False, default=0.0)
    d_scoreall = Column(Integer, nullable=False, default=0)
    d_scorenum = Column(SmallInteger, nullable=False, default=0)
    d_addtime = Column(Integer, nullable=False, default=0)
    d_time = Column(Integer, nullable=False, default='0')
    d_hitstime = Column(Integer, nullable=False, default='0')
    d_maketime = Column(Integer, nullable=False, default='0')
    d_content = Column(Text, nullable=False)
    d_playfrom = Column(String(255), nullable=False, default='')
    d_playserver = Column(String(255), nullable=False, default='')
    d_playnote = Column(String(255), nullable=False, default='')
    d_playurl = Column(Text, nullable=False)
    d_downfrom = Column(String(255), nullable=False, default='')
    d_downserver = Column(String(255), nullable=False, default='')
    d_downnote = Column(String(255), nullable=False, default='')
    d_downurl = Column(MEDIUMTEXT, nullable=False)
