#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-06-19 11:30:04
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

from api import app

if __name__ == "__main__":
    app.run(debug=True,port=8083,host='0.0.0.0')