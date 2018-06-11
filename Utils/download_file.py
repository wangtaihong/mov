#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-11 16:04:39
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

import requests
import os

def requests_get(url):
    retry = 5
    while retry > 0:
        try:
            return requests.get(url)
        except Exception as e:
            retry -= 1
    return False

def DownloadFile(url,path,filename):
    # local_filename = path+url.split('/')[-1]
    local_filename = filename
    r = requests.get(url)
    if r == False:
        return r
    if r.status_code == 404:
        return False
    try:
        os.makedirs(path)
    except Exception as e:
        pass
    f = open(local_filename, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024):
        if chunk:  # filter out keep-alive new chunks
            f.write(chunk)
    f.close()
    return local_filename
