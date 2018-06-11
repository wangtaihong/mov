# coding: utf8

from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Movies(Base):
    # 表的名字:
    __tablename__ = 'movies'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    desc = Column(String(60), nullable=True)
    json = Column(Text, nullable=True)
    created_at = Column(Integer, nullable=True)
