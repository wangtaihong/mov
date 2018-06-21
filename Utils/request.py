#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-26 11:58:38
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    :
# @Version : $Id$

# coding:utf-8
import requests, chardet
import sys
import time
reload(sys)
sys.setdefaultencoding('utf8')
import user_agent


def requests_get(url, session = None,headers=None, data={}, timeout=60,cookies=None):
    retry = 5
    print(url)
    if not headers:
        headers = {}
        ua = user_agent.generate_navigator(os=None, navigator=None, platform=None, device_type=None)
        headers["User-Agent"] = ua["user_agent"]
    while retry > 0:
        try:
            if session==None:
                r = requests.get(url=url, headers=headers, timeout=timeout,params=data)
            else:
                r = session.get(url=url, headers=headers, timeout=timeout,params=data)
            if r.encoding == u'GBK':
                text = r.text
                text.decode('utf-8')
            else:
                r.encoding='utf-8'
                text = r.text
            print(chardet.detect(str(text))['encoding'])
            return text
            break
        except requests.exceptions.ProxyError as e:
            print('requests_get url:', url)
            print('requests_get ProxyError:', str(e))
            # update_session(proxy)
            # retry = 5
        except requests.exceptions.ConnectionError as e:
            print('requests_get url:', url)
            print('requests_get ConnectionError:', str(e))
            print("Connection refused by the server..sleep 5 seconds")
            time.sleep(5)
            # update_session(proxy)
        except requests.exceptions.TooManyRedirects as e:
            print('requests_get url:', url)
            print('requests_get:', str(e))
            print("TooManyRedirects by the server..sleep 5 seconds")
            time.sleep(5)
            # update_session(proxy)
        except requests.exceptions.Timeout as e:
            print('requests_get url:', url)
            print('requests_get:', str(e))
            print("Timeout by the server..sleep 5 seconds")
            time.sleep(5)
            # update_session(proxy)
            # retry = 5
        except requests.exceptions.RequestException as e:
            print('requests_get url:', url)
            print('requests_get RequestException:', str(e))
            # update_session(proxy)
        except Exception as e:
            print('requests_get url:', url)
            print('requests_get Exception:', str(e))
            # update_session(proxy)
        retry -= 1
    return False

def requests_post(url, session = None,headers=None, data=None, timeout=60,cookies=None):
    retry = 5
    if not headers:
        headers = {}
        ua = user_agent.generate_navigator(os=None, navigator=None, platform=None, device_type=None)
        headers["User-Agent"] = ua["user_agent"]
    while retry > 0:
        try:
            if session==None:
                r = requests.post(url=url, headers=headers, timeout=timeout, data=data)
            else:
                r = session.post(url=url, headers=headers, timeout=timeout,data=data)
            print("post",r.encoding)
            r.encoding='utf-8'
            return r.text
            break
        except requests.exceptions.ProxyError as e:
            print('requests_get url:', url)
            print('requests_get ProxyError:', str(e))
            # update_session(proxy)
            # retry = 5
        except requests.exceptions.ConnectionError as e:
            print('requests_get url:', url)
            print('requests_get ConnectionError:', str(e))
            print("Connection refused by the server..sleep 5 seconds")
            time.sleep(5)
            # update_session(proxy)
        except requests.exceptions.TooManyRedirects as e:
            print('requests_get url:', url)
            print('requests_get:', str(e))
            print("TooManyRedirects by the server..sleep 5 seconds")
            time.sleep(5)
            # update_session(proxy)
        except requests.exceptions.Timeout as e:
            print('requests_get url:', url)
            print('requests_get:', str(e))
            print("Timeout by the server..sleep 5 seconds")
            time.sleep(5)
            # update_session(proxy)
            # retry = 5
        except requests.exceptions.RequestException as e:
            print('requests_get url:', url)
            print('requests_get RequestException:', str(e))
            # update_session(proxy)
        except Exception as e:
            print('requests_get url:', url)
            print('requests_get Exception:', str(e))
            # update_session(proxy)
        retry -= 1
    return False