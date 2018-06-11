#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-14 08:22:12
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

import os
import re

words = u'study in 山海，大学'
# regex_str = u".*?([\u4E00-\u9FA5]+大学)"
# regex_str = u".*?([\u4E00-\u9FA5]+大学)"

# ：([^。]+?)。
re.sub(u'( [A-Za-z]*)',"",u'牛仔和hehe外星人 Cowboys & Aliens')
re.sub(u'( [A-Za-z]*)',"",u'HD高清托马斯和朋友 第一季 Thomas the Tank Engine &amp; Friends Season 1').replace(u"高清",'').replace(u"HD","")

# re.search('[^(A-Za-z)]',u'黑衣女人 The Woman in Black')
regex_str = u"[\u4E00-\u9FA5]([^[\u4E00-\u9FA5]]+?)[\u4E00-\u9FA5]"
match_obj = re.match(u'([\u4E00-\u9FA5])', words)
if match_obj:
    print(match_obj.group(1))