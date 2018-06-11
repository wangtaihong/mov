# coding=utf-8
from sqlalchemy import Column, String, Integer, Text, SmallInteger
from sqlalchemy.dialects.mysql import \
    BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
    DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
    LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
    NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
    TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR, DECIMAL
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class CmsContent(Base):
    __tablename__ = 'cms_content'  # 表的名字  影视数据表
    # code = Column(String(64), charset='utf8',
    #               default=None, comment='内容code')
    code = Column(String(64),default=None, comment='内容code')
    id = Column(BIGINT, primary_key=True)
    type_name = Column(String(20), default=None, comment='内容分类名')
    user_id = Column(Integer, default=None, comment='操作用户id')
    code_cp_id = Column(String(100), default=None, comment='内容所属平台id')
    series_flag = Column(Integer, default=None, comment='多集单集标志 1多集 0单集')
    director = Column(String(50), default=None, comment='导演')
    # name = Column(String(100), charset='utf8', default=None,)
    name = Column(String(100), default=None,)
    actor = Column(String(200), default=None, comment='演员')
    image_v = Column(String(255), default=None, comment='竖版海报')
    image_h = Column(String(255), default=None, comment='横版海报')
    image_s = Column(String(255), default=None, comment='方海报')
    status = Column(Integer, default=None, comment='内容状态')
    alias = Column(String(20), default=None, comment='别名')
    small_type = Column(String(100), default=None, comment='小分类')
    kind = Column(String(100), default=None, comment='种类')
    show_time = Column(DATETIME, default=None, comment='发布时间')
    create_time = Column(DATETIME, default=None,)
    update_time = Column(DATETIME, default=None,)
    language = Column(String(20), default=None, comment='语言')
    region = Column(String(100), default=None, comment='地区')
    duration = Column(BIGINT, default=None, comment='时长')
    all_episode = Column(BIGINT, default=None, comment='总集数')
    summary = Column(String(500), default=None, comment='简介')
    source = Column(String(30), default=None, comment='来源')
    keyword = Column(String(20), default=None, comment='核心词')
    score = Column(Integer, default=None, comment='评分')
    attention_degree = Column(Integer, default=None, comment='关注度')
    search_volume = Column(BIGINT, default='0', comment='搜索量')
    comment_volume = Column(BIGINT, default='0', comment='评论量')
    playback_volume = Column(BIGINT, default='0', comment='播放量')
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
    parent_code = Column(String(100), default=None, comment='父code')
    episode = Column(Integer, default=None, comment='第几集')
    screen_writer = Column(String(255), default=None, comment='编剧')
    tag = Column(String(255), default=None, comment='标签')
    # PRIMARY KEY (`id`),
    # KEY `code` (`code`) USING HASH
    mysql_engine = 'InnoDB'
    # ENGINE=InnoDB AUTO_INCREMENT=318060 DEFAULT CHARSET=utf8mb4