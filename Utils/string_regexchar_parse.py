#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-25 11:43:53
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

import os, re

re_string = ["$","(",")","*","+",".","[","?","^","{","|","}","\b","\B"]  #正则字符
def regexchar_parse(doc):
	for x in re_string:
		if x in doc:
			doc = doc.replace(x,"\\"+x)
	return doc

if __name__ == '__main__':
	doc = ''''''
	regexchar_parse(doc)