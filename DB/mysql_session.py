# coding:utf-8
# coding: utf8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy import inspect
import sys

sys.path.append('../')
import config
sys.path.append('./')
# print('mysql+mysqlconnector://'+config.MYSQL_USER+':'+config.MYSQL_PASSWORD+'@'+config.MYSQL_HOST+':'+config.MYSQL_PORT+'/'+config.MYSQL_DB+'')
engine = create_engine('mysql+mysqlconnector://'+config.MYSQL_USER+':'+config.MYSQL_PASSWORD+'@'+config.MYSQL_HOST+':'+config.MYSQL_PORT+'/'+config.MYSQL_DB+'')
# DBSession = sessionmaker(bind=engine)
DBSession = sessionmaker(autoflush=True,autocommit=False,bind=engine)
# session = DBSession()
# session = scoped_session(sessionmaker(autoflush=True,autocommit=False,bind=engine))
session = scoped_session(DBSession)
# self.db_engine = create_engine(DATABASE_CONNECTION_INFO, echo=False)


def find(model,params):
	inst = inspect(model)
	attr_names = [c_attr.key for c_attr in inst.mapper.column_attrs]
	data = session.query(model).filter(params).all()
	result = {}
	if data:
		for attr in attr_names:
			result[attr] = eval('data[0].' + attr)
	session.commit()
	session.close()
	return result

def select(model,params = None):
	if params is None:
		data = session.query(model).all()
	else:
		data = session.query(model).filter(params).all()
	inst = inspect(model)
	attr_names = [c_attr.key for c_attr in inst.mapper.column_attrs]
	result = []
	if data:
		for item in data:
			temp = {}
			for attr in attr_names:
				temp[attr] = eval('item.' + attr)
			result.append(temp)
	session.commit()
	session.close()
	return result
